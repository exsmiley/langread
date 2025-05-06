import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  SimpleGrid,
  VStack,
  HStack,
  Input,
  InputGroup,
  InputLeftElement,
  Badge,
  Divider,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Tag,
  TagLabel,
  TagCloseButton,
  Select,
  useColorModeValue,
  Spinner,
  Flex,
  Icon,
  Tooltip,
  useToast
} from '@chakra-ui/react';
import { SearchIcon, StarIcon, AddIcon } from '@chakra-ui/icons';
import { FaLanguage, FaBook, FaRegStar, FaStar } from 'react-icons/fa';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';

// Mock vocabulary data
const MOCK_VOCABULARY = [
  {
    id: 'word1',
    word: '인공지능',
    language: 'ko',
    part_of_speech: 'noun',
    translations: { 'en': 'Artificial Intelligence' },
    definition: 'The theory and development of computer systems able to perform tasks that normally require human intelligence.',
    examples: ['인공지능 기술이 발전하고 있다', '인공지능을 활용한 서비스'],
    article_references: ['article1'],
    tags: ['technology', 'computing', 'advanced'],
    created_at: '2025-04-20T10:30:00Z',
    mastery_level: 0.2
  },
  {
    id: 'word2',
    word: '발전',
    language: 'ko',
    part_of_speech: 'noun',
    translations: { 'en': 'Development / Progress' },
    definition: 'Growth or improvement over time.',
    examples: ['경제 발전', '기술 발전'],
    article_references: ['article1', 'article3'],
    tags: ['general', 'intermediate'],
    created_at: '2025-04-20T10:35:00Z',
    mastery_level: 0.5
  },
  {
    id: 'word3',
    word: '음식',
    language: 'ko',
    part_of_speech: 'noun',
    translations: { 'en': 'Food' },
    definition: 'Any nutritious substance that people or animals eat or drink to maintain life and growth.',
    examples: ['한국 음식은 맛있다', '건강한 음식을 먹어야 한다'],
    article_references: ['article2'],
    tags: ['food', 'daily-life', 'beginner'],
    created_at: '2025-04-21T09:15:00Z',
    mastery_level: 0.8
  },
  {
    id: 'word4',
    word: '여행',
    language: 'ko',
    part_of_speech: 'noun',
    translations: { 'en': 'Travel / Trip' },
    definition: 'The act of going from one place to another, especially over a long distance.',
    examples: ['여행을 좋아해요', '해외 여행'],
    article_references: ['article3'],
    tags: ['travel', 'leisure', 'intermediate'],
    created_at: '2025-04-22T14:20:00Z',
    mastery_level: 0.3
  },
  {
    id: 'word5',
    word: '영화',
    language: 'ko',
    part_of_speech: 'noun',
    translations: { 'en': 'Movie / Film' },
    definition: 'A series of moving pictures recorded with sound that tells a story.',
    examples: ['영화를 보다', '한국 영화'],
    article_references: ['article4'],
    tags: ['entertainment', 'leisure', 'beginner'],
    created_at: '2025-04-22T16:45:00Z',
    mastery_level: 0.6
  }
];

// Mock flashcard data
const MOCK_FLASHCARDS = [
  {
    id: 'card1',
    front: '인공지능',
    back: 'Artificial Intelligence',
    example: '인공지능 기술이 발전하고 있다',
    tags: ['technology', 'computing', 'advanced', 'article1'],
    language: 'ko',
    created_at: '2025-04-20T10:30:00Z',
    last_reviewed: '2025-04-22T15:30:00Z',
    interval: 2,
    ease_factor: 2.5,
    times_reviewed: 3
  },
  {
    id: 'card2',
    front: '발전',
    back: 'Development / Progress',
    example: '경제 발전',
    tags: ['general', 'intermediate', 'article1', 'article3'],
    language: 'ko',
    created_at: '2025-04-20T10:35:00Z',
    last_reviewed: '2025-04-23T09:15:00Z',
    interval: 1,
    ease_factor: 2.2,
    times_reviewed: 2
  },
  {
    id: 'card3',
    front: '음식',
    back: 'Food',
    example: '한국 음식은 맛있다',
    tags: ['food', 'daily-life', 'beginner', 'article2'],
    language: 'ko',
    created_at: '2025-04-21T09:15:00Z',
    last_reviewed: null,
    interval: 0,
    ease_factor: 2.5,
    times_reviewed: 0
  }
];

interface VocabularyItem {
  id: string;
  word: string;
  language: string;
  part_of_speech: string;
  translations: { [key: string]: string };
  definition: string;
  examples: string[];
  article_references: string[];
  tags: string[];
  created_at: string;
  mastery_level: number;
}

