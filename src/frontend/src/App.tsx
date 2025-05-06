import React, { Suspense, useEffect } from 'react';
import { ChakraProvider, Box, theme, Spinner, Center, useToast } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { LanguageProvider, useLanguagePreferences } from './contexts/LanguageContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Import i18n configuration
import './i18n/i18n';
import i18n from './i18n/i18n';

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
import SettingsPage from './pages/SettingsPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';

// Import components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';

// Create React Query client
const queryClient = new QueryClient();

// Language synchronization component to manage user language preferences
const LanguageSynchronizer = ({ children }: { children: React.ReactNode }) => {
  const { user, isAuthenticated } = useAuth();
  const { setUILanguage, uiLanguage } = useLanguagePreferences();
  const toast = useToast();

  // Apply user's native language when user loads or changes
  useEffect(() => {
    if (user && user.native_language && user.native_language !== uiLanguage) {
      console.log(`App: Setting UI language to user's native language: ${user.native_language}`);
      setUILanguage(user.native_language);
      
      // Toast notification when language is applied
      toast({
        title: i18n.t('common.languageChanged', { lng: user.native_language }),
        description: i18n.t('common.languageApplied', { lng: user.native_language }),
        status: 'info',
        duration: 3000,
        isClosable: true,
        position: 'bottom-right'
      });
    }
  }, [user, setUILanguage, uiLanguage]);

  return <>{children}</>;
};

// Component to conditionally render home page based on auth status
const ConditionalHome = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <LoggedInHomePage /> : <HomePage />;
};

// Loading component for Suspense fallback
const Loading = () => (
  <Center height="100vh">
    <Spinner size="xl" color="blue.500" thickness="4px" />
  </Center>
);

function App() {
  return (
    <ChakraProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <LanguageProvider>
            {/* Wrap app in Suspense for i18n lazy loading */}
            <Suspense fallback={<Loading />}>
              <LanguageSynchronizer>
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
                                <SettingsPage />
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
              </LanguageSynchronizer>
            </Suspense>
          </LanguageProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ChakraProvider>
  );
}

export default App;
