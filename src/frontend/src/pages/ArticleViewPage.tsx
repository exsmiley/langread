import React, { useState, useEffect } from 'react';
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
  AlertDescription
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';

// Interfaces to match the API response structure
interface Section {
  type: string;
  content: string;
  order: number;
  caption?: string;
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

const ArticleViewPage: React.FC = () => {
  const { articleId } = useParams<{ articleId: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  useEffect(() => {
    const fetchArticle = async () => {
      setIsLoading(true);
      setError(null);
      
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
  
  // Render loading state
  if (isLoading) {
    return (
      <Container maxW="container.md" py={10} centerContent>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Loading article...</Text>
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
          <AlertTitle mr={2}>Error loading article</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button colorScheme="blue" onClick={() => navigate('/articles')}>
          Back to articles
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
        Back to articles
      </Button>
      
      {article && (
        <Box 
          bg={bgColor} 
          p={6} 
          borderRadius="lg" 
          boxShadow="md" 
          border="1px" 
          borderColor={borderColor}
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
            
            {/* Tags */}
            {article.tag_ids && article.tag_ids.length > 0 && (
              <HStack wrap="wrap" spacing={2}>
                {article.tag_ids.map((tagId, index) => (
                  <Badge key={index} colorScheme="teal" variant="subtle">
                    {tagId}
                  </Badge>
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
                alt="Article illustration" 
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
                    return (
                      <Text key={index} fontSize="md" lineHeight="tall">
                        {section.content}
                      </Text>
                    );
                }
              })}
            {/* If the article has only plain text content, display it as paragraphs */}
            {(!article.sections || article.sections.length === 0) && article.text && 
              article.text.split('\n').map((paragraph, index) => (
                paragraph.trim() && (
                  <Text key={index} fontSize="md" lineHeight="tall">
                    {paragraph}
                  </Text>
                )
              ))
            }
          </VStack>
          
          {/* Article footer */}
          <Box mt={10} pt={6} borderTop="1px" borderColor={borderColor}>
            <HStack justify="space-between">
              <Text fontSize="sm" color="gray.600">
                Language: {article.language === 'ko' ? '한국어' : 'English'}
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
                  View original article
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
