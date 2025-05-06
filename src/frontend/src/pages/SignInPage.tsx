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
import { useTranslation } from 'react-i18next';

const SignInPage = () => {
  const { t } = useTranslation();
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
        setError(t('auth.invalidCredentials'));
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || t('auth.signInFailed'));
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Container maxW="lg" py={{ base: '12', md: '24' }} px={{ base: '0', sm: '8' }}>
      <Stack spacing="8">
        <Stack spacing="6" align="center">
          <Heading size="xl" fontWeight="bold">{t('auth.signInTitle')}</Heading>
          <Text color="gray.500">
            {t('auth.signInSubtext')}
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
                <FormLabel>{t('auth.email')}</FormLabel>
                <Input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t('auth.emailPlaceholder')}
                />
              </FormControl>
              
              <FormControl id="password" isRequired>
                <FormLabel>{t('auth.password')}</FormLabel>
                <InputGroup>
                  <Input 
                    type={showPassword ? 'text' : 'password'} 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                  />
                  <InputRightElement>
                    <IconButton
                      aria-label={showPassword ? t('auth.hidePassword') : t('auth.showPassword')}
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
                {t('auth.signIn')}
              </Button>
            </Stack>
          </form>
        </Box>
        
        <Stack spacing="3" align="center">
          <Text>{t('auth.noAccount')} <Link as={RouterLink} to="/signup" color="blue.500">{t('auth.signUp')}</Link></Text>
          <Link as={RouterLink} to="/forgot-password" color="blue.500">{t('auth.forgotPassword')}</Link>
        </Stack>
      </Stack>
    </Container>
  );
};

export default SignInPage;
