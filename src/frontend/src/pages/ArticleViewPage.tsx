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
  Popover, 
  PopoverTrigger, 
  PopoverContent, 
  PopoverArrow, 
  PopoverBody,
  useDisclosure,
  useColorModeValue,
  Flex,
  useToast,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Radio,
  RadioGroup,
  Stack,
  chakra
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

// Mock article data for development
const MOCK_ARTICLE = {
  id: '1',
  title: '인공지능의 발전과 미래',
  description: '최근 인공지능 기술의 발전과 그 영향에 대한 분석',
  source: 'Tech Korea',
  date_published: '2025-04-22T10:30:00Z',
  language: 'ko',
  topics: ['기술', '인공지능', 'AI'],
  content: [
    {
      type: 'heading',
      content: '인공지능 기술의 현재와 미래',
      order: 0
    },
    {
      type: 'image',
      content: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485',
      caption: '인공지능 기술은 우리의 일상을 변화시키고 있습니다.',
      order: 1
    },
    {
      type: 'text',
      content: '인공지능 기술은 지난 10년간 놀라운 속도로 발전해왔습니다. 특히 딥러닝 기술의 혁신은 컴퓨터 비전, 자연어 처리, 음성 인식 등 다양한 분야에서 획기적인 성과를 이끌어냈습니다. 이제 인공지능은 단순한 기술을 넘어 우리 사회와 일상의 모든 영역에 스며들고 있습니다.',
      order: 2
    },
    {
      type: 'text',
      content: '현재 인공지능 기술은 의료, 금융, 교통, 교육 등 다양한 산업 분야에서 활용되고 있습니다. 의료 분야에서는 질병 진단과 신약 개발에, 금융 분야에서는 투자 분석과 사기 탐지에, 교통 분야에서는 자율주행 기술에, 교육 분야에서는 개인화된 학습 경험을 제공하는 데 인공지능이 사용되고 있습니다.',
      order: 3
    },
    {
      type: 'heading',
      content: '한국의 인공지능 기술 발전',
      order: 4
    },
    {
      type: 'text',
      content: '한국은 인공지능 기술 개발에 적극적으로 투자하고 있으며, 특히 정부 주도의 다양한 지원 정책이 시행되고 있습니다. 삼성전자, 네이버, 카카오 등 대기업들도 인공지능 연구에 많은 자원을 투입하고 있으며, 수많은 스타트업들이 혁신적인 인공지능 솔루션을 개발하고 있습니다.',
      order: 5
    },
    {
      type: 'image',
      content: 'https://images.unsplash.com/photo-1591453089816-0fbb971b454c',
      caption: '한국의 AI 연구센터들은 세계적인 수준의 기술을 개발하고 있습니다.',
      order: 6
    },
    {
      type: 'text',
      content: '특히 한국의 강점인 반도체 기술과 결합된 AI 칩 개발은 글로벌 시장에서도 주목받고 있습니다. 이러한 하드웨어 기술의 발전은 더 효율적이고 강력한 인공지능 시스템 구축을 가능하게 합니다.',
      order: 7
    },
    {
      type: 'heading',
      content: '인공지능이 가져올 사회 변화',
      order: 8
    },
    {
      type: 'text',
      content: '인공지능 기술의 발전은 우리 사회에 큰 변화를 가져올 것으로 예상됩니다. 일자리 시장의 변화, 교육 시스템의 혁신, 의료 서비스의 개선 등 다양한 영역에서 변화가 일어날 것입니다. 이러한 변화에 적응하기 위해서는 교육과 재교육이 더욱 중요해질 것입니다.',
      order: 9
    },
    {
      type: 'text',
      content: '그러나 인공지능 기술의 발전에는 도전과제도 존재합니다. 개인정보 보호, 알고리즘 편향성, 책임 소재, 일자리 대체 등의 문제는 사회적 논의와 합의가 필요한 부분입니다. 기술 발전과 함께 이러한 윤리적, 사회적 측면에 대한 고려도 중요합니다.',
      order: 10
    },
    {
      type: 'text',
      content: '미래 사회에서 인공지능은 더욱 발전하여 인간의 창의성과 협업하는 방향으로 진화할 것으로 예상됩니다. 인간의 직관과 인공지능의 분석 능력이 결합될 때 우리는 더 큰 혁신을 이룰 수 있을 것입니다.',
      order: 11
    }
  ]
};

