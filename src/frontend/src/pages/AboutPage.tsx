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

const AboutPage = () => {
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
              alt="Lingogi mascot" 
              boxSize="80px" 
              borderRadius="full" 
              border="2px solid"
              borderColor={borderColor}
            />
          </Box>
          <Heading as="h1" size="2xl">
            About Lingogi
          </Heading>
        </Flex>
        <Text fontSize="xl" maxW="3xl">
          Lingogi is a next-generation language learning platform that helps you improve your language skills through authentic content, context-aware translations, and intelligent vocabulary building.
        </Text>
      </VStack>

      {/* Our mission */}
      <Box bg={bgColor} p={8} borderRadius="lg" mb={16}>
        <VStack spacing={6}>
          <Heading as="h2" size="xl">Our Mission</Heading>
          <Text fontSize="lg" textAlign="center" maxW="3xl">
            Lingogi's mission is to make language learning more engaging and effective by connecting learners with authentic content in their target language. We believe that reading real articles, understanding words in context, and building vocabulary systematically is the key to language mastery.
          </Text>
        </VStack>
      </Box>

      {/* Our story */}
      <VStack spacing={8} mb={16}>
        <Heading as="h2" size="xl">Our Story</Heading>
        <Text fontSize="lg">
          The name "Lingogi" is a blend of "lingo" (language) and "gi" (기), the Korean word for tool or device. Our mascot, a cute meat character with a halo, plays on the Korean word "gogi" (고기/meat) and creates a memorable visual identity with cultural relevance to Korean cuisine.
        </Text>
        <Text fontSize="lg">
          Lingogi started with a focus on Korean language learners who speak English, but our platform is designed to expand to support multiple language pairs, helping learners worldwide connect with authentic content in their target languages.
        </Text>
      </VStack>

      {/* Key features */}
      <Box mb={16}>
        <Heading as="h2" size="xl" mb={8} textAlign="center">Key Features</Heading>
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={10}>
          <FeatureCard 
            title="Article Aggregation"
            description="Discover content from various sources, filtered and organized by difficulty level and topic."
            icon="🔍"
          />
          <FeatureCard 
            title="Context-Aware Translation"
            description="Translate words and phrases with consideration for the surrounding context, providing more accurate meanings."
            icon="🔤"
          />
          <FeatureCard 
            title="Vocabulary Building"
            description="Automatically save words you've looked up and review them with our flashcard system."
            icon="📚"
          />
          <FeatureCard 
            title="Comprehension Testing"
            description="Test your understanding with auto-generated quizzes based on article content."
            icon="✏️"
          />
        </SimpleGrid>
      </Box>

      {/* Team section */}
      <Box mb={16}>
        <Heading as="h2" size="xl" mb={8} textAlign="center">Meet Our Mascot</Heading>
        <Flex direction={{ base: 'column', md: 'row' }} align="center" justify="center">
          <Box mr={{ base: 0, md: 10 }} mb={{ base: 6, md: 0 }}>
            <Image 
              src="/images/mascot.png" 
              alt="Gogi - The Lingogi Mascot" 
              borderRadius="md"
              boxSize="200px"
              objectFit="cover"
              border="2px solid"
              borderColor={borderColor}
            />
          </Box>
          <VStack align="start" maxW="md" spacing={4}>
            <Heading as="h3" size="lg">Gogi</Heading>
            <Text>
              Meet Gogi, our friendly mascot! As a cute meat character with a halo, Gogi represents the Korean word "gogi" (meat) combined with learning enlightenment. Gogi guides users through their language learning journey, making the experience more engaging and fun.
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
