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
import { useTranslation } from 'react-i18next';

// Define the LearningLanguage interface locally
interface LearningLanguage {
  language: string;
  proficiency: string;
  isDefault?: boolean;
}

// Simple component for language settings
const SimpleSettingsPage = () => {
  // All hooks at the top level
  const { t } = useTranslation();
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
          if (lang && lang.language) {
            languages.push({
              language: lang.language,
              proficiency: lang.proficiency || 'beginner',
              isDefault: false
            });
          }
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
          title: t('settings.saveSuccess'),
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
          <VStack spacing={3}>
            <Spinner size="xl" />
            <Text>{t('settings.loadingProfile')}</Text>
          </VStack>
        </Center>
      </Container>
    );
  }
  
  return (
    <Container maxW="container.md" py={10}>
      <VStack spacing={8} align="stretch">
        <Heading>{t('settings.languageSettings')}</Heading>
        
        {error && <Text color="red.500">{error}</Text>}
        
        <Box p={5} shadow="md" borderWidth="1px" bg={bgColor}>
          <VStack spacing={4} align="stretch">
            <FormControl>
              <FormLabel>{t('settings.yourNativeLanguage')}</FormLabel>
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
              <Heading size="sm" mb={2}>{t('settings.learningLanguages')}</Heading>
              {studyLanguages.length === 0 ? (
                <Text color="gray.500">{t('settings.noLanguagesAddedYetShort')}</Text>
              ) : (
                <VStack align="stretch" spacing={2}>
                  {studyLanguages.map((lang, index) => (
                    <HStack key={index} p={2} borderWidth="1px" borderRadius="md">
                      <Text flex="1">{lang.language}</Text>
                      <Text color="gray.500">{lang.proficiency}</Text>
                      {lang.isDefault && <Text color="green.500">(Default)</Text>}
                      <IconButton
                        aria-label={t('settings.setAsDefault')}
                        icon={<CheckIcon />}
                        size="sm"
                        colorScheme={lang.isDefault ? 'green' : 'gray'}
                        onClick={() => handleSetDefaultLanguage(index)}
                      />
                      <IconButton
                        aria-label={t('settings.removeLanguage')}
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
              <Heading size="sm" mb={2}>{t('settings.addLanguage')}</Heading>
              <HStack>
                <Select 
                  placeholder={t('settings.selectLanguage')} 
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
                  {t('settings.add')}
                </Button>
              </HStack>
            </Box>
            
            <Button 
              colorScheme="green" 
              mt={4} 
              onClick={handleSaveSettings} 
              isLoading={isSaving}
              leftIcon={<CheckIcon />}
            >
              {t('settings.saveSettings')}
            </Button>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default SimpleSettingsPage;
