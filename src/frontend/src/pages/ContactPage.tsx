import React from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  SimpleGrid,
  Input,
  Textarea,
  Button,
  FormControl,
  FormLabel,
  useColorModeValue,
  Icon,
  Flex,
} from '@chakra-ui/react';
import { FaEnvelope, FaGithub, FaTwitter } from 'react-icons/fa';
import { useTranslation } from 'react-i18next';

const ContactPage = () => {
  const { t } = useTranslation();
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Container maxW="container.xl" py={10}>
      <VStack spacing={10} align="start">
        <Heading as="h1" size="2xl">{t('contact.title')}</Heading>
        
        <Text fontSize="lg" maxW="3xl">
          {t('contact.intro')}
        </Text>
        
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={10} width="100%">
          {/* Contact Form */}
          <Box 
            p={8} 
            bg={cardBgColor} 
            borderRadius="lg" 
            boxShadow="md"
            borderWidth="1px"
            borderColor={borderColor}
          >
            <VStack spacing={5} align="start">
              <Heading as="h3" size="md">{t('contact.form.title')}</Heading>
              
              <FormControl isRequired>
                <FormLabel>{t('contact.form.nameLabel')}</FormLabel>
                <Input placeholder={t('contact.form.namePlaceholder')} />
              </FormControl>
              
              <FormControl isRequired>
                <FormLabel>{t('contact.form.emailLabel')}</FormLabel>
                <Input placeholder={t('contact.form.emailPlaceholder')} type="email" />
              </FormControl>
              
              <FormControl isRequired>
                <FormLabel>{t('contact.form.subjectLabel')}</FormLabel>
                <Input placeholder={t('contact.form.subjectPlaceholder')} />
              </FormControl>
              
              <FormControl isRequired>
                <FormLabel>{t('contact.form.messageLabel')}</FormLabel>
                <Textarea placeholder={t('contact.form.messagePlaceholder')} rows={5} />
              </FormControl>
              
              <Button colorScheme="blue" size="lg" width="100%">
                {t('contact.form.sendButton')}
              </Button>
              
              <Text fontSize="sm" color="gray.500" mt={2}>
                {t('contact.form.responseTime')}
              </Text>
            </VStack>
          </Box>
          
          {/* Contact Information */}
          <VStack align="start" spacing={8}>
            <Box 
              p={8} 
              bg={cardBgColor} 
              borderRadius="lg" 
              boxShadow="md"
              borderWidth="1px"
              borderColor={borderColor}
              width="100%"
            >
              <VStack spacing={5} align="start">
                <Heading as="h3" size="md">{t('contact.info.title')}</Heading>
                
                <HStack spacing={4}>
                  <Flex
                    align="center"
                    justify="center"
                    width="40px"
                    height="40px"
                    borderRadius="full"
                    bg="blue.100"
                    color="blue.500"
                  >
                    <Icon as={FaEnvelope} boxSize={5} />
                  </Flex>
                  <VStack align="start" spacing={0}>
                    <Text fontWeight="bold">{t('contact.info.emailLabel')}</Text>
                    <Text>contact@lingogi.com</Text>
                  </VStack>
                </HStack>
              </VStack>
            </Box>
            
            <Box 
              p={8} 
              bg={cardBgColor} 
              borderRadius="lg" 
              boxShadow="md"
              borderWidth="1px"
              borderColor={borderColor}
              width="100%"
            >
              <VStack spacing={5} align="start">
                <Heading as="h3" size="md">{t('contact.social.title')}</Heading>
                
                <HStack spacing={4}>
                  <Flex
                    align="center"
                    justify="center"
                    width="40px"
                    height="40px"
                    borderRadius="full"
                    bg="gray.100"
                    color="gray.500"
                  >
                    <Icon as={FaGithub} boxSize={5} />
                  </Flex>
                  <VStack align="start" spacing={0}>
                    <Text fontWeight="bold">{t('contact.social.githubLabel')}</Text>
                    <Text>github.com/lingogi</Text>
                  </VStack>
                </HStack>
                
                <HStack spacing={4}>
                  <Flex
                    align="center"
                    justify="center"
                    width="40px"
                    height="40px"
                    borderRadius="full"
                    bg="blue.100"
                    color="blue.400"
                  >
                    <Icon as={FaTwitter} boxSize={5} />
                  </Flex>
                  <VStack align="start" spacing={0}>
                    <Text fontWeight="bold">{t('contact.social.twitterLabel')}</Text>
                    <Text>@lingogi</Text>
                  </VStack>
                </HStack>
              </VStack>
            </Box>
            
            <Box 
              p={8} 
              bg={cardBgColor} 
              borderRadius="lg" 
              boxShadow="md"
              borderWidth="1px"
              borderColor={borderColor}
              width="100%"
            >
              <VStack spacing={5} align="start">
                <Heading as="h3" size="md">{t('contact.hours.title')}</Heading>
                <Text>{t('contact.hours.schedule')}</Text>
                <Text>{t('contact.hours.response')}</Text>
              </VStack>
            </Box>
          </VStack>
        </SimpleGrid>
      </VStack>
    </Container>
  );
};

export default ContactPage;
