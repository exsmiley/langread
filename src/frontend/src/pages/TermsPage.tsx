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

const TermsPage = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Container maxW="container.xl" py={10}>
      <VStack spacing={10} align="start">
        <Heading as="h1" size="2xl">Terms of Service</Heading>
        
        <Divider />
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">1. Agreement to Terms</Heading>
          <Text fontSize="md" lineHeight="tall">
            By using Lingogi, you agree to these Terms of Service. Our platform is provided "as is" without any warranties, expressed or implied. If you do not agree with any part of these terms, please do not use our service.
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">2. Use of Service</Heading>
          <Text fontSize="md" lineHeight="tall">
            Lingogi provides a platform for language learning through authentic content, translations, and vocabulary building. You may use our service for personal, non-commercial purposes only.
          </Text>
          <Text fontSize="md" lineHeight="tall">
            You agree not to:
          </Text>
          <Box as="ul" pl={5} alignSelf="stretch">
            <Box as="li" pb={2}>
              <Text>Use the service in any way that violates applicable laws or regulations</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Attempt to gain unauthorized access to any part of the service</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Use the service to distribute malware or other harmful code</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Interfere with or disrupt the service or servers</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>Scrape, data mine, or otherwise extract data from the service without permission</Text>
            </Box>
          </Box>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">3. User Accounts</Heading>
          <Text fontSize="md" lineHeight="tall">
            To access certain features of the service, you may need to create an account. You are responsible for maintaining the confidentiality of your account information and for all activities that occur under your account.
          </Text>
          <Text fontSize="md" lineHeight="tall">
            We reserve the right to terminate or suspend your account at our sole discretion, without notice, for conduct that we believe violates these Terms or is harmful to other users, us, or third parties, or for any other reason.
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">4. Intellectual Property Rights</Heading>
          <Text fontSize="md" lineHeight="tall">
            Users are responsible for ensuring they have the right to access and use the content available through our service. Lingogi respects intellectual property rights and expects users to do the same.
          </Text>
          <Text fontSize="md" lineHeight="tall">
            The service and its original content, features, and functionality are owned by Lingogi and are protected by international copyright, trademark, patent, trade secret, and other intellectual property or proprietary rights laws.
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">5. User-Generated Content</Heading>
          <Text fontSize="md" lineHeight="tall">
            Users may have the ability to submit, post, or display content on the service. By submitting content, you grant us a worldwide, non-exclusive, royalty-free license to use, reproduce, modify, adapt, publish, translate, and distribute it in any medium and format.
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">6. Limitation of Liability</Heading>
          <Text fontSize="md" lineHeight="tall">
            In no event shall Lingogi, its directors, employees, partners, agents, suppliers, or affiliates be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses.
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">7. Changes to Terms</Heading>
          <Text fontSize="md" lineHeight="tall">
            We reserve the right to modify these terms at any time. Continued use of the service after changes constitutes acceptance of the new terms. It is your responsibility to review these Terms periodically for changes.
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">8. Governing Law</Heading>
          <Text fontSize="md" lineHeight="tall">
            These Terms shall be governed by and construed in accordance with the laws of the jurisdiction in which Lingogi operates, without regard to its conflict of law provisions.
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">9. Contact Information</Heading>
          <Text fontSize="md" lineHeight="tall">
            For any questions about these Terms, please contact us at <strong>terms@lingogi.com</strong>.
          </Text>
          <Text fontSize="md" lineHeight="tall">
            Last updated: April 30, 2025
          </Text>
        </VStack>
      </VStack>
    </Container>
  );
};

export default TermsPage;
