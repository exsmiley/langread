import React from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  Divider,
  useColorModeValue,
} from '@chakra-ui/react';

const PrivacyPage = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Container maxW="container.xl" py={10}>
      <VStack spacing={10} align="start">
        <Heading as="h1" size="2xl">Privacy Policy</Heading>
        
        <Divider />
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">Information We Collect</Heading>
          <Text fontSize="md" lineHeight="tall">
            At Lingogi, we take your privacy seriously. We only collect the information necessary to provide you with a personalized language learning experience.
          </Text>
          <Text fontSize="md" lineHeight="tall">
            We collect the following types of information:
          </Text>
          <Box as="ul" pl={5} alignSelf="stretch">
            <Box as="li" pb={2}>
              <Text>Personal information you provide (email if you create an account)</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Language preferences and learning progress</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Vocabulary lists and saved articles</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Usage data and interaction patterns</Text>
            </Box>
          </Box>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">How We Use Your Information</Heading>
          <Text fontSize="md" lineHeight="tall">
            We use the information we collect to:
          </Text>
          <Box as="ul" pl={5} alignSelf="stretch">
            <Box as="li" pb={2}>
              <Text>Provide and maintain our language learning service</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Personalize your learning experience</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Track your progress and suggest appropriate content</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Improve our platform based on usage patterns</Text>
            </Box>
          </Box>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">Cookies and Similar Technologies</Heading>
          <Text fontSize="md" lineHeight="tall">
            We use cookies to remember your language preferences and learning progress. Cookies help us provide features like automatic login and remembering your vocabulary lists.
          </Text>
          <Text fontSize="md" lineHeight="tall">
            You can control cookies through your browser settings. However, disabling cookies may limit your access to certain features of our service.
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">Data Security</Heading>
          <Text fontSize="md" lineHeight="tall">
            Your vocabulary and saved articles are stored securely and are never shared with third parties without your explicit consent. We implement appropriate security measures to protect your personal information from unauthorized access or disclosure.
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">Third-Party Services</Heading>
          <Text fontSize="md" lineHeight="tall">
            Lingogi may use third-party services for analytics, hosting, and other functions. These services may collect information sent by your browser as part of a web page request. They have their own privacy policies regarding the information we are required to provide to them.
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">Your Rights</Heading>
          <Text fontSize="md" lineHeight="tall">
            You have the right to:
          </Text>
          <Box as="ul" pl={5} alignSelf="stretch">
            <Box as="li" pb={2}>
              <Text>Access the personal information we have about you</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Correct inaccuracies in your personal information</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Delete your personal information</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Object to the processing of your personal information</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Export your data in a portable format</Text>
            </Box>
          </Box>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">Changes to This Policy</Heading>
          <Text fontSize="md" lineHeight="tall">
            We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the effective date.
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">Contact Us</Heading>
          <Text fontSize="md" lineHeight="tall">
            For more information about our data practices, please contact us at <strong>privacy@lingogi.com</strong>.
          </Text>
          <Text fontSize="md" lineHeight="tall">
            Last updated: April 30, 2025
          </Text>
        </VStack>
      </VStack>
    </Container>
  );
};

export default PrivacyPage;