// Mock translation data
const MOCK_TRANSLATIONS = {
  '인공지능': {
    word: '인공지능',
    translation: 'Artificial Intelligence',
    part_of_speech: 'noun',
    definition: 'The theory and development of computer systems able to perform tasks that normally require human intelligence.',
    examples: ['인공지능 기술이 발전하고 있다', '인공지능을 활용한 서비스'],
  },
  '기술': {
    word: '기술',
    translation: 'Technology',
    part_of_speech: 'noun',
    definition: 'The application of scientific knowledge for practical purposes.',
    examples: ['최신 기술', '기술 발전'],
  },
  '발전': {
    word: '발전',
    translation: 'Development / Progress',
    part_of_speech: 'noun',
    definition: 'Growth or improvement over time.',
    examples: ['경제 발전', '기술 발전'],
  },
  '혁신': {
    word: '혁신',
    translation: 'Innovation',
    part_of_speech: 'noun',
    definition: 'A new method, idea, or product.',
    examples: ['기술 혁신', '혁신적인 제품'],
  },
};

// Mock quiz data
const MOCK_QUIZ = {
  questions: [
    {
      id: 'q1',
      question: '인공지능 기술이 지난 몇 년간 발전해왔다고 언급되었나요?',
      options: ['5년', '10년', '15년', '20년'],
      correct_answer: '10년',
      evidence: '인공지능 기술은 지난 10년간 놀라운 속도로 발전해왔습니다.',
    },
    {
      id: 'q2',
      question: '인공지능 기술이 활용되는 분야가 아닌 것은?',
      options: ['의료', '금융', '교통', '농업'],
      correct_answer: '농업',
      evidence: '현재 인공지능 기술은 의료, 금융, 교통, 교육 등 다양한 산업 분야에서 활용되고 있습니다.',
    },
    {
      id: 'q3',
      question: '한국의 인공지능 기술 발전에 투자하고 있는 기업이 아닌 것은?',
      options: ['삼성전자', '네이버', '카카오', 'LG화학'],
      correct_answer: 'LG화학',
      evidence: '삼성전자, 네이버, 카카오 등 대기업들도 인공지능 연구에 많은 자원을 투입하고 있으며',
    },
    {
      id: 'q4',
      question: '인공지능 기술 발전에 따른 도전과제가 아닌 것은?',
      options: ['개인정보 보호', '알고리즘 편향성', '책임 소재', '기후 변화'],
      correct_answer: '기후 변화',
      evidence: '개인정보 보호, 알고리즘 편향성, 책임 소재, 일자리 대체 등의 문제는 사회적 논의와 합의가 필요한 부분입니다.',
    },
    {
      id: 'q5',
      question: '미래 사회에서 인공지능은 어떤 방향으로 진화할 것으로 예상되나요?',
      options: [
        '인간을 대체하는 방향', 
        '인간의 창의성과 협업하는 방향', 
        '독립적으로 발전하는 방향', 
        '발전이 정체될 것'
      ],
      correct_answer: '인간의 창의성과 협업하는 방향',
      evidence: '미래 사회에서 인공지능은 더욱 발전하여 인간의 창의성과 협업하는 방향으로 진화할 것으로 예상됩니다.',
    },
  ]
};

interface ContentSection {
  type: string;
  content: string;
  caption?: string;
  order: number;
}

interface Article {
  id: string;
  title: string;
  description: string;
  source: string;
  date_published: string;
  language: string;
  topics: string[];
  content: ContentSection[];
}

interface Translation {
  word: string;
  translation: string;
  part_of_speech: string;
  definition: string;
  examples: string[];
}

