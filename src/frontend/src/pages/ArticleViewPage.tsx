import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Container, 
  Heading, 
  Text, 
  Image, 
  Spinner, 
  VStack, 
  HStack, 
  Badge, 
  Divider, 
  Button,
  useToast,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Popover,
  PopoverContent,
  PopoverArrow,
  PopoverBody,
  useDisclosure,
  Select,
  Flex,
  Checkbox
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '../api';
import axios from 'axios';
import { useLanguagePreferences, LANGUAGE_OPTIONS } from '../contexts/LanguageContext';

// Backend API configuration
const API_BASE_URL = 'http://localhost:8000'; // This would be configured differently in production

// Interfaces to match the API response structure
interface Section {
  type: string;
  content: string;
  order: number;
  caption?: string;
}

interface Translation {
  word: string;
  translation: string;
  part_of_speech: string;
  definition?: string;
  examples?: string[];
  context?: string; // The surrounding context where the word appears
}

interface Article {
  _id: string;
  title: string;
  description?: string;
  source: string;
  date_published?: string | null;
  date_created: string;
  language: string;
  author?: string;
  tag_ids?: string[];
  sections?: Section[];
  content?: Section[]; // Keeping for backward compatibility with mock data
  text?: string;
  summary?: string;
  difficulty?: string;
  url?: string;
  image_url?: string;
  grouped?: boolean;
  group_id?: string;
}

// Mock article data for development fallback
const MOCK_ARTICLE: Article = {
  _id: 'mock-article-1',
  title: '인공지능의 발전과 미래',
  description: '최근 인공지능 기술의 발전과 그 영향에 대한 분석',
  source: 'Tech Korea',
  date_published: '2025-04-22T10:30:00Z',
  date_created: '2025-04-22T10:30:00Z',
  language: 'ko',
  tag_ids: ['기술', '인공지능', 'AI'],
  sections: [
    {
      type: 'heading',
      content: '인공지능 기술의 현재와 미래',
      order: 0
    },
    {
      type: 'text',
      content: '인공지능 기술은 최근 몇 년간 급속도로 발전하고 있습니다. 특히 딥러닝과 자연어 처리 분야에서 눈부신 성과를 이루었으며, 이는 다양한 산업 분야에 큰 변화를 가져오고 있습니다.',
      order: 1
    },
    {
      type: 'text',
      content: '한국은 AI 기술 개발에 있어 세계적으로 중요한 위치를 차지하고 있으며, 정부와 기업들은 AI 인재 양성과 연구 개발에 많은 투자를 하고 있습니다.',
      order: 2
    },
    {
      type: 'image',
      content: 'https://images.unsplash.com/photo-1677442135132-141665fed0c1',
      order: 3
    },
    {
      type: 'heading',
      content: 'AI가 가져올 사회적 변화',
      order: 4
    },
    {
      type: 'text',
      content: 'AI 기술의 발전은 일자리 시장과 교육 시스템에도 큰 영향을 미칠 것으로 예상됩니다. 많은 전문가들은 반복적인 작업이 자동화되면서 새로운 형태의 직업이 등장할 것이라고 전망합니다.',
      order: 5
    }
  ],
  difficulty: 'intermediate'
};

