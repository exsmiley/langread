import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  Text,
  VStack,
  Heading
} from '@chakra-ui/react';

interface ArticlePreviewProps {
  content: string;
  truncateLength?: number;
}

/**
 * ArticlePreview component that displays the article content with a toggle option
 * to show the full text or a truncated preview.
 */
const ArticlePreview: React.FC<ArticlePreviewProps> = ({ 
  content, 
  truncateLength = 500 // Default to 500 characters, which should show several paragraphs
}) => {
  const [showFullContent, setShowFullContent] = useState(false);
  
  // Don't truncate if content is already short
  const shouldTruncate = content.length > truncateLength;
  
  // Prepare displayed content - either full or truncated
  const displayedContent = showFullContent || !shouldTruncate 
    ? content 
    : content.substring(0, truncateLength);
  
  return (
    <VStack align="stretch" spacing={4}>
      <Box whiteSpace="pre-wrap">
        <Text lineHeight="taller">
          {displayedContent}
          {!showFullContent && shouldTruncate && '...'}
        </Text>
      </Box>
      
      {shouldTruncate && (
        <Button 
          onClick={() => setShowFullContent(!showFullContent)}
          colorScheme="blue"
          variant="outline"
          size="sm"
          alignSelf="flex-start"
        >
          {showFullContent ? 'Show Less' : 'Toggle Content Preview'}
        </Button>
      )}
    </VStack>
  );
};

export default ArticlePreview;
