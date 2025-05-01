import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  Box,
  Button,
  Container,
  FormControl,
  FormLabel,
  FormErrorMessage,
  Heading,
  Input,
  Stack,
  Text,
  Link,
  useColorModeValue,
  Alert,
  AlertIcon,
  InputGroup,
  InputRightElement,
  IconButton,
  Checkbox,
  Flex,
  Spinner,
  Select,
} from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import axios from 'axios';

const SignUpPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    nativeLanguage: 'en',
    learningLanguage: 'ko',
    agreeToTerms: false
  });
  
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [emailError, setEmailError] = useState('');
  const [isCheckingEmail, setIsCheckingEmail] = useState(false);
  const [emailDebounceTimeout, setEmailDebounceTimeout] = useState<NodeJS.Timeout | null>(null);
  
  const navigate = useNavigate();
  const { signIn, signUp } = useAuth();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // Check if email already exists
  const checkEmailExists = async (email: string) => {
    if (!email || !email.includes('@')) return;
    
    try {
      setIsCheckingEmail(true);
      const response = await axios.get(`http://localhost:8000/api/auth/check-email/${encodeURIComponent(email)}`);
      
      if (response.data && response.data.exists) {
        setEmailError('This email is already registered');
      } else {
        setEmailError('');
      }
    } catch (err) {
      console.error('Error checking email:', err);
    } finally {
      setIsCheckingEmail(false);
    }
  };
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    // For email field, check if already exists after user stops typing
    if (name === 'email') {
      if (emailDebounceTimeout) {
        clearTimeout(emailDebounceTimeout);
      }
      
      const timeout = setTimeout(() => {
        checkEmailExists(value);
      }, 800); // 800ms debounce
      
      setEmailDebounceTimeout(timeout);
    }
  };
  
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData({ ...formData, [name]: checked });
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    console.log('Form submission started', formData);
    // Prevent the default form submission behavior
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Log the signup attempt for debugging
    console.log('Submitting registration with language settings:', {
      native: formData.nativeLanguage,
      learning: formData.learningLanguage
    });
    
    // Basic validation
    if (emailError) {
      setError('Please use a different email address');
      setIsLoading(false);
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }
    
    if (!formData.agreeToTerms) {
      setError('You must agree to the terms of service');
      setIsLoading(false);
      return;
    }
    
    try {
      console.log('Using AuthContext signUp function with auto-login capabilities...');
      
      // Use the AuthContext signUp function that handles auth token and auto-login
      const signupSuccess = await signUp({
        email: formData.email,
        password: formData.password,
        name: formData.name,
        native_language: formData.nativeLanguage,
        learning_language: formData.learningLanguage
      });
      
      if (signupSuccess) {
        console.log('Registration and auto-login successful, redirecting to home page');
        navigate('/');
      } else {
        console.error('Registration failed');
        setError('Failed to create account. Please try again.');
      }
    } catch (err: any) {
      console.error('Registration error (outer):', err);
      setError(err.response?.data?.detail || 'Failed to create account. Please try again.');
      setIsLoading(false);
    }
  };
  
  return (
    <Container maxW="lg" py={{ base: '12', md: '24' }} px={{ base: '0', sm: '8' }}>
      <Stack spacing="8">
        <Stack spacing="6" align="center">
          <Heading size="xl" fontWeight="bold">Create your account</Heading>
          <Text color="gray.500">
            Join Lingogi to improve your language skills
          </Text>
        </Stack>
        
        <Box
          py="8"
          px="10"
          bg={bgColor}
          boxShadow="base"
          borderRadius="xl"
          borderWidth="1px"
          borderColor={borderColor}
        >
          {error && (
            <Alert status="error" mb={4} borderRadius="md">
              <AlertIcon />
              {error}
            </Alert>
          )}
          
          <form onSubmit={handleSubmit}>
            <Stack spacing="6">
              <FormControl id="name" isRequired>
                <FormLabel>Name</FormLabel>
                <Input 
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Your name"
                />
              </FormControl>
              
              <FormControl id="email" isRequired isInvalid={!!emailError}>
                <FormLabel>Email address</FormLabel>
                <InputGroup>
                  <Input
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                  />
                  {isCheckingEmail && (
                    <InputRightElement>
                      <Spinner size="sm" color="blue.500" />
                    </InputRightElement>
                  )}
                </InputGroup>
                {emailError && <FormErrorMessage>{emailError}</FormErrorMessage>}
              </FormControl>
              
              <FormControl id="password" isRequired>
                <FormLabel>Password</FormLabel>
                <InputGroup>
                  <Input 
                    type={showPassword ? 'text' : 'password'} 
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                  />
                  <InputRightElement>
                    <IconButton
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                      onClick={() => setShowPassword(!showPassword)}
                      variant="ghost"
                      size="sm"
                      tabIndex={-1} /* Skip this button in tab order */
                    />
                  </InputRightElement>
                </InputGroup>
              </FormControl>
              
              <FormControl id="confirmPassword" isRequired>
                <FormLabel>Confirm Password</FormLabel>
                <Input 
                  type={showPassword ? 'text' : 'password'} 
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="••••••••"
                />
              </FormControl>
              
              <Stack spacing={4}>
                <FormControl id="learningLanguage" isRequired>
                  <FormLabel>Language You're Learning</FormLabel>
                  <Select 
                    name="learningLanguage"
                    value={formData.learningLanguage}
                    onChange={handleChange}
                  >
                    <option value="ko">Korean</option>
                    <option value="en">English</option>
                    <option value="ja">Japanese</option>
                    <option value="zh">Chinese</option>
                  </Select>
                  <FormHelperText>You can change your language preferences later in your profile settings</FormHelperText>
                </FormControl>
              </Stack>
              
              <FormControl id="agreeToTerms">
                <Checkbox 
                  name="agreeToTerms"
                  isChecked={formData.agreeToTerms}
                  onChange={handleCheckboxChange}
                >
                  I agree to the <Link as={RouterLink} to="/terms" color="blue.500">Terms of Service</Link> and <Link as={RouterLink} to="/privacy" color="blue.500">Privacy Policy</Link>
                </Checkbox>
              </FormControl>
              
              <Button 
                type="submit" 
                colorScheme="blue" 
                size="lg" 
                fontSize="md"
                isLoading={isLoading}
              >
                Create Account
              </Button>
            </Stack>
          </form>
        </Box>
        
        <Flex justifyContent="center">
          <Text>Already have an account? <Link as={RouterLink} to="/signin" color="blue.500">Sign in</Link></Text>
        </Flex>
      </Stack>
    </Container>
  );
};

export default SignUpPage;
