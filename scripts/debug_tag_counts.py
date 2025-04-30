#!/usr/bin/env python3
"""
Script to debug tag counts and article retrieval issues in Lingogi.
This will:
1. Verify the actual number of articles per tag vs. stored tag.article_count
2. Check why technology articles aren't being retrieved when the tag is selected
3. Fix any discrepancies in the database
"""

import os
import sys
from pymongo import MongoClient
from bson import ObjectId
from pprint import pprint

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.langread

def check_tag_counts():
    """Compare stored tag article_count with actual article counts"""
    print("Checking tag article count accuracy...")
    
    # Get all tags
    tags = list(db.tags.find().sort('article_count', -1))
    print(f"Found {len(tags)} tags in the database")
    
    # Check the top tags
    for tag in tags[:15]:
        tag_id = tag['_id']
        stored_count = tag.get('article_count', 0)
        
        # Count articles that actually have this tag
        actual_count = db.articles.count_documents({'tag_ids': str(tag_id)})
        obj_id_count = db.articles.count_documents({'tag_ids': tag_id})
        
        # Check if counts match
        match_status = "✓" if stored_count == actual_count else "✗"
        
        print(f"Tag: {tag.get('name'):<20} | Stored: {stored_count:>3} | Actual: {actual_count:>3} | As ObjectId: {obj_id_count:>3} | {match_status}")
        
        # If mismatch, provide more details
        if stored_count != actual_count:
            if actual_count == 0 and obj_id_count > 0:
                print(f"  - Found {obj_id_count} articles with ObjectId, but tag_ids should be strings")

def check_technology_articles():
    """Check if technology tag is correctly associated with articles"""
    print("\nChecking technology tag articles...")
    
    # Find technology tag
    tech_tags = list(db.tags.find({"name": "technology"}))
    
    if not tech_tags:
        print("No tag with name 'technology' found")
        return
        
    tech_tag = tech_tags[0]
    tech_tag_id = tech_tag['_id']
    print(f"Found technology tag with ID: {tech_tag_id}")
    
    # Check for articles with this tag
    articles_with_tag_string = list(db.articles.find({'tag_ids': str(tech_tag_id)}).limit(5))
    articles_with_tag_object = list(db.articles.find({'tag_ids': tech_tag_id}).limit(5))
    
    print(f"Articles with technology tag as string: {len(articles_with_tag_string)}")
    print(f"Articles with technology tag as ObjectId: {len(articles_with_tag_object)}")
    
    # Check a sample article with the tag
    if articles_with_tag_string:
        print("\nSample article with technology tag:")
        sample = articles_with_tag_string[0]
        print(f"Title: {sample.get('title')}")
        print(f"Language: {sample.get('language')}")
        print(f"Content type: {sample.get('content_type')}")
        print(f"Difficulty: {sample.get('difficulty')}")
        print(f"Tag IDs: {sample.get('tag_ids')}")
    elif articles_with_tag_object:
        print("\nSample article with technology tag (as ObjectId):")
        sample = articles_with_tag_object[0]
        print(f"Title: {sample.get('title')}")
        print(f"Language: {sample.get('language')}")
        print(f"Content type: {sample.get('content_type')}")
        print(f"Difficulty: {sample.get('difficulty')}")
        print(f"Tag IDs: {sample.get('tag_ids')}")
    else:
        print("No articles found with technology tag")
    
    # Check tag translation issue - could be a mismatch with '기술' tag
    korean_tech_tags = list(db.tags.find({"translations.ko": "기술"}))
    if korean_tech_tags:
        for tag in korean_tech_tags:
            if tag['_id'] != tech_tag_id:
                print(f"\nFound Korean tech tag that doesn't match English one:")
                print(f"ID: {tag['_id']}")
                print(f"Name: {tag['name']}")
                print(f"Translations: {tag.get('translations')}")
                
                # Check articles with this tag
                k_articles = list(db.articles.find({'tag_ids': str(tag['_id'])}).limit(5))
                print(f"Articles with this tag: {len(k_articles)}")

def fix_tag_id_formats():
    """Fix articles with ObjectId tag_ids instead of strings"""
    print("\nChecking for tag ID format issues...")
    
    # Get sample articles
    sample_articles = list(db.articles.find().limit(5))
    
    # Check tag_ids format
    for article in sample_articles:
        if 'tag_ids' in article:
            tag_ids = article['tag_ids']
            if tag_ids and isinstance(tag_ids, list):
                # Check first tag id
                first_id = tag_ids[0] if tag_ids else None
                if first_id:
                    print(f"Article {article['_id']} first tag_id: {first_id} (type: {type(first_id).__name__})")
    
    # Check for articles with ObjectId in tag_ids
    object_id_count = 0
    for article in db.articles.find():
        if 'tag_ids' in article:
            tag_ids = article['tag_ids']
            if tag_ids and isinstance(tag_ids, list):
                contains_object_id = any(isinstance(tag_id, ObjectId) for tag_id in tag_ids)
                if contains_object_id:
                    object_id_count += 1
    
    print(f"Found {object_id_count} articles with ObjectId in tag_ids")
    
    if object_id_count > 0:
        fix = input("Do you want to fix articles with ObjectId tag_ids? (y/n): ")
        if fix.lower() == 'y':
            fixed_count = 0
            for article in db.articles.find():
                if 'tag_ids' in article:
                    tag_ids = article['tag_ids']
                    if tag_ids and isinstance(tag_ids, list):
                        new_tag_ids = [str(tag_id) if isinstance(tag_id, ObjectId) else tag_id for tag_id in tag_ids]
                        if new_tag_ids != tag_ids:
                            db.articles.update_one({'_id': article['_id']}, {'$set': {'tag_ids': new_tag_ids}})
                            fixed_count += 1
            print(f"Fixed {fixed_count} articles with ObjectId in tag_ids")

def recalculate_tag_counts():
    """Recalculate all tag article_count fields based on actual article associations"""
    print("\nRecalculating tag article counts...")
    
    # Get all tags
    tags = list(db.tags.find())
    print(f"Found {len(tags)} tags to update")
    
    # Update each tag's article_count
    updated_count = 0
    for tag in tags:
        tag_id = tag['_id']
        # Count articles with this tag (as string)
        actual_count = db.articles.count_documents({'tag_ids': str(tag_id)})
        
        # Update tag if count is different
        if tag.get('article_count', 0) != actual_count:
            db.tags.update_one({'_id': tag_id}, {'$set': {'article_count': actual_count}})
            updated_count += 1
    
    print(f"Updated article counts for {updated_count} tags")

def main():
    """Main function to run all diagnostics"""
    print("=" * 60)
    print("Lingogi Tag System Diagnostic")
    print("=" * 60)
    
    # Run diagnostics
    check_tag_counts()
    check_technology_articles()
    fix_tag_id_formats()
    
    # Ask to recalculate tag counts
    should_recalculate = input("\nDo you want to recalculate all tag article counts? (y/n): ")
    if should_recalculate.lower() == 'y':
        recalculate_tag_counts()
    
    print("\nDiagnostic complete")

if __name__ == "__main__":
    main()
