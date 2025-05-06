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
import { useTranslation } from 'react-i18next';

const PrivacyPage = () => {
  const { t } = useTranslation();
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Container maxW="container.xl" py={10}>
      <VStack spacing={10} align="start">
        <Heading as="h1" size="2xl">{t('privacy.title')}</Heading>
        
        <Divider />
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('privacy.collect.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('privacy.collect.intro')}
          </Text>
          <Text fontSize="md" lineHeight="tall">
            {t('privacy.collect.types')}
          </Text>
          <Box as="ul" pl={5} alignSelf="stretch">
            <Box as="li" pb={2}>
              <Text>{t('privacy.collect.item1')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('privacy.collect.item2')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('privacy.collect.item3')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('privacy.collect.item4')}</Text>
            </Box>
          </Box>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('privacy.use.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('privacy.use.intro')}
          </Text>
          <Box as="ul" pl={5} alignSelf="stretch">
            <Box as="li" pb={2}>
              <Text>{t('privacy.use.item1')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('privacy.use.item2')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('privacy.use.item3')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('privacy.use.item4')}</Text>
            </Box>
          </Box>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('privacy.cookies.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('privacy.cookies.info')}
          </Text>
          <Text fontSize="md" lineHeight="tall">
            {t('privacy.cookies.control')}
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('privacy.security.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('privacy.security.info')}
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('privacy.thirdParty.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('privacy.thirdParty.info')}
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('privacy.rights.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('privacy.rights.intro')}
          </Text>
          <Box as="ul" pl={5} alignSelf="stretch">
            <Box as="li" pb={2}>
              <Text>{t('privacy.rights.item1')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('privacy.rights.item2')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('privacy.rights.item3')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('privacy.rights.item4')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('privacy.rights.item5')}</Text>
            </Box>
          </Box>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('privacy.changes.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('privacy.changes.info')}
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('privacy.contact.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('privacy.contact.info')} <strong>privacy@lingogi.com</strong>.
          </Text>
          <Text fontSize="md" lineHeight="tall">
            {t('privacy.lastUpdated')}: {t('privacy.updateDate')}
          </Text>
        </VStack>
      </VStack>
    </Container>
  );
};

export default PrivacyPage;
