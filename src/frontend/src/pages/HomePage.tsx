import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Container, 
  Flex, 
  Heading, 
  Text, 
  Select, 
  VStack, 
  HStack,
  FormControl,
  FormLabel,
  useColorModeValue,
  useToast,
  Radio,
  RadioGroup,
  Stack,
  Image
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';



// Language options
const languageOptions = [
  { value: 'en', label: 'English' },
  { value: 'ko', label: 'Korean' },
  { value: 'fr', label: 'French' },
  { value: 'es', label: 'Spanish' },
  { value: 'de', label: 'German' },
  { value: 'ja', label: 'Japanese' },
  { value: 'zh', label: 'Chinese' },
  { value: 'ru', label: 'Russian' }
];

const HomePage = () => {
  // Language and difficulty states
  const [nativeLanguage, setNativeLanguage] = useState('en');
  const [targetLanguage, setTargetLanguage] = useState('ko');
  const [difficulty, setDifficulty] = useState('intermediate');
  
  const [isLoading, setIsLoading] = useState(false);
  
  const toast = useToast();
  const navigate = useNavigate();
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const formBgColor = useColorModeValue('white', 'gray.800');
  const boxShadow = '0px 4px 10px rgba(0, 0, 0, 0.05)';
  


  const handleSubmit = () => {
    setIsLoading(true);
    
    // Navigate to the articles page with default parameters
    setTimeout(() => {
      setIsLoading(false);
      navigate(`/articles?nativeLanguage=${nativeLanguage}&targetLanguage=${targetLanguage}&difficulty=${difficulty}`);
    }, 500);
  };
  
  return (
    <Container maxW="container.xl" p={0}>
        <Flex 
        direction="column" 
        align="center" 
        py={10}
        px={8}
        bg={bgColor}
        borderRadius="md"
        width="100%"
      >
        <VStack 
          align="flex-start" 
          spacing={5}
          maxW={{ base: '100%' }}
        >
          <Flex align="center">
            <Box mr={4}>
              <Image src="/images/mascot.png" alt="Lingogi mascot" boxSize="60px" borderRadius="full" />
            </Box>
            <Heading as="h1" size="2xl">
              Lingogi
            </Heading>
          </Flex>
          <Text fontSize="xl" color="gray.600">
            Improve your language skills by reading authentic content in your target language.
            Discover articles on any topic, translate words with a hover, and build your vocabulary.
          </Text>
          <Box 
            display="flex"
            justifyContent="center"
            pt={8}
            pb={4}
            w="100%"
          >
            <Button 
              colorScheme="blue" 
              onClick={handleSubmit}
              isLoading={isLoading}
              loadingText="Searching..."
              size="lg"
              px={10}
              py={7}
              fontSize="xl"
              borderRadius="md"
              _hover={{ transform: "translateY(-2px)", boxShadow: "lg" }}
              transition="all 0.2s"
            >
              Find Articles
            </Button>
          </Box>
        </VStack>
        

      </Flex>
      
      <VStack spacing={10} py={16} px={8}>
        <Heading as="h2" size="xl" textAlign="center">
          How Lingogi Works
        </Heading>
        
        <Stack 
          direction={{ base: 'column', md: 'row' }} 
          justifyContent="space-between"
          alignItems="center"
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
        </Stack>
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
