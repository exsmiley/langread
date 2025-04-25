"""
Vocabulary management module for extracting, storing, and retrieving vocabulary from articles.
Uses LLM agents to understand words in context and provide comprehensive learning materials.
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from pydantic import BaseModel, Field
import os
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
import logging

# Set up logging
logger = logging.getLogger(__name__)

class WordDefinition(BaseModel):
    """Model for word definitions"""
    word: str
    part_of_speech: str
    definition: str
    example_sentence: str
    difficulty_level: str = Field(..., description="One of: beginner, intermediate, advanced")
    
class VocabularyItem(BaseModel):
    """Model for vocabulary items"""
    word: str
    language: str
    part_of_speech: Optional[str] = None
    definitions: List[WordDefinition] = Field(default_factory=list)
    translations: Dict[str, str] = Field(default_factory=dict)
    context_examples: List[Dict[str, str]] = Field(default_factory=list)
    article_references: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class VocabularyManager:
    """
    Manager for extracting, storing, and retrieving vocabulary from articles.
    Uses LLM to analyze words in context and provide comprehensive learning materials.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the vocabulary manager
        
        Args:
            openai_api_key: OpenAI API key (if None, will try to get from environment)
        """
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it as an argument or as OPENAI_API_KEY environment variable.")
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0,
            api_key=self.api_key
        )
        
    async def extract_vocabulary(self, 
                               text: str, 
                               language: str,
                               user_level: str = "intermediate",
                               max_words: int = 20) -> List[VocabularyItem]:
        """
        Extract vocabulary from text
        
        Args:
            text: The text to extract vocabulary from
            language: Language code of the text
            user_level: User's language level (beginner, intermediate, advanced)
            max_words: Maximum number of words to extract
            
        Returns:
            List of vocabulary items
        """
        try:
            # Create a prompt for the LLM
            prompt = ChatPromptTemplate.from_template(
                """You are an expert language teacher and linguist.
                
                Analyze the following text in {language} and extract {max_words} most valuable vocabulary words 
                for a {user_level} level learner.
                
                For each word:
                1. Provide the word in its base form
                2. Identify its part of speech
                3. Give its definition in English
                4. Include an example sentence from the original text
                5. Assign a difficulty level (beginner, intermediate, advanced)
                
                Text to analyze:
                {text}
                
                Identify words that would be most valuable for a {user_level} learner to expand their vocabulary.
                Focus on words that are:
                - Common enough to be useful
                - Challenging but appropriate for {user_level} level
                - Representative of the topic
                
                Respond with a structured list of vocabulary items.
                """
            )
            
            # Use an output parser to get structured output
            parser = PydanticOutputParser(pydantic_object=List[WordDefinition])
            
            # Create a chain
            chain = prompt | self.llm | parser
            
            # Run the chain
            result = await chain.ainvoke({
                "language": language,
                "text": text,
                "user_level": user_level,
                "max_words": max_words
            })
            
            # Convert to vocabulary items
            vocabulary_items = []
            for word_def in result:
                vocab_item = VocabularyItem(
                    word=word_def.word,
                    language=language,
                    part_of_speech=word_def.part_of_speech,
                    definitions=[word_def],
                    translations={"en": word_def.definition},
                    context_examples=[{"text": word_def.example_sentence, "source": "extracted"}],
                    tags=[word_def.difficulty_level],
                )
                vocabulary_items.append(vocab_item)
            
            return vocabulary_items
        except Exception as e:
            logger.error(f"Error extracting vocabulary: {str(e)}")
            raise

    async def get_word_details(self, 
                             word: str, 
                             language: str,
                             context: Optional[str] = None) -> VocabularyItem:
        """
        Get detailed information about a word
        
        Args:
            word: The word to get details for
            language: Language code of the word
            context: Optional context where the word appears
            
        Returns:
            Vocabulary item with details
        """
        try:
            # Create a prompt for the LLM
            prompt = ChatPromptTemplate.from_template(
                """You are an expert linguist and language teacher.
                
                Provide detailed information about the {language} word "{word}".
                
                {context_text}
                
                Include:
                1. The base form of the word
                2. Part of speech
                3. Multiple definitions with example sentences
                4. Common collocations or phrases
                5. Related words (synonyms, antonyms)
                6. Any special usage notes
                
                Respond with a structured analysis of the word.
                """
            )
            
            context_text = ""
            if context:
                context_text = f"Context where the word appears: \"{context}\""
            
            # Use the LLM to get detailed information
            result = await self.llm.ainvoke(
                prompt.format(
                    language=language,
                    word=word,
                    context_text=context_text
                )
            )
            
            # For now, return a mock response
            # In a real implementation, we would parse the LLM's response
            mock_item = VocabularyItem(
                word=word,
                language=language,
                part_of_speech="noun",
                definitions=[
                    WordDefinition(
                        word=word,
                        part_of_speech="noun",
                        definition="Sample definition",
                        example_sentence=f"This is an example sentence with the word {word}.",
                        difficulty_level="intermediate"
                    )
                ],
                translations={"en": "Sample translation"},
                context_examples=[{"text": f"Sample context with {word}", "source": "user_query"}],
                tags=["sample", "intermediate"],
            )
            
            return mock_item
        except Exception as e:
            logger.error(f"Error getting word details: {str(e)}")
            raise
            
    async def create_flashcards(self,
                              vocabulary_items: List[VocabularyItem],
                              target_language: str = "en") -> List[Dict[str, Any]]:
        """
        Create flashcards from vocabulary items
        
        Args:
            vocabulary_items: List of vocabulary items
            target_language: Target language for translations
            
        Returns:
            List of flashcards
        """
        flashcards = []
        
        for item in vocabulary_items:
            # Basic flashcard with word on front, definition on back
            flashcard = {
                "id": f"fc_{item.word}_{datetime.now().timestamp()}",
                "front": item.word,
                "back": item.translations.get(target_language, "No translation available"),
                "example": item.context_examples[0]["text"] if item.context_examples else "",
                "tags": item.tags + [f"source:{ref}" for ref in item.article_references],
                "language": item.language,
                "created_at": datetime.now().isoformat()
            }
            flashcards.append(flashcard)
            
        return flashcards