// Mock translations for offline/fallback use
const MOCK_TRANSLATIONS: Record<string, Translation> = {
  '인공지능': {
    word: '인공지능',
    translation: 'Artificial Intelligence',
    part_of_speech: 'noun',
    definition: 'Intelligence demonstrated by machines, in contrast to natural intelligence displayed by humans.',
    examples: ['인공지능 기술이 발전하고 있다.', '그는 인공지능 연구자이다.'],
    context: 'AI technology is advancing rapidly'
  },
  '기술': {
    word: '기술',
    translation: 'Technology',
    part_of_speech: 'noun',
    definition: 'The application of scientific knowledge for practical purposes.',
    examples: ['새로운 기술이 개발되었다.', '기술의 발전은 사회를 변화시킨다.'],
    context: 'New technology was developed'
  },
  '개발': {
    word: '개발',
    translation: 'Development',
    part_of_speech: 'noun',
    definition: 'The process of developing or being developed.',
    examples: ['소프트웨어 개발에 많은 시간이 걸린다.', '그 지역의 개발이 진행 중이다.'],
    context: 'Software development takes a lot of time'
  },
  '센터': {
    word: '센터',
    translation: 'Center',
    part_of_speech: 'noun',
    definition: 'A place or building used for a specified purpose or activity.',
    examples: ['이 센터는 다양한 활동을 제공합니다.', '학습 센터에서 공부합니다.'],
    context: 'This center provides various activities'
  },
  '혁신': {
    word: '혁신',
    translation: 'Innovation',
    part_of_speech: 'noun',
    definition: 'A new method, idea, product, etc. that represents a significant change or development.',
    examples: ['우리 회사는 혁신을 중요시합니다.', '그의 혁신적인 아이디어가 성공으로 이어졌다.'],
    context: 'Our company values innovation'
  },
  '참가': {
    word: '참가',
    translation: 'Participation',
    part_of_speech: 'noun',
    definition: 'The action of taking part in something.',
    examples: ['대회 참가를 위해 등록했습니다.', '많은 사람들이 행사에 참가했다.'],
    context: 'I registered for participation in the competition'
  },
  '모집': {
    word: '모집',
    translation: 'Recruitment',
    part_of_speech: 'noun',
    definition: 'The action of enlisting or enrolling people for a position, task or program.',
    examples: ['신입 사원 모집 공고가 나왔다.', '학생들을 모집하고 있습니다.'],
    context: 'The job opening for new employees has been posted'
  },
  '경기': {
    word: '경기',
    translation: 'Gyeonggi',
    part_of_speech: 'noun',
    definition: 'A province in South Korea surrounding Seoul.',
    examples: ['경기도에 살고 있어요.', '경기도 지역의 발전 계획이 발표되었다.'],
    context: 'I live in Gyeonggi Province'
  },
  '경기창조경제혁신센터': {
    word: '경기창조경제혁신센터',
    translation: 'Gyeonggi Center for Creative Economy and Innovation',
    part_of_speech: 'noun',
    definition: 'An institution in Gyeonggi Province, South Korea, that supports startup growth and innovation.',
    examples: ['경기창조경제혁신센터에서 창업 지원 프로그램을 운영합니다.'],
    context: 'The center provides various programs for startups'
  },
  '유니콘': {
    word: '유니콘',
    translation: 'Unicorn',
    part_of_speech: 'noun',
    definition: 'In business, a startup company valued at over $1 billion.',
    examples: ['그 스타트업은 유니콘 기업이 되었다.'],
    context: 'That startup became a unicorn company'
  },
  '국민은행': {
    word: '국민은행',
    translation: 'Kookmin Bank',
    part_of_speech: 'noun',
    definition: 'One of the largest banks in South Korea.',
    examples: ['국민은행에서 계좌를 개설했습니다.'],
    context: 'I opened an account at Kookmin Bank'
  },
  '스타트업': {
    word: '스타트업',
    translation: 'Startup',
    part_of_speech: 'noun',
    definition: 'A newly established business, especially one that is in a phase of development.',
    examples: ['많은,스타트업이 투자를 유치하고 있다.'],
    context: 'Many startups are attracting investment'
  }
};



// Interface for Tag structure
interface Tag {
  _id: string;
  name: string;
  description?: string;
  language: string;
  count?: number;
}



