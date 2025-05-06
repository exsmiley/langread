import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Text,
  Select,
  Tag,
  TagLabel,
  TagCloseButton,
  Input,
  InputGroup,
  InputLeftElement,
  Button,
  HStack,
  VStack,
  Flex,
  Heading,
  useColorModeValue,
  Wrap,
  WrapItem,
  Spinner
} from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';
import { api } from '../api';

type TagType = {
  _id: string;
  name: string;
  localized_name?: string;
  original_language: string;
  translations: Record<string, string>;
  article_count: number;
};

type TagSelectorProps = {
  onSelectionChange: (languages: {native: string, target: string}, tagIds: string[]) => void;
  defaultNativeLanguage?: string;
  defaultTargetLanguage?: string;
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

const TagSelector: React.FC<TagSelectorProps> = ({ 
  onSelectionChange, 
  defaultNativeLanguage = 'en',
  defaultTargetLanguage = 'ko'
}) => {
  const [availableTags, setAvailableTags] = useState<TagType[]>([]);
  const [filteredTags, setFilteredTags] = useState<TagType[]>([]);
  const [selectedTags, setSelectedTags] = useState<TagType[]>([]);
  const [selectedTagIds, setSelectedTagIds] = useState<string[]>([]);
  const { t } = useTranslation();
  
  const [
    searchQuery,
    setSearchQuery
  ] = useState('');
  const [nativeLanguage, setNativeLanguage] = useState(defaultNativeLanguage);
  const [targetLanguage, setTargetLanguage] = useState(defaultTargetLanguage);
  const [loading, setLoading] = useState(true);

  const tagBgColor = useColorModeValue('gray.100', 'gray.700');
  const selectedTagBgColor = useColorModeValue('blue.100', 'blue.700');

  // Fetch available tags when component mounts or language changes
  useEffect(() => {
    fetchTags();
  }, [targetLanguage]);
  
  // Inform parent when component is ready
  useEffect(() => {
    // Once we're no longer loading, notify parent component
    if (!loading) {
      onSelectionChange(
        { native: nativeLanguage, target: targetLanguage },
        selectedTagIds
      );
    }
  }, [loading]);

  // Filter tags based on search query
  useEffect(() => {
    filterTags();
  }, [availableTags, searchQuery]);

  // Notify parent component when selection changes
  useEffect(() => {
    onSelectionChange(
      { native: nativeLanguage, target: targetLanguage },
      selectedTagIds
    );
  }, [nativeLanguage, targetLanguage, selectedTagIds, onSelectionChange]);

  const fetchTags = async () => {
    try {
      setLoading(true);
      // Fetch tags for the target language (language the user is learning)
      console.log(`Fetching tags for language: ${targetLanguage}`);
      const response = await api.get(`/api/tags?language=${targetLanguage}&active=true`);
      
      console.log('Tag API response:', response.data);
      
      // Check if we received data - handle both array and object with tags property
      if (response.data && response.data.tags && Array.isArray(response.data.tags) && response.data.tags.length > 0) {
        console.log('Successfully loaded tags from tags property:', response.data.tags.length);
        setAvailableTags(response.data.tags);
      } else if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        console.log('Successfully loaded tags from direct array:', response.data.length);
        setAvailableTags(response.data);
      } else {
        // If no tags found in the backend, use fallback tags that are consistent with HomePage
        const fallbackTags: TagType[] = [
          {
            _id: '1',
            name: 'technology',
            original_language: 'en',
            translations: { en: 'technology', ko: '기술', fr: 'technologie' },
            article_count: 12
          },
          {
            _id: '2',
            name: 'sports',
            original_language: 'en',
            translations: { en: 'sports', ko: '스포츠', fr: 'sports' },
            article_count: 8
          },
          {
            _id: '3',
            name: 'music',
            original_language: 'en',
            translations: { en: 'music', ko: '음악', fr: 'musique' },
            article_count: 6
          },
          {
            _id: '4',
            name: 'food',
            original_language: 'en',
            translations: { en: 'food', ko: '음식', fr: 'nourriture' },
            article_count: 10
          },
          {
            _id: '5',
            name: 'travel',
            original_language: 'en',
            translations: { en: 'travel', ko: '여행', fr: 'voyage' },
            article_count: 7
          },
          {
            _id: '6',
            name: 'politics',
            original_language: 'en',
            translations: { en: 'politics', ko: '정치', fr: 'politique' },
            article_count: 9
          }
        ];
        console.log('No tags found in backend, using fallback tags');
        setAvailableTags(fallbackTags);
      }
    } catch (error) {
      console.error('Error fetching tags:', error);
      
      // Use fallback tags in case of an error - exactly same as in HomePage
      const fallbackTags: TagType[] = [
        {
          _id: '1',
          name: 'technology',
          original_language: 'en',
          translations: { en: 'technology', ko: '기술', fr: 'technologie' },
          article_count: 12
        },
        {
          _id: '2',
          name: 'sports',
          original_language: 'en',
          translations: { en: 'sports', ko: '스포츠', fr: 'sports' },
          article_count: 8
        },
        {
          _id: '3',
          name: 'music',
          original_language: 'en',
          translations: { en: 'music', ko: '음악', fr: 'musique' },
          article_count: 6
        },
        {
          _id: '4',
          name: 'food',
          original_language: 'en',
          translations: { en: 'food', ko: '음식', fr: 'nourriture' },
          article_count: 10
        },
        {
          _id: '5',
          name: 'travel',
          original_language: 'en',
          translations: { en: 'travel', ko: '여행', fr: 'voyage' },
          article_count: 7
        },
        {
          _id: '6',
          name: 'politics',
          original_language: 'en',
          translations: { en: 'politics', ko: '정치', fr: 'politique' },
          article_count: 9
        }
      ];
      console.log('Error fetching tags, using fallback tags');
      setAvailableTags(fallbackTags);
    } finally {
      setLoading(false);
    }
  };

  const filterTags = () => {
    if (!searchQuery) {
      setFilteredTags(availableTags);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = availableTags.filter(tag => {
      // Search in name
      if (tag.name.toLowerCase().includes(query)) return true;
      
      // Search in localized name
      if (tag.localized_name && tag.localized_name.toLowerCase().includes(query)) return true;
      
      // Search in translations
      for (const lang in tag.translations) {
        if (tag.translations[lang].toLowerCase().includes(query)) return true;
      }
      
      return false;
    });

    setFilteredTags(filtered);
  };

  const handleTagSelection = (tag: TagType) => {
    if (selectedTagIds.includes(tag._id)) {
      // Remove tag if already selected
      setSelectedTags(selectedTags.filter(t => t._id !== tag._id));
      setSelectedTagIds(selectedTagIds.filter(id => id !== tag._id));
    } else {
      // Add tag if not already selected
      setSelectedTags([...selectedTags, tag]);
      setSelectedTagIds([...selectedTagIds, tag._id]);
    }
  };

  const handleLanguageChange = (language: string, type: 'native' | 'target') => {
    if (type === 'native') {
      setNativeLanguage(language);
    } else {
      // If target language changes, we need to:
      // 1. Update the target language
      setTargetLanguage(language);
      // 2. Clear selected tags as they may not be available in the new language
      setSelectedTags([]);
      setSelectedTagIds([]);
      // 3. Fetch tags for the new language (handled by useEffect)
    }
  };

  // Get display name for a tag based on language preference
  const getTagDisplayName = (tag: TagType) => {
    // Display tags in the target language (the language being learned)
    // This matches the behavior in HomePage and shows Korean tags when learning Korean
    if (tag.translations && tag.translations[targetLanguage]) {
      return tag.translations[targetLanguage];
    }
    // Fallback to canonical name (usually English)
    return tag.name;
  };

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading size="md" mb={2}>{t('components.tagSelector.languageSettings')}</Heading>
          <Flex direction={{ base: 'column', md: 'row' }} gap={4}>
            <Box flex="1">
              <Text mb={1}>{t('components.tagSelector.nativeLanguage')}</Text>
              <Select
                value={nativeLanguage}
                onChange={(e) => handleLanguageChange(e.target.value, 'native')}
              >
                {Object.entries(languageNames).map(([code, name]) => (
                  <option key={`native-${code}`} value={code}>{name}</option>
                ))}
              </Select>
            </Box>
            <Box flex="1">
              <Text mb={1}>{t('components.tagSelector.targetLanguage')}</Text>
              <Select
                value={targetLanguage}
                onChange={(e) => handleLanguageChange(e.target.value, 'target')}
              >
                {Object.entries(languageNames)
                  .filter(([code]) => code !== nativeLanguage)
                  .map(([code, name]) => (
                    <option key={`target-${code}`} value={code}>{name}</option>
                  ))}
              </Select>
            </Box>
          </Flex>
        </Box>

        <Box>
          <Heading size="md" mb={2}>{t('components.tagSelector.selectedTopics')}</Heading>
          {selectedTags.length === 0 ? (
            <Text color="gray.500">{t('components.tagSelector.noTopicsSelected')}</Text>
          ) : (
            <Wrap spacing={2}>
              {selectedTags.map(tag => (
                <WrapItem key={`selected-${tag._id}`}>
                  <Tag 
                    size="md" 
                    borderRadius="full" 
                    variant="solid" 
                    colorScheme="blue"
                  >
                    <TagLabel>{getTagDisplayName(tag)}</TagLabel>
                    <TagCloseButton onClick={() => handleTagSelection(tag)} />
                  </Tag>
                </WrapItem>
              ))}
            </Wrap>
          )}
        </Box>

        <Box>
          <Heading size="md" mb={2}>{t('components.tagSelector.availableTopics')}</Heading>
          <InputGroup mb={4}>
            <InputLeftElement pointerEvents="none">
              <SearchIcon color="gray.300" />
            </InputLeftElement>
            <Input 
              placeholder={t('components.tagSelector.searchTopics')} 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </InputGroup>

          {loading ? (
            <Flex justify="center" p={4}>
              <Spinner />
            </Flex>
          ) : filteredTags.length === 0 ? (
            <Text color="gray.500">{t('components.tagSelector.noTopicsFound')}</Text>
          ) : (
            <Wrap spacing={2}>
              {filteredTags.map(tag => (
                <WrapItem key={tag._id}>
                  <Tag 
                    size="md" 
                    borderRadius="full"
                    variant={selectedTagIds.includes(tag._id) ? "solid" : "subtle"}
                    colorScheme={selectedTagIds.includes(tag._id) ? "blue" : "gray"}
                    cursor="pointer"
                    onClick={() => handleTagSelection(tag)}
                  >
                    <TagLabel>{getTagDisplayName(tag)}</TagLabel>
                  </Tag>
                </WrapItem>
              ))}
            </Wrap>
          )}
        </Box>
      </VStack>
    </Box>
  );
};

export default TagSelector;
