# LangRead

A mobile-friendly web application for intermediate and advanced language learners who want to take their skills to the next level.

## Overview

LangRead helps language learners improve their skills by reading authentic native-language content. The application initially targets Korean language learners who speak English as their primary language, with potential to expand to other language pairs in the future.

## Key Features

### Article Aggregation Service

- **On-demand article fetching**: Users can request to see articles from various native language sources
- **Daily caching**: Articles fetched on a given day are stored to prevent repeated requests to source websites
- **Diverse sources**: Content is aggregated from multiple sources to provide variety
- **Content types**: Initially focused on news articles, with capability to expand to other content types
- **Content preservation**: Scrapes text, images, captions, and attempts to maintain the original structure
- **Ad removal**: Filters out advertisements from the original content

### Reading Enhancement Tools

- **Word/phrase translation**: Hover over words or highlight phrases to see English translations in a popup
- **Context-aware translations**: Translations consider the context of the word/phrase within the article
- **Seamless reading experience**: Native content is presented with minimal disruption to the reading flow

### Comprehension Testing

- **Auto-generated quizzes**: Multiple-choice tests generated for each article
- **Short answer options**: Additional short answer questions available
- **Evidence-based answers**: Each answer is linked to the specific section in the article it comes from
- **Immediate feedback**: Users can check their understanding as they go

### Vocabulary Management

- **Automatic vocabulary collection**: Words from viewed articles are added to the user's vocabulary bank
- **Flashcard generation**: Vocabulary items can be converted into flashcards for review
- **Topic tagging**: Words are tagged with the articles they appear in, allowing for topic-based study
- **Progress tracking**: Users can monitor their vocabulary growth over time

## Technical Architecture

- **Frontend**: Mobile-friendly responsive web interface built with a modern JavaScript framework (React, Vue, etc.)
- **Backend**: Python-based API service for article fetching, processing, and storage
  - Web scraping via BeautifulSoup/Scrapy
  - NLP processing via libraries like NLTK, spaCy, or transformers
  - API framework: FastAPI or Flask
- **Database**: MongoDB or PostgreSQL for storing articles, user vocabulary, and learning progress
- **Caching**: Redis for temporary storage and rate limiting

## Development Roadmap

### Phase 1 - Core Features
- Article aggregation and display functionality
- Basic word/phrase translation on hover/highlight
- Simple vocabulary collection

### Phase 2 - Enhanced Learning
- Quiz generation system
- Expanded vocabulary management
- Flashcard functionality

### Phase 3 - Optimization
- Performance improvements
- User experience refinements
- Support for additional language pairs

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- MongoDB (optional, can be replaced with other databases)
- Redis (optional, for caching)
- OpenAI API key (for the LLM agent functionality)

### Backend Setup

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (create a `.env` file in the project root):
   ```
   OPENAI_API_KEY=your_api_key_here
   MONGODB_URI=your_mongodb_uri_here
   ```

4. Run the FastAPI backend:
   ```bash
   cd src/api
   uvicorn main:app --reload
   ```
   The API will be available at http://localhost:8000

### Frontend Setup

1. Install the frontend dependencies:
   ```bash
   cd src/frontend
   npm install
   ```

2. Run the frontend development server:
   ```bash
   npm run start
   ```
   The frontend will be available at http://localhost:3000

## Current Implementation Status

### Backend (Python/FastAPI)

- ✅ Basic API structure set up
- ✅ LLM agent-based content fetcher architecture
- ✅ Article model definition
- ✅ Vocabulary management system
- ⬜ Database integration
- ⬜ Authentication system
- ⬜ Caching layer

### Frontend (React)

- ✅ Core UI components (Navbar, Footer, etc.)
- ✅ Homepage with language/topic selection
- ✅ Article listing page
- ✅ Article view page with hover translation
- ✅ Vocabulary management page
- ✅ Flashcard UI
- ⬜ User authentication UI
- ⬜ Mobile responsiveness optimization

## Next Steps

1. Implement the database layer for article and vocabulary storage
2. Complete the LLM agent integration with real API calls
3. Add user authentication
4. Implement vocabulary tracking across articles
5. Connect frontend and backend
6. Deploy the application

## API Reference

### Articles

- `POST /articles` - Get articles based on query, language, and content type
- `POST /translate` - Translate text from source language to target language
- `POST /generate-quiz` - Generate a quiz for an article