const ArticleViewPage = () => {
  const { articleId } = useParams<{ articleId: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedText, setSelectedText] = useState('');
  const [translation, setTranslation] = useState<Translation | null>(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [popupPosition, setPopupPosition] = useState({ top: 0, left: 0 });
  const [tags, setTags] = useState<{[key: string]: Tag}>({});
  
  // Use the centralized language context
  const { 
    targetLanguage, 
    setTargetLanguage, 
    useNativeLanguage, 
    setUseNativeLanguage,
    getValidLanguageOptions 
  } = useLanguagePreferences();
  
  const navigate = useNavigate();
  const toast = useToast();
  const popoverProps = useDisclosure();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  useEffect(() => {
    const fetchArticle = async () => {
      setIsLoading(true);
      setError(null);
      
    // Don't fetch all tags on load as we'll use the lookup endpoint
    // only when we have an article with tag IDs
      
      try {
        if (!articleId) {
          setError('Article ID is missing');
          setIsLoading(false);
          return;
        }
        
        console.log(`Fetching article with ID: ${articleId}`);
        const response = await api.get(`/api/articles/${articleId}`);
        
        if (response.data) {
          console.log('Article data received:', response.data);
          setArticle(response.data);
        } else {
          setError('No article data received');
          // Fallback to mock data in development
          if (process.env.NODE_ENV !== 'production') {
            setArticle(MOCK_ARTICLE);
            toast({
              title: 'Using sample article',
              description: 'Could not load the real article. Using sample content.',
              status: 'warning',
              duration: 5000,
              isClosable: true,
            });
          }
        }
      } catch (err: any) {
        console.error('Error fetching article:', err);
        setError(err.response?.data?.detail || 'Failed to load article');
        
        // Fallback to mock data in development
        if (process.env.NODE_ENV !== 'production') {
          setArticle(MOCK_ARTICLE);
          toast({
            title: 'Using sample article',
            description: 'Could not load the real article. Using sample content.',
            status: 'warning',
            duration: 5000,
            isClosable: true,
          });
        }
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchArticle();
  }, [articleId, toast]);
  
  // Fetch tags whenever article changes and has tag IDs
  useEffect(() => {
    if (!article || !article.tag_ids || article.tag_ids.length === 0) return;
    
    const lookupTags = async () => {
      try {
        // Use the new lookup endpoint to get tag info for specific IDs
        const response = await axios.post('http://localhost:8000/tags/lookup', {
          tag_ids: article.tag_ids
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (response.data && response.data.tags) {
          // Convert array to lookup object
          const tagsObject = response.data.tags.reduce((acc: {[key: string]: Tag}, tag: any) => {
            if (!tag.missing) {
              acc[tag._id] = tag;
            }
            return acc;
          }, {});
          
          setTags(tagsObject);
          console.log('Tags looked up successfully:', Object.keys(tagsObject).length);
        }
      } catch (error) {
        console.error('Error looking up tags:', error);
        // Don't set any fallback tags - we'll hide them if lookup fails
        setTags({});
      }
    };
    
    lookupTags();
  }, [article]);
  
  // Get the surrounding sentence for a text node
  const getSurroundingSentence = (node: Node, offset: number): string => {
    if (node.nodeType !== Node.TEXT_NODE) return '';
    
    const textContent = node.textContent || '';
    const sentenceRegex = /([^.!?]+[.!?]+)/g;
    const sentences = textContent.match(sentenceRegex) || [textContent];
    
    // Find which sentence contains our selection
    let currentPos = 0;
    for (const sentence of sentences) {
      if (currentPos <= offset && offset < currentPos + sentence.length) {
        return sentence.trim();
      }
      currentPos += sentence.length;
    }
    
    // Fallback to the paragraph or a portion of the text
    return textContent.length > 200 ? 
      textContent.substring(Math.max(0, offset - 100), Math.min(textContent.length, offset + 100)) : 
      textContent;
  };
  
  // Handle text selection for translation
  const handleTextSelection = () => {
    console.log('Text selection event triggered');
    const selection = window.getSelection();
    const selectedText = selection?.toString().trim();
    console.log('Selected text:', selectedText);
    
    if (selectedText && selectedText.length > 0) {
      console.log('Valid text selection detected');
      // Get position of selection for popup placement
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        
        // Position popup above selected text
        const position = {
          top: rect.top + window.scrollY - 10, // 10px above selection
          left: rect.left + window.scrollX + (rect.width / 2) // Center of selection
        };
        console.log('Setting popup position:', position);
        setPopupPosition(position);
        
        // Get the surrounding sentence for context
        let context = '';
        if (range.startContainer) {
          context = getSurroundingSentence(range.startContainer, range.startOffset);
          console.log('Found context:', context);
        }
        
        // Set the selected text first
        setSelectedText(selectedText);
        
        // Then translate it with context
        translateText(selectedText, context);
      } else {
        // Fallback if we can't get range info
        setSelectedText(selectedText);
        translateText(selectedText, '');
      }
      
      // Show translation popup
      console.log('Opening popup');
      popoverProps.onOpen();
    } else {
      // Close popup when nothing is selected
      console.log('No valid selection, closing popup');
      popoverProps.onClose();
    }
  };
  
  // Translate text using API or fallback to mock data
  const translateText = async (text: string, context: string = '') => {
    console.log('Translating text:', text, 'with context:', context);
    // Don't translate if it's the same as the current selection and translation exists
    if (text === selectedText && translation) {
      console.log('Text already translated, reusing existing translation');
      return;
    }
    
    // Set loading state
    setIsTranslating(true);
    
    try {
      // Fetch translation from the backend vocabulary translation endpoint
      try {
        console.log(`Using target language: ${targetLanguage}`);
        
        // Call the specialized context-aware vocabulary translation endpoint
        try {
          // If useNativeLanguage is true, definitions will be in the article's language
          // Otherwise, use the selected target language
          const effectiveTargetLang = useNativeLanguage ? (article?.language || 'ko') : targetLanguage;
          
          // For the definition language (language terms are explained in), always use the selected language
          // This ensures Korean definitions when Korean is selected, regardless of article language
          const definitionLang = targetLanguage;
          console.log('Using effective target language:', effectiveTargetLang, 
                    '(Native mode:', useNativeLanguage, ', Selected:', targetLanguage, ')');
            
          const response = await axios.post(`${API_BASE_URL}/api/vocabulary/context-aware-translate`, {
            text,
            context,
            source_lang: article?.language || 'ko',
            target_lang: effectiveTargetLang,
            definition_lang: definitionLang  // Always use the explicitly selected language for definitions
          });
          
          if (response.data && response.status === 200) {
            console.log('Translation received from vocabulary API:', response.data);
            setTranslation(response.data);
            return;
          }
        } catch (apiErr) {
          console.warn('Vocabulary translation API error:', apiErr);
          
          // Try the regular translation API as fallback
          try {
            const fallbackResponse = await axios.post(`${API_BASE_URL}/api/translate`, {
              text,
              source_lang: article?.language || 'ko',
              target_lang: useNativeLanguage ? (article?.language || 'ko') : targetLanguage
            }, {
              params: { 
                text, 
                source_lang: article?.language || 'ko', 
                target_lang: useNativeLanguage ? (article?.language || 'ko') : targetLanguage,
                definition_lang: targetLanguage  // Always use selected language for definitions
              }
            });
            
            if (fallbackResponse.data) {
              // Convert general translation response to our Translation format
              const simpleTranslation: Translation = {
                word: text,
                translation: fallbackResponse.data.translated_text,
                part_of_speech: 'unknown',
                definition: 'Simple translation without detailed information',
                examples: []
              };
              
              setTranslation(simpleTranslation);
              return;
            }
          } catch (fallbackErr) {
            console.warn('All translation APIs failed, using mock data');
          }
        }
      } catch (apiErr) {
        console.warn('Error fetching translation from all APIs, using fallback:', apiErr);
      }
      
      // Check if we have this in the mock translations
      if (MOCK_TRANSLATIONS[text]) {
        const mockTranslation = MOCK_TRANSLATIONS[text];
        // Add context if it wasn't there
        if (!mockTranslation.context && context) {
          mockTranslation.context = context;
        }
        setTranslation(mockTranslation);
        return;
      }
      
      // For Korean text, create a simulated LLM-style response
      const hasKoreanChars = /[\u3131-\u314e\u314f-\u3163\uac00-\ud7a3]/.test(text);
      
      // Create a more sophisticated fallback that simulates LLM analysis
      if (hasKoreanChars) {
        // Simulate an LLM analyzing unknown Korean words
        const simulatedLLMTranslation = simulateKoreanLLMTranslation(text, context, targetLanguage);
        setTranslation(simulatedLLMTranslation);
      } else {
        setTranslation({
          word: text,
          translation: `Translation not available`,
          part_of_speech: 'unknown',
          definition: 'We couldn\'t find a definition for this term.',
          examples: [],
          context: context
        });
      }
      
      console.log(`Using fallback translation for: ${text}`);
    } catch (err) {
      console.error('Error translating text:', err);
      toast({
        title: 'Translation error',
        description: 'Failed to translate the selected text.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsTranslating(false);
    }
  };
  
  // Helper function to simulate LLM Korean translation for unknown words
  const simulateKoreanLLMTranslation = (text: string, context: string, targetLanguage: string): Translation => {
    // First, try to normalize the word to its base form
    const normalizedText = normalizeKoreanWord(text);
    
    // Determine the part of speech
    let partOfSpeech = determinePartOfSpeech(normalizedText);
    
    // Generate a translation based on common Korean words and patterns
    const { translationText, meaningDefinition } = generateBasicTranslation(normalizedText);
    
    // Create an example sentence
    const example = createExampleSentence(normalizedText, partOfSpeech);
    
    return {
      word: text, // Keep the original selected text
      translation: translationText,
      part_of_speech: partOfSpeech,
      definition: meaningDefinition,
      examples: [example],
      context: context // Store context but don't display it
    };
  };
  
  // Helper function to normalize Korean words by removing conjugations
  const normalizeKoreanWord = (word: string): string => {
    // Common Korean verb endings to remove
    const verbEndings = ['합니다', '했습니다', '하세요', '합니까', '하는', '했던', '했다', '한다', '하고', '하면', '해요', '해서'];
    const adjEndings = ['합니다', '했습니다', '하세요', '합니까', '하는', '했던', '했다', '한다', '하고', '하면', '해요', '해서'];
    
    // Try to strip common conjugation patterns
    let normalized = word;
    
    // Check for verb pattern 하다 (to do)
    for (const ending of verbEndings) {
      if (word.endsWith(ending)) {
        // Remove ending and add 하다 as the standard form
        normalized = word.slice(0, word.length - ending.length) + '하다';
        return normalized;
      }
    }
    
    // Check for other common word endings
    if (word.endsWith('을')) normalized = word.slice(0, -1);
    if (word.endsWith('를')) normalized = word.slice(0, -1);
    if (word.endsWith('은')) normalized = word.slice(0, -1);
    if (word.endsWith('는')) normalized = word.slice(0, -1);
    if (word.endsWith('이')) normalized = word.slice(0, -1);
    if (word.endsWith('가')) normalized = word.slice(0, -1);
    
    return normalized;
  };
  
  // Helper function to determine part of speech for Korean words
  const determinePartOfSpeech = (word: string): string => {
    // Common patterns for Korean parts of speech
    if (word.endsWith('하다') || word.endsWith('되다') || word.endsWith('시다')) {
      return 'verb';
    } else if (word.endsWith('적') || word.endsWith('스럽다') || word.endsWith('롭다')) {
      return 'adjective';
    } else if (word.endsWith('게') || word.endsWith('히') || word.endsWith('이')) {
      return 'adverb';
    }
    
    // Common Korean particles (조사) indicate it's likely a noun
    return 'noun'; // Default to noun for unknown patterns
  };
  


  // Helper function for fallback: generate basic Korean translation
  const generateBasicTranslation = (word: string): { translationText: string, meaningDefinition: string } => {
    // Very basic Korean vocabulary for fallback
    const basicWords: Record<string, { en: string, definition: string }> = {
      '경기': { en: 'Gyeonggi', definition: 'A province in South Korea' },
      '혁신': { en: 'Innovation', definition: 'A new idea or method' },
      '센터': { en: 'Center', definition: 'A building or place used for a specific purpose' },
      '참가': { en: 'Participation', definition: 'The act of taking part in something' },
      '모집': { en: 'Recruitment', definition: 'The process of finding new people to join' }
    };
    
    // Check if it's a known basic word
    if (basicWords[word]) {
      return {
        translationText: basicWords[word].en,
        meaningDefinition: basicWords[word].definition
      };
    }
    
    // Fallback for unknown words
    return {
      translationText: `${word}`,
      meaningDefinition: `Unable to translate this term`
    };
  };
  
  // Helper to create example sentences
  const createExampleSentence = (word: string, partOfSpeech: string): string => {
    if (partOfSpeech === 'noun') {
      return `${word}가 중요합니다.`; // "[Word] is important."
    } else if (partOfSpeech === 'verb') {
      return `저는 매일 ${word}.`; // "I [verb] everyday."
    } else if (partOfSpeech === 'adjective') {
      return `그것은 ${word}.`; // "It is [adjective]."
    } else {
      return `그것은 ${word} 설명되어 있습니다.`; // "It is [adverb] explained."
    }
  };

  // Helper to format date
  const formatDate = (dateString?: string | null) => {
    if (!dateString) return 'Unknown date';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch (e) {
      return dateString;
    }
  };
  
  // Get translation function
  const { t } = useTranslation();

  // Render loading state
  if (isLoading) {
    return (
      <Container maxW="container.md" py={10} centerContent>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>{t('common.loading')}</Text>
        </VStack>
      </Container>
    );
  }
  
  // Render error state
  if (error && !article) {
    return (
      <Container maxW="container.md" py={10}>
        <Alert status="error" borderRadius="md" mb={6}>
          <AlertIcon />
          <AlertTitle mr={2}>{t('errors.somethingWentWrong')}</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button colorScheme="blue" onClick={() => navigate('/articles')}>
          {t('articles.browse')}
        </Button>
      </Container>
    );
  }
  
  // Render article content
  return (
    <Container maxW="container.md" py={8}>
      {/* Back button */}
      <Button 
        mb={6} 
        leftIcon={<span>←</span>} 
        variant="outline" 
        onClick={() => navigate('/articles')}
      >
        {t('articles.browse')}
      </Button>
      
      {article && (
        <Box 
          bg={bgColor} 
          p={6} 
          borderRadius="lg" 
          boxShadow="md" 
          border="1px" 
          borderColor={borderColor}
          onMouseUp={handleTextSelection}
          position="relative" // Added to ensure the popup position is relative to this container
        >
          {/* Article header */}
          <VStack align="start" spacing={4} mb={6}>
            <Heading as="h1" size="xl">{article.title}</Heading>
            
            {/* Source and date */}
            <HStack fontSize="sm" color="gray.600">
              <Text fontWeight="bold">{article.source}</Text>
              <Text>•</Text>
              <Text>{formatDate(article.date_published || article.date_created)}</Text>
              {article.difficulty && (
                <>
                  <Text>•</Text>
                  <Badge colorScheme={
                    article.difficulty === 'beginner' ? 'green' : 
                    article.difficulty === 'intermediate' ? 'blue' : 
                    'purple'
                  }>
                    {article.difficulty}
                  </Badge>
                </>
              )}
            </HStack>
            
            {/* Tags - only show when we have proper tag data */}
            {article.tag_ids && article.tag_ids.length > 0 && Object.keys(tags).length > 0 && (
              <HStack wrap="wrap" spacing={2}>
                {article.tag_ids.map((tagId, index) => (
                  tags[tagId] && (
                    <Badge key={index} colorScheme="teal" variant="subtle">
                      {tags[tagId].name}
                    </Badge>
                  )
                ))}
              </HStack>
            )}
            
            {/* Description if available */}
            {article.description && (
              <Text fontSize="lg" fontStyle="italic" color="gray.600">
                {article.description}
              </Text>
            )}
          </VStack>
          
          <Divider my={6} />
          
          {/* Article image if available */}
          {article.image_url && (
            <Box mb={6} w="100%">
              <Image 
                src={article.image_url} 
                alt={t('articles.illustration')} 
                borderRadius="md"
                width="100%"
                maxHeight="400px"
                objectFit="cover"
                fallbackSrc="https://via.placeholder.com/800x400?text=Image+not+available"
              />
            </Box>
          )}
          
          {/* Article content */}
          <VStack align="start" spacing={6}>
            {/* If the article has sections, display them */}
            {article.sections && article.sections.length > 0 && article.sections
              .sort((a, b) => a.order - b.order)
              .map((section, index) => {
                switch(section.type) {
                  case 'heading':
                    return (
                      <Heading as="h2" size="lg" key={index} pt={4}>
                        {section.content}
                      </Heading>
                    );
                  case 'subheading':
                    return (
                      <Heading as="h3" size="md" key={index} pt={2}>
                        {section.content}
                      </Heading>
                    );
                  case 'image':
                    return (
                      <Box key={index} w="100%">
                        <Image 
                          src={section.content} 
                          alt={section.caption || "Article illustration"} 
                          borderRadius="md"
                          width="100%"
                          maxHeight="400px"
                          objectFit="cover"
                          fallbackSrc="https://via.placeholder.com/800x400?text=Image+not+available"
                        />
                        {section.caption && (
                          <Text fontSize="sm" color="gray.500" mt={1} textAlign="center">
                            {section.caption}
                          </Text>
                        )}
                      </Box>
                    );
                  case 'text':
                  default:
                    // Process the content to avoid showing translations
                    // Korean content might have translations after it
                    const processedContent = section.content.split(/\n.*?(?:Gyeonggi|See more|Centre d'innovation)/)[0];
                    console.log('Section content:', { original: section.content, processed: processedContent });
                    return (
                      <Text as="div" key={index} fontSize="md" lineHeight="tall">
                        {processedContent}
                      </Text>
                    );
                }
              })}
              
            {/* If the article has only plain text content, display it as paragraphs */}
            {(!article.sections || article.sections.length === 0) && article.text && 
              article.text.split('\n').map((paragraph, index) => (
                paragraph.trim() && (
                  <Text as="div" key={index} fontSize="md" lineHeight="tall">
                    {paragraph}
                  </Text>
                )
              ))
            }
          </VStack>
          
          {/* Translation popup */}
          {popoverProps.isOpen && (
            <Box 
              position="absolute"
              top={`${popupPosition.top}px`}
              left={`${popupPosition.left}px`}
              transform="translate(-50%, -100%)"
              zIndex={10}
              bg={bgColor}
              borderRadius="md"
              boxShadow="lg"
              p={4}
              maxW="350px"
              borderColor={borderColor}
              border="1px"
            >
              {isTranslating ? (
                <VStack align="center" spacing={4} py={2}>
                  <Spinner size="md" color="blue.500" />
                  <Box fontSize="sm">{t('common.loading')} "{selectedText}"...</Box>
                </VStack>
              ) : translation ? (
                <VStack align="start" spacing={2}>
                  <HStack justify="space-between" width="100%">
                    <Text fontWeight="bold" fontSize="lg">{translation.word}</Text>
                    <Badge colorScheme="blue">{translation.part_of_speech}</Badge>
                  </HStack>
                  <Box fontSize="md" fontWeight="bold" color="blue.500">
                    {translation.translation}
                  </Box>
                  {translation.definition && (
                    <Box fontSize="sm">{translation.definition}</Box>
                  )}
                  {translation.examples && translation.examples.length > 0 && (
                    <VStack width="100%" mt={2} align="start" spacing={1}>
                      <Box fontSize="xs" fontWeight="bold" color="gray.500">{t('reading.examples').toUpperCase()}</Box>
                      {translation.examples.map((example, i) => (
                        <Box key={i} fontSize="xs" fontStyle="italic">{example}</Box>
                      ))}
                    </VStack>
                  )}
                  {/* Context section removed to make popup smaller */}
                  <Flex justify="space-between" width="100%" mt={2}>
                    <Button 
                      size="xs" 
                      colorScheme="blue" 
                      variant="outline"
                      onClick={() => {
                        toast({
                          title: t('reading.addedToVocabulary'),
                          description: `${translation.word}`,
                          status: "success",
                          duration: 2000,
                          isClosable: true,
                        });
                      }}
                    >
                      {t('reading.addToVocabulary')}
                    </Button>
                    <Button 
                      size="xs" 
                      variant="ghost"
                      onClick={popoverProps.onClose}
                    >
                      {t('common.close')}
                    </Button>
                  </Flex>
                </VStack>
              ) : (
                <Spinner size="sm" />
              )}
            </Box>
          )}
          
          {/* Translation Language Selector */}
          <Box mt={8} p={4} borderRadius="md" bg={useColorModeValue('gray.50', 'gray.800')}>
            <Flex direction="column" gap={3} mt={2}>
              <Flex alignItems="center" justify="space-between" wrap="wrap" gap={2}>
                <Text fontWeight="bold">{t('reading.translateTo')}:</Text>
                <Select 
                  value={targetLanguage === article?.language ? 
                          (article?.language === 'en' ? 'ko' : 'en') : 
                          targetLanguage} 
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                    console.log('Language changed to:', e.target.value);
                    setTargetLanguage(e.target.value);
                    // Clear any existing translation when language changes
                    setTranslation(null);
                  }}
                  width={['full', 'auto']} 
                  maxW="200px"
                  isDisabled={useNativeLanguage}
                >
                  {getValidLanguageOptions(article?.language)
                    .map(lang => (
                      <option key={lang.value} value={lang.value}>{lang.label}</option>
                  ))}
                </Select>
              </Flex>
              
              <Flex alignItems="center">
                <Checkbox 
                  isChecked={useNativeLanguage} 
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setUseNativeLanguage(e.target.checked);
                    // Clear any existing translation when this option changes
                    setTranslation(null);
                  }}
                  colorScheme="blue"
                  mr={2}
                >
                  {t('reading.showOriginal')}
                </Checkbox>
                <Box as="span" fontSize="sm" color="gray.500">
                  ({article?.language === 'ko' ? t('reading.korean') : t('reading.english')})
                </Box>
              </Flex>
            </Flex>
            <Text fontSize="sm" color="gray.500" mt={2}>
              {t('reading.highlightText')}{useNativeLanguage ? '' : ` ${LANGUAGE_OPTIONS.find(l => l.value === targetLanguage)?.label || t('reading.english')}`}.
              <Box mt={1} fontStyle="italic">
                {t('reading.translationSettings')}
              </Box>
            </Text>
          </Box>

          {/* Article footer */}
          <Box mt={10} pt={6} borderTop="1px" borderColor={borderColor}>
            <HStack justify="space-between">
              <Text fontSize="sm" color="gray.600">
                {t('articles.language')}: {article.language === 'ko' ? t('reading.korean') : t('reading.english')}
              </Text>
              {article.url && (
                <Button 
                  as="a" 
                  href={article.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  size="sm" 
                  variant="outline"
                >
                  {t('articles.viewArticle')}
                </Button>
              )}
            </HStack>
          </Box>
        </Box>
      )}
    </Container>
  );
};

export default ArticleViewPage;
