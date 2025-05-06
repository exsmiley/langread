import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  Grid,
  GridItem,
  Button,
  VStack,
  HStack,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Divider,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  SimpleGrid,
  useToast,
  Spinner,
  Code,
  Badge,
  Alert,
  AlertIcon,
  AlertDescription,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '../api';

const AdminDashboardPage: React.FC = () => {
  const { t } = useTranslation();
  const [cacheStats, setCacheStats] = useState<any>(null);
  const [cachedQueries, setCachedQueries] = useState<any[]>([]);
  const [bulkFetchStatus, setBulkFetchStatus] = useState<any>(null);
  const [bulkFetchId, setBulkFetchId] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [fetchInProgress, setFetchInProgress] = useState<boolean>(false);
  const toast = useToast();
  
  // Load cache stats on component mount
  useEffect(() => {
    fetchCacheStats();
    fetchCachedQueries();
  }, []);
  
  const fetchCacheStats = async () => {
    try {
      setLoading(true);
      const response = await api.get('/cache/stats');
      setCacheStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching cache stats:', error);
      toast({
        title: 'Error',
        description: 'Could not fetch cache statistics',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setLoading(false);
    }
  };
  
  const fetchCachedQueries = async () => {
    try {
      const response = await api.get('/cache/queries');
      setCachedQueries(response.data.queries || []);
    } catch (error) {
      console.error('Error fetching cached queries:', error);
    }
  };
  
  // Helper function to format bytes to human-readable format
  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };
  
  // Calculate cache hit rate
  const calculateHitRate = () => {
    if (!cacheStats) return 0;
    const total = (cacheStats.hits || 0) + (cacheStats.misses || 0);
    if (total === 0) return 0;
    return Math.round((cacheStats.hits / total) * 100);
  };

  const fetchBulkStatus = async () => {
    if (!bulkFetchId) {
      toast({
        title: 'Error',
        description: 'No bulk fetch ID provided',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    try {
      const response = await api.get(`/bulk-fetch-status/${bulkFetchId}`);
      setBulkFetchStatus(response.data);
    } catch (error) {
      console.error('Error fetching bulk status:', error);
      toast({
        title: 'Error',
        description: 'Could not fetch bulk operation status',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const startBulkFetch = async (language: string) => {
    try {
      setFetchInProgress(true);
      const response = await api.post('/bulk-fetch', {
        language: language,
        fetch_only: false,
        process_steps: ["fetch", "aggregate", "rewrite"]
      });
      
      setBulkFetchId(response.data.operation_id);
      toast({
        title: 'Success',
        description: `Bulk fetch started with ID: ${response.data.operation_id}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      // Automatically fetch status after starting
      setTimeout(fetchBulkStatus, 2000);
    } catch (error) {
      console.error('Error starting bulk fetch:', error);
      toast({
        title: 'Error',
        description: 'Could not start bulk fetch operation',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setFetchInProgress(false);
    }
  };
  
  const clearCache = async () => {
    try {
      await api.post('/cache/clear');
      toast({
        title: 'Cache Cleared',
        description: 'The article cache has been cleared',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      fetchCacheStats();
      fetchCachedQueries();
    } catch (error) {
      console.error('Error clearing cache:', error);
      toast({
        title: 'Error',
        description: 'Could not clear cache',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Box p={5}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading as="h1" size="xl">{t('admin.dashboard')}</Heading>
          <Text color="gray.600">{t('admin.dashboardDescription')}</Text>
        </Box>

        <Tabs variant="enclosed">
          <TabList>
            <Tab>System Status</Tab>
            <Tab>{t('admin.bulkOperations')}</Tab>
            <Tab>{t('admin.cacheManagement')}</Tab>
          </TabList>

          <TabPanels>
            <TabPanel>
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={5}>
                <Card>
                  <CardHeader>
                    <Heading size="md">{t('admin.functions')}</Heading>
                  </CardHeader>
                  <CardBody>
                    <VStack align="stretch" spacing={4}>
                      <Button as={RouterLink} to="/admin/tags" colorScheme="blue">
                        {t('admin.tagManager')}
                      </Button>
                      <Button onClick={() => startBulkFetch("all")} colorScheme="green" isLoading={fetchInProgress}>
                        Start Bulk Fetch (All Languages)
                      </Button>
                      <Button onClick={clearCache} colorScheme="red">
                        {t('admin.clearCache')}
                      </Button>
                    </VStack>
                  </CardBody>
                </Card>

                <Card>
                  <CardHeader>
                    <Heading size="md">{t('admin.cacheStatistics')}</Heading>
                  </CardHeader>
                  <CardBody>
                    {loading ? (
                      <Spinner />
                    ) : cacheStats ? (
                      <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                        <Stat>
                          <StatLabel>Cache Hits</StatLabel>
                          <StatNumber>{cacheStats.hits}</StatNumber>
                        </Stat>
                        <Stat>
                          <StatLabel>Cache Misses</StatLabel>
                          <StatNumber>{cacheStats.misses}</StatNumber>
                        </Stat>
                        <Stat>
                          <StatLabel>Queries</StatLabel>
                          <StatNumber>{cacheStats.total_queries || 0}</StatNumber>
                        </Stat>
                        <Stat>
                          <StatLabel>Articles</StatLabel>
                          <StatNumber>{cacheStats.total_articles || 0}</StatNumber>
                        </Stat>
                      </Grid>
                    ) : (
                      <Text>{t('admin.noCacheStats')}</Text>
                    )}
                  </CardBody>
                </Card>

                <Card>
                  <CardHeader>
                    <Heading size="md">{t('admin.apiEndpoints')}</Heading>
                  </CardHeader>
                  <CardBody>
                    <VStack align="stretch" spacing={2}>
                      <Text fontWeight="bold">{t('admin.backendApi')}</Text>
                      <Code p={2} borderRadius="md">http://localhost:8000</Code>
                      
                      <Text fontWeight="bold" mt={2}>{t('admin.documentationLabel')}</Text>
                      <Button as="a" href="http://localhost:8000/docs" target="_blank" size="sm" colorScheme="blue">
                        {t('admin.openapiDocs')}
                      </Button>
                    </VStack>
                  </CardBody>
                </Card>
              </SimpleGrid>
            </TabPanel>

            <TabPanel>
              <Box>
                <Heading size="md" mb={4}>{t('admin.bulkOperations')}</Heading>
                
                <Card mb={5}>
                  <CardHeader>
                    <Heading size="md">{t('admin.startNewBulkFetch')}</Heading>
                  </CardHeader>
                  <CardBody>
                    <Text mb={3}>{t('admin.selectLanguageToFetch')}</Text>
                    <HStack spacing={4}>
                      <Button onClick={() => startBulkFetch("ko")} colorScheme="blue" isLoading={fetchInProgress}>
                        Korean (ko)
                      </Button>
                      <Button onClick={() => startBulkFetch("en")} colorScheme="green" isLoading={fetchInProgress}>
                        English (en)
                      </Button>
                      <Button onClick={() => startBulkFetch("all")} colorScheme="purple" isLoading={fetchInProgress}>
                        All Languages
                      </Button>
                    </HStack>
                  </CardBody>
                </Card>
                
                <Card>
                  <CardHeader>
                    <Heading size="md">{t('admin.bulkFetchStatus')}</Heading>
                  </CardHeader>
                  <CardBody>
                    <HStack spacing={4} mb={4}>
                      <Button onClick={fetchBulkStatus} colorScheme="blue" isDisabled={!bulkFetchId}>
                        {t('admin.checkStatus')}
                      </Button>
                      <Text>Current Operation ID: {bulkFetchId || "None"}</Text>
                    </HStack>
                    
                    {bulkFetchStatus ? (
                      <VStack align="start" spacing={3}>
                        <HStack>
                          <Text fontWeight="bold">{t('admin.status')}</Text>
                          <Badge colorScheme={
                            bulkFetchStatus.status === "completed" ? "green" : 
                            bulkFetchStatus.status === "failed" ? "red" : "yellow"
                          }>
                            {bulkFetchStatus.status}
                          </Badge>
                        </HStack>
                        
                        <HStack>
                          <Text fontWeight="bold">{t('admin.progressLabel')}</Text>
                          <Text>{bulkFetchStatus.completed_steps || 0} / {bulkFetchStatus.total_steps || 0} steps</Text>
                        </HStack>
                        
                        <Box w="100%">
                          <Text fontWeight="bold" mb={2}>{t('admin.messages')}</Text>
                          <Box p={3} bg="gray.50" borderRadius="md" maxH="200px" overflowY="auto">
                            {bulkFetchStatus.messages?.map((msg: string, i: number) => (
                              <Text key={i} fontSize="sm" mb={1}>{msg}</Text>
                            )) || <Text>{t('admin.noMessagesAvailable')}</Text>}
                          </Box>
                        </Box>
                      </VStack>
                    ) : (
                      <Alert status="info">
                        <AlertIcon />
                        <AlertDescription>{t('admin.enterOperationIdAndCheckStatus')}</AlertDescription>
                      </Alert>
                    )}
                  </CardBody>
                </Card>
              </Box>
            </TabPanel>

            <TabPanel>
              <Box>
                <Heading size="md" mb={4}>{t('admin.cacheManagement')}</Heading>
                
                <Card mb={5}>
                  <CardHeader>
                    <Heading size="md">{t('admin.cachedQueries')}</Heading>
                  </CardHeader>
                  <CardBody>
                    <Box maxH="300px" overflowY="auto">
                      {cachedQueries.length > 0 ? (
                        <VStack align="stretch" spacing={2}>
                          {cachedQueries.map((query, index) => (
                            <Card key={index} size="sm" variant="outline">
                              <CardBody>
                                <Grid templateColumns="repeat(3, 1fr)" gap={2}>
                                  <Box>
                                    <Text fontWeight="bold">{t('admin.query')}:</Text>
                                    <Text>{query.query}</Text>
                                  </Box>
                                  <Box>
                                    <Text fontWeight="bold">{t('admin.language')}:</Text>
                                    <Badge>{query.language}</Badge>
                                  </Box>
                                  <Box>
                                    <Text fontWeight="bold">{t('admin.articles')}:</Text>
                                    <Badge colorScheme="blue">{query.article_count}</Badge>
                                  </Box>
                                </Grid>
                              </CardBody>
                            </Card>
                          ))}
                        </VStack>
                      ) : (
                        <Text>{t('admin.noCachedQueries')}</Text>
                      )}
                    </Box>
                  </CardBody>
                  <CardFooter>
                    <Button onClick={clearCache} colorScheme="red" size="sm">{t('admin.clearAllCache')}</Button>
                  </CardFooter>
                </Card>
                
                <Card>
                  <CardHeader>
                    <Heading size="md">{t('admin.cacheInfo')}</Heading>
                  </CardHeader>
                  <CardBody>
                    <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                      <Box>
                        <Text fontWeight="bold">{t('admin.totalSize')}:</Text>
                        <Text>{formatBytes(cacheStats?.size || 0)}</Text>
                      </Box>
                      <Box>
                        <Text fontWeight="bold">{t('admin.hitRate')}</Text>
                        <Text>
                          {cacheStats ? 
                            `${Math.round((cacheStats.hits / (cacheStats.hits + cacheStats.misses || 1)) * 100)}%` : 
                            'Unknown'}
                        </Text>
                      </Box>
                    </Grid>
                  </CardBody>
                </Card>
              </Box>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>
    </Box>
  );
};

export default AdminDashboardPage;
