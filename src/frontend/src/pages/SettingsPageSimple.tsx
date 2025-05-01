import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  VStack,
  Spinner,
  Center,
  useToast,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getToken } from '../utils/tokenUtils';

/**
 * A simplified Settings page to test basic functionality
 */
const SettingsPageSimple = () => {
  // Hooks at the top level
  const navigate = useNavigate();
  const toast = useToast();
  const auth = useAuth();
  
  // State (all hooks at top level)
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  // Safely extract auth values
  const user = auth?.user;
  const loading = auth?.loading;
  
  // Redirect if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      console.log('[SettingsPage] Not authenticated, redirecting to sign in');
      navigate('/signin');
    }
  }, [loading, user, navigate]);
  
  // Function to handle a test API request
  const testBackendConnection = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      const token = getToken();
      if (!token) {
        setMessage('No authentication token found. Please sign in again.');
        setIsLoading(false);
        return;
      }
      
      // Simple Get request to test connection
      const response = await fetch('http://localhost:8000/api/user/profile', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessage(`Connected successfully! User: ${data.name}`);
        
        toast({
          title: 'Connection successful',
          description: 'Backend API is accessible',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
      } else {
        setMessage(`Error ${response.status}: ${response.statusText}`);
      }
    } catch (err: any) {
      console.error('Connection test failed:', err);
      setMessage(`Connection failed: ${err?.message || 'Unknown error'}`);
      
      toast({
        title: 'Connection failed',
        description: 'Could not reach the backend server',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Loading state while checking authentication
  if (loading) {
    return (
      <Container maxW="container.md" py={10}>
        <Center h="200px">
          <VStack>
            <Spinner size="xl" />
            <Text mt={4}>Loading your profile...</Text>
          </VStack>
        </Center>
      </Container>
    );
  }
  
  return (
    <Container maxW="container.md" py={10}>
      <VStack spacing={6} align="stretch">
        <Heading size="lg">Settings (Simple Version)</Heading>
        
        <Box p={6} borderWidth={1} borderRadius="md">
          <VStack spacing={4} align="stretch">
            <Text>{user ? `Logged in as: ${user.name}` : 'Not logged in'}</Text>
            
            <Button 
              colorScheme="blue" 
              onClick={testBackendConnection}
              isLoading={isLoading}
            >
              Test Backend Connection
            </Button>
            
            {message && (
              <Text 
                mt={4} 
                p={3} 
                bg={message.includes('success') ? 'green.100' : 'red.100'} 
                borderRadius="md"
              >
                {message}
              </Text>
            )}
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default SettingsPageSimple;
