import React, { useEffect, useState, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Text,
  Stack,
  Avatar,
  Divider,
  FormControl,
  FormLabel,
  Input,
  Select,
  useColorModeValue,
  Alert,
  AlertIcon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useToast,
  IconButton,
  Badge,
} from '@chakra-ui/react';
import { EditIcon, CheckIcon, CloseIcon } from '@chakra-ui/icons';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useNavigate } from 'react-router-dom';

interface UserProfile {
  _id: string;
  name: string;
  email: string;
  native_language: string;
  learning_language: string;
  created_at: string;
  saved_articles: string[];
  studied_words: string[];
}

const ProfilePage: React.FC = () => {
  const { t } = useTranslation();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    native_language: '',
    learning_language: '',
  });
  
  const navigate = useNavigate();
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const accentColor = useColorModeValue('blue.500', 'blue.300');
  
  useEffect(() => {
    fetchUserProfile();
  }, []);
  
  const fetchUserProfile = async () => {
    const token = Cookies.get('lingogi_token');
    
    if (!token) {
      navigate('/signin');
      return;
    }
    
    try {
      setIsLoading(true);
      
      const response = await axios.get('http://localhost:8000/api/user/profile', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (response.data) {
        setProfile(response.data);
        setFormData({
          name: response.data.name,
          native_language: response.data.native_language,
          learning_language: response.data.learning_language,
        });
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch profile');
      
      // If unauthorized, redirect to sign in
      if (err.response?.status === 401) {
        Cookies.remove('lingogi_token');
        navigate('/signin');
      }
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };
  
  const handleUpdateProfile = async () => {
    const token = Cookies.get('lingogi_token');
    
    if (!token) {
      navigate('/signin');
      return;
    }
    
    try {
      const response = await axios.put(
        'http://localhost:8000/api/user/profile',
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      
      if (response.data) {
        setProfile({
          ...profile!,
          ...formData,
        });
        
        setEditing(false);
        toast({
          title: 'Profile updated',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      }
    } catch (err: any) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to update profile',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  const handleSignOut = () => {
    Cookies.remove('lingogi_token');
    navigate('/signin');
    toast({
      title: 'Signed out successfully',
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
  };
  
  const getLanguageName = (code: string) => {
    const languages: { [key: string]: string } = {
      en: 'English',
      ko: 'Korean',
      ja: 'Japanese',
      zh: 'Chinese',
      es: 'Spanish',
      fr: 'French',
    };
    return languages[code] || code;
  };
  
  if (isLoading) {
    return (
      <Container maxW="container.lg" py={8}>
        <Text fontSize="xl">{t('profile.loading')}</Text>
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container maxW="container.lg" py={8}>
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
      </Container>
    );
  }
  
  if (!profile) {
    return (
      <Container maxW="container.lg" py={8}>
        <Alert status="warning">
          <AlertIcon />
          Profile not found. Please sign in.
        </Alert>
      </Container>
    );
  }
  
  return (
    <Container maxW="container.lg" py={8}>
      <Tabs variant="enclosed">
        <TabList>
          <Tab>Profile</Tab>
          <Tab>Saved Articles</Tab>
          <Tab>Vocabulary</Tab>
          <Tab>Settings</Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel>
            <Box
              bg={bgColor}
              boxShadow="base"
              borderRadius="xl"
              borderWidth="1px"
              borderColor={borderColor}
              p={6}
            >
              <Flex
                direction={{ base: 'column', md: 'row' }}
                align={{ base: 'center', md: 'start' }}
                justify="space-between"
                mb={6}
              >
                <Flex align="center" direction={{ base: 'column', md: 'row' }}>
                  <Avatar 
                    size="xl" 
                    name={profile.name} 
                    mb={{ base: 4, md: 0 }}
                    mr={{ base: 0, md: 4 }}
                    bg={accentColor} 
                  />
                  <Box textAlign={{ base: 'center', md: 'left' }}>
                    <Heading size="lg">{profile.name}</Heading>
                    <Text color="gray.500">{profile.email}</Text>
                    <Flex mt={2} wrap="wrap" justify={{ base: 'center', md: 'flex-start' }}>
                      <Badge colorScheme="blue" mr={2} mb={2}>
                        Native: {getLanguageName(profile.native_language)}
                      </Badge>
                      <Badge colorScheme="green" mb={2}>
                        Learning: {getLanguageName(profile.learning_language)}
                      </Badge>
                    </Flex>
                  </Box>
                </Flex>
                
                <Flex mt={{ base: 4, md: 0 }}>
                  {!editing ? (
                    <Button
                      leftIcon={<EditIcon />}
                      colorScheme="blue"
                      variant="outline"
                      onClick={() => setEditing(true)}
                    >
                      Edit Profile
                    </Button>
                  ) : (
                    <Flex>
                      <IconButton
                        aria-label="Save"
                        icon={<CheckIcon />}
                        colorScheme="green"
                        mr={2}
                        onClick={handleUpdateProfile}
                      />
                      <IconButton
                        aria-label="Cancel"
                        icon={<CloseIcon />}
                        colorScheme="red"
                        variant="outline"
                        onClick={() => {
                          setEditing(false);
                          setFormData({
                            name: profile.name,
                            native_language: profile.native_language,
                            learning_language: profile.learning_language,
                          });
                        }}
                      />
                    </Flex>
                  )}
                </Flex>
              </Flex>
              
              <Divider mb={6} />
              
              {editing ? (
                <Stack spacing={4}>
                  <FormControl id="name">
                    <FormLabel>Name</FormLabel>
                    <Input
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                    />
                  </FormControl>
                  
                  <Flex
                    direction={{ base: 'column', md: 'row' }}
                    gap={{ base: 4, md: 6 }}
                  >
                    <FormControl id="native_language">
                      <FormLabel>Native Language</FormLabel>
                      <Select
                        name="native_language"
                        value={formData.native_language}
                        onChange={handleChange}
                      >
                        <option value="en">English</option>
                        <option value="ko">Korean</option>
                        <option value="ja">Japanese</option>
                        <option value="zh">Chinese</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                      </Select>
                    </FormControl>
                    
                    <FormControl id="learning_language">
                      <FormLabel>Language You're Learning</FormLabel>
                      <Select
                        name="learning_language"
                        value={formData.learning_language}
                        onChange={handleChange}
                      >
                        <option value="ko">Korean</option>
                        <option value="en">English</option>
                        <option value="ja">Japanese</option>
                        <option value="zh">Chinese</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                      </Select>
                    </FormControl>
                  </Flex>
                </Stack>
              ) : (
                <Stack spacing={4}>
                  <Box>
                    <Text fontWeight="bold" mb={1}>
                      {t('profile.memberSince')}
                    </Text>
                    <Text>
                      {new Date(profile.created_at).toLocaleDateString()}
                    </Text>
                  </Box>
                  
                  <Box>
                    <Text fontWeight="bold" mb={1}>
                      {t('profile.learningProgress')}
                    </Text>
                    <Text>
                      {profile.saved_articles?.length || 0} saved articles
                    </Text>
                    <Text>
                      {profile.studied_words?.length || 0} vocabulary words studied
                    </Text>
                  </Box>
                </Stack>
              )}
              
              <Divider my={6} />
              
              <Button
                colorScheme="red"
                variant="outline"
                onClick={handleSignOut}
              >
                {t('profile.signOut')}
              </Button>
            </Box>
          </TabPanel>
          
          <TabPanel>
            <Box
              bg={bgColor}
              boxShadow="base"
              borderRadius="xl"
              borderWidth="1px"
              borderColor={borderColor}
              p={6}
            >
              <Heading size="md" mb={4}>
                {t('profile.savedArticles')}
              </Heading>
              
              {profile.saved_articles && profile.saved_articles.length > 0 ? (
                <Text>{t('profile.featureComingSoon')}</Text>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  You haven't saved any articles yet.
                </Alert>
              )}
            </Box>
          </TabPanel>
          
          <TabPanel>
            <Box
              bg={bgColor}
              boxShadow="base"
              borderRadius="xl"
              borderWidth="1px"
              borderColor={borderColor}
              p={6}
            >
              <Heading size="md" mb={4}>
                Vocabulary
              </Heading>
              
              {profile.studied_words && profile.studied_words.length > 0 ? (
                <Text>{t('profile.featureComingSoon')}</Text>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  You haven't studied any vocabulary words yet.
                </Alert>
              )}
            </Box>
          </TabPanel>
          
          <TabPanel>
            <Box
              bg={bgColor}
              boxShadow="base"
              borderRadius="xl"
              borderWidth="1px"
              borderColor={borderColor}
              p={6}
            >
              <Heading size="md" mb={4}>
                {t('profile.accountSettings')}
              </Heading>
              
              <Stack spacing={4}>
                <Button colorScheme="blue" variant="outline">
                  {t('profile.changePassword')}
                </Button>
                <Button colorScheme="red" variant="outline">
                  {t('profile.deleteAccount')}
                </Button>
              </Stack>
            </Box>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Container>
  );
};

export default ProfilePage;
