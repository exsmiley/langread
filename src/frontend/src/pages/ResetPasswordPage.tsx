import React, { useState, useEffect } from 'react';
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
  IconButton,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const ResetPasswordPage: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [token, setToken] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // Extract token from query parameters on component mount
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tokenParam = params.get('token');
    if (tokenParam) {
      setToken(tokenParam);
    } else {
      setError(t('auth.noResetToken'));
    }
  }, [location, t]);
  
  const validatePasswords = () => {
    if (!newPassword) {
      setPasswordError(t('auth.passwordRequired'));
      return false;
    }
    
    if (newPassword.length < 8) {
      setPasswordError(t('auth.passwordLength'));
      return false;
    }
    
    if (newPassword !== confirmPassword) {
      setPasswordError(t('auth.passwordsMismatch'));
      return false;
    }
    
    return true;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validatePasswords()) {
      return;
    }
    
    setIsLoading(true);
    setError('');
    setPasswordError('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/auth/reset-password', {
        token,
        new_password: newPassword
      });
      
      if (response.data.success) {
        setIsSuccess(true);
        // Automatically redirect to login after 5 seconds
        setTimeout(() => {
          navigate('/signin');
        }, 5000);
      } else {
        setError(t('auth.resetFailed'));
      }
    } catch (err: any) {
      console.error('Error resetting password:', err);
      setError(err.response?.data?.detail || t('auth.resetFailed'));
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Container maxW="lg" py={{ base: '12', md: '24' }} px={{ base: '0', sm: '8' }}>
      <Stack spacing="8">
        <Stack spacing="6" align="center">
          <Heading size="xl" fontWeight="bold">{t('auth.setNewPassword')}</Heading>
          <Text color="gray.500">
            {t('auth.createNewPassword')}
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
          {!token ? (
            <Alert status="error" borderRadius="md">
              <AlertIcon />
              {t('auth.noResetToken')}
            </Alert>
          ) : isSuccess ? (
            <Stack spacing="6">
              <Alert status="success" borderRadius="md">
                <AlertIcon />
                {t('auth.resetSuccess')}
              </Alert>
              
              <Link as={RouterLink} to="/signin" color="blue.500" textAlign="center">
                {t('auth.signInNow')}
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
                  <FormControl id="password" isRequired isInvalid={!!passwordError}>
                    <FormLabel>{t('auth.newPassword')}</FormLabel>
                    <InputGroup>
                      <Input
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder={t('auth.passwordPlaceholder')}
                      />
                      <InputRightElement h="full">
                        <IconButton
                          aria-label={showPassword ? t('auth.hidePassword') : t('auth.showPassword')}
                          icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                          variant="ghost"
                          onClick={() => setShowPassword((showPassword) => !showPassword)}
                          tabIndex={-1} /* Skip this button in tab order */
                        />
                      </InputRightElement>
                    </InputGroup>
                  </FormControl>
                  
                  <FormControl id="confirmPassword" isRequired isInvalid={!!passwordError}>
                    <FormLabel>{t('auth.confirmPassword')}</FormLabel>
                    <Input
                      name="confirmPassword"
                      type={showPassword ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder={t('auth.confirmPasswordPlaceholder')}
                    />
                    {passwordError && <FormErrorMessage>{passwordError}</FormErrorMessage>}
                  </FormControl>
                  
                  <Button
                    type="submit"
                    colorScheme="blue"
                    size="lg"
                    fontSize="md"
                    isLoading={isLoading}
                  >
                    {t('auth.resetPassword')}
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

export default ResetPasswordPage;
