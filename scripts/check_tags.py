from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.langread

# Check tags
tags = list(db.tags.find().sort('article_count', -1))
print(f'Total tags: {len(tags)}')
for tag in tags[:15]:
    print(f"Tag: {tag.get('name')} | Articles: {tag.get('article_count', 0)}")

# Check articles with tags
articles_with_tags = db.articles.count_documents({'tag_ids': {'$exists': True, '$ne': []}})
total_articles = db.articles.count_documents({})
print(f'\nArticles with tags: {articles_with_tags} out of {total_articles} total articles')

# Check a sample article with tags
article_with_tags = db.articles.find_one({'tag_ids': {'$exists': True, '$ne': []}})
if article_with_tags:
    print(f"\nSample article with tags: {article_with_tags.get('title')}")
    print(f"Tags: {article_with_tags.get('tag_ids', [])}")
else:
    print("\nNo articles found with tags")
