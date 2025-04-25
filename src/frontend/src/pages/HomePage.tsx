import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  Container, 
  Flex, 
  Heading, 
  Text, 
  Input, 
  Select, 
  VStack, 
  HStack,
  FormControl,
  FormLabel,
  Image,
  useColorModeValue,
  useToast
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const [query, setQuery] = useState('');
  const [language, setLanguage] = useState('ko');
  const [topicType, setTopicType] = useState('news');
  const [isLoading, setIsLoading] = useState(false);
  
  const toast = useToast();
  const navigate = useNavigate();
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const formBgColor = useColorModeValue('white', 'gray.800');
  const boxShadow = '0px 4px 10px rgba(0, 0, 0, 0.05)';
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      toast({
        title: 'Empty query',
        description: "Please enter a topic to search for articles",
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    setIsLoading(true);
    // In a real app, we would submit the form data to the backend
    // and then navigate to the articles page with the results
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Navigate to articles page with query parameters
      navigate(`/articles?query=${encodeURIComponent(query)}&language=${language}&topicType=${topicType}`);
    }, 1000);
  };
  
  return (
    <Container maxW="container.xl" p={0}>
      <Flex 
        direction={{ base: 'column', md: 'row' }} 
        align="center" 
        justify="space-between"
        py={10}
        px={8}
        bg={bgColor}
        borderRadius="md"
      >
        <VStack 
          align="flex-start" 
          spacing={5}
          maxW={{ base: '100%', md: '50%' }}
          mb={{ base: 10, md: 0 }}
        >
          <Heading as="h1" size="2xl">
            LangRead
          </Heading>
          <Text fontSize="xl" color="gray.600">
            Improve your language skills by reading authentic content in your target language.
            Discover articles on any topic, translate words with a hover, and build your vocabulary.
          </Text>
          <Box 
            bg={formBgColor} 
            p={6} 
            borderRadius="md" 
            w="100%" 
            boxShadow={boxShadow}
          >
            <form onSubmit={handleSubmit}>
              <VStack spacing={4} align="stretch">
                <FormControl isRequired>
                  <FormLabel>What would you like to read about?</FormLabel>
                  <Input 
                    placeholder="Enter a topic, e.g., 'Korean food', 'K-pop', 'Technology'" 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </FormControl>
                
                <HStack spacing={4}>
                  <FormControl>
                    <FormLabel>Language</FormLabel>
                    <Select value={language} onChange={(e) => setLanguage(e.target.value)}>
                      <option value="ko">Korean (한국어)</option>
                      <option value="ja">Japanese (日本語)</option>
                      <option value="zh">Chinese (中文)</option>
                      <option value="es">Spanish (Español)</option>
                      <option value="fr">French (Français)</option>
                      <option value="de">German (Deutsch)</option>
                    </Select>
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Content Type</FormLabel>
                    <Select value={topicType} onChange={(e) => setTopicType(e.target.value)}>
                      <option value="news">News Articles</option>
                      <option value="blogs">Blog Posts</option>
                      <option value="stories">Short Stories</option>
                      <option value="educational">Educational Content</option>
                    </Select>
                  </FormControl>
                </HStack>
                
                <Button 
                  colorScheme="blue" 
                  size="lg" 
                  width="100%" 
                  type="submit"
                  isLoading={isLoading}
                >
                  Find Articles
                </Button>
              </VStack>
            </form>
          </Box>
        </VStack>
        
        <Box
          maxW={{ base: '100%', md: '45%' }}
          boxShadow="xl"
          borderRadius="md"
          overflow="hidden"
        >
          <Image 
            src="https://images.unsplash.com/photo-1546953304-5d96f43c2e94?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80" 
            alt="Person reading"
            objectFit="cover"
            fallbackSrc="https://via.placeholder.com/500x400?text=LangRead"
          />
        </Box>
      </Flex>
      
      <VStack spacing={10} py={16} px={8}>
        <Heading as="h2" size="xl" textAlign="center">
          How LangRead Works
        </Heading>
        
        <Flex 
          direction={{ base: 'column', md: 'row' }} 
          justify="space-between"
          align="center"
          w="100%"
          spacing={8}
        >
          <FeatureCard 
            title="Discover Content" 
            description="Search for articles, blogs, stories and more in your target language. Our AI finds the best content for your language level."
            iconUrl="🔍"
          />
          <FeatureCard 
            title="Read with Assistance" 
            description="Hover over words to see translations. The app adapts to your level and helps you understand complex text."
            iconUrl="📚"
          />
          <FeatureCard 
            title="Build Vocabulary" 
            description="Every word you encounter is saved to your vocabulary bank. Create flashcards and track your progress."
            iconUrl="📝"
          />
          <FeatureCard 
            title="Test Comprehension" 
            description="Test your understanding with auto-generated quizzes based on what you've read."
            iconUrl="✅"
          />
        </Flex>
      </VStack>
    </Container>
  );
};

interface FeatureCardProps {
  title: string;
  description: string;
  iconUrl: string;
}

const FeatureCard = ({ title, description, iconUrl }: FeatureCardProps) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  
  return (
    <Box 
      bg={cardBg} 
      p={5} 
      borderRadius="lg" 
      boxShadow="md" 
      textAlign="center"
      maxW="xs"
      mx="auto"
      mb={{ base: 6, md: 0 }}
    >
      <Text fontSize="4xl" mb={4}>
        {iconUrl}
      </Text>
      <Heading as="h3" size="md" mb={2}>
        {title}
      </Heading>
      <Text color="gray.600">
        {description}
      </Text>
    </Box>
  );
};

export default HomePage;
