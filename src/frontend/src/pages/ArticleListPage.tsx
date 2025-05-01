import React, { useState, useEffect, useCallback, useMemo, useRef, FormEvent, ChangeEvent } from 'react';
import { useLanguagePreferences } from '../hooks/useLanguagePreferences';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  FormControl,
  FormLabel,
  Select,
  Input,
  InputGroup,
  InputLeftElement,
  Radio,
  RadioGroup,
  Stack,
  Flex,
  Wrap,
  WrapItem,
  Tag,
  TagLabel,
  TagCloseButton,
  Spinner,
  useColorModeValue,
  useToast,
  Alert,
  AlertIcon,
  Badge,
  SimpleGrid,
  Image,
  Divider
} from '@chakra-ui/react';
import { SearchIcon, ChevronUpIcon, ChevronDownIcon } from '@chakra-ui/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';

// Type definitions
interface Article {
  id: string;
  title: string;
  description: string;
  source: string;
  date_published: string;
  topics?: string[];
  tag_ids?: string[];
  image_url?: string;
  content?: string | any[];
  difficulty?: string;
  language?: string;
}

interface Tag {
  _id: string;
  name: string;
  localized_name?: string;
  original_language: string;
  translations: Record<string, string>;
  article_count?: number;
  active?: boolean;
}

// Utility functions for handling article data
const getArticleId = (article: Article | any): string => {
  return article?.id || article?._id || 'unknown';
};

const getArticleTitle = (article: Article | any): string => {
  return article?.title || 'Untitled Article';
};

const getArticleDescription = (article: Article | any): string => {
  // If the article has an explicit description, use it
  if (article?.description) {
    return article.description;
  }
  
  // Otherwise, try to extract the first paragraph from content
  if (Array.isArray(article?.content)) {
    // Find the first text section
    const textSection = article.content.find((section: any) => 
      section.type === 'text' && section.content
    );
    
    if (textSection?.content) {
      // Extract the first paragraph (up to first newline)
      const firstParagraph = textSection.content.split('\n')[0];
      return firstParagraph || '';
    }
  } else if (typeof article?.content === 'string') {
    // Split by newline and get first paragraph
    return article.content.split('\n')[0] || '';
  }
  
  // Fallback to empty string if no description can be found
  return '';
};

const getArticleSource = (article: Article | any): string => {
  // If no source, return unknown
  if (!article?.source) return 'Unknown Source';
  
  const source = article.source;
  
  // Filter out generic feed URLs
  if (source.includes('feeds.feedburner.com') || source === 'feeds') {
    // Try to get publication info from the article
    if (article.publication) return article.publication;
    if (article.publisher) return article.publisher;
    
    // For Korean news articles, use a better generic source label
    return article.language === 'ko' ? '한국 뉴스' : 'News Source';
  }
  
  // Extract domain name from URLs
  if (source.startsWith('http')) {
    try {
      const url = new URL(source);
      // Remove common prefixes like 'www.' and extract the domain name
      return url.hostname.replace(/^www\./, '');
    } catch {
      // If URL parsing fails, use the original source
      return source;
    }
  }
  
  return source;
};

const getArticleDate = (article: Article | any): string => {
  return article?.date_published || new Date().toISOString();
};

// This function needs to be defined inside the component to access state variables
function getArticleTopicsFactory(availableTags: Tag[], nativeLanguage: string) {
  // List of tag names to filter out (case insensitive)
  const filteredOutTags = ['rss', 'ko', 'en', 'es', 'fr', 'de', 'ja', 'zh'];
  
  return (article: Article | any): string[] => {
    let result: string[] = [];
    
    // If the article has tags, use those
if (Array.isArray(article?.tag_ids) && article.tag_ids.length > 0 && availableTags.length > 0) {
      result = article.tag_ids
        .map((tagId: string) => {
          // Find the tag object that matches this ID
          const tag = availableTags.find(t => t._id === tagId);
          if (!tag) return null;
          
          // Get the display name in user's native language or fallback to English
          if (tag.translations && tag.translations[nativeLanguage]) {
            return tag.translations[nativeLanguage];
          }
          // Fallback to the canonical name
          return tag.name;
        })
        .filter(Boolean) as string[]; // Remove nulls
    }
    
    // Filter out unwanted tags
    if (result.length > 0) {
      return result.filter(
        tag => !filteredOutTags.includes(tag.toLowerCase())
      );
    }
    
    return [];
  };
};

// Function to be defined inside the component
// DO NOT define getArticleTopics here - we'll use getArticleTopicsFn inside the component

