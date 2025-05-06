import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  HStack,
  Badge,
  Input,
  Select,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Switch,
  useToast,
  Flex,
  Tag,
  TagLabel,
  Spinner,
  InputGroup,
  InputLeftElement,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  TagCloseButton
} from '@chakra-ui/react';
import { SearchIcon, ChevronDownIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '../api';

type Tag = {
  _id: string;
  name: string;
  original_language: string;
  language_specific: boolean;
  translations: Record<string, string>;
  article_count: number;
  active: boolean;
  auto_approved: boolean;
  created_at: string;
  updated_at: string;
  localized_name?: string;
};

type TagStats = {
  total: number;
  by_language: Record<string, number>;
  by_active: Record<string, number>;
  popular_tags: Array<{
    id: string;
    name: string;
    count: number;
  }>;
};

const languageNames: Record<string, string> = {
  en: 'English',
  ko: 'Korean',
  fr: 'French',
  es: 'Spanish',
  de: 'German',
  ja: 'Japanese',
  zh: 'Chinese',
  ru: 'Russian',
  pt: 'Portuguese',
  ar: 'Arabic',
  hi: 'Hindi',
  bn: 'Bengali',
  it: 'Italian',
};

const AdminTagsPage: React.FC = () => {
  const { t } = useTranslation();
  const [tags, setTags] = useState<Tag[]>([]);
  const [filteredTags, setFilteredTags] = useState<Tag[]>([]);
  const [stats, setStats] = useState<TagStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortBy, setSortBy] = useState('article_count');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentTag, setCurrentTag] = useState<Tag | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  const navigate = useNavigate();

  // Fetch tags on component mount
  useEffect(() => {
    fetchTags();
    fetchTagStats();
  }, []);

  // Apply filters whenever they change
  useEffect(() => {
    applyFilters();
  }, [tags, searchQuery, languageFilter, statusFilter, sortBy, sortOrder]);

  const fetchTags = async () => {
    try {
      setLoading(true);
      const response = await api.get('/tags');
      if (response.data && response.data.tags) {
        setTags(response.data.tags);
      } else {
        console.error('Unexpected response format:', response.data);
        setTags([]);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching tags:', error);
      toast({
        title: t('admin.errorFetchingTags'),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      setLoading(false);
    }
  };

  const fetchTagStats = async () => {
    try {
      const response = await api.get('/tags/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching tag stats:', error);
    }
  };

  const applyFilters = () => {
    let filtered = [...tags];

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(tag => {
        // Search in name and translations
        if (tag.name.toLowerCase().includes(query)) return true;
        
        // Search in translations
        if (tag.translations) {
          for (const lang in tag.translations) {
            if (tag.translations[lang].toLowerCase().includes(query)) return true;
          }
        }
        
        return false;
      });
    }

    // Apply language filter
    if (languageFilter) {
      filtered = filtered.filter(tag => 
        tag.original_language === languageFilter ||
        (tag.translations && tag.translations[languageFilter])
      );
    }

    // Apply status filter
    if (statusFilter) {
      if (statusFilter === 'active') {
        filtered = filtered.filter(tag => tag.active);
      } else if (statusFilter === 'inactive') {
        filtered = filtered.filter(tag => !tag.active);
      } else if (statusFilter === 'auto_approved') {
        filtered = filtered.filter(tag => tag.auto_approved);
      }
    }

    // Apply sorting
    filtered.sort((a, b) => {
      if (sortBy === 'name') {
        return sortOrder === 'asc' 
          ? a.name.localeCompare(b.name) 
          : b.name.localeCompare(a.name);
      } else if (sortBy === 'article_count') {
        return sortOrder === 'asc' 
          ? a.article_count - b.article_count 
          : b.article_count - a.article_count;
      } else if (sortBy === 'created_at') {
        return sortOrder === 'asc' 
          ? new Date(a.created_at).getTime() - new Date(b.created_at).getTime() 
          : new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
      return 0;
    });

    setFilteredTags(filtered);
  };

  const handleTagActivation = async (tagId: string, active: boolean) => {
    try {
      if (active) {
        await api.post(`/tags/${tagId}/activate`);
      } else {
        await api.post(`/tags/${tagId}/deactivate`);
      }
      
      // Update local state
      setTags(tags.map(tag => 
        tag._id === tagId ? { ...tag, active } : tag
      ));
      
      toast({
        title: t('admin.tagActivated', { active }),
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
      
      // Refresh tag stats
      fetchTagStats();
    } catch (error) {
      console.error(`Error ${active ? 'activating' : 'deactivating'} tag:`, error);
      toast({
        title: t('admin.errorActivatingTag', { active }),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleEditTag = (tag: Tag) => {
    setCurrentTag(tag);
    onOpen();
  };

  const handleDeleteTag = async (tagId: string) => {
    if (!window.confirm(t('admin.confirmDeleteTag'))) {
      return;
    }

    try {
      await api.delete(`/tags/${tagId}`);
      
      // Update local state
      setTags(tags.filter(tag => tag._id !== tagId));
      
      toast({
        title: t('admin.tagDeleted'),
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
      
      // Refresh tag stats
      fetchTagStats();
    } catch (error) {
      console.error('Error deleting tag:', error);
      toast({
        title: t('admin.errorDeletingTag'),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleSaveTag = async () => {
    if (!currentTag) return;

    try {
      await api.patch(`/tags/${currentTag._id}`, {
        name: currentTag.name,
        translations: currentTag.translations,
        active: currentTag.active
      });
      
      // Update local state
      setTags(tags.map(tag => 
        tag._id === currentTag._id ? currentTag : tag
      ));
      
      toast({
        title: t('admin.tagUpdated'),
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
      
      onClose();
      
      // Refresh data
      fetchTags();
      fetchTagStats();
    } catch (error) {
      console.error('Error updating tag:', error);
      toast({
        title: t('admin.errorUpdatingTag'),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleTranslationChange = (language: string, value: string) => {
    if (!currentTag) return;

    const updatedTranslations = {
      ...currentTag.translations,
      [language]: value
    };

    setCurrentTag({
      ...currentTag,
      translations: updatedTranslations
    });
  };

  const handleAddTranslation = (language: string) => {
    if (!currentTag) return;
    
    // Skip if this language already has a translation
    if (currentTag.translations && currentTag.translations[language]) return;
    
    handleTranslationChange(language, '');
  };

  const handleRemoveTranslation = (language: string) => {
    if (!currentTag || !currentTag.translations) return;
    
    const updatedTranslations = { ...currentTag.translations };
    delete updatedTranslations[language];
    
    setCurrentTag({
      ...currentTag,
      translations: updatedTranslations
    });
  };

  return (
    <Box p={5}>
      <Heading as="h1" size="xl" mb={8}>{t('admin.tagManagement')}</Heading>

      {/* Stats Section */}
      {stats && (
        <Box mb={6} p={4} borderWidth="1px" borderRadius="lg">
          <Heading size="md" mb={4}>{t('admin.tagStatistics')}</Heading>
          
          <Box p={4} borderWidth="1px" borderRadius="md">
            <Text mb={2} fontWeight="bold">{t('admin.totalTags')} {stats.total || 0}</Text>
            
            <Text mb={2} fontWeight="bold">{t('admin.activeTags')} {stats.by_active?.true || 0}</Text>
            
            <Text mb={2} fontWeight="bold">{t('admin.inactiveTags')} {stats.by_active?.false || 0}</Text>
            
            <Text fontWeight="bold">{t('admin.topLanguages')}</Text>
            <HStack mt={1} spacing={2}>
              {Object.entries(stats.by_language || {})
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([lang, count]) => (
                  <Tag size="md" key={lang} colorScheme="blue">
                    <TagLabel>{languageNames[lang] || lang}: {count}</TagLabel>
                  </Tag>
                ))}
            </HStack>
          </Box>
          
          <Box mt={4}>
            <Text fontWeight="bold" mb={2}>{t('admin.mostUsedTags')}</Text>
            <HStack spacing={2} wrap="wrap">
              {stats.popular_tags?.map(tag => (
                <Tag size="md" key={tag.id} colorScheme="green">
                  <TagLabel>{tag.name} ({tag.count})</TagLabel>
                </Tag>
              ))}
            </HStack>
          </Box>
        </Box>
      )}

      {/* Filters Section */}
      <Box mb={6} p={4} borderWidth="1px" borderRadius="lg">
        <Heading size="md" mb={3}>{t('admin.filters')}</Heading>
        <Flex flexWrap="wrap" gap={4}>
          <Box flex="1" minW="250px">
            <InputGroup>
              <InputLeftElement pointerEvents="none">
                <SearchIcon color="gray.300" />
              </InputLeftElement>
              <Input
                placeholder={t('admin.searchTags')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </InputGroup>
          </Box>
          <Box flex="1" minW="200px">
            <Select
              placeholder={t('admin.filterByLanguage')}
              value={languageFilter}
              onChange={(e) => setLanguageFilter(e.target.value)}
            >
              <option value="">All Languages</option>
              {Object.entries(languageNames).map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </Select>
          </Box>
          <Box flex="1" minW="200px">
            <Select
              placeholder={t('admin.filterByStatus')}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="active">{t('admin.active')}</option>
              <option value="inactive">{t('admin.inactive')}</option>
              <option value="auto_approved">{t('admin.autoApproved')}</option>
            </Select>
          </Box>
          <Box flex="1" minW="200px">
            <Menu>
              <MenuButton as={Button} rightIcon={<ChevronDownIcon />} w="100%">
                Sort: {sortBy === 'name' ? t('admin.name') : sortBy === 'article_count' ? t('admin.usage') : t('admin.dateCreated')} ({sortOrder === 'asc' ? t('admin.ascending') : t('admin.descending')})
              </MenuButton>
              <MenuList>
                <MenuItem onClick={() => { setSortBy('name'); setSortOrder('asc'); }}>{t('admin.nameAZ')}</MenuItem>
                <MenuItem onClick={() => { setSortBy('name'); setSortOrder('desc'); }}>{t('admin.nameZA')}</MenuItem>
                <MenuItem onClick={() => { setSortBy('article_count'); setSortOrder('desc'); }}>{t('admin.mostUsed')}</MenuItem>
                <MenuItem onClick={() => { setSortBy('article_count'); setSortOrder('asc'); }}>{t('admin.leastUsed')}</MenuItem>
                <MenuItem onClick={() => { setSortBy('created_at'); setSortOrder('desc'); }}>{t('admin.newestFirst')}</MenuItem>
                <MenuItem onClick={() => { setSortBy('created_at'); setSortOrder('asc'); }}>{t('admin.oldestFirst')}</MenuItem>
              </MenuList>
            </Menu>
          </Box>
        </Flex>
      </Box>

      {/* Tags Table */}
      <Box overflowX="auto">
        {loading ? (
          <Flex justify="center" p={10}>
            <Spinner size="xl" />
          </Flex>
        ) : (
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>{t('admin.tagName')}</Th>
                <Th>{t('admin.language')}</Th>
                <Th>{t('admin.translations')}</Th>
                <Th isNumeric>{t('admin.articles')}</Th>
                <Th>{t('admin.status')}</Th>
                <Th>{t('admin.actions')}</Th>
              </Tr>
            </Thead>
            <Tbody>
              {filteredTags.map((tag) => (
                <Tr key={tag._id}>
                  <Td fontWeight="medium">{tag.name}</Td>
                  <Td>{languageNames[tag.original_language] || tag.original_language}</Td>
                  <Td>
                    <HStack wrap="wrap" spacing={2}>
                      {tag.translations && Object.entries(tag.translations).map(([lang, translation]) => (
                        <Tag size="sm" key={lang} colorScheme="gray">
                          <TagLabel title={languageNames[lang] || lang}>{lang}: {translation}</TagLabel>
                        </Tag>
                      ))}
                      {(!tag.translations || Object.keys(tag.translations).length === 0) && (
                        <Text color="gray.500" fontSize="sm">{t('admin.noTranslations')}</Text>
                      )}
                    </HStack>
                  </Td>
                  <Td isNumeric>{tag.article_count}</Td>
                  <Td>
                    <HStack spacing={2}>
                      <Badge colorScheme={tag.active ? "green" : "red"}>
                        {tag.active ? t('admin.active') : t('admin.inactive')}
                      </Badge>
                      {tag.auto_approved && (
                        <Badge colorScheme="blue">{t('admin.autoApproved')}</Badge>
                      )}
                    </HStack>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <Button 
                        size="sm" 
                        colorScheme={tag.active ? "red" : "green"}
                        onClick={() => handleTagActivation(tag._id, !tag.active)}
                      >
                        {tag.active ? t('admin.deactivate') : t('admin.activate')}
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleEditTag(tag)}
                      >
                        {t('admin.edit')}
                      </Button>
                      <Button
                        size="sm"
                        colorScheme="red"
                        variant="outline"
                        onClick={() => handleDeleteTag(tag._id)}
                      >
                        {t('admin.delete')}
                      </Button>
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}

        {!loading && filteredTags.length === 0 && (
          <Box textAlign="center" p={10}>
            <Text fontSize="lg" color="gray.500">
              {t('admin.noTagsFound')}
            </Text>
          </Box>
        )}
      </Box>

      {/* Edit Tag Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('admin.editTag')}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {currentTag && (
              <Box>
                <FormControl mb={4}>
                  <FormLabel>{t('admin.tagName')}</FormLabel>
                  <Input 
                    value={currentTag.name} 
                    onChange={(e) => setCurrentTag({...currentTag, name: e.target.value})}
                  />
                </FormControl>
                
                <FormControl mb={4}>
                  <FormLabel>{t('admin.originalLanguage')}</FormLabel>
                  <Input 
                    value={languageNames[currentTag.original_language] || currentTag.original_language} 
                    isReadOnly
                  />
                </FormControl>
                
                <FormControl mb={4} display="flex" alignItems="center">
                  <FormLabel mb={0}>{t('admin.active')}</FormLabel>
                  <Switch 
                    isChecked={currentTag.active}
                    onChange={(e) => setCurrentTag({...currentTag, active: e.target.checked})}
                    isDisabled={currentTag.auto_approved}
                  />
                  {currentTag.auto_approved && (
                    <Badge ml={2} colorScheme="blue">{t('admin.autoApproved')}</Badge>
                  )}
                </FormControl>

                <Box mb={4}>
                  <FormLabel>{t('admin.translations')}</FormLabel>
                  {currentTag.translations && Object.entries(currentTag.translations).map(([lang, translation]) => (
                    <Flex key={lang} mb={2} align="center">
                      <Text width="80px" fontWeight="medium">{lang}:</Text>
                      <Input 
                        value={translation} 
                        onChange={(e) => handleTranslationChange(lang, e.target.value)}
                        mr={2}
                      />
                      <IconButton
                        aria-label={t('admin.removeTranslation')}
                        icon={<TagCloseButton />}
                        size="sm"
                        onClick={() => handleRemoveTranslation(lang)}
                      />
                    </Flex>
                  ))}
                  
                  <Menu>
                    <MenuButton as={Button} size="sm" mt={2}>
                      Add Translation
                    </MenuButton>
                    <MenuList>
                      {Object.entries(languageNames)
                        .filter(([code]) => !currentTag.translations || !currentTag.translations[code])
                        .map(([code, name]) => (
                          <MenuItem 
                            key={code} 
                            onClick={() => handleAddTranslation(code)}
                          >
                            {name} ({code})
                          </MenuItem>
                        ))}
                    </MenuList>
                  </Menu>
                </Box>

                <FormControl mb={4}>
                  <FormLabel>Article Count</FormLabel>
                  <Input 
                    value={currentTag.article_count} 
                    isReadOnly
                  />
                </FormControl>
              </Box>
            )}
          </ModalBody>

          <ModalFooter>
            <Button mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="blue" onClick={handleSaveTag}>
              Save
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default AdminTagsPage;
