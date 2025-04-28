import React, { Component, ErrorInfo, ReactNode } from 'react';
import { 
  Box, 
  Heading, 
  Text, 
  Button, 
  VStack, 
  Container, 
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Code
} from '@chakra-ui/react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error to console
    console.error("Uncaught error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  private handleResetError = (): void => {
    // Reset the error state to allow re-rendering
    this.setState({ hasError: false, error: null, errorInfo: null });
    // Redirect to homepage
    window.location.href = '/';
  }

  public render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      // Custom fallback UI
      if (fallback) {
        return fallback;
      }

      // Default fallback UI
      return (
        <Container maxW="container.md" py={10}>
          <Alert 
            status="error" 
            variant="subtle"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            textAlign="center"
            borderRadius="md"
            py={6}
            mb={6}
          >
            <AlertIcon boxSize="40px" mr={0} />
            <AlertTitle mt={4} mb={1} fontSize="lg">
              Something went wrong
            </AlertTitle>
            <AlertDescription maxWidth="sm">
              The application encountered an unexpected error. 
            </AlertDescription>
          </Alert>
          
          <VStack spacing={4} align="stretch">
            <Box>
              <Heading size="md" mb={2}>Error Details</Heading>
              <Code p={3} borderRadius="md" width="100%" overflow="auto" display="block" whiteSpace="pre-wrap">
                {error?.toString()}
              </Code>
            </Box>
            
            {errorInfo && (
              <Box>
                <Heading size="md" mb={2}>Component Stack</Heading>
                <Code p={3} borderRadius="md" width="100%" overflow="auto" display="block" whiteSpace="pre-wrap">
                  {errorInfo.componentStack}
                </Code>
              </Box>
            )}
            
            <Box pt={4}>
              <Button colorScheme="blue" onClick={this.handleResetError}>
                Back to Home
              </Button>
            </Box>
          </VStack>
        </Container>
      );
    }

    // Render children when there's no error
    return children;
  }
}

export default ErrorBoundary;