const getArticleImageUrl = (article: Article | any): string => {
  // If article already has an image_url, use it (unless it's an expired DALL-E URL)
  if (article?.image_url) {
    const imageUrl = article.image_url;
    
    // Check if it's likely a DALL-E URL (which might be expired)
    if (imageUrl.startsWith('https://oaidalleapiprodscus.blob.core.windows.net')) {
      // Skip expired DALL-E URLs and use our fallbacks instead
      console.log('Potential expired DALL-E URL detected, using fallback');
    } else {
      return imageUrl;
    }
  }

  // If article has an image section in content, use that
  if (Array.isArray(article?.content)) {
    const imageSection = article.content.find((section: any) => section.type === 'image');
    if (imageSection?.content) {
      return imageSection.content;
    }
  }

  // Use high-quality defaults based on language and topics
  // These are beautiful, topic-specific images that work well as article covers
  const language = article?.language || 'en';
  const topics = Array.isArray(article?.topics) ? article.topics : [];
  const tagIds = Array.isArray(article?.tag_ids) ? article.tag_ids : [];
  
  // Get a deterministic but seemingly random image based on article ID
  // This ensures the same article always gets the same image but different articles get different images
  const getConsistentRandomValue = (max: number, seed: string) => {
    // Simple hash function
    let hash = 0;
    for (let i = 0; i < seed.length; i++) {
      hash = ((hash << 5) - hash) + seed.charCodeAt(i);
      hash |= 0; // Convert to 32bit integer
    }
    // Get a value between 0 and max-1
    return Math.abs(hash) % max;
  };
  
  // Korean-specific high quality images for various topics
  const koreanImages = [
    'https://images.unsplash.com/photo-1534274867514-d5b47ef89ed7', // Seoul skyline
    'https://images.unsplash.com/photo-1538485399081-7c8ed8f9fbfe', // Korean street
    'https://images.unsplash.com/photo-1585023523603-be7898ba6aac', // Korean palace
    'https://images.unsplash.com/photo-1548115184-bc6544d06a58', // Korean technology
    'https://images.unsplash.com/photo-1546874177-9e664107314e', // Korean business district
    'https://images.unsplash.com/photo-1588411393236-d2524cca2710', // Korean market
    'https://images.unsplash.com/photo-1605538795375-22e881db42fd', // Korean cafe
    'https://images.unsplash.com/photo-1599624927761-8fe85504ec77'  // Korean garden
  ];
  
  // Default images for other languages
  const defaultImages = {
    en: 'https://images.unsplash.com/photo-1499951360447-b19be8fe80f5',
    es: 'https://images.unsplash.com/photo-1503152394-c571994fd383',
    fr: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34',
    de: 'https://images.unsplash.com/photo-1560969184-10fe8719e047',
    ja: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e',
    zh: 'https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b'
  };
  
  if (language === 'ko') {
    // For Korean articles, use our specially curated Korean images
    const seed = article?._id || article?.title || 'default';
    const imageIndex = getConsistentRandomValue(koreanImages.length, seed);
    return koreanImages[imageIndex];
  }
  
  // For other languages, use the default image for that language
  return defaultImages[language as keyof typeof defaultImages] || defaultImages.en;
};

const getArticleContent = (article: Article | any): string => {
  // Handle content as an array of sections (as used in the API)
  if (Array.isArray(article?.content)) {
    return article.content
      .filter((section: any) => section.type === 'text')
      .map((section: any) => section.content)
      .join('\n\n');
  }
  
  // Handle content as a simple string
  return article?.content || article?.description || '';
};

const getArticleDifficulty = (article: Article | any): string => {
  return article?.difficulty || 'intermediate';
};

