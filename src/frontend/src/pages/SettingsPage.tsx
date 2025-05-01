import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Container, 
  Heading, 
  Text, 
  VStack, 
  HStack,
  FormControl, 
  FormLabel, 
  Select, 
  Spinner, 
  Center, 
  IconButton,
  Input,
  FormHelperText,
  Flex,
  Tag,
  Alert,
  AlertIcon,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton
} from '@chakra-ui/react';
import { AddIcon, CheckIcon, CloseIcon } from '@chakra-ui/icons';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getToken } from '../utils/tokenUtils';

// Define the LearningLanguage interface
interface LearningLanguage {
  language: string;
  proficiency: string;
  isDefault?: boolean;
}

// Define language options
const LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'ko', label: 'Korean' },
  { value: 'ja', label: 'Japanese' },
  { value: 'zh', label: 'Chinese' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
  { value: 'ru', label: 'Russian' },
];

/**
 * Settings page wrapper component
 * This separates authentication logic from the main content
 */
const SettingsPage = () => {
  // Basic non-context state
  const [isReady, setIsReady] = useState(false);
  
  // Auth-related hooks
  const navigate = useNavigate();
  const auth = useAuth();
  
  // Effect to check authentication status
  useEffect(() => {
    if (!auth.loading) {
      if (!auth.user) {
        // Redirect to sign in if not authenticated
        navigate('/signin');
      } else {
        // User is authenticated, content can be rendered
        setIsReady(true);
      }
    }
  }, [auth.loading, auth.user, navigate]);
  
  // Show loading spinner while checking auth
  if (!isReady) {
    return (
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    );
  }
  
  // Once authenticated, render the main content
  return <SettingsPageContent />;
};

/**
 * Main settings page content component
 * Only rendered after authentication is confirmed
 */
