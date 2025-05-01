import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Box, Spinner, Center, Text } from '@chakra-ui/react';
import Cookies from 'js-cookie';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * A wrapper component that restricts access to authenticated users only.
 * Redirects to the sign-in page if the user is not authenticated.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  // While checking authentication status, show a loading spinner
  if (loading) {
    return (
      <Center h="calc(100vh - 80px)">
        <Box textAlign="center">
          <Spinner size="xl" color="blue.500" mb={4} />
          <Text>Loading your profile...</Text>
        </Box>
      </Center>
    );
  }

  // If not authenticated (as determined by AuthContext), redirect to sign in page
  if (!isAuthenticated) {
    console.log('Protected route access denied - Not authenticated');
    return <Navigate to="/signin" state={{ from: location.pathname }} replace />;
  }

  // If authenticated, render the protected content
  return <>{children}</>;
};

export default ProtectedRoute;
