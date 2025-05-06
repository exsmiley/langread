import React from 'react';
import { 
  Box, 
  Flex, 
  Text, 
  Button, 
  Stack, 
  useColorModeValue, 
  useDisclosure,
  IconButton,
  Collapse,
  Link as ChakraLink,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Avatar,
  Tooltip,
  Icon
} from '@chakra-ui/react';
import { HamburgerIcon, CloseIcon, ChevronDownIcon, ExternalLinkIcon } from '@chakra-ui/icons';
import { FaGlobe } from 'react-icons/fa';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { useLanguagePreferences, LANGUAGE_OPTIONS } from '../contexts/LanguageContext';

const Navbar = () => {
  const { t } = useTranslation();
  const { isOpen, onToggle } = useDisclosure();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const { user, isAuthenticated, signOut } = useAuth();
  const { uiLanguage, setUILanguage, getNativeLanguageName } = useLanguagePreferences();
  const navigate = useNavigate();

  return (
    <Box>
      <Flex
        bg={bgColor}
        color={useColorModeValue('gray.600', 'white')}
        minH={'60px'}
        py={{ base: 2 }}
        px={{ base: 4 }}
        borderBottom={1}
        borderStyle={'solid'}
        borderColor={borderColor}
        align={'center'}
      >
        <Flex
          flex={{ base: 1, md: 'auto' }}
          ml={{ base: -2 }}
          display={{ base: 'flex', md: 'none' }}
        >
          <IconButton
            onClick={onToggle}
            icon={isOpen ? <CloseIcon w={3} h={3} /> : <HamburgerIcon w={5} h={5} />}
            variant={'ghost'}
            aria-label={t('navigation.toggle')}
          />
        </Flex>
        <Flex flex={{ base: 1 }} justify={{ base: 'center', md: 'start' }}>
          <Flex align="center" as={RouterLink} to="/" _hover={{ textDecoration: 'none' }}>
            <Box mr={2}>
              <img src="/images/mascot.png" alt={t('common.mascot')} style={{ width: '30px', height: '30px', borderRadius: '50%' }} />
            </Box>
            <Text
              textAlign={useColorModeValue('left', 'center')}
              fontFamily={'heading'}
              color={useColorModeValue('gray.800', 'white')}
              fontWeight="bold"
              fontSize="xl"
            >
              Lingogi
            </Text>
          </Flex>

          <Flex display={{ base: 'none', md: 'flex' }} ml={10}>
            <DesktopNav />
          </Flex>
        </Flex>

        <Stack
          flex={{ base: 1, md: 0 }}
          justify={'flex-end'}
          direction={'row'}
          spacing={6}
          align="center"
        >
          {/* Language Switcher */}
          <Menu>
            <Tooltip label={t('navigation.changeLanguage')} placement="bottom">
              <MenuButton
                as={IconButton}
                icon={<FaGlobe />}
                variant="ghost"
                borderRadius="full"
                aria-label={t('navigation.changeLanguage')}
                size="md"
              />
            </Tooltip>
            <MenuList zIndex={100}>
              {LANGUAGE_OPTIONS.map(lang => (
                <MenuItem 
                  key={lang.value} 
                  onClick={() => setUILanguage(lang.value)}
                  fontWeight={uiLanguage === lang.value ? 'bold' : 'normal'}
                >
                  <Flex align="center">
                    {uiLanguage === lang.value && (
                      <Box as="span" mr={2} color="blue.500" fontWeight="bold">
                        ✓
                      </Box>
                    )}
                    {getNativeLanguageName(lang.value)}
                  </Flex>
                </MenuItem>
              ))}
            </MenuList>
          </Menu>

          {isAuthenticated ? (
            <Menu>
              <MenuButton
                as={Button}
                rounded={'full'}
                variant={'link'}
                cursor={'pointer'}
                minW={0}
              >
                <Flex align="center">
                  <Avatar
                    size={'sm'}
                    mr={2}
                    name={user?.name}
                    bg="blue.500"
                  />
                  <Box display={{ base: 'none', md: 'block' }}>
                    <Text fontWeight="medium">{user?.name}</Text>
                    <Text fontSize="xs" color="gray.500" lineHeight="shorter">
                      {t('navigation.userRole')}
                    </Text>
                  </Box>
                  <ChevronDownIcon ml={1} />
                </Flex>
              </MenuButton>
              <MenuList>
                <MenuItem as={RouterLink} to="/settings">{t('navigation.settings')}</MenuItem>
                <MenuDivider />
                <MenuItem onClick={() => {
                  signOut();
                  navigate('/');
                }}>{t('navigation.signOut')}</MenuItem>
              </MenuList>
            </Menu>
          ) : (
            <>
              <Button
                as={RouterLink}
                to="/signin"
                fontSize={'sm'}
                fontWeight={400}
                variant={'link'}
              >
                {t('navigation.signIn')}
              </Button>
              <Button
                as={RouterLink}
                to="/signup"
                display={{ base: 'none', md: 'inline-flex' }}
                fontSize={'sm'}
                fontWeight={600}
                color={'white'}
                bg={'blue.400'}
                _hover={{
                  bg: 'blue.300',
                }}
              >
                {t('navigation.signUp')}
              </Button>
            </>
          )}
        </Stack>
      </Flex>

      <Collapse in={isOpen} animateOpacity>
        <MobileNav />
      </Collapse>
    </Box>
  );
};

