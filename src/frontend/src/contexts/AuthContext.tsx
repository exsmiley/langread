import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { getToken, saveToken, removeToken } from '../utils/tokenUtils';

// Interface for a language the user is learning
export interface LearningLanguage {
  language: string;
  proficiency: string; // beginner, intermediate, advanced
  isDefault?: boolean;
}

export interface User {
  _id: string;
  name: string;
  email: string;
  native_language: string;
  learning_language: string; // Primary learning language (for backward compatibility)
  proficiency?: string; // Proficiency level for primary language
  additional_languages?: LearningLanguage[]; // Additional languages being learned
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  signIn: (email: string, password: string) => Promise<boolean>;
  signUp: (userData: SignUpData) => Promise<boolean>;
  signOut: () => void;
  clearError: () => void;
}

interface SignUpData {
  email: string;
  password: string;
  name: string;
  native_language: string;
  learning_language: string;
}

interface AuthProviderProps {
  children: ReactNode;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Token management functions are now imported from tokenUtils

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    console.log('AuthContext: Token check on page load:', token ? 'Token exists' : 'No token');
    if (!token) setUser(null);
  }, []);

  useEffect(() => {
    const checkAuthStatus = async () => {
      console.log('AuthContext: Checking authentication status...');
      const token = getToken();
      
      if (token) {
        console.log('AuthContext: Token found');
        // Basic validation that it looks like a JWT
        if (token.split('.').length !== 3) {
          console.error('AuthContext: Token appears malformed');
          removeToken();
          setLoading(false);
          return;
        }
      } else {
        console.log('AuthContext: No token found, setting not authenticated');
        setLoading(false);
        return;
      }
      
      try {
        console.log('AuthContext: Making profile request with token');
        // Handle the case where token could be null (though this shouldn't happen here)
        if (!token) {
          console.error('AuthContext: No token available for profile request');
          removeToken();
          setLoading(false);
          return;
        }
        
        const response = await axios.get('http://localhost:8000/api/user/profile', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.data) {
          console.log('AuthContext: User profile loaded successfully');
          setUser(response.data);
        } else {
          console.log('AuthContext: Empty response data from profile endpoint');
        }
      } catch (err) {
        // Handle token expiration or other errors
        console.error('AuthContext: Error fetching user profile:', err);
        removeToken();
      } finally {
        console.log('AuthContext: Authentication check completed');
        setLoading(false);
      }
    };
    
    checkAuthStatus();
  }, []);

  const signIn = async (email: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('http://localhost:8000/api/auth/signin', {
        email,
        password
      });
      
      if (response.data && response.data.token) {
        // Save token using our central function
        console.log('AuthContext: Storing new token');
        if (!saveToken(response.data.token)) {
          console.error('AuthContext: Failed to save token');
          setError('Failed to save authentication token');
          setLoading(false);
          return false;
        }
        
        // Double-check token was saved
        const storedToken = getToken();
        if (!storedToken) {
          console.error('AuthContext: Token storage verification failed');
          setError('Authentication failed - please try again');
          setLoading(false);
          return false;
        }
        
        // Fetch user profile
        const profileResponse = await axios.get('http://localhost:8000/api/user/profile', {
          headers: {
            'Authorization': `Bearer ${response.data.token}`
          }
        });
        
        if (profileResponse.data) {
          setUser(profileResponse.data);
        }
        
        return true;
      }
      
      return false;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sign in');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (userData: SignUpData): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('http://localhost:8000/api/auth/signup', userData);
      console.log('Signup response:', response.data);
      
      if (response.data && response.data.success) {
        // Immediately try to sign in with the new credentials
        try {
          // Auto sign-in after successful registration
          const signInResponse = await axios.post('http://localhost:8000/api/auth/signin', {
            email: userData.email,
            password: userData.password
          });
          
          if (signInResponse.data && signInResponse.data.token) {
            // Store token using our utility function
            saveToken(signInResponse.data.token);
            
            // Fetch user profile
            const profileResponse = await axios.get('http://localhost:8000/api/user/profile', {
              headers: {
                Authorization: `Bearer ${signInResponse.data.token}`
              }
            });
            
            if (profileResponse.data) {
              setUser(profileResponse.data);
              console.log('Auto-login successful after signup');
              return true;
            }
          }
        } catch (signInErr) {
          console.error('Auto-login failed after signup:', signInErr);
          // Continue with success since signup was successful even if auto-login failed
        }
        return true;
      }
      
      return false;
    } catch (err: any) {
      console.error('Signup error:', err);
      setError(err.response?.data?.detail || 'Failed to create account');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const signOut = () => {
    console.log('AuthContext: Signing out user');
    // Use our central token remover
    removeToken();
    setUser(null);
    console.log('AuthContext: User signed out successfully');
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    signIn,
    signUp,
    signOut,
    clearError
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};
