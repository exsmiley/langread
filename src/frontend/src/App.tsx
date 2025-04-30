import React from 'react';
import { ChakraProvider, Box, theme } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { LanguageProvider } from './contexts/LanguageContext';

// Import pages
import HomePage from './pages/HomePage';
import ArticleListPage from './pages/ArticleListPage';
import ArticleViewPage from './pages/ArticleViewPage';
import VocabularyPage from './pages/VocabularyPage';
import AdminTagsPage from './pages/AdminTagsPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import AboutPage from './pages/AboutPage';
import PrivacyPage from './pages/PrivacyPage';
import TermsPage from './pages/TermsPage';
import ContactPage from './pages/ContactPage';

// Import components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';

// Create React Query client
const queryClient = new QueryClient();

function App() {
  return (
    <ChakraProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <LanguageProvider>
          <Router>
            <Box minH="100vh" display="flex" flexDirection="column">
            <Navbar />
            <Box flex="1" p={4}>
              <ErrorBoundary>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/articles" element={<ErrorBoundary><ArticleListPage /></ErrorBoundary>} />
                  <Route path="/articles/:articleId" element={<ErrorBoundary><ArticleViewPage /></ErrorBoundary>} />
                  <Route path="/vocabulary" element={<ErrorBoundary><VocabularyPage /></ErrorBoundary>} />
                  <Route path="/about" element={<ErrorBoundary><AboutPage /></ErrorBoundary>} />
                  <Route path="/privacy" element={<ErrorBoundary><PrivacyPage /></ErrorBoundary>} />
                  <Route path="/terms" element={<ErrorBoundary><TermsPage /></ErrorBoundary>} />
                  <Route path="/contact" element={<ErrorBoundary><ContactPage /></ErrorBoundary>} />
                  <Route path="/admin" element={<ErrorBoundary><AdminDashboardPage /></ErrorBoundary>} />
                  <Route path="/admin/tags" element={<ErrorBoundary><AdminTagsPage /></ErrorBoundary>} />
                </Routes>
              </ErrorBoundary>
            </Box>
            <Footer />
            </Box>
          </Router>
        </LanguageProvider>
      </QueryClientProvider>
    </ChakraProvider>
  );
}

export default App;
