import React from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Image,
  Stack,
  VStack,
  HStack,
  Flex,
  SimpleGrid,
  useColorModeValue,
  Divider,
  Link,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';

const AboutPage = () => {
  const { t } = useTranslation();
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Container maxW="container.xl" py={10}>
      {/* Hero section */}
      <VStack spacing={8} textAlign="center" mb={16}>
        <Flex alignItems="center" justifyContent="center">
          <Box mr={4}>
            <Image 
              src="/images/mascot.png" 
              alt={t('common.mascot')} 
              boxSize="80px" 
              borderRadius="full" 
              border="2px solid"
              borderColor={borderColor}
            />
          </Box>
          <Heading as="h1" size="2xl">
            {t('about.title')} {t('common.appName')}
          </Heading>
        </Flex>
        <Text fontSize="xl" maxW="3xl">
          {t('about.description')}
        </Text>
      </VStack>

      {/* Our mission */}
      <Box bg={bgColor} p={8} borderRadius="lg" mb={16}>
        <VStack spacing={6}>
          <Heading as="h2" size="xl">{t('about.mission.title')}</Heading>
          <Text fontSize="lg" textAlign="center" maxW="3xl">
            {t('about.mission.description')}
          </Text>
        </VStack>
      </Box>

      {/* Our story */}
      <VStack spacing={8} mb={16}>
        <Heading as="h2" size="xl">{t('about.story.title')}</Heading>
        <Text fontSize="lg">
          {t('about.story.part1')}
        </Text>
        <Text fontSize="lg">
          {t('about.story.part2')}
        </Text>
      </VStack>

      {/* Key features */}
      <Box mb={16}>
        <Heading as="h2" size="xl" mb={8} textAlign="center">{t('about.features.title')}</Heading>
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={10}>
          <FeatureCard 
            title={t('about.features.article.title')}
            description={t('about.features.article.description')}
            icon="🔍"
          />
          <FeatureCard 
            title={t('about.features.translation.title')}
            description={t('about.features.translation.description')}
            icon="🔤"
          />
          <FeatureCard 
            title={t('about.features.vocabulary.title')}
            description={t('about.features.vocabulary.description')}
            icon="📚"
          />
          <FeatureCard 
            title={t('about.features.comprehension.title')}
            description={t('about.features.comprehension.description')}
            icon="✏️"
          />
        </SimpleGrid>
      </Box>

      {/* Team section */}
      <Box mb={16}>
        <Heading as="h2" size="xl" mb={8} textAlign="center">{t('about.mascot.title')}</Heading>
        <Flex direction={{ base: 'column', md: 'row' }} align="center" justify="center">
          <Box mr={{ base: 0, md: 10 }} mb={{ base: 6, md: 0 }}>
            <Image 
              src="/images/mascot.png" 
              alt={t('about.mascot.alt')} 
              borderRadius="md"
              boxSize="200px"
              objectFit="cover"
              border="2px solid"
              borderColor={borderColor}
            />
          </Box>
          <VStack align="start" maxW="md" spacing={4}>
            <Heading as="h3" size="lg">{t('about.mascot.name')}</Heading>
            <Text>
              {t('about.mascot.description')}
            </Text>
          </VStack>
        </Flex>
      </Box>


    </Container>
  );
};

// Feature card component
interface FeatureCardProps {
  title: string;
  description: string;
  icon: string;
}

const FeatureCard = ({ title, description, icon }: FeatureCardProps) => {
  const cardBgColor = useColorModeValue('white', 'gray.800');
  
  return (
    <Box 
      p={6} 
      boxShadow="md" 
      borderRadius="lg" 
      bg={cardBgColor}
      borderWidth="1px"
      borderColor={useColorModeValue('gray.200', 'gray.700')}
    >
      <HStack spacing={4} mb={3}>
        <Box fontSize="2xl">{icon}</Box>
        <Heading as="h3" size="md">{title}</Heading>
      </HStack>
      <Text>{description}</Text>
    </Box>
  );
};

export default AboutPage;