// Simple page content without dependency on context hooks
const SettingsPageContent = () => {
  // Get references passed from parent
  const navigate = useNavigate();
  const auth = useAuth();
  
  // Local state first - before any potential context dependencies
  const [isModalOpen, setIsModalOpen] = useState(false);
  const onOpen = () => setIsModalOpen(true);
  const onClose = () => setIsModalOpen(false);
  
  // Form state
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [nativeLanguage, setNativeLanguage] = useState('en');
  const [studyLanguages, setStudyLanguages] = useState<LearningLanguage[]>([]);
  const [loading, setLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState('');
  
  // Add language modal
  const [newLanguage, setNewLanguage] = useState('');
  const [newProficiency, setNewProficiency] = useState('beginner');
  
  // Get user data from auth context
  
  // Log authentication status
  useEffect(() => {
    console.log('[SettingsPage] Authentication status:', 
      auth.loading ? 'loading' : (auth.user ? 'authenticated' : 'not authenticated'));
  }, [auth.loading, auth.user]);

  // Initialize user data
  useEffect(() => {
    if (auth.user) {
      // Set initial values from user object
      setName(auth.user.name || '');
      setEmail(auth.user.email || '');
      setNativeLanguage(auth.user.native_language || 'en');

      // Set initial study languages array
      let initialLanguages = [];

      // Add main learning language if it exists
      if (auth.user.learning_language) {
        initialLanguages.push({
          language: auth.user.learning_language,
          proficiency: auth.user.proficiency || 'intermediate',
          isDefault: true
        });
      }

      // Add additional languages if they exist
      if (auth.user.additional_languages && Array.isArray(auth.user.additional_languages)) {
        auth.user.additional_languages.forEach(lang => {
          if (lang && lang.language) {
            initialLanguages.push({
              language: lang.language,
              proficiency: lang.proficiency || 'beginner',
              isDefault: false
            });
          }
        });
      }

      setStudyLanguages(initialLanguages);
    }
  }, [auth.user]);
  
  // Handle setting a language as default
  const handleSetDefaultLanguage = (index: number) => {
    const updatedLanguages = [...studyLanguages];
    
    // Reset all defaults
    updatedLanguages.forEach(lang => {
      lang.isDefault = false;
    });
    
    // Set the new default
    updatedLanguages[index].isDefault = true;
    
    setStudyLanguages(updatedLanguages);
    setHasChanges(true);
  };
  
  // Handle removing a language
  const handleRemoveLanguage = (index: number) => {
    const updatedLanguages = [...studyLanguages];
    
    // If removing the default language, make another one default if available
    if (updatedLanguages[index].isDefault && updatedLanguages.length > 1) {
      // Find next language to make default
      const nextDefaultIndex = index === 0 ? 1 : 0;
      updatedLanguages[nextDefaultIndex].isDefault = true;
    }
    
    updatedLanguages.splice(index, 1);
    setStudyLanguages(updatedLanguages);
    setHasChanges(true);
  };
  
  // Handle adding a new language
  const handleAddLanguage = () => {
    // Validate input
    if (!newLanguage) {
      setError('Please select a language');
      return;
    }
    
    // Check if language already exists
    if (studyLanguages.some(lang => lang.language === newLanguage)) {
      setError('You are already studying this language');
      return;
    }
    
    // Add new language
    const updatedLanguages = [...studyLanguages];
    updatedLanguages.push({
      language: newLanguage,
      proficiency: newProficiency,
      isDefault: updatedLanguages.length === 0 // Make it default if it's the first language
    });
    
    setStudyLanguages(updatedLanguages);
    setNewLanguage('');
    setNewProficiency('beginner');
    setError('');
    onClose();
    setHasChanges(true);
  };

  // Handle saving settings
  const handleSaveSettings = async () => {
    setIsSaving(true);
    setError('');
    setSaveSuccess(false);

    try {
      // Prepare the update data
      const updateData: any = {
        name,
        native_language: nativeLanguage
      };

      // Find the default language and other languages
      const defaultLang = studyLanguages.find(lang => lang.isDefault === true);
      const additionalLangs = studyLanguages.filter(lang => !lang.isDefault);

      // Add learning language and proficiency fields
      if (defaultLang) {
        Object.assign(updateData, {
          learning_language: defaultLang.language,
          proficiency: defaultLang.proficiency,
          additional_languages: additionalLangs
        });
      } else if (studyLanguages.length > 0) {
        // If no default is set but we have languages, make the first one default
        const firstLang = studyLanguages[0];
        Object.assign(updateData, {
          learning_language: firstLang.language,
          proficiency: firstLang.proficiency,
          additional_languages: studyLanguages.slice(1)
        });
      } else {
        // No languages set
        Object.assign(updateData, {
          learning_language: '',
          proficiency: 'beginner',
          additional_languages: []
        });
      }

      console.log('Updating profile with:', updateData);
      
      // Get the authentication token
      const token = getToken();
      if (!token) {
        setError('Authentication token not found. Please sign in again.');
        setIsSaving(false);
        return;
      }
      
      try {
        console.log('[SettingsPage] Saving profile settings...');
        
        // Use axios directly - this is what worked in previous versions
        console.log('[SettingsPage] Making API request with axios');
        
        const response = await axios.put(
          'http://localhost:8000/api/user/profile',
          updateData,
          {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        console.log('[SettingsPage] API request successful:', response.data);
        
        // Success notification
        console.log('Profile saved successfully!');
        
        // Update the user data in AuthContext to reflect the changes
        await auth.updateUser();
        console.log('[SettingsPage] User context updated after save');
        
        setSaveSuccess(true);
        setHasChanges(false);
      } catch (err: any) {
        console.error('[SettingsPage] API request failed:', err);
        
        // Display a more detailed error message
        const errorMessage = err?.response?.data?.detail ||
                         err?.message ||
                         'Failed to update profile. Please check your connection and try again.';
        
        setError(errorMessage);
        
        console.error('Failed to save profile. Please try again.');
      }
    } catch (err: any) {
      console.error('Failed to update profile:', err);
      setError(err.response?.data?.detail || 'Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  // Helper functions
  const getLanguageLabel = (value: string) => {
    return LANGUAGE_OPTIONS.find(lang => lang.value === value)?.label || value;
  };
  
  const getProficiencyLabel = (value: string) => {
    switch(value) {
      case 'beginner': return 'Beginner';
      case 'intermediate': return 'Intermediate';
      case 'advanced': return 'Advanced';
      default: return value;
    }
  };
  
  // Loading state is now handled at the top of the component
  
  return (
    <Container maxW="container.md" py={10}>
      <VStack spacing={8} align="stretch">
        <Heading as="h1" size="xl">Account Settings</Heading>
        
        {saveSuccess && (
          <Alert status="success">
            <AlertIcon />
            Your settings have been saved successfully!
          </Alert>
        )}
        
        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}
        
        <Box p={6} bg="white" borderRadius="md" borderWidth="1px" borderColor="gray.200">
          <VStack spacing={6} align="stretch">
            <Heading as="h2" size="md">Personal Information</Heading>
            
            <FormControl>
              <FormLabel>Name</FormLabel>
              <Input
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  setHasChanges(true);
                }}
              />
            </FormControl>
            
            <FormControl>
              <FormLabel>Email</FormLabel>
              <Input
                value={email}
                isReadOnly
                bg="gray.100"
              />
              <FormHelperText>Email cannot be changed</FormHelperText>
            </FormControl>
            
            <FormControl>
              <FormLabel>My Native Language</FormLabel>
              <Select
                value={nativeLanguage}
                onChange={(e) => {
                  setNativeLanguage(e.target.value);
                  setHasChanges(true);
                }}
              >
                {LANGUAGE_OPTIONS.map(lang => (
                  <option key={lang.value} value={lang.value}>{lang.label}</option>
                ))}
              </Select>
            </FormControl>
          </VStack>
        </Box>
        
        <Box p={6} bg="white" borderRadius="md" borderWidth="1px" borderColor="gray.200">
          <VStack spacing={6} align="stretch">
            <Flex justify="space-between" align="center">
              <Heading as="h2" size="md">Languages I'm Learning</Heading>
              <Button leftIcon={<AddIcon />} colorScheme="blue" size="sm" onClick={onOpen}>
                Add Language
              </Button>
            </Flex>
            
            {studyLanguages.length === 0 ? (
              <Alert status="info">
                <AlertIcon />
                You haven't added any languages to study. Add a language to get started.
              </Alert>
            ) : (
              <VStack spacing={4} align="stretch">
                {studyLanguages.map((lang, index) => (
                  <Flex 
                    key={index} 
                    p={4} 
                    borderWidth="1px" 
                    borderRadius="md" 
                    borderColor={lang.isDefault ? 'blue.500' : 'gray.200'}
                    bg={lang.isDefault ? 'blue.50' : 'transparent'}
                    justify="space-between"
                    align="center"
                  >
                    <VStack align="start" spacing={1}>
                      <Text fontWeight="bold">{getLanguageLabel(lang.language)}</Text>
                      <HStack>
                        <Tag size="sm" colorScheme={lang.isDefault ? 'blue' : 'gray'}>
                          {lang.isDefault ? 'Default' : 'Additional'}
                        </Tag>
                        <Tag size="sm">
                          {getProficiencyLabel(lang.proficiency)}
                        </Tag>
                      </HStack>
                    </VStack>
                    
                    <HStack>
                      {!lang.isDefault && (
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => handleSetDefaultLanguage(index)}
                        >
                          Make Default
                        </Button>
                      )}
                      <Button 
                        size="sm" 
                        colorScheme="red" 
                        variant="ghost"
                        isDisabled={studyLanguages.length === 1}
                        onClick={() => handleRemoveLanguage(index)}
                      >
                        Remove
                      </Button>
                    </HStack>
                  </Flex>
                ))}
              </VStack>
            )}
          </VStack>
        </Box>
        
        <Flex justify="flex-end">
          <Button 
            colorScheme="blue" 
            isLoading={isSaving} 
            isDisabled={!hasChanges || studyLanguages.length === 0}
            onClick={handleSaveSettings}
          >
            Save Changes
          </Button>
        </Flex>
      </VStack>
      
      {/* Add Language Modal */}
      <Modal isOpen={isModalOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add New Language</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              {error && (
                <Alert status="error" mb={5}>
                  <AlertIcon />
                  {error}
                </Alert>
              )}
              
              <FormControl isRequired>
                <FormLabel>Language</FormLabel>
                <Select 
                  value={newLanguage} 
                  onChange={(e) => setNewLanguage(e.target.value)}
                >
                  <option value="">Select a language</option>
                  {LANGUAGE_OPTIONS.map(lang => (
                    <option 
                      key={lang.value} 
                      value={lang.value}
                      disabled={studyLanguages.some(l => l.language === lang.value)}
                    >
                      {lang.label}
                    </option>
                  ))}
                </Select>
              </FormControl>
              
              <FormControl>
                <FormLabel>Proficiency Level</FormLabel>
                <Select 
                  value={newProficiency}
                  onChange={(e) => setNewProficiency(e.target.value)}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </Select>
              </FormControl>
            </VStack>
          </ModalBody>
          
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="blue" onClick={handleAddLanguage}>
              Add Language
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Container>
  );
};

export default SettingsPage;
