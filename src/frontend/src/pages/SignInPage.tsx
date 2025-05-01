import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  Box,
  Button,
  Container,
  FormControl,
  FormLabel,
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
} from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import axios from 'axios';
import Cookies from 'js-cookie';

const SignInPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const navigate = useNavigate();
  const { signIn } = useAuth();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      // Use the AuthContext's signIn function
      const success = await signIn(email, password);
      
      if (success) {
        // Redirect to home page
        navigate('/');
        console.log('Sign in successful, redirecting to home page');
      } else {
        setError('Invalid credentials');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sign in. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Container maxW="lg" py={{ base: '12', md: '24' }} px={{ base: '0', sm: '8' }}>
      <Stack spacing="8">
        <Stack spacing="6" align="center">
          <Heading size="xl" fontWeight="bold">Sign in to your account</Heading>
          <Text color="gray.500">
            Enter your email and password to access your account
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
              <FormControl id="email" isRequired>
                <FormLabel>Email</FormLabel>
                <Input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your.email@example.com"
                />
              </FormControl>
              
              <FormControl id="password" isRequired>
                <FormLabel>Password</FormLabel>
                <InputGroup>
                  <Input 
                    type={showPassword ? 'text' : 'password'} 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
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
              
              <Button 
                type="submit" 
                colorScheme="blue" 
                size="lg" 
                fontSize="md"
                isLoading={isLoading}
              >
                Sign in
              </Button>
            </Stack>
          </form>
        </Box>
        
        <Stack spacing="3" align="center">
          <Text>Don't have an account? <Link as={RouterLink} to="/signup" color="blue.500">Sign up</Link></Text>
          <Link as={RouterLink} to="/forgot-password" color="blue.500">Forgot password?</Link>
        </Stack>
      </Stack>
    </Container>
  );
};

export default SignInPage;