const DesktopNav = () => {
  const { t } = useTranslation();
  const linkColor = useColorModeValue('gray.600', 'gray.200');
  const linkHoverColor = useColorModeValue('gray.800', 'white');
  const { isAuthenticated } = useAuth();
  
  // Filter nav items based on authentication status
  const visibleNavItems = NAV_ITEMS(t).filter(item => {
    // Always show Home
    if (item.navKey === 'home') {
      return true;
    }
    // Show About only when not authenticated
    if (item.navKey === 'about') {
      return !isAuthenticated;
    }
    // Only show Articles and Vocabulary when authenticated
    return isAuthenticated;
  });

  return (
    <Stack direction={'row'} spacing={4}>
      {visibleNavItems.map((navItem) => (
        <Box key={navItem.label}>
          <ChakraLink
            as={RouterLink}
            p={2}
            to={navItem.href ?? '#'}
            fontSize={'sm'}
            fontWeight={500}
            color={linkColor}
            _hover={{
              textDecoration: 'none',
              color: linkHoverColor,
            }}
          >
            {navItem.label}
          </ChakraLink>
        </Box>
      ))}
    </Stack>
  );
};

const MobileNav = () => {
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();
  
  // Filter nav items based on authentication status (same logic as DesktopNav)
  const visibleNavItems = NAV_ITEMS(t).filter(item => {
    // Always show Home
    if (item.navKey === 'home') {
      return true;
    }
    // Show About only when not authenticated
    if (item.navKey === 'about') {
      return !isAuthenticated;
    }
    // Only show Articles and Vocabulary when authenticated
    return isAuthenticated;
  });
  
  return (
    <Stack
      bg={useColorModeValue('white', 'gray.800')}
      p={4}
      display={{ md: 'none' }}
    >
      {visibleNavItems.map((navItem) => (
        <MobileNavItem key={navItem.label} {...navItem} />
      ))}
    </Stack>
  );
};

const MobileNavItem = ({ label, href }: NavItem) => {
  return (
    <Stack spacing={4}>
      <ChakraLink
        as={RouterLink}
        to={href ?? '#'}
        py={2}
        _hover={{
          textDecoration: 'none',
        }}
      >
        <Text fontWeight={600} color={useColorModeValue('gray.600', 'gray.200')}>
          {label}
        </Text>
      </ChakraLink>
    </Stack>
  );
};

interface NavItem {
  navKey: string;
  label: string;
  href?: string;
}

// Add navigation.changeLanguage key to the translation files
const addMissingTranslationKeys = () => {
  try {
    const tWithoutPrefix = (key: string) => key;
    // This just helps identify if we're missing any required translation keys
    tWithoutPrefix('navigation.changeLanguage');
  } catch (e) {
    console.warn('Missing translation key: navigation.changeLanguage');
  }
};

// Function to return translated navigation items
const NAV_ITEMS = (t: any): Array<NavItem> => [
  {
    navKey: 'home',
    label: t('navigation.home'),
    href: '/',
  },
  {
    navKey: 'articles',
    label: t('navigation.articles'),
    href: '/articles',
  },
  {
    navKey: 'vocabulary',
    label: t('navigation.vocabulary'),
    href: '/vocabulary',
  },
  {
    navKey: 'about',
    label: t('navigation.about'),
    href: '/about',
  },
];

export default Navbar;
