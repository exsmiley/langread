import React from 'react';
import { Box, Container, Stack, Text, Link, useColorModeValue } from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';

const Footer = () => {
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();
  
  // Replace the year in the copyright message
  const copyright = t('footer.copyright').replace('2023-2025', `2023-${currentYear}`);
  
  return (
    <Box
      bg={useColorModeValue('gray.50', 'gray.900')}
      color={useColorModeValue('gray.700', 'gray.200')}
      width="100%"
      mt="auto"
    >
      <Container
        as={Stack}
        maxW={'6xl'}
        py={4}
        direction={{ base: 'column', md: 'row' }}
        spacing={4}
        justify={{ base: 'center', md: 'space-between' }}
        align={{ base: 'center', md: 'center' }}
      >
        <Text>{copyright}</Text>
        <Stack direction={'row'} spacing={6}>
          <Link href={'/privacy'}>{t('footer.privacy')}</Link>
          <Link href={'/terms'}>{t('footer.terms')}</Link>
          <Link href={'/about'}>{t('footer.about')}</Link>
          <Link href={'/contact'}>{t('footer.contact')}</Link>
        </Stack>
      </Container>
    </Box>
  );
};

export default Footer;