interface Flashcard {
  id: string;
  front: string;
  back: string;
  example: string;
  tags: string[];
  language: string;
  created_at: string;
  last_reviewed: string | null;
  interval: number;
  ease_factor: number;
  times_reviewed: number;
}

interface ArticleReference {
  id: string;
  title: string;
}

// Mock article references
const MOCK_ARTICLE_REFERENCES: { [key: string]: ArticleReference } = {
  'article1': { id: '1', title: '인공지능의 발전과 미래' },
  'article2': { id: '2', title: '한국 요리의 세계화: 비빔밥부터 김치까지' },
  'article3': { id: '3', title: '2025년 봄 여행지 추천: 국내 명소 10곳' },
  'article4': { id: '4', title: '최신 영화 리뷰: 올해의 기대작' },
};

const VocabularyPage = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  
  const [vocabulary, setVocabulary] = useState<VocabularyItem[]>([]);
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<string>('');
  const [selectedLanguage, setSelectedLanguage] = useState<string>(user?.learning_language || 'all');
  
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBgColor = useColorModeValue('gray.50', 'gray.700');
  
  useEffect(() => {
    const fetchVocabularyAndFlashcards = async () => {
      setIsLoading(true);
      
      try {
        // In a real app, we would fetch from the API
        // const vocabResponse = await axios.get('/api/vocabulary');
        // const flashcardResponse = await axios.get('/api/flashcards');
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Use mock data for now
        setVocabulary(MOCK_VOCABULARY);
        setFlashcards(MOCK_FLASHCARDS);
      } catch (err) {
        console.error('Error fetching data:', err);
        toast({
          title: 'Error',
          description: 'Failed to load vocabulary data.',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchVocabularyAndFlashcards();
  }, [toast]);
  
  const handleTagSelect = (tag: string) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };
  
  const handleCreateFlashcard = (word: VocabularyItem) => {
    const newFlashcard: Flashcard = {
      id: `card${flashcards.length + 1}`,
      front: word.word,
      back: word.translations['en'] || 'No translation',
      example: word.examples[0] || '',
      tags: [...word.tags, ...word.article_references],
      language: word.language,
      created_at: new Date().toISOString(),
      last_reviewed: null,
      interval: 0,
      ease_factor: 2.5,
      times_reviewed: 0
    };
    
    setFlashcards([...flashcards, newFlashcard]);
    
    toast({
      title: 'Flashcard created',
      description: `Flashcard for '${word.word}' has been created.`,
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };
  
  const formatDate = (dateString: string) => {
    if (!dateString) return 'Never';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };
  
  const filteredVocabulary = vocabulary.filter(word => {
    const matchesSearch = searchTerm === '' || 
      word.word.toLowerCase().includes(searchTerm.toLowerCase()) ||
      word.translations['en']?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesTags = selectedTags.length === 0 || 
      selectedTags.every(tag => word.tags.includes(tag) || word.article_references.includes(tag));
    
    const matchesArticle = selectedArticle === '' || 
      word.article_references.includes(selectedArticle);
    
    const matchesLanguage = selectedLanguage === 'all' || 
      word.language === selectedLanguage;
    
    return matchesSearch && matchesTags && matchesArticle && matchesLanguage;
  });
  
  const filteredFlashcards = flashcards.filter(card => {
    const matchesSearch = searchTerm === '' || 
      card.front.toLowerCase().includes(searchTerm.toLowerCase()) ||
      card.back.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesTags = selectedTags.length === 0 || 
      selectedTags.every(tag => card.tags.includes(tag));
    
    const matchesArticle = selectedArticle === '' || 
      card.tags.includes(selectedArticle);
    
    const matchesLanguage = selectedLanguage === 'all' || 
      card.language === selectedLanguage;
    
    return matchesSearch && matchesTags && matchesArticle && matchesLanguage;
  });
  
  // Get unique tags from vocabulary
  const allTags = vocabulary.reduce((tags, word) => {
    word.tags.forEach(tag => {
      if (!tags.includes(tag)) {
        tags.push(tag);
      }
    });
    return tags;
  }, [] as string[]);
  
  // Get unique article references
  const articleReferences = vocabulary.reduce((refs, word) => {
    word.article_references.forEach(ref => {
      if (!refs.includes(ref)) {
        refs.push(ref);
      }
    });
    return refs;
  }, [] as string[]);
  
  const renderMasteryLevel = (level: number) => {
    const fullStars = Math.floor(level * 5);
    const emptyStars = 5 - fullStars;
    
    return (
      <HStack spacing={1}>
        {[...Array(fullStars)].map((_, i) => (
          <Icon key={`full-${i}`} as={FaStar} color="yellow.400" />
        ))}
        {[...Array(emptyStars)].map((_, i) => (
          <Icon key={`empty-${i}`} as={FaRegStar} color="gray.300" />
        ))}
      </HStack>
    );
  };
  
  if (isLoading) {
    return (
      <Container maxW="container.xl" centerContent py={10}>
        <Spinner size="xl" thickness="4px" color="blue.500" />
        <Text mt={4}>{t('vocabulary.loading')}</Text>
      </Container>
    );
  }
  
  return (
    <Container maxW="container.xl" py={6}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading as="h1" size="xl">
            {t('vocabulary.title')}
          </Heading>
          <Text mt={2} color="gray.600">
            {t('vocabulary.description')}
          </Text>
        </Box>
        
        <Box 
          bg={bgColor}
          borderRadius="md"
          borderWidth="1px"
          borderColor={borderColor}
          p={6}
        >
          <VStack spacing={4} align="stretch">
            <HStack spacing={4}>
              <InputGroup size="md" flex={1}>
                <InputLeftElement pointerEvents="none">
                  <SearchIcon color="gray.400" />
                </InputLeftElement>
                <Input 
                  placeholder={t('vocabulary.searchPlaceholder')} 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </InputGroup>
              
              <Select 
                width="200px" 
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
              >
                <option value="all">{t('vocabulary.allLanguages')}</option>
                <option value="ko">{t('settings.languages.korean')} (한국어)</option>
                <option value="ja">{t('settings.languages.japanese')} (日本語)</option>
                <option value="zh">{t('settings.languages.chinese')} (中文)</option>
                <option value="es">{t('settings.languages.spanish')} (Español)</option>
              </Select>
            </HStack>
            
            <Box>
              <Text fontWeight="medium" mb={2}>{t('vocabulary.filterByTags')}</Text>
              <Flex flexWrap="wrap" gap={2}>
                {allTags.map(tag => (
                  <Tag 
                    key={tag}
                    size="md"
                    variant={selectedTags.includes(tag) ? "solid" : "subtle"}
                    colorScheme="blue"
                    cursor="pointer"
                    onClick={() => handleTagSelect(tag)}
                  >
                    <TagLabel>{tag}</TagLabel>
                  </Tag>
                ))}
              </Flex>
            </Box>
            
            <Box>
              <Text fontWeight="medium" mb={2}>{t('vocabulary.filterByArticle')}</Text>
              <Select 
                placeholder={t('vocabulary.allArticles')} 
                value={selectedArticle}
                onChange={(e) => setSelectedArticle(e.target.value)}
              >
                <option value="">{t('vocabulary.allArticles')}</option>
                {articleReferences.map(ref => (
                  <option key={ref} value={ref}>
                    {MOCK_ARTICLE_REFERENCES[ref]?.title || ref}
                  </option>
                ))}
              </Select>
            </Box>
          </VStack>
        </Box>
        
        <Tabs colorScheme="blue" variant="enclosed">
          <TabList>
            <Tab>Vocabulary ({filteredVocabulary.length})</Tab>
            <Tab>Flashcards ({filteredFlashcards.length})</Tab>
          </TabList>
          
          <TabPanels>
            <TabPanel px={0}>
              {filteredVocabulary.length === 0 ? (
                <Box 
                  p={8} 
                  textAlign="center" 
                  borderRadius="md" 
                  borderWidth="1px"
                  borderStyle="dashed"
                  borderColor={borderColor}
                >
                  <Text fontSize="lg" color="gray.500">
                    {t('vocabulary.noItemsFound')}
                  </Text>
                  <Button 
                    mt={4} 
                    colorScheme="blue" 
                    variant="outline"
                    onClick={() => {
                      setSearchTerm('');
                      setSelectedTags([]);
                      setSelectedArticle('');
                      setSelectedLanguage('all');
                    }}
                  >
                    {t('vocabulary.clearFilters')}
                  </Button>
                </Box>
              ) : (
                <VStack spacing={4} align="stretch">
                  {filteredVocabulary.map(word => (
                    <Box 
                      key={word.id}
                      borderWidth="1px"
                      borderRadius="md"
                      borderColor={borderColor}
                      p={4}
                      _hover={{ bg: hoverBgColor }}
                      transition="background 0.2s"
                    >
                      <Flex justify="space-between" align="start">
                        <VStack align="start" spacing={1}>
                          <HStack>
                            <Heading as="h3" size="md">
                              {word.word}
                            </Heading>
                            <Badge colorScheme="blue">{word.part_of_speech}</Badge>
                          </HStack>
                          
                          <Text fontSize="lg" fontWeight="bold" color="blue.500">
                            {word.translations['en']}
                          </Text>
                          
                          <Text fontSize="sm" color="gray.600" fontStyle="italic">
                            {word.definition}
                          </Text>
                          
                          {word.examples.length > 0 && (
                            <Box mt={2}>
                              <Text fontSize="xs" fontWeight="bold" color="gray.500">
                                EXAMPLE
                              </Text>
                              <Text fontSize="sm">{word.examples[0]}</Text>
                            </Box>
                          )}
                          
                          <HStack mt={2} spacing={2} flexWrap="wrap">
                            {word.tags.map(tag => (
                              <Tag key={tag} size="sm" colorScheme="gray">
                                {tag}
                              </Tag>
                            ))}
                            {word.article_references.map(ref => (
                              <Tag key={ref} size="sm" colorScheme="purple">
                                {MOCK_ARTICLE_REFERENCES[ref]?.title.substring(0, 15) + '...' || ref}
                              </Tag>
                            ))}
                          </HStack>
                        </VStack>
                        
                        <VStack align="end" spacing={2}>
                          {renderMasteryLevel(word.mastery_level)}
                          
                          <Tooltip label={t('vocabulary.createFlashcard')}>
                            <Button 
                              size="sm" 
                              colorScheme="blue" 
                              leftIcon={<AddIcon />}
                              onClick={() => handleCreateFlashcard(word)}
                              isDisabled={flashcards.some(card => card.front === word.word)}
                            >
                              Flashcard
                            </Button>
                          </Tooltip>
                        </VStack>
                      </Flex>
                    </Box>
                  ))}
                </VStack>
              )}
            </TabPanel>
            
            <TabPanel px={0}>
              {filteredFlashcards.length === 0 ? (
                <Box 
                  p={8} 
                  textAlign="center" 
                  borderRadius="md" 
                  borderWidth="1px"
                  borderStyle="dashed"
                  borderColor={borderColor}
                >
                  <Text fontSize="lg" color="gray.500">
                    {t('vocabulary.noFlashcardsFound')}
                  </Text>
                  <Button 
                    mt={4} 
                    colorScheme="blue" 
                    variant="outline"
                    onClick={() => {
                      setSearchTerm('');
                      setSelectedTags([]);
                      setSelectedArticle('');
                      setSelectedLanguage('all');
                    }}
                  >
                    {t('vocabulary.clearFilters')}
                  </Button>
                </Box>
              ) : (
                <VStack spacing={4} align="stretch">
                  <Flex justify="flex-end">
                    <Button 
                      colorScheme="blue" 
                      size="lg"
                      isDisabled={filteredFlashcards.length === 0}
                      onClick={() => {
                        toast({
                          title: t('vocabulary.studySessionStarted'),
                          description: t('vocabulary.flashcardStudyComingSoon'),
                          status: 'info',
                          duration: 3000,
                          isClosable: true,
                        });
                      }}
                    >
                      {t('vocabulary.studyFlashcards')}
                    </Button>
                  </Flex>
                  
                  <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                    {filteredFlashcards.map(card => (
                      <Box 
                        key={card.id}
                        borderWidth="1px"
                        borderRadius="md"
                        borderColor={borderColor}
                        p={4}
                        height="250px"
                        position="relative"
                        bg={bgColor}
                        _hover={{ 
                          transform: 'translateY(-4px)',
                          shadow: 'md',
                          zIndex: 1,
                        }}
                        transition="all 0.3s ease"
                      >
                        <VStack spacing={4} height="100%">
                          <Heading as="h3" size="md" textAlign="center">
                            {card.front}
                          </Heading>
                          
                          <Divider />
                          
                          <Text fontSize="lg" fontWeight="bold" color="blue.500" textAlign="center">
                            {card.back}
                          </Text>
                          
                          {card.example && (
                            <Text fontSize="sm" fontStyle="italic" textAlign="center">
                              "{card.example}"
                            </Text>
                          )}
                          
                          <Flex mt="auto" w="100%" justifyContent="space-between" alignItems="center">
                            <Text fontSize="xs" color="gray.500">
                              {t('vocabulary.lastReviewed')}: {formatDate(card.last_reviewed || '')}
                            </Text>
                            
                            <HStack>
                              <Badge colorScheme={card.times_reviewed > 0 ? "green" : "gray"}>
                                {card.times_reviewed} {t('vocabulary.reviews')}
                              </Badge>
                            </HStack>
                          </Flex>
                        </VStack>
                      </Box>
                    ))}
                  </SimpleGrid>
                </VStack>
              )}
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>
    </Container>
  );
};

export default VocabularyPage;