interface Quiz {
  questions: {
    id: string;
    question: string;
    options: string[];
    correct_answer: string;
    evidence: string;
  }[];
}

const ArticleViewPage = () => {
  const { articleId } = useParams<{ articleId: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedText, setSelectedText] = useState('');
  const [translation, setTranslation] = useState<Translation | null>(null);
  const [showQuiz, setShowQuiz] = useState(false);
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [quizAnswers, setQuizAnswers] = useState<Record<string, string>>({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizScore, setQuizScore] = useState(0);
  const textRefs = useRef<Record<string, HTMLSpanElement | null>>({});
  
  const navigate = useNavigate();
  const toast = useToast();
  const popoverProps = useDisclosure();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  useEffect(() => {
    const fetchArticle = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // In a real app, we would fetch from the API
        // const response = await axios.get(`/api/articles/${articleId}`);
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Use mock data for now
        setArticle(MOCK_ARTICLE);
        
        // Fetch quiz data
        await new Promise(resolve => setTimeout(resolve, 500));
        setQuiz(MOCK_QUIZ);
      } catch (err) {
        console.error('Error fetching article:', err);
        setError('Failed to fetch article. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchArticle();
  }, [articleId]);
  
  const handleTextSelection = () => {
    const selectedText = window.getSelection()?.toString().trim();
    
    if (selectedText && selectedText.length > 0) {
      translateText(selectedText);
    }
  };
  
  const handleWordHover = (word: string) => {
    translateText(word);
  };
  
  const translateText = async (text: string) => {
    // Don't translate if it's the same as the current selection
    if (text === selectedText) return;
    
    setSelectedText(text);
    popoverProps.onOpen();
    
    try {
      // In a real app, we would fetch from the API
      // const response = await axios.post('/api/translate', {
      //   text,
      //   source_lang: article?.language || 'ko',
      //   target_lang: 'en'
      // });
      
      // Use mock data for now
      if (MOCK_TRANSLATIONS[text]) {
        setTranslation(MOCK_TRANSLATIONS[text]);
      } else {
        // Generate a simple translation for words not in the mock data
        setTranslation({
          word: text,
          translation: `Translation for "${text}"`,
          part_of_speech: 'unknown',
          definition: `Definition for "${text}" would appear here.`,
          examples: [`Example sentence with "${text}".`],
        });
      }
      
      // Add to vocabulary (would be implemented in real app)
      console.log(`Added to vocabulary: ${text}`);
    } catch (err) {
      console.error('Error translating text:', err);
      toast({
        title: 'Translation error',
        description: 'Failed to translate the selected text.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(article?.language === 'ko' ? 'ko-KR' : 'en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };
  
  const handleQuizSubmit = () => {
    if (!quiz) return;
    
    let score = 0;
    quiz.questions.forEach(question => {
      if (quizAnswers[question.id] === question.correct_answer) {
        score++;
      }
    });
    
    setQuizScore(score);
    setQuizSubmitted(true);
    
    toast({
      title: 'Quiz Submitted',
      description: `Your score: ${score}/${quiz.questions.length}`,
      status: score === quiz.questions.length ? 'success' : 'info',
      duration: 5000,
      isClosable: true,
    });
  };
  
  const handleAnswerChange = (questionId: string, answer: string) => {
    setQuizAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };
  
  // Split text into words to enable hover functionality
  const renderText = (text: string, index: number) => {
    const words = text.split(/(\s+)/);
    
    return (
      <Box key={`text-${index}`} my={4} lineHeight="taller">
        {words.map((word, wordIndex) => {
          if (word.trim() === '') {
            return <React.Fragment key={`space-${wordIndex}`}>{word}</React.Fragment>;
          }
          
          return (
            <Popover
              key={`word-${wordIndex}`}
              trigger="hover"
              placement="top"
              isOpen={selectedText === word.trim() && popoverProps.isOpen}
              onOpen={() => handleWordHover(word.trim())}
            >
              <PopoverTrigger>
                <chakra.span
                  ref={el => textRefs.current[`${index}-${wordIndex}`] = el}
                  display="inline"
                  px="1px"
                  borderBottom="2px solid transparent"
                  _hover={{
                    borderBottom: "2px solid",
                    borderColor: "blue.500",
                    cursor: "pointer",
                  }}
                  textDecoration={selectedText === word.trim() ? "underline" : "none"}
                  textDecorationColor="blue.500"
                >
                  {word}
                </chakra.span>
              </PopoverTrigger>
              <PopoverContent bg={bgColor} borderColor={borderColor} shadow="xl" width="300px">
                <PopoverArrow bg={bgColor} />
                <PopoverBody p={4}>
                  {translation ? (
                    <VStack align="start" spacing={2}>
                      <HStack justify="space-between" width="100%">
                        <Text fontWeight="bold" fontSize="lg">{translation.word}</Text>
                        <Badge colorScheme="blue">{translation.part_of_speech}</Badge>
                      </HStack>
                      <Text fontSize="md" fontWeight="bold" color="blue.500">
                        {translation.translation}
                      </Text>
                      <Text fontSize="sm">{translation.definition}</Text>
                      {translation.examples && translation.examples.length > 0 && (
                        <Box width="100%" mt={2}>
                          <Text fontSize="xs" fontWeight="bold" color="gray.500">EXAMPLES</Text>
                          {translation.examples.map((example, i) => (
                            <Text key={i} fontSize="xs" fontStyle="italic">{example}</Text>
                          ))}
                        </Box>
                      )}
                      <Button 
                        size="xs" 
                        colorScheme="blue" 
                        variant="outline" 
                        mt={2}
                        width="100%"
                        onClick={() => console.log(`Added to flashcards: ${translation.word}`)}
                      >
                        Add to Flashcards
                      </Button>
                    </VStack>
                  ) : (
                    <Spinner size="sm" />
                  )}
                </PopoverBody>
              </PopoverContent>
            </Popover>
          );
        })}
      </Box>
    );
  };
  
  const renderContent = (content: ContentSection[]) => {
    return content.sort((a, b) => a.order - b.order).map((section, index) => {
      switch (section.type) {
        case 'heading':
          return (
            <Heading as="h2" size="lg" mt={6} mb={4} key={`heading-${index}`}>
              {section.content}
            </Heading>
          );
        case 'text':
          return renderText(section.content, index);
        case 'image':
          return (
            <Box key={`image-${index}`} my={6}>
              <Image 
                src={section.content}
                alt={section.caption || 'Article image'}
                borderRadius="md"
                width="100%"
              />
              {section.caption && (
                <Text fontSize="sm" color="gray.600" mt={2} textAlign="center">
                  {section.caption}
                </Text>
              )}
            </Box>
          );
        default:
          return null;
      }
    });
  };
  
  if (isLoading) {
    return (
      <Container maxW="container.md" centerContent py={10}>
        <Spinner size="xl" thickness="4px" color="blue.500" />
        <Text mt={4}>Loading article...</Text>
      </Container>
    );
  }
  
  if (error || !article) {
    return (
      <Container maxW="container.md" centerContent py={10}>
        <Box 
          p={6} 
          borderRadius="md" 
          bg="red.50" 
          color="red.600"
          textAlign="center"
          width="100%"
        >
          <Text>{error || 'Article not found'}</Text>
          <Button 
            mt={4} 
            colorScheme="blue" 
            onClick={() => navigate('/articles')}
          >
            Back to Articles
          </Button>
        </Box>
      </Container>
    );
  }
  
  return (
    <Container maxW="container.md" py={6} onClick={handleTextSelection}>
      <VStack spacing={4} align="stretch">
        <Box>
          <Heading as="h1" size="xl" lineHeight="1.2" mb={2}>
            {article.title}
          </Heading>
          
          <Text fontSize="md" color="gray.600" mb={4}>
            {article.source} • {formatDate(article.date_published)}
          </Text>
          
          <HStack spacing={2} mb={6}>
            {article.topics.map(topic => (
              <Badge key={topic} colorScheme="blue">
                {topic}
              </Badge>
            ))}
          </HStack>
          
          <Divider />
        </Box>
        
        <Box 
          bg={bgColor} 
          borderRadius="md" 
          p={6} 
          shadow="sm"
          borderWidth="1px"
          borderColor={borderColor}
        >
          {renderContent(article.content)}
          
          <Divider my={6} />
          
          <Flex justify="center" my={4}>
            <Button 
              colorScheme="blue" 
              size="lg" 
              onClick={() => setShowQuiz(!showQuiz)}
            >
              {showQuiz ? 'Hide Quiz' : 'Test Your Understanding'}
            </Button>
          </Flex>
          
          {showQuiz && quiz && (
            <Box mt={6}>
              <Heading as="h3" size="md" mb={4}>
                Comprehension Quiz
              </Heading>
              
              <Accordion allowToggle>
                {quiz.questions.map((question, index) => (
                  <AccordionItem 
                    key={question.id} 
                    border="1px solid"
                    borderColor={borderColor}
                    borderRadius="md"
                    mb={4}
                    overflow="hidden"
                  >
                    <h2>
                      <AccordionButton 
                        py={4}
                        bg={
                          quizSubmitted 
                            ? quizAnswers[question.id] === question.correct_answer 
                              ? 'green.50' 
                              : 'red.50'
                            : bgColor
                        }
                      >
                        <Box flex="1" textAlign="left" fontWeight="medium">
                          {index + 1}. {question.question}
                        </Box>
                        <AccordionIcon />
                      </AccordionButton>
                    </h2>
                    <AccordionPanel pb={4}>
                      <RadioGroup 
                        onChange={(value) => handleAnswerChange(question.id, value)} 
                        value={quizAnswers[question.id] || ''}
                        isDisabled={quizSubmitted}
                      >
                        <Stack spacing={2}>
                          {question.options.map((option) => (
                            <Radio 
                              key={option} 
                              value={option}
                              colorScheme="blue"
                              size="md"
                            >
                              {option}
                            </Radio>
                          ))}
                        </Stack>
                      </RadioGroup>
                      
                      {quizSubmitted && (
                        <Box 
                          mt={4} 
                          p={3} 
                          bg={quizAnswers[question.id] === question.correct_answer ? 'green.50' : 'red.50'} 
                          borderRadius="md"
                        >
                          <Text fontWeight="bold">
                            {quizAnswers[question.id] === question.correct_answer 
                              ? '✓ Correct!' 
                              : `✗ Incorrect. The correct answer is "${question.correct_answer}"`}
                          </Text>
                          <Text mt={2} fontSize="sm">
                            <Text as="span" fontWeight="bold">Evidence: </Text>
                            {question.evidence}
                          </Text>
                        </Box>
                      )}
                    </AccordionPanel>
                  </AccordionItem>
                ))}
              </Accordion>
              
              {!quizSubmitted ? (
                <Button 
                  colorScheme="blue" 
                  mt={4} 
                  width="100%" 
                  onClick={handleQuizSubmit}
                  isDisabled={Object.keys(quizAnswers).length !== quiz.questions.length}
                >
                  Submit Answers
                </Button>
              ) : (
                <VStack spacing={4} mt={6} p={4} bg="blue.50" borderRadius="md">
                  <Heading as="h4" size="md">
                    Your Score: {quizScore}/{quiz.questions.length}
                  </Heading>
                  <Text>
                    {quizScore === quiz.questions.length 
                      ? 'Perfect! You understood the article completely.' 
                      : `You got ${quizScore} out of ${quiz.questions.length} correct. Review the article and try again!`}
                  </Text>
                  <Button 
                    colorScheme="blue" 
                    variant="outline"
                    onClick={() => {
                      setQuizSubmitted(false);
                      setQuizAnswers({});
                      setQuizScore(0);
                    }}
                  >
                    Retry Quiz
                  </Button>
                </VStack>
              )}
            </Box>
          )}
        </Box>
      </VStack>
    </Container>
  );
};

export default ArticleViewPage;
