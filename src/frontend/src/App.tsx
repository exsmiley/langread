import React from 'react';
import { ChakraProvider, Box, theme } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';

// Import pages
import HomePage from './pages/HomePage';
import ArticleListPage from './pages/ArticleListPage';
import ArticleViewPage from './pages/ArticleViewPage';
import VocabularyPage from './pages/VocabularyPage';

// Import components
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Create React Query client
const queryClient = new QueryClient();

function App() {
  return (
    <ChakraProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Box minH="100vh" display="flex" flexDirection="column">
            <Navbar />
            <Box flex="1" p={4}>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/articles" element={<ArticleListPage />} />
                <Route path="/articles/:articleId" element={<ArticleViewPage />} />
                <Route path="/vocabulary" element={<VocabularyPage />} />
              </Routes>
            </Box>
            <Footer />
          </Box>
        </Router>
      </QueryClientProvider>
    </ChakraProvider>
  );
}

export default App;