const ArticleListPage: React.FC = () => {
  // State management with URL parameters
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchInitiated, setSearchInitiated] = useState(false);
  
  // Ref for article results section
  const articlesResultsRef = useRef<HTMLDivElement>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const toast = useToast();
  
  // Get user authentication context
  const { user } = useAuth();

  // Language and tag states - use user's native language from profile
  const [nativeLanguage, setNativeLanguage] = useState(() => {
    // If we have a user with a native language preference, use that
    if (user?.native_language) {
      return user.native_language;
    }
    // Otherwise fall back to URL param or default to English
    return searchParams.get('native') || 'en';
  });
  const nativeLanguageRef = useRef(nativeLanguage);
  
  // Additional state for article list page
  const [availableTags, setAvailableTags] = useState<Tag[]>([]);
  const [filteredTags, setFilteredTags] = useState<Tag[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<Tag[]>([]);
  const [selectedTagIds, setSelectedTagIds] = useState<string[]>(() => {
    const tagParam = searchParams.get('tags');
    return tagParam ? tagParam.split(',') : [];
  });
  const [tagsLoading, setTagsLoading] = useState(true);
  const [initialTagLimit, setInitialTagLimit] = useState(10);
  
  // UI color values
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const formBgColor = useColorModeValue('white', 'gray.800');
  const boxShadow = '0px 4px 10px rgba(0, 0, 0, 0.05)';
  
  // Use our custom hook to manage target language and difficulty
  const { 
    targetLanguage, 
    difficulty, 
    setTargetLanguage, 
    setDifficulty 
  } = useLanguagePreferences(
    searchParams.get('target'),
    searchParams.get('difficulty')
  );

  // Language options for dropdown
  const languageOptions = [
    { value: 'en', label: 'English' },
    { value: 'ko', label: 'Korean' },
    { value: 'fr', label: 'French' },
    { value: 'es', label: 'Spanish' },
    { value: 'de', label: 'German' },
    { value: 'ja', label: 'Japanese' },
    { value: 'zh', label: 'Chinese' },
    { value: 'ru', label: 'Russian' }
  ];
  
  // Initial helper function to extract topics from articles
  const extractArticleTopics = useCallback((article: Article | any): string[] => {
    // Default implementation
    if (Array.isArray(article?.topics)) return article.topics;
    return [];
  }, []);
  
  // Create the actual getArticleTopics function with access to state
  const [getArticleTopicsFn, setGetArticleTopicsFn] = useState<(article: Article | any) => string[]>(extractArticleTopics);
  
  // Update the getArticleTopics function when tags or language change
  useEffect(() => {
    nativeLanguageRef.current = nativeLanguage;
    const topicsFn = getArticleTopicsFactory(availableTags, nativeLanguage);
    setGetArticleTopicsFn(() => topicsFn);
  }, [availableTags, nativeLanguage]);
  
  // Safe filter function for articles
  const safeFilterArticles = useCallback((articleList: Article[], tagFilter: string[]) => {
    if (!Array.isArray(articleList)) return [];
    try {
      return articleList.filter(article => {
        if (tagFilter.length === 0) return true;
        const articleTopics = getArticleTopicsFn(article);
        return articleTopics.some(topic => tagFilter.includes(topic));
      });
    } catch (e) {
      console.error('Error filtering articles:', e);
      return [];
    }
  }, [getArticleTopicsFn]);

  // Safe filter function to ensure we have valid article data
  const memoizedSafeFilterArticles = useMemo(() => safeFilterArticles, [safeFilterArticles]);
  
  // Fetch available tags from the backend API
  const fetchTags = async () => {
    try {
      setTagsLoading(true);
      console.log(`Fetching tags for language: ${targetLanguage}`);
      
      // Connect to the backend API to get tags
      const response = await api.get(`/api/tags?language=${targetLanguage}&active=true`);
      
      if (response.data && response.data.tags && Array.isArray(response.data.tags)) {
        // Sort tags by article count (most popular first)
        const sortedTags = [...response.data.tags].sort((a, b) => 
          (b.article_count || 0) - (a.article_count || 0)
        );
        setAvailableTags(sortedTags);
        setFilteredTags(sortedTags); // Initialize filtered tags with all tags
      } else {
        // Use fallback tags
        const fallbackTags: Tag[] = [
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
          }
        ];
        setAvailableTags(fallbackTags);
        setFilteredTags(fallbackTags);
      }
    } catch (error) {
      console.error('Error fetching tags:', error);
    } finally {
      setTagsLoading(false);
    }
  };

  // Handle tag selection
  const handleTagClick = (tag: Tag) => {
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
  
  // Handle form submission
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    // Update search params - only include non-empty values
    const params: Record<string, string> = {};
    
    if (nativeLanguage) params.native = nativeLanguage;
    if (targetLanguage) params.target = targetLanguage;
    if (difficulty) params.difficulty = difficulty;
    
    if (selectedTagIds.length > 0) {
      params.tags = selectedTagIds.join(',');
    }
    
    setSearchParams(params);
  };

  // Fetch tags when the component mounts or target language changes
  useEffect(() => {
    fetchTags();
  }, [targetLanguage]);

  // Fetch articles function
  const fetchArticles = useCallback(async () => {
    // Reset state
    setLoading(true);
    setError(null);
    setArticles([]);
    
    try {
      // Get current search parameters
      const targetLang = searchParams.get('target');
      const difficultyLevel = searchParams.get('difficulty');
      const tagIdsParam = searchParams.get('tags');
      
      if (!targetLang) {
        console.log('No target language specified, skipping article fetch');
        setLoading(false);
        return;
      }
      
      console.log(`Fetching articles for language: ${targetLang}, difficulty: ${difficultyLevel}`);
      
      // Parse tag IDs from the URL parameter
      const tagIds = tagIdsParam ? tagIdsParam.split(',') : [];
      
      // Create request payload for the POST request
      const requestPayload = {
        language: targetLang,
        difficulty: difficultyLevel || undefined,
        tag_ids: tagIds.length > 0 ? tagIds : undefined
      };
      
      // Send POST request to the browse articles endpoint
      const response = await api.post('/api/articles-browse', requestPayload);
      
      if (response.data && Array.isArray(response.data.articles)) {
        setArticles(response.data.articles);
        
        // Scroll to articles section after a short delay (to allow render)
        setTimeout(() => {
          if (articlesResultsRef.current && response.data.articles.length > 0) {
            articlesResultsRef.current.scrollIntoView({ behavior: 'smooth' });
          }
        }, 300);
      } else {
        console.warn('Invalid articles response format:', response.data);
        setArticles([]);
      }
    } catch (error) {
      console.error('Error fetching articles:', error);
      setError('Failed to load articles. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, [searchParams]);
  
  // Fetch articles when search parameters change if URL has parameters
  useEffect(() => {
    // Only auto-fetch if URL has search parameters
    if (searchParams.toString()) {
      setSearchInitiated(true);
      fetchArticles();
    } else {
      // Reset loading state when no search parameters
      setLoading(false);
    }
  }, [fetchArticles, searchParams]);
  
  // Handle article click
  const handleArticleClick = useCallback((articleId: string) => {
    if (!articleId) {
      console.error('Attempted to navigate to article with invalid ID');
      return;
    }
    navigate(`/articles/${articleId}`);
  }, [navigate]);

  return (
    <Container maxW="container.xl" py={5}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading as="h1" size="xl" mb={4}>Browse Articles</Heading>
          <Text color="gray.600">Find articles in your target language based on your interests.</Text>
        </Box>

        <Box bg={formBgColor} p={6} borderRadius="md" boxShadow={boxShadow}>
          <form onSubmit={handleSubmit}>
            <VStack spacing={5} align="stretch">
              <FormControl id="targetLanguage" isRequired>
                <FormLabel fontWeight="bold">Target Language</FormLabel>
                <Select
                  value={targetLanguage}
                  onChange={(e) => {
                    const newLanguage = e.target.value;
                    setTargetLanguage(newLanguage);
                    // Reset tags when language changes
                    setSelectedTags([]);
                    setSelectedTagIds([]);
                  }}
                  placeholder="Select target language"
                >
                  {languageOptions.map(lang => (
                    <option key={lang.value} value={lang.value}>{lang.label}</option>
                  ))}
                </Select>
              </FormControl>

              <FormControl id="difficultyLevel" isRequired>
                <FormLabel fontWeight="bold">Difficulty Level</FormLabel>
                <RadioGroup 
                  value={difficulty} 
                  onChange={(newDifficulty) => {
                    setDifficulty(newDifficulty);
                  }}
                >
                  <Stack direction="row" spacing={4}>
                    <Radio value="beginner">Beginner</Radio>
                    <Radio value="intermediate">Intermediate</Radio>
                    <Radio value="advanced">Advanced</Radio>
                  </Stack>
                </RadioGroup>
              </FormControl>

              <FormControl id="tagSelection">
                <FormLabel fontWeight="bold">Select Tags</FormLabel>
                
                {/* Add search bar for tags */}
                <InputGroup mb={3}>
                  <InputLeftElement pointerEvents="none">
                    <SearchIcon color="gray.400" />
                  </InputLeftElement>
                  <Input
                    placeholder="Search for tags..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </InputGroup>

                {/* Selected Tags */}
                {selectedTags.length > 0 && (
                  <Box mb={4}>
                    <Text fontSize="sm" mb={2}>Selected Tags:</Text>
                    <Wrap>
                      {selectedTags.map(tag => (
                        <WrapItem key={tag._id}>
                          <Tag
                            size="md"
                            borderRadius="full"
                            variant="solid"
                            colorScheme="blue"
                          >
                            <TagLabel>
                              {tag.translations && tag.translations[nativeLanguage] 
                                ? tag.translations[nativeLanguage] 
                                : tag.name}
                            </TagLabel>
                            <TagCloseButton onClick={() => handleTagClick(tag)} />
                          </Tag>
                        </WrapItem>
                      ))}
                    </Wrap>
                  </Box>
                )}

                {/* Available Tags */}
                <Box maxH="150px" overflowY="auto" p={2} borderWidth="1px" borderRadius="md">
                  {tagsLoading ? (
                    <Flex justify="center" align="center" h="100px">
                      <Spinner />
                    </Flex>
                  ) : filteredTags.length > 0 ? (
                    <Wrap>
                      {filteredTags.map(tag => (
                        <WrapItem key={tag._id}>
                          <Tag
                            size="md"
                            borderRadius="full"
                            variant={selectedTagIds.includes(tag._id) ? 'solid' : 'outline'}
                            colorScheme={selectedTagIds.includes(tag._id) ? 'blue' : 'gray'}
                            cursor="pointer"
                            onClick={() => handleTagClick(tag)}
                            m={1}
                          >
                            <TagLabel>
                              {tag.translations && tag.translations[nativeLanguage] 
                                ? tag.translations[nativeLanguage] 
                                : tag.name}
                            </TagLabel>
                            {tag.article_count ? (
                              <Badge ml={1} fontSize="0.6em" colorScheme={selectedTagIds.includes(tag._id) ? 'blue' : 'gray'}>
                                {tag.article_count}
                              </Badge>
                            ) : null}
                          </Tag>
                        </WrapItem>
                      ))}
                    </Wrap>
                  ) : (
                    <Text textAlign="center" color="gray.500" py={4}>
                      No tags found for this language.
                    </Text>
                  )}
                </Box>
              </FormControl>

              <Button
                type="submit"
                colorScheme="blue"
                size="lg"
                width="100%"
                isLoading={loading}
                onClick={() => setSearchInitiated(true)}
              >
                Find Articles
              </Button>
            </VStack>
          </form>
        </Box>

        {error && (
          <Alert status="error" mb={4}>
            <AlertIcon />
            {error}
          </Alert>
        )}

        {loading ? (
          <Flex justify="center" py={10}>
            <Spinner size="xl" />
          </Flex>
        ) : articles.length > 0 ? (
          <>
            <Heading as="h2" size="lg" mt={6} mb={4} ref={articlesResultsRef}>
              {articles.length} Articles Found
            </Heading>
            
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
              {articles.map(article => (
                <Box
                  key={getArticleId(article)}
                  borderWidth="1px"
                  borderRadius="lg"
                  overflow="hidden"
                  onClick={() => handleArticleClick(getArticleId(article))}
                  cursor="pointer"
                  transition="all 0.2s"
                  _hover={{ transform: 'translateY(-4px)', boxShadow: 'lg' }}
                  h="100%"
                  bg="white"
                >
                  <Image
                    src={getArticleImageUrl(article)}
                    alt={getArticleTitle(article)}
                    objectFit="cover"
                    w="100%"
                    h="180px"
                  />
                  <Box p={5}>
                    <Text fontWeight="semibold" fontSize="lg" mb={2} noOfLines={2}>
                      {getArticleTitle(article)}
                    </Text>
                    <Text color="gray.600" mb={3} noOfLines={3}>
                      {getArticleDescription(article)}
                    </Text>
                    <Flex justify="space-between" align="center">
                      <Text fontSize="sm" color="gray.500">
                        {getArticleSource(article)}
                      </Text>
                      <Text fontSize="sm" color="gray.500">
                        {new Date(getArticleDate(article)).toLocaleDateString()}
                      </Text>
                    </Flex>
                    {/* Display article tags but filter out unwanted ones */}
                    {getArticleTopicsFn(article).length > 0 && (
                      <HStack mt={3} spacing={2} flexWrap="wrap">
                        {getArticleTopicsFn(article).slice(0, 3).map((topic: string, i: number) => (
                          <Badge key={`${topic}-${i}`} colorScheme="blue" fontSize="xs">
                            {topic}
                          </Badge>
                        ))}
                      </HStack>
                    )}
                  </Box>
                </Box>
              ))}
            </SimpleGrid>
          </>
        ) : !loading && !error && searchInitiated ? (
          <Box textAlign="center" py={10}>
            <Heading as="h2" size="lg" mb={4}>No Articles Found</Heading>
            <Text>Try adjusting your search criteria or selecting different tags.</Text>
          </Box>
        ) : null}
      </VStack>
    </Container>
  );
};

export default ArticleListPage;
