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

const TermsPage = () => {
  const { t } = useTranslation();
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Container maxW="container.xl" py={10}>
      <VStack spacing={10} align="start">
        <Heading as="h1" size="2xl">{t('terms.title')}</Heading>
        
        <Divider />
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('terms.agreement.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.agreement.content')}
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('terms.use.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.use.content')}
          </Text>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.use.restrictions')}
          </Text>
          <Box as="ul" pl={5} alignSelf="stretch">
            <Box as="li" pb={2}>
              <Text>{t('terms.use.item1')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('terms.use.item2')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('terms.use.item3')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('terms.use.item4')}</Text>
            </Box>
            <Box as="li" pb={2}>
              <Text>{t('terms.use.item5')}</Text>
            </Box>
          </Box>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('terms.accounts.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.accounts.responsibility')}
          </Text>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.accounts.termination')}
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('terms.ip.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.ip.userResponsibility')}
          </Text>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.ip.ownership')}
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('terms.ugc.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.ugc.license')}
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('terms.liability.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.liability.limitation')}
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('terms.changes.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.changes.right')}
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('terms.law.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.law.jurisdiction')}
          </Text>
        </VStack>
        
        <VStack spacing={6} align="start" width="100%">
          <Heading as="h2" size="lg">{t('terms.contact.title')}</Heading>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.contact.questions')} <strong>terms@lingogi.com</strong>.
          </Text>
          <Text fontSize="md" lineHeight="tall">
            {t('terms.lastUpdated')}: {t('terms.updateDate')}
          </Text>
        </VStack>
      </VStack>
    </Container>
  );
};

export default TermsPage;
