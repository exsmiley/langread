"""
Agent-based content fetcher that can search and scrape content on any topic in any language.
Uses LLM to guide the search and extraction process.
"""
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import logging
import re
import time
import random
import asyncio
from urllib.parse import urlparse, urljoin
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool, StructuredTool
from langchain.schema import SystemMessage
from pydantic import BaseModel, Field
import requests
import aiohttp
from bs4 import BeautifulSoup, NavigableString
import json
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# For RSS feeds
import feedparser

# For better article extraction
from newspaper import Article as NewspaperArticle
from newspaper import Config as NewspaperConfig

# For Google search (if needed as fallback)
from googleapiclient.discovery import build

# Configure logging
from loguru import logger

class SearchResult(BaseModel):
    """Model for search results"""
    title: str
    url: str
    snippet: str
    relevance: float = 0.0


class ContentSection(BaseModel):
    """Model for content sections"""
    type: str
    content: str
    caption: Optional[str] = None
    order: int


class ArticleContent(BaseModel):
    """Model for article content"""
    title: str
    url: str
    source: str
    language: str
    date_published: Optional[datetime] = None
    content: List[ContentSection]
    topics: List[str]


class GroupedArticleContent(BaseModel):
    """Model for grouped and rewritten article content"""
    title: str
    language: str
    date_created: datetime = Field(default_factory=datetime.now)
    content: List[ContentSection]
    topics: List[str]
    difficulty_level: str
    source_articles: List[str]  # List of source article IDs or URLs
    key_vocabulary: List[Dict[str, str]] = []  # List of important vocabulary with definitions


