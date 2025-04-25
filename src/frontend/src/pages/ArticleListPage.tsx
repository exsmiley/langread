import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Container, 
  Heading, 
  Text, 
  VStack, 
  HStack, 
  Spinner, 
  Image, 
  Badge, 
  Divider,
  Flex,
  Button,
  useColorModeValue,
  SimpleGrid
} from '@chakra-ui/react';
import { useNavigate, useSearchParams, Link as RouterLink } from 'react-router-dom';
import axios from 'axios';

// Mock data for development
const MOCK_ARTICLES = [
  {
    id: '1',
    title: '인공지능의 발전과 미래',
    description: '최근 인공지능 기술의 발전과 그 영향에 대한 분석',
    source: 'Tech Korea',
    date_published: '2025-04-22T10:30:00Z',
    topics: ['기술', '인공지능', 'AI'],
    image_url: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485'
  },
  {
    id: '2',
    title: '한국 요리의 세계화: 비빔밥부터 김치까지',
    description: '한국 음식이 세계 각국에서 인기를 얻고 있는 이유',
    source: 'Food & Culture',
    date_published: '2025-04-21T14:15:00Z',
    topics: ['음식', '문화', '한국요리'],
    image_url: 'https://images.unsplash.com/photo-1590301157890-4810ed352733'
  },
  {
    id: '3',
    title: '2025년 봄 여행지 추천: 국내 명소 10곳',
    description: '봄을 맞아 방문하기 좋은 국내 여행지 추천',
    source: 'Travel Magazine',
    date_published: '2025-04-20T09:45:00Z',
    topics: ['여행', '봄', '국내여행'],
    image_url: 'https://images.unsplash.com/photo-1551918120-9739cb430c6d'
  },
  {
    id: '4',
    title: '최신 영화 리뷰: 올해의 기대작',
    description: '2025년 상반기 개봉한 영화들에 대한 평론가들의 리뷰',
    source: 'Cinema Today',
    date_published: '2025-04-19T16:30:00Z',
    topics: ['영화', '리뷰', '엔터테인먼트'],
    image_url: 'https://images.unsplash.com/photo-1536440136628-849c177e76a1'
  },
  {
    id: '5',
    title: '건강한 생활습관: 전문가들의 조언',
    description: '일상에서 실천할 수 있는 건강한 생활 습관에 대한 전문가들의 조언',
    source: 'Health & Wellness',
    date_published: '2025-04-18T11:20:00Z',
    topics: ['건강', '생활습관', '웰빙'],
    image_url: 'https://images.unsplash.com/photo-1549576490-b0b4831ef60a'
  }
];

interface Article {
  id: string;
  title: string;
  description: string;
  source: string;
  date_published: string;
  topics: string[];
  image_url: string;
}

const ArticleListPage = () => {
  const [searchParams] = useSearchParams();
  const [articles, setArticles] = useState<Article[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const query = searchParams.get('query') || '';
  const language = searchParams.get('language') || 'ko';
  const topicType = searchParams.get('topicType') || 'news';
  
  useEffect(() => {
    const fetchArticles = async () => {
      // Don't fetch if there's no query
      if (!query) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        // In a real app, we would fetch from the API
        // const response = await axios.post('/api/articles', {
        //   query,
        //   language,
        //   topic_type: topicType,
        //   max_sources: 10
        // });
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Use mock data for now
        setArticles(MOCK_ARTICLES);
      } catch (err) {
        console.error('Error fetching articles:', err);
        setError('Failed to fetch articles. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchArticles();
  }, [query, language, topicType]);
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(language === 'ko' ? 'ko-KR' : 'en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };
  
  return (
    <Container maxW="container.xl" p={4}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading as="h1" size="xl">
            {topicType === 'news' ? 'News Articles' : 'Articles'} {query ? `about "${query}"` : ''}
          </Heading>
          <Text color="gray.600" mt={2}>
            {language === 'ko' ? '한국어' : language === 'ja' ? '日本語' : 'Other language'} • 
            {topicType === 'news' ? ' News' : 
             topicType === 'blogs' ? ' Blogs' : 
             topicType === 'stories' ? ' Stories' : ' Educational Content'}
          </Text>
        </Box>
        
        <Divider />
        
        {isLoading ? (
          <Flex justify="center" align="center" minH="300px">
            <VStack>
              <Spinner size="xl" color="blue.500" />
              <Text mt={4}>Finding the best articles for you...</Text>
            </VStack>
          </Flex>
        ) : error ? (
          <Box 
            p={6} 
            borderRadius="md" 
            bg="red.50" 
            color="red.600"
            textAlign="center"
          >
            <Text>{error}</Text>
            <Button 
              mt={4} 
              colorScheme="red" 
              variant="outline"
              onClick={() => window.location.reload()}
            >
              Try Again
            </Button>
          </Box>
        ) : articles.length === 0 ? (
          <Box 
            p={6} 
            borderRadius="md" 
            bg="gray.50" 
            textAlign="center"
          >
            <Text>No articles found. Try a different search query.</Text>
            <Button 
              mt={4} 
              colorScheme="blue" 
              onClick={() => navigate('/')}
            >
              Back to Search
            </Button>
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {articles.map(article => (
              <Box 
                key={article.id}
                as={RouterLink}
                to={`/articles/${article.id}`}
                borderWidth="1px"
                borderRadius="lg"
                borderColor={borderColor}
                overflow="hidden"
                bg={bgColor}
                _hover={{ 
                  transform: 'translateY(-4px)',
                  shadow: 'md',
                  transition: 'all 0.3s ease'
                }}
                transition="all 0.3s ease"
              >
                <Image 
                  src={`${article.image_url}?auto=format&fit=crop&w=600&q=80`}
                  alt={article.title}
                  objectFit="cover"
                  h="200px"
                  w="100%"
                  fallbackSrc="https://via.placeholder.com/600x200?text=Image+Not+Available"
                />
                
                <Box p={5}>
                  <HStack spacing={2} mb={2}>
                    {article.topics.slice(0, 3).map(topic => (
                      <Badge key={topic} colorScheme="blue" variant="subtle">
                        {topic}
                      </Badge>
                    ))}
                  </HStack>
                  
                  <Heading as="h3" size="md" mb={2} noOfLines={2}>
                    {article.title}
                  </Heading>
                  
                  <Text fontSize="sm" color="gray.500" mb={3}>
                    {article.source} • {formatDate(article.date_published)}
                  </Text>
                  
                  <Text noOfLines={3} color="gray.600">
                    {article.description}
                  </Text>
                </Box>
              </Box>
            ))}
          </SimpleGrid>
        )}
      </VStack>
    </Container>
  );
};

export default ArticleListPage;
