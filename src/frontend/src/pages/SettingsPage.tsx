import React, { useState, useEffect, useContext } from 'react';
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
  useToast,
  IconButton,
  useColorModeValue
} from '@chakra-ui/react';
import { AddIcon, CheckIcon, CloseIcon } from '@chakra-ui/icons';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getToken } from '../utils/tokenUtils';

// Define the LearningLanguage interface locally
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
 * Simplified Settings page that allows users to manage language preferences
 */
const SettingsPage = () => {
  // All hooks at the top level to follow React's rules
  const navigate = useNavigate();
  const toast = useToast();
  const auth = useAuth();
  
  // Form state
  const [name, setName] = useState('');
  const [nativeLanguage, setNativeLanguage] = useState('en');
  const [studyLanguages, setStudyLanguages] = useState<LearningLanguage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Get user data from auth context
  const user = auth?.user;
  
  // Form state
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [nativeLanguage, setNativeLanguage] = useState('en');
  const [studyLanguages, setStudyLanguages] = useState<LearningLanguage[]>([]);
  const [availableLanguages, setAvailableLanguages] = useState<{ code: string; name: string; }[]>([]);
  const [error, setError] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  // Add language modal
  const [newLanguage, setNewLanguage] = useState('');
  const [newProficiency, setNewProficiency] = useState('beginner');
  
  // Colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
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

  // Redirect if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      console.log('[SettingsPage] Not authenticated, redirecting to sign in');
      navigate('/signin');
    }
  }, [loading, user, navigate]);

  // Initialize user data
  useEffect(() => {
    if (user) {
      // Set initial values from user object
      setName(user.name || '');
      setEmail(user.email || '');
      setNativeLanguage(user.native_language || 'en');

      // Set initial study languages array
      let initialLanguages = [];

      // Add main learning language if it exists
      if (user.learning_language) {
        initialLanguages.push({
          language: user.learning_language,
          proficiency: user.proficiency || 'intermediate',
          isDefault: true
        });
      }

      // Add additional languages if they exist
      if (user.additional_languages && Array.isArray(user.additional_languages)) {
        user.additional_languages.forEach(lang => {
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
  }, [user]);

  // Handle saving settings
  const handleSaveSettings = async () => {
    setIsSaving(true);
    setError('');
    setSaveSuccess(false);

    try {
      // Prepare the update data
      const updateData = {
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
        const responseData = response.data;
        
        // Axios response handling is done above
        
        // Success notification
        toast({
          title: 'Settings saved',
          description: 'Your profile settings have been updated successfully.',
          status: 'success',
          duration: 5000,
          isClosable: true,
          position: 'top'
        });
        
        setSaveSuccess(true);
        setHasChanges(false);
      } catch (err: any) {
        console.error('[SettingsPage] API request failed:', err);
        
        // Display a more detailed error message
        const errorMessage = err?.response?.data?.detail ||
                         err?.message ||
                         'Failed to update profile. Please check your connection and try again.';
        
        setError(errorMessage);
        
        toast({
          title: 'Settings update failed',
          description: errorMessage,
          status: 'error',
          duration: 7000,
          isClosable: true,
          position: 'top'
        });
      }
    } catch (err: any) {
      console.error('Failed to update profile:', err);
      setError(err.response?.data?.detail || 'Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  // Simple helper function for debugging
  const logDebug = (message: string) => {
    console.log(`[SettingsPage] ${message}`);
  };
  
  // Show loading spinner while authentication status is being checked
  if (loading) {
    return (
      <Container maxW="container.md" py={10}>
        <Center h="200px">
          <Spinner size="xl" />
          <Text ml={4}>Loading your settings...</Text>
        </Center>
      </Container>
    );
  }
  
  // Redirect happens in the useEffect if not authenticated
  if (!user) {
    return null;
  }
  
  // Get language label by value
  const getLanguageLabel = (value: string) => {
    return LANGUAGE_OPTIONS.find(lang => lang.value === value)?.label || value;
  };
  
  // Get proficiency label
  const getProficiencyLabel = (value: string) => {
    switch(value) {
      case 'beginner': return 'Beginner';
      case 'intermediate': return 'Intermediate';
      case 'advanced': return 'Advanced';
      default: return value;
    }
  };
  
  if (loading) {
    return (
      <Container maxW="container.md" py={10}>
        <Flex justify="center" align="center" minH="60vh">
          <Text>Loading settings...</Text>
        </Flex>
      </Container>
    );
  }
  
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
        
        <Box p={6} bg={bgColor} borderRadius="md" borderWidth="1px" borderColor={borderColor}>
          <VStack spacing={6} align="stretch">
            <Heading as="h2" size="md">Personal Information</Heading>
            
            <FormControl>
              <FormLabel>Name</FormLabel>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </FormControl>
            
            <FormControl>
              <FormLabel>Email</FormLabel>
              <Input
                value={email}
                isReadOnly
                bg={useColorModeValue('gray.100', 'gray.700')}
              />
              <FormHelperText>Email cannot be changed</FormHelperText>
            </FormControl>
            
            <FormControl>
              <FormLabel>My Native Language</FormLabel>
              <Select
                value={nativeLanguage}
                onChange={(e) => setNativeLanguage(e.target.value)}
              >
                {LANGUAGE_OPTIONS.map(lang => (
                  <option key={lang.value} value={lang.value}>{lang.label}</option>
                ))}
              </Select>
            </FormControl>
          </VStack>
        </Box>
        
        <Box p={6} bg={bgColor} borderRadius="md" borderWidth="1px" borderColor={borderColor}>
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
                    borderColor={lang.isDefault ? 'blue.500' : borderColor}
                    bg={lang.isDefault ? useColorModeValue('blue.50', 'blue.900') : 'transparent'}
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
        
        {saveSuccess && (
          <Alert status="success" mt={4} variant="solid" colorScheme="green">
            <AlertIcon />
            Your settings have been saved successfully!
          </Alert>
        )}
        
        {error && (
          <Alert status="error" mt={4} variant="solid">
            <AlertIcon />
            {error}
          </Alert>
        )}
      </VStack>
      
      {/* Add Language Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
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

// Simple component for language settings
const SettingsPage = () => {
  // All hooks at the top level
  const navigate = useNavigate();
  const toast = useToast();
  const auth = useAuth();
  const bgColor = useColorModeValue('white', 'gray.800');
  
  // State for language preferences
  const [nativeLanguage, setNativeLanguage] = useState('en');
  const [studyLanguages, setStudyLanguages] = useState<LearningLanguage[]>([]);
  const [newLanguage, setNewLanguage] = useState('');
  const [newProficiency, setNewProficiency] = useState('beginner');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  
  // Get user data
  const user = auth?.user;
  const loading = auth?.loading || false;
  
  // Handle redirects
  useEffect(() => {
    if (!loading && !user) {
      navigate('/signin');
    }
  }, [loading, user, navigate]);
  
  // Initialize data from user
  useEffect(() => {
    if (user) {
      setNativeLanguage(user.native_language || 'en');
      
      let languages: LearningLanguage[] = [];
      
      // Add main learning language
      if (user.learning_language) {
        languages.push({
          language: user.learning_language,
          proficiency: user.proficiency || 'beginner',
          isDefault: true
        });
      }
      
      // Add additional languages
      if (user.additional_languages && Array.isArray(user.additional_languages)) {
        user.additional_languages.forEach(lang => {
          languages.push({
            language: lang.language,
            proficiency: lang.proficiency,
            isDefault: false
          });
        });
      }
      
      setStudyLanguages(languages);
    }
  }, [user]);
  
  // Add a new language
  const handleAddLanguage = () => {
    if (!newLanguage) return;
    
    // Check if language already exists
    if (studyLanguages.some(lang => lang.language === newLanguage)) {
      setError('You are already studying this language');
      return;
    }
    
    const updatedLanguages = [...studyLanguages];
    updatedLanguages.push({
      language: newLanguage,
      proficiency: newProficiency,
      isDefault: updatedLanguages.length === 0 // Make default if first
    });
    
    setStudyLanguages(updatedLanguages);
    setNewLanguage('');
    setNewProficiency('beginner');
  };
  
  // Remove a language
  const handleRemoveLanguage = (index: number) => {
    const updatedLanguages = [...studyLanguages];
    
    // If removing default, make another default
    if (updatedLanguages[index].isDefault && updatedLanguages.length > 1) {
      const nextIndex = index === 0 ? 1 : 0;
      updatedLanguages[nextIndex].isDefault = true;
    }
    
    updatedLanguages.splice(index, 1);
    setStudyLanguages(updatedLanguages);
  };
  
  // Set a language as default
  const handleSetDefaultLanguage = (index: number) => {
    const updatedLanguages = [...studyLanguages];
    
    // Reset all defaults
    updatedLanguages.forEach(lang => {
      lang.isDefault = false;
    });
    
    updatedLanguages[index].isDefault = true;
    setStudyLanguages(updatedLanguages);
  };
  
  // Save settings
  const handleSaveSettings = async () => {
    setIsSaving(true);
    setError('');
    
    try {
      // Get token
      const token = localStorage.getItem('lingogi_token') || 
                   document.cookie.replace(/(?:(?:^|.*;\s*)lingogi_token\s*=\s*([^;]*).*$)|^.*$/, '$1');
      
      if (!token) {
        setError('Authentication token not found');
        setIsSaving(false);
        return;
      }
      
      // Prepare data
      const defaultLang = studyLanguages.find(lang => lang.isDefault);
      const additionalLangs = studyLanguages.filter(lang => !lang.isDefault);
      
      const updateData = {
        name: user?.name || '',
        native_language: nativeLanguage
      };
      
      if (defaultLang) {
        Object.assign(updateData, {
          learning_language: defaultLang.language,
          proficiency: defaultLang.proficiency,
          additional_languages: additionalLangs
        });
      }
      
      // Make the API request directly with fetch
      const response = await fetch('http://localhost:8000/api/user/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updateData)
      });
      
      if (response.ok) {
        toast({
          title: 'Settings saved',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update settings');
      }
    } catch (err: any) {
      console.error('Error saving settings:', err);
      setError(err.message || 'Network error');
    } finally {
      setIsSaving(false);
    }
  };
  
  // Loading state
  if (loading) {
    return (
      <Container maxW="container.md" py={10}>
        <Center h="300px">
          <Spinner size="xl" />
        </Center>
      </Container>
    );
  }
  
  return (
    <Container maxW="container.md" py={10}>
      <VStack spacing={8} align="stretch">
        <Heading>Language Settings</Heading>
        
        {error && <Text color="red.500">{error}</Text>}
        
        <Box p={5} shadow="md" borderWidth="1px" bg={bgColor}>
          <VStack spacing={4} align="stretch">
            <FormControl>
              <FormLabel>Native Language</FormLabel>
              <Select 
                value={nativeLanguage} 
                onChange={(e) => setNativeLanguage(e.target.value)}
              >
                <option value="en">English</option>
                <option value="ko">Korean</option>
                <option value="ja">Japanese</option>
                <option value="zh">Chinese</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
              </Select>
            </FormControl>
            
            <Box>
              <Heading size="sm" mb={2}>Languages You're Learning</Heading>
              {studyLanguages.length === 0 ? (
                <Text color="gray.500">No languages added yet</Text>
              ) : (
                <VStack align="stretch" spacing={2}>
                  {studyLanguages.map((lang, index) => (
                    <HStack key={index} p={2} borderWidth="1px" borderRadius="md">
                      <Text flex="1">{lang.language}</Text>
                      <Text color="gray.500">{lang.proficiency}</Text>
                      {lang.isDefault && <Text color="green.500">(Default)</Text>}
                      <IconButton
                        aria-label="Set as default"
                        icon={<CheckIcon />}
                        size="sm"
                        colorScheme={lang.isDefault ? 'green' : 'gray'}
                        onClick={() => handleSetDefaultLanguage(index)}
                      />
                      <IconButton
                        aria-label="Remove language"
                        icon={<CloseIcon />}
                        size="sm"
                        colorScheme="red"
                        onClick={() => handleRemoveLanguage(index)}
                      />
                    </HStack>
                  ))}
                </VStack>
              )}
            </Box>
            
            <Box>
              <Heading size="sm" mb={2}>Add Language</Heading>
              <HStack>
                <Select 
                  placeholder="Select language" 
                  value={newLanguage}
                  onChange={(e) => setNewLanguage(e.target.value)}
                >
                  <option value="en">English</option>
                  <option value="ko">Korean</option>
                  <option value="ja">Japanese</option>
                  <option value="zh">Chinese</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </Select>
                <Select
                  value={newProficiency}
                  onChange={(e) => setNewProficiency(e.target.value)}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </Select>
                <Button
                  leftIcon={<AddIcon />}
                  colorScheme="blue"
                  onClick={handleAddLanguage}
                >
                  Add
                </Button>
              </HStack>
            </Box>
            
            <Button 
              colorScheme="green" 
              mt={4} 
              onClick={handleSaveSettings} 
              isLoading={isSaving}
            >
              Save Settings
            </Button>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default SettingsPage;