class ContentAgent:
    """
    Agent that can search for and extract content on any topic in any language.
    Uses LLM to guide the search and extraction process for any target language.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, model_name: str = "gpt-4.1-nano"):
        """
        Initialize the agent with necessary components
        
        Args:
            openai_api_key: OpenAI API key (if None, will try to get from environment)
            model_name: OpenAI model to use (default: gpt-4.1-nano)
        """
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it as an argument or as OPENAI_API_KEY environment variable.")
        
        try:
            # Initialize the LLM
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                api_key=self.api_key,
                request_timeout=60,  # Increased timeout for complex queries
                max_retries=3  # Add retries for transient errors
            )
            
            # Initialize tools
            self.tools = self._create_tools()
            
            # Initialize the agent
            self.agent = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
                system_message=SystemMessage(content="""
                You are an expert content researcher and extractor for language learning purposes. Your job is to:
                1. Search for high-quality content based on the user's query and target language
                2. Select the most relevant, authentic, and comprehensive sources
                3. Extract the content while preserving its structure (text, images, etc.)
                4. Remove any ads or irrelevant content
                5. Return the cleaned and structured content that would be valuable for a language learner
                
                Be thorough and make sure to capture all relevant content from the source.
                Preserve images and their captions when they are part of the content.
                For language learning, prioritize authentic content from native sources.
                """)
            )
            
            logger.info("ContentAgent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ContentAgent: {str(e)}")
            raise
    
    def _create_tools(self) -> List[BaseTool]:
        """Create the tools for the agent"""
        
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
        def search_web(query: str, language: str = "en", min_relevance: float = 0.25, fetch_all: bool = False) -> List[SearchResult]:
            """
            Search the web for content based on query and language.
            Primary method: RSS feeds from major news sources
            Fallback: Google Custom Search API if available
            
            Args:
                query: Search query
                language: Language code (e.g., 'en', 'ko', 'es')
                
            Returns:
                List of search results
            """
            logger.info(f"Searching for: {query} in language: {language}")
            
            # Maps language codes to RSS feeds of major news sources
            rss_feeds = {
                "ko": [
                    # Korean technology news sources - prioritized for tech queries
                    "https://www.etnews.com/rss/rss.xml",                           # Electronic Times
                    "https://feeds.feedburner.com/bloter",                           # Bloter.net
                    "https://www.itworld.co.kr/rss/feed/idx/5",                     # IT World Korea
                    "https://rss.zdnet.co.kr/section/news.xml",                      # ZDNet Korea
                    "https://feeds.feedburner.com/venturesquare",                   # Venture Square (Tech Startup News)
                    "https://www.aitimes.com/rss/allArticle.xml",                   # AI Times Korea
                    
                    # General Korean news sources
                    "https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml",  # Chosun Ilbo
                    "https://www.hani.co.kr/rss/",                                   # Hankyoreh
                    "https://www.khan.co.kr/rss/rssdata/total_news.xml",            # Kyunghyang Shinmun
                    "https://www.ytn.co.kr/feed/index.php",                          # YTN
                    "https://rss.donga.com/total.xml",                               # Dong-A Ilbo
                    "https://www.mk.co.kr/rss/40300001/",                           # Maeil Business
                ],
                "en": [
                    # English news sources
                    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",        # New York Times
                    "https://feeds.bbci.co.uk/news/world/rss.xml",                   # BBC
                    "https://www.theguardian.com/world/rss",                         # The Guardian
                    "https://feeds.washingtonpost.com/rss/world",                    # Washington Post
                ],
                # Add more languages as needed
            }
            
            # Get RSS feeds for the requested language (or default to English)
            language_feeds = rss_feeds.get(language, rss_feeds.get("en"))
            
            results = []
            
            # Try RSS feeds first
            if language_feeds:
                for feed_url in language_feeds:
                    try:
                        feed = feedparser.parse(feed_url)
                        
                        # Filter entries by query if provided
                        for entry in feed.entries[:20]:  # Limit to first 20 entries for efficiency
                            title = entry.get('title', '')
                            description = entry.get('description', '') or entry.get('summary', '')
                            content = ''
                            
                            # Extract content if available
                            if 'content' in entry:
                                for content_item in entry.content:
                                    if 'value' in content_item:
                                        content += content_item.value
                            
                            # Advanced matching for Korean language
                            match_score = 0
                            max_score = 0
                            
                            # Break query into terms for better matching
                            query_terms = [term.strip() for term in query.split() if term.strip()]
                            max_score = len(query_terms) * 2  # Maximum possible score
                            
                            # Score based on presence of query terms in title (highest weight)
                            for term in query_terms:
                                if term.lower() in title.lower():
                                    match_score += 2
                            
                            # Score based on presence of query terms in description/content
                            for term in query_terms:
                                if (term.lower() in description.lower() or term.lower() in content.lower()):
                                    match_score += 1
                            
                            # Calculate relevance percentage
                            relevance = (match_score / max_score) if max_score > 0 else 0
                            
                            # Include all results if fetch_all is True, otherwise filter by relevance
                            if fetch_all or relevance > min_relevance:
                                url = entry.get('link', '')
                                if url:  # Only add if URL exists
                                    # Clean up description - remove HTML
                                    soup = BeautifulSoup(description, 'html.parser')
                                    clean_description = soup.get_text()
                                    
                                    # Store the result with its relevance score for sorting later
                                    results.append(SearchResult(
                                        title=title,
                                        url=url,
                                        snippet=f"[Relevance: {relevance:.2f}] " + clean_description[:200] + "..."
                                    ))
                    except Exception as e:
                        logger.error(f"Error parsing RSS feed {feed_url}: {str(e)}")
            
            # If we don't have enough results from RSS or searching for tech topics, try Google Search API if available
            tech_related = any(term in query.lower() for term in ["기술", "테크", "tech", "technology", "트렌드", "trends", "it", "ai", "인공지능"])
            
            if (len(results) < 5 or tech_related) and os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_CSE_ID"):
                try:
                    # Use Google Custom Search API
                    service = build("customsearch", "v1", developerKey=os.getenv("GOOGLE_API_KEY"))
                    
                    # Customize search parameters based on the query type
                    search_params = {
                        "q": query,
                        "cx": os.getenv("GOOGLE_CSE_ID"),
                        "lr": f"lang_{language}",  # Language restriction
                        "num": 8  # More results for better filtering
                    }
                    
                    # Add tech-specific search parameters for tech queries
                    if tech_related and language == "ko":
                        search_params["sort"] = "date"  # Get latest articles
                        # Add tech sites to search
                        search_params["siteSearch"] = "zdnet.co.kr OR etnews.com OR bloter.net OR itworld.co.kr"
                    
                    res = service.cse().list(**search_params).execute()
                    
                    search_items = res.get("items", [])
                    for item in search_items:
                        # Use a relevance score of 0.75 (higher than RSS threshold) for Google results
                        results.append(SearchResult(
                            title=item.get("title", ""),
                            url=item.get("link", ""),
                            snippet=f"[Relevance: 0.75] " + item.get("snippet", "")
                        ))
                except Exception as e:
                    logger.error(f"Error using Google Custom Search: {str(e)}")
            
            # If still no results, create some default ones based on common news sites in that language
            if len(results) == 0:
                default_sites = {
                    "ko": [
                        ("https://www.chosun.com", "조선일보"),
                        ("https://www.hani.co.kr", "한겨레"),
                    ],
                    "en": [
                        ("https://www.bbc.com/news/world", "BBC World News"),
                        ("https://www.nytimes.com/section/world", "New York Times World News"),
                    ]
                }
                
                sites = default_sites.get(language, default_sites["en"])
                for site_url, site_name in sites:
                    results.append(SearchResult(
                        title=f"{site_name}: {query}",
                        url=site_url,
                        snippet=f"Find articles about {query} on {site_name}"
                    ))
            
            # Deduplicate results by URL
            unique_results = []
            seen_urls = set()
            for result in results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    unique_results.append(result)
            
            # Add initial relevance scores from keyword matching
            for result in unique_results:
                snippet = result.snippet
                match = re.search(r'\[Relevance: ([0-9.]+)\]', snippet)
                keyword_relevance = float(match.group(1)) if match else 0.0
                result.relevance = keyword_relevance
                # Clean up the snippet
                result.snippet = re.sub(r'\[Relevance: [0-9.]+\] ', '', result.snippet)
            
            # Use LLM for relevance checking if we have enough results
            if os.getenv("OPENAI_API_KEY") and len(unique_results) > 1:
                try:
                    # Use the lightweight nano model for relevance scoring
                    llm = ChatOpenAI(
                        model="gpt-4.1-nano",
                        temperature=0,
                        api_key=os.getenv("OPENAI_API_KEY")
                    )
                    
                    # Prepare the article data for the LLM
                    articles_for_scoring = []
                    for i, result in enumerate(unique_results):
                        articles_for_scoring.append({
                            "id": i,
                            "title": result.title,
                            "snippet": result.snippet
                        })
                    
                    # Prepare the prompt for scoring relevance
                    prompt = f"""
                    You are evaluating the relevance of articles to a search query.
                    
                    QUERY: "{query}" (language: {language})
                    
                    ARTICLES TO EVALUATE:
                    {json.dumps(articles_for_scoring, ensure_ascii=False, indent=2)}
                    
                    Please rate the relevance of each article to the query on a scale of 0.0 to 1.0,
                    where 1.0 means extremely relevant and 0.0 means completely irrelevant.
                    
                    Respond with ONLY a JSON array of objects with each object having the id and the relevance score.
                    Example: [{{"id": 0, "relevance": 0.8}}, {{"id": 1, "relevance": 0.3}}]
                    """
                    
                    response = llm.predict(prompt)
                    
                    # Parse the response
                    try:
                        relevance_scores = json.loads(response)
                        
                        # Add the relevance scores to the results
                        id_to_score = {item["id"]: item["relevance"] for item in relevance_scores}
                        for i, result in enumerate(unique_results):
                            result.relevance = id_to_score.get(i, result.relevance)  # Fall back to keyword score if missing
                            
                        logger.info(f"LLM relevance scores: {relevance_scores}")
                    except json.JSONDecodeError:
                        # If parsing fails, fall back to the keyword-based ranking
                        logger.warning(f"Failed to parse LLM relevance scores: {response}")
                except Exception as e:
                    logger.warning(f"Error using LLM for relevance ranking: {str(e)}")
            
            # Sort by relevance score (highest first)
            unique_results.sort(key=lambda r: getattr(r, 'relevance', 0.0), reverse=True)
            
            return unique_results[:10]  # Return top 10 results
        
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10),
              retry=retry_if_exception_type((requests.RequestException, ConnectionError)))
        def extract_content(url: str) -> ArticleContent:
            """
            Extract content from a URL using a combination of newspaper3k and BeautifulSoup
            for robust article extraction.
            
            Args:
                url: URL to extract content from
                
            Returns:
                Extracted and structured content
            """
            logger.info(f"Extracting content from: {url}")
            
            try:
                # Configure newspaper with browser user-agent to avoid blocks
                config = NewspaperConfig()
                config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'
                config.request_timeout = 10
                
                # Extract with newspaper3k
                article = NewspaperArticle(url, config=config)
                article.download()
                article.parse()
                
                # Get the main metadata
                title = article.title
                source = urlparse(url).netloc.replace('www.', '')
                date_published = article.publish_date or datetime.now()
                
                # Detect language from HTML or URL
                # If we couldn't download or parse, we may not have language info
                if not article.text:
                    # Attempt a direct request
                    headers = {'User-Agent': config.browser_user_agent}
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Look for language in HTML tag
                        html_tag = soup.find('html')
                        if html_tag and html_tag.get('lang'):
                            language = html_tag.get('lang').split('-')[0]
                        else:
                            # Default based on domain
                            tld = urlparse(url).netloc.split('.')[-1]
                            language = 'ko' if tld == 'kr' else 'en'
                    else:
                        language = 'en'  # Default
                else:
                    # Detect language from HTML meta tags
                    language = article.meta_lang or 'en'
                    # Cross-check with URL TLD as a hint
                    tld = urlparse(url).netloc.split('.')[-1]
                    if language == 'en' and tld == 'kr':
                        language = 'ko'  # Override if strong indication from domain
                
                # Extract content sections
                content_sections = []
                order = 0
                
                # We'll re-parse with BeautifulSoup to get better structure
                if article.html:
                    soup = BeautifulSoup(article.html, 'html.parser')
                    
                    # Remove common non-content elements
                    for element in soup.select('nav, footer, aside, .comments, .advertisement, script, style'):
                        element.decompose()
                    
                    # Get the main content area
                    main_content = soup.select_one('main, article, .article, .content, .post, #content, .story')
                    if not main_content:
                        main_content = soup  # Use the entire document if we can't find a content area
                    
                    # Extract headings and paragraphs
                    for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'img']):
                        if element.name.startswith('h') and element.get_text().strip():
                            # Add heading
                            heading_text = element.get_text().strip()
                            if heading_text and heading_text != title:  # Skip if it's the main title
                                content_sections.append(
                                    ContentSection(
                                        type="heading",
                                        content=heading_text,
                                        order=order
                                    )
                                )
                                order += 1
                        elif element.name == 'p' and element.get_text().strip():
                            # Add paragraph text
                            content_sections.append(
                                ContentSection(
                                    type="text",
                                    content=element.get_text().strip(),
                                    order=order
                                )
                            )
                            order += 1
                        elif element.name == 'img' and element.get('src'):
                            # Add image
                            img_url = element.get('src')
                            if not img_url.startswith(('http://', 'https://')):
                                img_url = urljoin(url, img_url)
                            
                            caption = ""
                            # Check for caption in figcaption or alt text
                            if element.parent and element.parent.name == 'figure':
                                figcaption = element.parent.find('figcaption')
                                if figcaption:
                                    caption = figcaption.get_text().strip()
                            
                            if not caption and element.get('alt'):
                                caption = element.get('alt')
                                
                            content_sections.append(
                                ContentSection(
                                    type="image",
                                    content=img_url,
                                    caption=caption,
                                    order=order
                                )
                            )
                            order += 1
                
                # If we couldn't extract structured content, use the raw text
                if not content_sections and article.text:
                    paragraphs = [p for p in article.text.split('\n\n') if p.strip()]
                    for i, paragraph in enumerate(paragraphs):
                        content_sections.append(
                            ContentSection(
                                type="text",
                                content=paragraph.strip(),
                                order=i
                            )
                        )
                
                # If still empty, we need a fallback
                if not content_sections:
                    content_sections.append(
                        ContentSection(
                            type="text",
                            content="The content could not be extracted from this webpage. It may be paywalled or use JavaScript to load content.",
                            order=0
                        )
                    )
                
                # Use LLM to extract topics if we have enough content
                topics = []
                
                if article.text and len(article.text) > 100:
                    try:
                        # Create a small LLM call to extract topics
                        # We'll use a synchronous version since we're in a non-async function
                        llm = ChatOpenAI(
                            model="gpt-4.1-nano",  # Use the lightweight nano model for efficiency
                            temperature=0,
                            api_key=os.getenv("OPENAI_API_KEY"),
                            max_tokens=50  # Keep it small to save tokens
                        )
                        
                        # Get a sample of the text (first 1000 chars) to save tokens
                        sample_text = article.text[:1000] + ("..." if len(article.text) > 1000 else "")
                        
                        prompt = f"""Extract 3-5 topic keywords from this {language} article. 
                        Return only a comma-separated list of lowercase keywords, no explanation:
                        
                        Title: {title}
                        
                        Text sample: {sample_text}
                        """
                        
                        response = llm.predict(prompt)
                        topic_list = response.strip().split(",")
                        topics = [topic.strip().lower() for topic in topic_list if topic.strip()]
                    except Exception as e:
                        logger.warning(f"Failed to extract topics with LLM: {str(e)}")
                
                # If LLM extraction failed or there's not enough content, fall back to simpler methods
                if not topics and article.meta_keywords:
                    # Try meta tags
                    topics = [k.strip() for k in article.meta_keywords.split(',')]
                
                # If still no topics, use simpler heuristics
                if not topics:
                    # Try to identify topics from the title
                    title_words = re.findall(r'\b\w{3,}\b', title.lower())
                    common_words = ['the', 'and', 'that', 'this', 'with', 'from']
                    topics = [w for w in title_words if w not in common_words][:3]
                    
                    # Add source as a topic
                    if source:
                        topics.append(source.split('.')[0])
                    
                    # Make sure we have at least one topic
                    if not topics:
                        topics = ["news", "article"]
                
                # Create article content
                article_content = ArticleContent(
                    title=title,
                    url=url,
                    source=source,
                    language=language,
                    date_published=date_published,
                    content=content_sections,
                    topics=topics
                )
                
                return article_content
            except Exception as e:
                logger.error(f"Error extracting content from {url}: {str(e)}")
                raise
        
        tools = [
            StructuredTool.from_function(
                func=search_web,
                name="search_web",
                description="Search the web for content based on a query and language"
            ),
            StructuredTool.from_function(
                func=extract_content,
                name="extract_content",
                description="Extract content from a URL"
            )
        ]
        
        return tools
    
    async def get_content(self, 
                         query: str, 
                         language: str = "en", 
                         topic_type: str = "news",
                         max_sources: int = 3,
                         group_and_rewrite: bool = False) -> List[ArticleContent]:
        """
        Get content based on query, language, and content type
        
        Args:
            query: Search query or topic
            language: Language code
            topic_type: Type of content to search for (news, blog, educational, etc.)
            max_sources: Maximum number of sources to fetch
            
        Returns:
            List of article content objects
        """
        prompt = f"""
        Find {max_sources} high-quality {topic_type} articles or content pieces about "{query}" in {language} language.
        For each article:
        1. First search for relevant content
        2. Select the most appropriate sources
        3. Extract the full content
        4. Structure it with proper headings, text, and images
        5. Remove any ads or irrelevant content
        
        Return all results in a well-structured format.
        """
        
        try:
            # Run the agent
            result = await self.agent.ainvoke({"input": prompt})
            
            # In a real implementation, we'd parse the agent's response
            # and convert it to the expected format
            
            # Step a: Find relevant sources through search
            search_results = await asyncio.to_thread(
                self.tools[0].func,  # search_web function
                query=query,
                language=language
            )
            
            # Step b: Use asyncio to concurrently extract content from all sources
            articles = []
            
            if search_results:
                # Process content extraction concurrently
                async def extract_and_process(search_result):
                    try:
                        article_content = await asyncio.to_thread(
                            self.tools[1].func,  # extract_content function
                            url=search_result.url
                        )
                        return article_content
                    except Exception as e:
                        logger.error(f"Error extracting content from {search_result.url}: {str(e)}")
                        return None
                
                # Extract content from search results concurrently
                tasks = [extract_and_process(result) for result in search_results[:max_sources]]
                article_contents = await asyncio.gather(*tasks)
                
                # Filter out None results (failed extractions)
                articles = [article for article in article_contents if article is not None]
            
            # If group_and_rewrite is True, process the articles
            if group_and_rewrite and len(articles) > 0:
                return await self.group_and_rewrite_articles(articles, language)
            
            return articles
        except Exception as e:
            logger.error(f"Error getting content: {str(e)}")
            raise
            
    async def group_and_rewrite_articles(self, 
                                       articles: List[ArticleContent], 
                                       language: str,
                                       target_difficulty: str = "intermediate") -> List[ArticleContent]:
        """
        Group related articles and use LLM to rewrite them into a cohesive, educational format
        
        Args:
            articles: List of articles to process
            language: Target language code
            target_difficulty: Desired difficulty level (beginner, intermediate, advanced)
            
        Returns:
            A list containing a single rewritten article that synthesizes the input articles
        """
        if not articles:
            return []
        
        try:
            # Step 1: Extract all content from articles as context
            article_texts = []
            topics = set()
            sources = []
            
            for article in articles:
                # Extract the full text content
                article_text = f"Title: {article.title}\n\n"
                for section in article.content:
                    if section.type == "heading":
                        article_text += f"## {section.content}\n\n"
                    elif section.type == "text":
                        article_text += f"{section.content}\n\n"
                    # Skip images in the context, but we'll reference them later
                
                article_texts.append(article_text)
                topics.update(article.topics)
                sources.append(article.url)
            
            # Step 2: Create a prompt for the LLM to rewrite the content
            context = "\n\n---\n\n".join(article_texts)
            difficulty_descriptions = {
                "beginner": "Use simple sentence structures and vocabulary. Focus on high-frequency words and basic grammar patterns.",
                "intermediate": "Use moderate complexity in sentences and incorporate some topic-specific vocabulary with explanations.",
                "advanced": "Use natural, native-level language with rich vocabulary and complex sentence structures."
            }
            
            difficulty_instruction = difficulty_descriptions.get(target_difficulty, difficulty_descriptions["intermediate"])
            
            prompt = f"""
            You are an expert language teacher creating educational content for language learners.
            
            I'm providing several articles on a similar topic. Your task is to create ENTIRELY NEW CONTENT that:
            
            1. Completely rewrites and transforms the information from these articles into ONE cohesive, educational piece for {language} language learners at a {target_difficulty} level.
            2. AVOIDS DIRECT COPYING of phrases or sentences from the original articles to prevent copyright issues.
            3. {difficulty_instruction}
            4. Presents the core facts and concepts in your own original language and structure.
            5. Includes citation notes at the end acknowledging the original sources but DOES NOT reproduce their exact content.
            6. Identify and highlight 5-10 key vocabulary items that would be valuable for learners.
            7. For each vocabulary item, provide a brief, clear definition in {language}.
            8. Structure the content with clear sections including an introduction and conclusion.
            9. Make the content engaging, educational, and substantially different from the original sources.
            
            Format your response as follows:
            TITLE: [Engaging title for the article - make this completely original]
            
            CONTENT: [The full article content with proper sections - COMPLETELY REWRITTEN in your own words]
            
            KEY_VOCABULARY:
            - word1: definition1
            - word2: definition2
            
            The articles to synthesize are:
            {context}
            """
            
            # Step 3: Use the LLM to rewrite the content
            response = await self.llm.ainvoke(prompt)
            response_text = response.content
            
            # Step 4: Parse the LLM response into structured content
            try:
                # Extract title
                title_match = None
                if "TITLE:" in response_text:
                    title_parts = response_text.split("TITLE:", 1)
                    if len(title_parts) > 1:
                        title_candidate = title_parts[1].strip().split("\n", 1)[0].strip()
                        if title_candidate:
                            title_match = title_candidate
                
                title = title_match or f"Article about {', '.join(list(topics)[:3])}"
                
                # Extract content sections
                content_sections = []
                content_match = None
                if "CONTENT:" in response_text:
                    content_parts = response_text.split("CONTENT:", 1)
                    if len(content_parts) > 1:
                        content_candidate = content_parts[1]
                        if "KEY_VOCABULARY:" in content_candidate:
                            content_candidate = content_candidate.split("KEY_VOCABULARY:", 1)[0].strip()
                        if content_candidate:
                            content_match = content_candidate
                
                if content_match:
                    # Process the content into sections
                    lines = content_match.split("\n")
                    current_section = None
                    current_content = ""
                    order = 0
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith("#") or (line and all(c == '=' for c in line) and current_content):
                            # Save previous section if exists
                            if current_content:
                                if current_section:
                                    content_sections.append(
                                        ContentSection(
                                            type="heading",
                                            content=current_section,
                                            order=order
                                        )
                                    )
                                    order += 1
                                
                                content_sections.append(
                                    ContentSection(
                                        type="text",
                                        content=current_content.strip(),
                                        order=order
                                    )
                                )
                                order += 1
                                current_content = ""
                            
                            # Start new section
                            if line.startswith("#"):
                                current_section = line.lstrip("#").strip()
                            else:  # It's an underline heading
                                current_section = prev_line.strip()
                        else:
                            prev_line = line
                            current_content += line + "\n"
                    
                    # Add final section
                    if current_content:
                        if current_section:
                            content_sections.append(
                                ContentSection(
                                    type="heading",
                                    content=current_section,
                                    order=order
                                )
                            )
                            order += 1
                        
                        content_sections.append(
                            ContentSection(
                                type="text",
                                content=current_content.strip(),
                                order=order
                            )
                        )
                else:
                    # Fallback if we couldn't parse content properly
                    content_sections = [
                        ContentSection(
                            type="text",
                            content="Content could not be properly extracted from the LLM response.",
                            order=0
                        )
                    ]
                
                # Extract vocabulary
                vocabulary = []
                vocab_match = None
                if "KEY_VOCABULARY:" in response_text:
                    vocab_parts = response_text.split("KEY_VOCABULARY:", 1)
                    if len(vocab_parts) > 1:
                        vocab_text = vocab_parts[1].strip()
                        vocab_lines = vocab_text.split("\n")
                        
                        for line in vocab_lines:
                            line = line.strip()
                            if line.startswith("-") and ":" in line:
                                parts = line[1:].split(":", 1)
                                if len(parts) == 2:
                                    word = parts[0].strip()
                                    definition = parts[1].strip()
                                    vocabulary.append({"word": word, "definition": definition})
                
                # Create the rewritten article
                rewritten_article = ArticleContent(
                    title=title,
                    url="",  # Rewritten article doesn't have a URL
                    source="AI-generated from multiple sources",
                    language=language,
                    date_published=datetime.now(),
                    content=content_sections,
                    topics=list(topics)
                )
                
                # In a real implementation, we would tag vocabulary in the content
                # For example, adding HTML tags around vocabulary words for highlighting
                
                return [rewritten_article]
            except Exception as e:
                logger.error(f"Error parsing LLM response: {str(e)}")
                # Return a basic fallback article using the original articles
                fallback_sections = [
                    ContentSection(
                        type="heading",
                        content="Synthesized Article",
                        order=0
                    ),
                    ContentSection(
                        type="text",
                        content="This article combines information from multiple sources on the topic.",
                        order=1
                    )
                ]
                
                # Add content from original articles
                order = 2
                for i, article in enumerate(articles):
                    fallback_sections.append(
                        ContentSection(
                            type="heading",
                            content=f"Source {i+1}: {article.title}",
                            order=order
                        )
                    )
                    order += 1
                    
                    for section in article.content:
                        if section.type == "text":
                            fallback_sections.append(
                                ContentSection(
                                    type="text",
                                    content=section.content,
                                    order=order
                                )
                            )
                            order += 1
                
                return [ArticleContent(
                    title=f"Synthesized Article on {', '.join(list(topics)[:3])}",
                    url="",
                    source="AI-generated from multiple sources",
                    language=language,
                    date_published=datetime.now(),
                    content=fallback_sections,
                    topics=list(topics)
                )]
        except Exception as e:
            logger.error(f"Error in group_and_rewrite_articles: {str(e)}")
            # Return the original articles if rewriting fails
            return articles
