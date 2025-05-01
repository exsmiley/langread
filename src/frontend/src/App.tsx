import React from 'react';
import { ChakraProvider, Box, theme } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { LanguageProvider } from './contexts/LanguageContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Import pages
import HomePage from './pages/HomePage';
import LoggedInHomePage from './pages/LoggedInHomePage';
import ArticleListPage from './pages/ArticleListPage';
import ArticleViewPage from './pages/ArticleViewPage';
import VocabularyPage from './pages/VocabularyPage';
import AdminTagsPage from './pages/AdminTagsPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import AboutPage from './pages/AboutPage';
import PrivacyPage from './pages/PrivacyPage';
import TermsPage from './pages/TermsPage';
import ContactPage from './pages/ContactPage';
import SignInPage from './pages/SignInPage';
import SignUpPage from './pages/SignUpPage';
import ProfilePage from './pages/ProfilePage';
import FixedSettingsPage from './pages/FixedSettingsPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';

// Import components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';

// Create React Query client
const queryClient = new QueryClient();

// Component to conditionally render home page based on auth status
const ConditionalHome = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <LoggedInHomePage /> : <HomePage />;
};

function App() {
  return (
    <ChakraProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <LanguageProvider>
          <Router>
            <Box minH="100vh" display="flex" flexDirection="column">
            <Navbar />
            <Box flex="1" p={4}>
              <ErrorBoundary>
                <Routes>
                  <Route path="/" element={<ConditionalHome />} />
                  <Route path="/articles" element={
                    <ErrorBoundary>
                      <ProtectedRoute>
                        <ArticleListPage />
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  <Route path="/articles/:articleId" element={
                    <ErrorBoundary>
                      <ProtectedRoute>
                        <ArticleViewPage />
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  <Route path="/vocabulary" element={
                    <ErrorBoundary>
                      <ProtectedRoute>
                        <VocabularyPage />
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  <Route path="/about" element={<ErrorBoundary><AboutPage /></ErrorBoundary>} />
                  <Route path="/privacy" element={<ErrorBoundary><PrivacyPage /></ErrorBoundary>} />
                  <Route path="/terms" element={<ErrorBoundary><TermsPage /></ErrorBoundary>} />
                  <Route path="/contact" element={<ErrorBoundary><ContactPage /></ErrorBoundary>} />
                  <Route path="/admin" element={
                    <ErrorBoundary>
                      <ProtectedRoute>
                        <AdminDashboardPage />
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  <Route path="/admin/tags" element={
                    <ErrorBoundary>
                      <ProtectedRoute>
                        <AdminTagsPage />
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  <Route path="/signin" element={<ErrorBoundary><SignInPage /></ErrorBoundary>} />
                  <Route path="/signup" element={<ErrorBoundary><SignUpPage /></ErrorBoundary>} />
                  <Route path="/profile" element={
                    <ErrorBoundary>
                      <ProtectedRoute>
                        <ProfilePage />
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  <Route path="/settings" element={
                    <ErrorBoundary>
                      <ProtectedRoute>
                        <FixedSettingsPage />
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  <Route path="/forgot-password" element={<ErrorBoundary><ForgotPasswordPage /></ErrorBoundary>} />
                  <Route path="/reset-password" element={<ErrorBoundary><ResetPasswordPage /></ErrorBoundary>} />
                </Routes>
              </ErrorBoundary>
            </Box>
            <Footer />
            </Box>
          </Router>
          </LanguageProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ChakraProvider>
  );
}

export default App;
