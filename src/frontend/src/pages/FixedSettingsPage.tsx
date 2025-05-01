import React, { useState, useEffect } from 'react';
import axios from 'axios';
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
  useColorModeValue,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import { AddIcon, CheckIcon, CloseIcon } from '@chakra-ui/icons';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

// Define the LearningLanguage interface locally
interface LearningLanguage {
  language: string;
  proficiency: string;
  isDefault?: boolean;
}

// Fixed settings page component
const FixedSettingsPage = () => {
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
  const [isSuccess, setIsSuccess] = useState(false);
  
  // Get user data
  const user = auth?.user;
  const loading = auth?.loading || false;
  
  // Handle redirects
  useEffect(() => {
    if (!loading && !user) {
      navigate('/signin');
    }
  }, [loading, user, navigate]);
  
  // Function to fetch the latest user data directly from the API
  const fetchUserData = async () => {
    try {
      // Get token
      let token = localStorage.getItem('lingogi_token') || '';
      if (!token) {
        const cookieToken = document.cookie
          .split(';')
          .find(c => c.trim().startsWith('lingogi_token='));
        if (cookieToken) {
          token = cookieToken.split('=')[1];
        }
      }
      
      if (!token) {
        console.error('[FixedSettingsPage] No token available to fetch user data');
        return;
      }
      
      const response = await axios.get('http://localhost:8000/api/user/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.data) {
        console.log('[FixedSettingsPage] Fresh user data loaded:', response.data);
        // Update the local state with fresh data
        updateLanguageState(response.data);
      }
    } catch (err) {
      console.error('[FixedSettingsPage] Error fetching user data:', err);
    }
  };
  
  // Helper function to extract and set language data
  const updateLanguageState = (userData: any) => {
    setNativeLanguage(userData.native_language || 'en');
    
    let languages: LearningLanguage[] = [];
    
    // Add main learning language
    if (userData.learning_language) {
      languages.push({
        language: userData.learning_language,
        proficiency: userData.proficiency || 'beginner',
        isDefault: true
      });
    }
    
    // Add additional languages - with better debugging
    if (userData.additional_languages && Array.isArray(userData.additional_languages)) {
      console.log('[FixedSettingsPage] Additional languages data:', userData.additional_languages);
      
      userData.additional_languages.forEach((lang: any) => {
        if (lang && lang.language) {
          languages.push({
            language: lang.language,
            proficiency: lang.proficiency || 'beginner',
            isDefault: !!lang.isDefault
          });
        }
      });
    } else {
      console.log('[FixedSettingsPage] No additional languages found in user data');
    }
    
    console.log('[FixedSettingsPage] Setting study languages:', languages);
    setStudyLanguages(languages);
  };
  
  // Initialize data from user
  useEffect(() => {
    if (user) {
      updateLanguageState(user);
    }
  }, [user]);
  
  // Initial data load on component mount
  useEffect(() => {
    // Fetch fresh data when the component mounts
    fetchUserData();
  }, []);
  
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
    setError('');
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
  
  // Save settings using direct approach that worked previously
  const handleSaveSettings = async () => {
    setIsSaving(true);
    setError('');
    setIsSuccess(false);
    
    try {
      // Get token - using the same approach as the working SettingsPage
      let token = '';
      // Get token from various sources for maximum reliability
      token = localStorage.getItem('lingogi_token') || '';
      if (!token) {
        const cookieToken = document.cookie
          .split(';')
          .find(c => c.trim().startsWith('lingogi_token='));
        if (cookieToken) {
          token = cookieToken.split('=')[1];
        }
      }
      
      if (!token) {
        setError('Authentication token not found. Please sign in again.');
        setIsSaving(false);
        return;
      }
      
      console.log('[FixedSettingsPage] Token found:', token ? 'Yes (length: ' + token.length + ')' : 'No');
      
      // Properly structure language data according to the backend model
      // First, find the default language
      const defaultLang = studyLanguages.find(lang => lang.isDefault);
      
      if (!defaultLang) {
        setError('Please set a default language');
        setIsSaving(false);
        return;
      }
      
      // All non-default languages are additional_languages
      // Make sure to include isDefault property for each language
      const additionalLangs = studyLanguages
        .filter(lang => !lang.isDefault)
        .map(lang => ({
          language: lang.language,
          proficiency: lang.proficiency,
          isDefault: false
        }));
      
      console.log('[FixedSettingsPage] Default language:', defaultLang);
      console.log('[FixedSettingsPage] Additional languages:', additionalLangs);
      
      // Create update data object according to backend model
      const updateData = {
        name: user?.name || '',
        native_language: nativeLanguage,
        learning_language: defaultLang.language,
        proficiency: defaultLang.proficiency,
        additional_languages: additionalLangs
      };
      
      console.log('[FixedSettingsPage] Sending data:', JSON.stringify(updateData));
      
      // Make API request with axios - using same method as working SettingsPage
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
      
      console.log('[FixedSettingsPage] API response:', response.data);
      
      // Success handling
      toast({
        title: 'Settings saved',
        description: 'Your profile settings have been updated successfully.',
        status: 'success',
        duration: 5000,
        isClosable: true,
        position: 'top'
      });
      
      setIsSuccess(true);
      
      // Fetch the updated user profile to refresh our UI with the latest data
      console.log('[FixedSettingsPage] Settings saved successfully, fetching updated data');
      
      // Wait a moment to ensure the database has been updated
      setTimeout(async () => {
        // Fetch fresh data directly from the API
        await fetchUserData();
        
        // Update success toast to confirm the fetch completed
        toast({
          title: 'Settings updated',
          description: 'Your language preferences have been saved and updated.',
          status: 'success',
          duration: 5000,
          isClosable: true,
          position: 'top'
        });
      }, 500);
    } catch (err: any) { // Type assertion for better error handling
      console.error('[FixedSettingsPage] Error saving settings:', err?.response?.data || err);
      
      let errorMessage = 'Failed to update settings';
      
      if (err?.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        errorMessage = err.response.data?.detail || 
                       err.response.data?.message || 
                       `Server error: ${err.response.status}`;
        console.error('[FixedSettingsPage] Server response error:', err.response.status, err.response.data);
      } else if (err?.request) {
        // The request was made but no response was received
        errorMessage = 'No response from server. Please check your network connection.';
        console.error('[FixedSettingsPage] No response error:', err.request);
      } else {
        // Something happened in setting up the request
        errorMessage = err?.message || 'Error preparing request';
        console.error('[FixedSettingsPage] Request setup error:', err?.message);
      }
      
      setError(errorMessage);
    } finally {
      setIsSaving(false);
    }
  };
  
  // Main render
  if (loading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    );
  }
  
  return (
    <Container maxW="800px" py={8}>
      <VStack spacing={6} align="stretch" bg={bgColor} p={6} borderRadius="md" boxShadow="md">
        <Heading as="h1" size="xl">Language Settings</Heading>
        
        {/* Native Language */}
        <Box>
          <Heading as="h2" size="md" mb={4}>Your Native Language</Heading>
          <FormControl>
            <FormLabel>Select your native language</FormLabel>
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
            </Select>
          </FormControl>
        </Box>
        
        {/* Study Languages */}
        <Box>
          <Heading as="h2" size="md" mb={4}>Languages You're Learning</Heading>
          
          {/* Existing languages */}
          <VStack spacing={3} align="stretch" mb={6}>
            {studyLanguages.length === 0 ? (
              <Text color="gray.500">No languages added yet. Add one below.</Text>
            ) : (
              studyLanguages.map((lang, index) => (
                <HStack key={index} p={2} bg={lang.isDefault ? "blue.50" : "gray.50"} borderRadius="md">
                  <Text flex="1">
                    {lang.language === 'en' ? 'English' : 
                     lang.language === 'ko' ? 'Korean' : 
                     lang.language === 'ja' ? 'Japanese' : 
                     lang.language === 'zh' ? 'Chinese' : 
                     lang.language === 'es' ? 'Spanish' : 
                     lang.language === 'fr' ? 'French' : lang.language}
                  </Text>
                  <Text flex="1">
                    {lang.proficiency === 'beginner' ? 'Beginner' : 
                     lang.proficiency === 'intermediate' ? 'Intermediate' : 
                     lang.proficiency === 'advanced' ? 'Advanced' : lang.proficiency}
                  </Text>
                  <HStack>
                    {!lang.isDefault && (
                      <IconButton
                        aria-label="Set as default"
                        icon={<CheckIcon />}
                        size="sm"
                        colorScheme="blue"
                        onClick={() => handleSetDefaultLanguage(index)}
                      />
                    )}
                    <IconButton
                      aria-label="Remove language"
                      icon={<CloseIcon />}
                      size="sm"
                      colorScheme="red"
                      onClick={() => handleRemoveLanguage(index)}
                    />
                  </HStack>
                  {lang.isDefault && <Text fontSize="sm" color="blue.500">Default</Text>}
                </HStack>
              ))
            )}
          </VStack>
          
          {/* Add new language */}
          <HStack mb={4}>
            <FormControl flex="1">
              <FormLabel>Language</FormLabel>
              <Select 
                value={newLanguage} 
                onChange={(e) => setNewLanguage(e.target.value)}
                placeholder="Select language"
              >
                <option value="en">English</option>
                <option value="ko">Korean</option>
                <option value="ja">Japanese</option>
                <option value="zh">Chinese</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
              </Select>
            </FormControl>
            <FormControl flex="1">
              <FormLabel>Proficiency</FormLabel>
              <Select 
                value={newProficiency} 
                onChange={(e) => setNewProficiency(e.target.value)}
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </Select>
            </FormControl>
            <IconButton
              aria-label="Add language"
              icon={<AddIcon />}
              mt={8}
              colorScheme="green"
              onClick={handleAddLanguage}
            />
          </HStack>
        </Box>
        
        {/* Error message */}
        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}
        
        {/* Success message */}
        {isSuccess && (
          <Alert status="success">
            <AlertIcon />
            Settings updated successfully!
          </Alert>
        )}
        
        {/* Submit button */}
        <Button 
          colorScheme="blue" 
          size="lg" 
          onClick={handleSaveSettings}
          isLoading={isSaving}
          loadingText="Saving..."
        >
          Save Settings
        </Button>
      </VStack>
    </Container>
  );
};

export default FixedSettingsPage;
