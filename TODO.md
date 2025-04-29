# LangRead: TODO List

This document tracks future improvements, fixes, and features planned for the LangRead application.

## High Priority

- **Improved Translation Caching**
  - Replace in-memory cache with Redis for better persistence and scalability
  - Include `definition_lang` in the cache key to correctly differentiate translations based on definition language
  - Implement cache expiration strategy to manage memory usage

- **Database Integration**
  - Implement persistent storage of translations in MongoDB
  - Create proper indexing for efficient retrieval
  - Add admin tools to view/manage translation cache

- **Error Handling and Resilience**
  - Add proper error handling for OpenAI API rate limits and outages
  - Implement fallback translation strategies when API calls fail
  - Add proper logging for API failures and cache performance

## Medium Priority

- **Performance Optimization**
  - Optimize article preprocessing for faster loading
  - Add pagination for articles and vocabulary lists
  - Implement lazy loading for content

- **User Experience Enhancements**
  - Add pronunciation guides for vocabulary
  - Implement offline mode with local storage for saved articles
  - Add reading progress tracking

- **Language Support Expansion**
  - Add support for more language pairs beyond Korean-English
  - Improve handling of different writing systems
  - Add language-specific grammar notes

## Future Extensions

- **Community Features**
  - User accounts and profiles
  - Shared vocabulary lists
  - User-contributed example sentences and notes

- **Advanced Learning Tools**
  - Spaced repetition system for vocabulary review
  - Adaptive difficulty based on user performance
  - Grammar pattern identification and explanation

- **Content Expansion**
  - Integration with more content sources (books, videos, podcasts)
  - User-uploaded content support
  - Audio-text alignment for listening practice

## Technical Debt

- **Code Quality**
  - Add more comprehensive test coverage
  - Refactor and modularize the article processing pipeline
  - Document API endpoints more thoroughly

- **Infrastructure**
  - Set up CI/CD pipeline for automated testing and deployment
  - Create Docker containers for easier development and deployment
  - Implement proper monitoring and alerting
