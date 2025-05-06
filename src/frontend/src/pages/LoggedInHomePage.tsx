import React from 'react';
import {
  Box,
  Heading,
  Text,
  Button,
  Container,
  VStack,
  HStack,
  Image,
  useColorModeValue,
  Divider,
  SimpleGrid,
  Icon,
  Flex,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { FaBook, FaPencilAlt, FaRegListAlt } from 'react-icons/fa';
import { MdTranslate } from 'react-icons/md';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';

const LoggedInHomePage = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const accentColor = useColorModeValue('blue.500', 'blue.300');
  
  // Helper function to get language name from code
  const getLanguageName = (code: string) => {
    const languages: { [key: string]: string } = {
      en: 'English',
      ko: 'Korean',
      ja: 'Japanese',
      zh: 'Chinese',
      es: 'Spanish',
      fr: 'French',
    };
    return languages[code] || code;
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Welcome Section */}
        <Box 
          p={8} 
          bg={bgColor} 
          borderRadius="xl" 
          borderWidth="1px"
          borderColor={borderColor}
          boxShadow="md"
        >
          <VStack align="start" spacing={4}>
            <Heading as="h1" size="xl">
              {t('home.welcomeBack', { name: user?.name })}
            </Heading>
            <Text fontSize="lg" color="gray.600">
              {t('home.continueJourney')}
            </Text>
            <Text>
              {/* Don't use the t() function with JSX directly - break it into parts */}
              {t('home.youreLearning', { language: '' })}
              <Text as="span" fontWeight="bold" color={accentColor}> {getLanguageName(user?.learning_language || 'ko')}</Text>
              {t('home.youreLearningEnd')}
            </Text>
            
            <HStack spacing={4} pt={4}>
              <Button 
                as={RouterLink} 
                to="/articles" 
                colorScheme="blue" 
                size="lg"
                leftIcon={<FaBook />}
              >
                {t('home.findArticles')}
              </Button>
              <Button 
                as={RouterLink} 
                to="/vocabulary" 
                colorScheme="green" 
                size="lg" 
                variant="outline"
                leftIcon={<MdTranslate />}
              >
                {t('nav.vocabulary')}
              </Button>
            </HStack>
          </VStack>
        </Box>
        
        {/* Quick Stats */}
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          <StatCard 
            title={t('home.articlesRead')} 
            value="0" 
            description={t('home.articlesReadDesc')} 
            icon={FaBook} 
            color="blue.500"
          />
          <StatCard 
            title={t('home.wordsLearned')} 
            value="0" 
            description={t('home.wordsLearnedDesc')} 
            icon={MdTranslate} 
            color="green.500"
          />
          <StatCard 
            title={t('home.studySessions')} 
            value="0" 
            description={t('home.studySessionsDesc')} 
            icon={FaPencilAlt} 
            color="purple.500"
          />
        </SimpleGrid>
        
        {/* Recommended Articles */}
        <Box>
          <Heading size="md" mb={4}>{t('home.recommendedForYou')}</Heading>
          <Divider mb={6} />
          
          <VStack spacing={4} align="stretch">
            <Text color="gray.500">
              {t('home.startExploring')}
            </Text>
            <Button 
              as={RouterLink} 
              to="/articles" 
              colorScheme="blue" 
              variant="outline"
              leftIcon={<FaRegListAlt />}
              alignSelf="flex-start"
            >
              {t('home.browseAllArticles')}
            </Button>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

// Stats card component
const StatCard = ({ 
  title, 
  value, 
  description, 
  icon, 
  color 
}: { 
  title: string; 
  value: string; 
  description: string; 
  icon: any; 
  color: string;
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  return (
    <Box 
      p={6} 
      bg={bgColor} 
      borderRadius="lg" 
      borderWidth="1px"
      borderColor={borderColor}
      boxShadow="sm"
    >
      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="md">{title}</Heading>
        <Icon as={icon} boxSize={6} color={color} />
      </Flex>
      <Heading size="2xl" mb={2}>{value}</Heading>
      <Text fontSize="sm" color="gray.500">{description}</Text>
    </Box>
  );
};

export default LoggedInHomePage;
