import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Container, 
  Flex, 
  Heading, 
  Text, 
  Select, 
  VStack, 
  HStack,
  FormControl,
  FormLabel,
  useColorModeValue,
  useToast,
  Radio,
  RadioGroup,
  Stack,
  Tag,
  TagLabel,
  TagCloseButton,
  Input,
  InputGroup,
  InputLeftElement,
  Wrap,
  WrapItem,
  Spinner,
  Image
} from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';

// Tag type definition
type Tag = {
  _id: string;
  name: string;
  localized_name?: string;
  original_language: string;
  translations: Record<string, string>;
  article_count?: number;
  active?: boolean;
};

// Language options
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

const HomePage = () => {
  // Language and difficulty states
  const [nativeLanguage, setNativeLanguage] = useState('en');
  const [targetLanguage, setTargetLanguage] = useState('ko');
  const [difficulty, setDifficulty] = useState('intermediate');
  
  // Tag states
  const [availableTags, setAvailableTags] = useState<Tag[]>([]);
  const [filteredTags, setFilteredTags] = useState<Tag[]>([]);
  const [selectedTags, setSelectedTags] = useState<Tag[]>([]);
  const [selectedTagIds, setSelectedTagIds] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [tagsLoading, setTagsLoading] = useState(true);
  
  const toast = useToast();
  const navigate = useNavigate();
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const formBgColor = useColorModeValue('white', 'gray.800');
  const boxShadow = '0px 4px 10px rgba(0, 0, 0, 0.05)';
  const tagBgColor = useColorModeValue('gray.100', 'gray.700');
  const selectedTagBgColor = useColorModeValue('blue.100', 'blue.700');
  
  // Fetch available tags when component mounts or language changes
  useEffect(() => {
    fetchTags();
  }, [targetLanguage]);

  // Filter tags based on search query
  useEffect(() => {
    filterTags();
  }, [availableTags, searchQuery]);

  const fetchTags = async () => {
    try {
      setTagsLoading(true);
      
      // Connect to the backend API to get tags
      const response = await api.get(`/tags?language=${targetLanguage}&active=true`);
      
      // Check if we received data
      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        setAvailableTags(response.data);
      } else {
        // If no tags found in the backend, use fallback tags
        const fallbackTags = [
          {
            _id: '1',
            name: 'technology',
            original_language: 'en',
            translations: { en: 'technology', ko: '기술', fr: 'technologie' }
          },
          {
            _id: '2',
            name: 'sports',
            original_language: 'en',
            translations: { en: 'sports', ko: '스포츠', fr: 'sports' }
          },
          {
            _id: '3',
            name: 'music',
            original_language: 'en',
            translations: { en: 'music', ko: '음악', fr: 'musique' }
          },
          {
            _id: '4',
            name: 'food',
            original_language: 'en',
            translations: { en: 'food', ko: '음식', fr: 'nourriture' }
          },
          {
            _id: '5',
            name: 'travel',
            original_language: 'en',
            translations: { en: 'travel', ko: '여행', fr: 'voyage' }
          },
          {
            _id: '6',
            name: 'politics',
            original_language: 'en',
            translations: { en: 'politics', ko: '정치', fr: 'politique' }
          }
        ];
        console.log('No tags found in backend, using fallback tags');
        setAvailableTags(fallbackTags);
      }
      
      setTagsLoading(false);
    } catch (error) {
      console.error('Error fetching tags:', error);
      
      // Use fallback tags in case of an error
      const fallbackTags = [
        {
          _id: '1',
          name: 'technology',
          original_language: 'en',
          translations: { en: 'technology', ko: '기술', fr: 'technologie' }
        },
        {
          _id: '2',
          name: 'sports',
          original_language: 'en',
          translations: { en: 'sports', ko: '스포츠', fr: 'sports' }
        },
        {
          _id: '3',
          name: 'music',
          original_language: 'en',
          translations: { en: 'music', ko: '음악', fr: 'musique' }
        }
      ];
      console.log('Error connecting to backend, using fallback tags');
      setAvailableTags(fallbackTags);
      setTagsLoading(false);
    }
  };

  const filterTags = () => {
    if (!searchQuery) {
      setFilteredTags(availableTags);
      return;
    }
    
    const filtered = availableTags.filter(tag => {
      // Search in tag name and translations
      const tagName = tag.name.toLowerCase();
      const query = searchQuery.toLowerCase();
      
      // Check original name
      if (tagName.includes(query)) return true;
      
      // Check translations
      if (tag.translations) {
        for (const lang in tag.translations) {
          if (tag.translations[lang].toLowerCase().includes(query)) {
            return true;
          }
        }
      }
      
      return false;
    });
    
    setFilteredTags(filtered);
  };

  const handleSelectTag = (tag: Tag) => {
    // Check if tag is already selected
    if (selectedTagIds.includes(tag._id)) return;
    
    // Add tag to selected tags
    setSelectedTags([...selectedTags, tag]);
    setSelectedTagIds([...selectedTagIds, tag._id]);
  };

  const handleRemoveTag = (tagId: string) => {
    setSelectedTags(selectedTags.filter(tag => tag._id !== tagId));
    setSelectedTagIds(selectedTagIds.filter(id => id !== tagId));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (selectedTagIds.length === 0) {
      toast({
        title: 'No tags selected',
        description: "Please select at least one tag to find relevant articles",
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    setIsLoading(true);
    
    // Call the backend API to get articles based on selected criteria
    // In a real implementation, this would be: 
    // api.post('/cached-articles', { language: targetLanguage, tags: selectedTagIds })
    
    // For now, just navigate to the articles page with the selected parameters
    setTimeout(() => {
      setIsLoading(false);
      const tagParams = selectedTagIds.join(',');
      navigate(`/articles?nativeLanguage=${nativeLanguage}&targetLanguage=${targetLanguage}&tags=${tagParams}&difficulty=${difficulty}`);
    }, 1000);
  };
  
  return (
    <Container maxW="container.xl" p={0}>
      <Flex 
        direction={{ base: 'column', md: 'row' }} 
        align="center" 
        justify="space-between"
        py={10}
        px={8}
        bg={bgColor}
        borderRadius="md"
      >
        <VStack 
          align="flex-start" 
          spacing={5}
          maxW={{ base: '100%', md: '50%' }}
          mb={{ base: 10, md: 0 }}
        >
          <Heading as="h1" size="2xl">
            LangRead
          </Heading>
          <Text fontSize="xl" color="gray.600">
            Improve your language skills by reading authentic content in your target language.
            Discover articles on any topic, translate words with a hover, and build your vocabulary.
          </Text>
          <Box 
            bg={formBgColor} 
            p={6} 
            borderRadius="md" 
            w="100%" 
            boxShadow={boxShadow}
          >
            <Heading as="h2" size="md" mb={4}>
              Find Articles
            </Heading>
            <form onSubmit={handleSubmit}>
              <VStack spacing={5} align="stretch">
                {/* Language Selection */}
                <HStack spacing={4}>
                  <FormControl id="nativeLanguage">
                    <FormLabel fontWeight="bold">My Language</FormLabel>
                    <Select
                      value={nativeLanguage}
                      onChange={(e) => setNativeLanguage(e.target.value)}
                    >
                      {languageOptions.map(lang => (
                        <option key={lang.value} value={lang.value}>{lang.label}</option>
                      ))}
                    </Select>
                  </FormControl>
                  
                  <FormControl id="targetLanguage">
                    <FormLabel fontWeight="bold">Target Language</FormLabel>
                    <Select
                      value={targetLanguage}
                      onChange={(e) => {
                        setTargetLanguage(e.target.value);
                        // Clear selected tags when language changes
                        setSelectedTags([]);
                        setSelectedTagIds([]);
                      }}
                    >
                      {languageOptions.map(lang => (
                        <option key={lang.value} value={lang.value}>{lang.label}</option>
                      ))}
                    </Select>
                  </FormControl>
                </HStack>

                {/* Tag Selection */}
                <FormControl id="tagSelection">
                  <FormLabel fontWeight="bold">Select Tags</FormLabel>
                  
                  {/* Search bar for tags */}
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
                  
                  {/* Selected tags */}
                  {selectedTags.length > 0 && (
                    <Box mb={3}>
                      <Text fontSize="sm" fontWeight="bold" mb={2}>
                        Selected Tags:
                      </Text>
                      <Wrap spacing={2}>
                        {selectedTags.map(tag => (
                          <WrapItem key={tag._id}>
                            <Tag 
                              size="md" 
                              borderRadius="full"
                              variant="solid"
                              colorScheme="blue"
                            >
                              <TagLabel>
                                {tag.translations && tag.translations[targetLanguage] 
                                  ? tag.translations[targetLanguage] 
                                  : tag.name}
                              </TagLabel>
                              <TagCloseButton onClick={() => handleRemoveTag(tag._id)} />
                            </Tag>
                          </WrapItem>
                        ))}
                      </Wrap>
                    </Box>
                  )}
                  
                  {/* Available tags */}
                  <Box maxH="200px" overflowY="auto" p={2} borderWidth="1px" borderRadius="md">
                    {tagsLoading ? (
                      <Flex justify="center" align="center" h="100px">
                        <Spinner size="md" />
                        <Text ml={3}>Loading tags...</Text>
                      </Flex>
                    ) : filteredTags.length > 0 ? (
                      <Wrap spacing={2}>
                        {filteredTags.map(tag => (
                          <WrapItem key={tag._id}>
                            <Tag
                              size="md"
                              borderRadius="full"
                              variant="subtle"
                              colorScheme="gray"
                              cursor="pointer"
                              _hover={{ bg: 'gray.200' }}
                              onClick={() => handleSelectTag(tag)}
                              opacity={selectedTagIds.includes(tag._id) ? 0.5 : 1}
                            >
                              <TagLabel>
                                {tag.translations && tag.translations[targetLanguage] 
                                  ? tag.translations[targetLanguage] 
                                  : tag.name}
                              </TagLabel>
                            </Tag>
                          </WrapItem>
                        ))}
                      </Wrap>
                    ) : (
                      <Text textAlign="center" py={4} color="gray.500">
                        No tags found. Try a different search or language.
                      </Text>
                    )}
                  </Box>
                </FormControl>

                {/* Difficulty Level Selection */}
                <FormControl id="difficultySelector" p={3} bg="gray.50" borderRadius="md">
                  <FormLabel fontWeight="bold">Difficulty Level</FormLabel>
                  <RadioGroup value={difficulty} onChange={setDifficulty}>
                    <Stack direction="row" spacing={4}>
                      <Radio value="beginner" colorScheme="green">
                        Beginner
                      </Radio>
                      <Radio value="intermediate" colorScheme="blue">
                        Intermediate
                      </Radio>
                      <Radio value="advanced" colorScheme="purple">
                        Advanced
                      </Radio>
                    </Stack>
                  </RadioGroup>
                </FormControl>
                
                <Button 
                  colorScheme="blue" 
                  type="submit"
                  isLoading={isLoading}
                  loadingText="Searching..."
                  size="lg"
                  mt={2}
                >
                  Find Articles
                </Button>
              </VStack>
            </form>
          </Box>
        </VStack>
        
        <Box
          maxW={{ base: '100%', md: '45%' }}
          boxShadow="xl"
          borderRadius="md"
          overflow="hidden"
        >
          <Image 
            src="https://images.unsplash.com/photo-1546953304-5d96f43c2e94?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80" 
            alt="Person reading"
            objectFit="cover"
            fallbackSrc="https://via.placeholder.com/500x400?text=LangRead"
          />
        </Box>
      </Flex>
      
      <VStack spacing={10} py={16} px={8}>
        <Heading as="h2" size="xl" textAlign="center">
          How LangRead Works
        </Heading>
        
        <Stack 
          direction={{ base: 'column', md: 'row' }} 
          justifyContent="space-between"
          alignItems="center"
          w="100%"
          spacing={8}
        >
          <FeatureCard 
            title="Discover Content" 
            description="Search for articles, blogs, stories and more in your target language. Our AI finds the best content for your language level."
            iconUrl="🔍"
          />
          <FeatureCard 
            title="Read with Assistance" 
            description="Hover over words to see translations. The app adapts to your level and helps you understand complex text."
            iconUrl="📚"
          />
          <FeatureCard 
            title="Build Vocabulary" 
            description="Every word you encounter is saved to your vocabulary bank. Create flashcards and track your progress."
            iconUrl="📝"
          />
          <FeatureCard 
            title="Test Comprehension" 
            description="Test your understanding with auto-generated quizzes based on what you've read."
            iconUrl="✅"
          />
        </Stack>
      </VStack>
    </Container>
  );
};

interface FeatureCardProps {
  title: string;
  description: string;
  iconUrl: string;
}

const FeatureCard = ({ title, description, iconUrl }: FeatureCardProps) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  
  return (
    <Box 
      bg={cardBg} 
      p={5} 
      borderRadius="lg" 
      boxShadow="md" 
      textAlign="center"
      maxW="xs"
      mx="auto"
      mb={{ base: 6, md: 0 }}
    >
      <Text fontSize="4xl" mb={4}>
        {iconUrl}
      </Text>
      <Heading as="h3" size="md" mb={2}>
        {title}
      </Heading>
      <Text color="gray.600">
        {description}
      </Text>
    </Box>
  );
};

export default HomePage;
