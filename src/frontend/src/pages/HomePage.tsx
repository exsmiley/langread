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
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';



// Language options will be created dynamically with translations

const HomePage = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  
  // Language and difficulty states - use user's native language if available
  const [nativeLanguage, setNativeLanguage] = useState(() => {
    return user?.native_language || 'en';
  });
  
  // For target language, use user's default language or first additional language
  const [targetLanguage, setTargetLanguage] = useState(() => {
    if (user?.additional_languages && user.additional_languages.length > 0) {
      const defaultLang = user.additional_languages.find(lang => lang.isDefault);
      if (defaultLang) return defaultLang.language;
      return user.additional_languages[0].language;
    }
    return user?.learning_language || 'ko';
  });
  
  const [difficulty, setDifficulty] = useState(() => {
    return user?.proficiency || 'intermediate';
  });
  
  const [isLoading, setIsLoading] = useState(false);
  
  // Language options with translations
  const languageOptions = [
    { value: 'en', label: t('settings.languages.english') },
    { value: 'ko', label: t('settings.languages.korean') },
    { value: 'fr', label: t('settings.languages.french') },
    { value: 'es', label: t('settings.languages.spanish') },
    { value: 'de', label: t('settings.languages.german') },
    { value: 'ja', label: t('settings.languages.japanese') },
    { value: 'zh', label: t('settings.languages.chinese') },
    { value: 'ru', label: t('settings.languages.russian') }
  ];
  
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
      navigate(`/articles?native=${nativeLanguage}&target=${targetLanguage}&difficulty=${difficulty}`);
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
              <Image src="/images/mascot.png" alt={t('common.mascot')} boxSize="60px" borderRadius="full" />
            </Box>
            <Heading as="h1" size="2xl">
              {t('common.appName')}
            </Heading>
          </Flex>
          <Text fontSize="xl" color="gray.600">
            {t('home.description')}
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
              loadingText={t('home.searching')}
              size="lg"
              px={10}
              py={7}
              fontSize="xl"
              borderRadius="md"
              _hover={{ transform: "translateY(-2px)", boxShadow: "lg" }}
              transition="all 0.2s"
            >
              {t('home.findArticles')}
            </Button>
          </Box>
        </VStack>
        

      </Flex>
      
      <VStack spacing={10} py={16} px={8}>
        <Heading as="h2" size="xl" textAlign="center">
          {t('home.howItWorks')}
        </Heading>
        
        <Stack 
          direction={{ base: 'column', md: 'row' }} 
          justifyContent="space-between"
          alignItems="center"
          w="100%"
          spacing={8}
        >
          <FeatureCard 
            title={t('home.features.discoverContent.title')} 
            description={t('home.features.discoverContent.description')}
            iconUrl="🔍"
          />
          <FeatureCard 
            title={t('home.features.readWithAssistance.title')} 
            description={t('home.features.readWithAssistance.description')}
            iconUrl="📚"
          />
          <FeatureCard 
            title={t('home.features.buildVocabulary.title')} 
            description={t('home.features.buildVocabulary.description')}
            iconUrl="📝"
          />
          <FeatureCard 
            title={t('home.features.testComprehension.title')} 
            description={t('home.features.testComprehension.description')}
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
