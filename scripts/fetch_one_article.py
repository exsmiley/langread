import asyncio
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from src.models.database import DatabaseService

async def main():
    db = DatabaseService()
    await db.connect()
    
    # First try to get an article with full content
    try:
        raw_articles = await db.articles_collection.find({"content_type": "raw"}).limit(1).to_list(length=1)
        if raw_articles:
            print("\n--- Example Raw Article Record with Full Content ---\n")
            import pprint
            article = raw_articles[0]
            # Convert ObjectId to string for printing
            if '_id' in article:
                article['_id'] = str(article['_id'])
            pprint.pprint(article)
        else:
            print("No raw article records found.")
            
            # Fall back to any article type
            articles = await db.get_articles(limit=1)
            print("\n--- Example Article Record (Non-Raw) ---\n")
            pprint.pprint(articles[0] if articles else "No articles found.")
    except Exception as e:
        print(f"Error: {e}")
        
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
