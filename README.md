# LangRead

A mobile-friendly web application for intermediate and advanced language learners who want to take their skills to the next level.

## Overview

LangRead helps language learners improve their skills by reading authentic native-language content. The application initially targets Korean language learners who speak English as their primary language, with potential to expand to other language pairs in the future.

## Quick Start Guide

### Prerequisites

- Python 3.9+
- Node.js 16+
- MongoDB (for database functionality)
- OpenAI API key (for the LLM agent functionality)

### Starting the System

#### 1. Setup Environment

Clone the repository and set up your environment:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/exsmiley/langread.git
cd langread

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd src/frontend
npm install
cd ../..
```

#### 2. Configure Environment Variables

Create a `.env` file in the project root with your API keys:

```
OPENAI_API_KEY=your_api_key_here
MONGODB_URI=your_mongodb_uri_here
```

#### 3. Start the Services

Start the backend server:

```bash
cd src/api
uvicorn main:app --reload --port 8000
```

In a new terminal, start the frontend server:

```bash
cd src/frontend
npm run dev
```

#### 4. Access the Application

- **Frontend:** http://localhost:5173
- **API Documentation:** http://localhost:8000/docs

### Stopping the Services

You can use the provided script to stop running services:

```bash
# Stop API server only
python kill_servers.py

# Stop all services including frontend (if needed)
python kill_servers.py --all

# Stop database services (if running locally)
python kill_servers.py --db
```

## Development Workflow

### Port Configuration

The system uses the following ports by default:

- **Backend API:** 8000
- **Frontend:** 5173
- **MongoDB:** 27017 (if running locally)

### Hot Reload

- Both the backend and frontend servers support hot reloading for development.
- The backend uses Uvicorn's `--reload` flag to watch for changes.
- The frontend uses Vite's built-in hot module replacement.

### Component Overview

- **Backend:** FastAPI server providing article fetching, processing, and API endpoints
- **Frontend:** React application with TypeScript and Vite build system
- **Database:** MongoDB for storing articles, user data, and vocabulary

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

- **Frontend**: React with TypeScript and Chakra UI for the interface
- **Backend**: Python FastAPI for the API service
  - Web scraping via newspaper3k
  - LLM-based content processing using the OpenAI API
  - RSS feed-based article discovery
- **Database**: MongoDB for storing articles, user vocabulary, and learning progress
- **Caching**: In-memory and file-based caching for article data

## API Reference

### Articles

- `POST /articles` - Get articles based on query, language, and content type
- `POST /rewrite` - Rewrite articles at specific difficulty levels
- `POST /translate` - Translate text from source language to target language
- `POST /generate-quiz` - Generate a quiz for an article
- `GET /articles/{content_type}` - Retrieve articles by content type with filters

### Cache Management

- `GET /cache/stats` - Get cache statistics
- `GET /cache/queries` - List all cached queries
- `POST /cache/clear` - Clear the entire cache

### Bulk Operations

- `POST /bulk-fetch` - Start a bulk fetch operation
- `GET /bulk-fetch/{operation_id}` - Get status of a bulk fetch operation

## Current Implementation Status

### Backend (Python/FastAPI)

- ✅ Basic API structure set up
- ✅ LLM agent-based content fetcher architecture
- ✅ Article model definition
- ✅ RSS feed-based article discovery
- ✅ Article grouping and rewriting at different difficulty levels
- ✅ Vocabulary management system
- ✅ Database integration
- ⬜ Authentication system

### Frontend (React)

- ✅ Core UI components (Navbar, Footer, etc.)
- ✅ Homepage with language/topic selection
- ✅ Article listing page
- ✅ Article view page with hover translation
- ✅ Vocabulary management page
- ✅ Flashcard UI
- ⬜ User authentication UI
- ⬜ Mobile responsiveness optimization

## Troubleshooting

### Common Issues

1. **Connection errors**: Ensure MongoDB is running if your configuration requires it
2. **API connectivity**: Verify that the API port (8000) is free and the server is running
3. **Frontend/backend communication**: Check that the frontend's API baseURL is correctly set to `http://localhost:8000`

### Logs

- Backend logs are stored in `langread.log` in the project root
- Frontend console logs can be viewed in the browser developer tools

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add some amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request
