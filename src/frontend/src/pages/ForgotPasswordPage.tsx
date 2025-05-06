import React, { useState } from 'react';
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
  FormErrorMessage,
  InputGroup,
  InputRightElement,
  Spinner,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const ForgotPasswordPage: React.FC = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');
  const [resetLink, setResetLink] = useState(''); // Only for demo purposes

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    setEmailError('');
  };

  const validateEmail = () => {
    if (!email) {
      setEmailError(t('auth.emailRequired'));
      return false;
    }
    if (!email.includes('@')) {
      setEmailError(t('auth.invalidEmail'));
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateEmail()) {
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/auth/forgot-password', {
        email
      });
      
      console.log('Response:', response.data);
      
      if (response.data.success) {
        setIsSuccess(true);
        // In a real app, you wouldn't expose the token to the user
        // This is just for development/demonstration purposes
        if (response.data.debug_link) {
          setResetLink(response.data.debug_link);
        }
      } else {
        setError(t('auth.resetRequestFailed'));
      }
    } catch (err: any) {
      console.error('Error requesting password reset:', err);
      setError(err.response?.data?.detail || t('auth.resetRequestFailed'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="lg" py={{ base: '12', md: '24' }} px={{ base: '0', sm: '8' }}>
      <Stack spacing="8">
        <Stack spacing="6" align="center">
          <Heading size="xl" fontWeight="bold">{t('auth.resetPassword')}</Heading>
          <Text color="gray.500">
            {t('auth.resetInstructions')}
          </Text>
        </Stack>
        
        <Box
          py={{ base: '0', sm: '8' }}
          px={{ base: '4', sm: '10' }}
          bg={bgColor}
          boxShadow={{ base: 'none', sm: 'md' }}
          borderRadius={{ base: 'none', sm: 'xl' }}
          borderWidth={{ base: '0', sm: '1px' }}
          borderColor={borderColor}
        >
          {isSuccess ? (
            <Stack spacing="6">
              <Alert status="success" borderRadius="md">
                <AlertIcon />
                {t('auth.resetLinkSent')}
              </Alert>
              
              {/* This section is only for development/demonstration purposes */}
              {resetLink && (
                <Box mt={4} p={4} bg="gray.50" borderRadius="md">
                  <Text fontSize="sm" fontWeight="bold">{t('common.developmentMode')}</Text>
                  <Text fontSize="xs" mb={2}>{t('auth.resetLinkDemo')}</Text>
                  <Link as={RouterLink} to={resetLink.replace('http://localhost:5173', '')} color="blue.500" fontSize="sm" wordBreak="break-all">
                    {resetLink}
                  </Link>
                </Box>
              )}
              
              <Link as={RouterLink} to="/signin" color="blue.500" textAlign="center">
                {t('auth.returnToSignIn')}
              </Link>
            </Stack>
          ) : (
            <Stack spacing="6">
              {error && (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  {error}
                </Alert>
              )}
              
              <form onSubmit={handleSubmit}>
                <Stack spacing="5">
                  <FormControl id="email" isInvalid={!!emailError}>
                    <FormLabel>{t('auth.emailAddress')}</FormLabel>
                    <Input
                      name="email"
                      type="email"
                      value={email}
                      onChange={handleEmailChange}
                      placeholder={t('auth.emailPlaceholder')}
                    />
                    {emailError && <FormErrorMessage>{emailError}</FormErrorMessage>}
                  </FormControl>
                  
                  <Button
                    type="submit"
                    colorScheme="blue"
                    size="lg"
                    fontSize="md"
                    isLoading={isLoading}
                  >
                    {t('auth.sendResetLink')}
                  </Button>
                </Stack>
              </form>
              
              <Stack pt={6}>
                <Text align="center">
                  {t('auth.rememberPassword')}{' '}
                  <Link as={RouterLink} to="/signin" color="blue.500">
                    {t('auth.signIn')}
                  </Link>
                </Text>
              </Stack>
            </Stack>
          )}
        </Box>
      </Stack>
    </Container>
  );
};

export default ForgotPasswordPage;
