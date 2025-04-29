#!/usr/bin/env python3
"""
Script to merge duplicate tags in the LangRead database.
This will identify tags with the same meaning but different IDs
and consolidate them into a single canonical tag.
"""

import os
import sys
from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, List, Any
import json

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.langread

# Tags to merge with their canonical names
TAGS_TO_MERGE = [
    # [canonical_name, [alternative_names]]
    ["technology", ["기술"]],
    ["politics", ["정치"]],
    ["news", ["뉴스"]],
    ["business", ["비즈니스"]],
    ["entertainment", ["엔터테인먼트"]],
    ["sports", ["스포츠"]],
    ["health", ["건강"]],
    ["science", ["과학"]],
    ["education", ["교육"]],
    ["environment", ["환경"]],
    ["culture", ["문화"]],
    ["travel", ["여행"]]
]

def get_all_tags():
    """Get all tags from the database"""
    return list(db.tags.find())

def find_duplicate_tags():
    """Find duplicate tags based on name and translations"""
    print("Finding duplicate tags...")
    
    all_tags = get_all_tags()
    print(f"Found {len(all_tags)} total tags")
    
    # Group tags by their canonical meaning
    grouped_tags = {}
    
    # First, group by exact English name
    for tag in all_tags:
        name = tag.get('name', '').lower()
        if name:
            if name not in grouped_tags:
                grouped_tags[name] = []
            grouped_tags[name].append(tag)
    
    # Find duplicates
    duplicates = {name: tags for name, tags in grouped_tags.items() if len(tags) > 1}
    
    print(f"Found {len(duplicates)} tag groups with multiple versions")
    for name, tags in duplicates.items():
        print(f"\nTag: {name} has {len(tags)} versions:")
        for i, tag in enumerate(tags):
            print(f"  {i+1}. ID: {tag['_id']} | Name: {tag['name']} | Article count: {tag.get('article_count', 0)}")
            if 'translations' in tag:
                print(f"     Translations: {tag['translations']}")
    
    # Check for tags with same meaning in different languages
    for canonical, alternatives in TAGS_TO_MERGE:
        canonical_tags = list(db.tags.find({"name": canonical}))
        
        for alt in alternatives:
            alt_tags = list(db.tags.find({"name": alt}))
            if alt_tags and canonical_tags:
                print(f"\nFound {len(alt_tags)} '{alt}' tags and {len(canonical_tags)} '{canonical}' tags")
                for tag in alt_tags:
                    print(f"  Alt: {tag['_id']} | {tag['name']} | Articles: {tag.get('article_count', 0)}")
                for tag in canonical_tags:
                    print(f"  Canon: {tag['_id']} | {tag['name']} | Articles: {tag.get('article_count', 0)}")

def merge_tag_group(canonical_name, alt_names=None):
    """Merge all tags with the same meaning into one canonical tag"""
    print(f"\nMerging tags for '{canonical_name}'...")
    
    # Find all tags with canonical name
    canonical_tags = list(db.tags.find({"name": canonical_name}))
    
    if not canonical_tags:
        print(f"No canonical tag found for '{canonical_name}'")
        return
    
    # Choose the tag with highest article count as the canonical one
    canonical_tags.sort(key=lambda x: x.get('article_count', 0), reverse=True)
    canonical_tag = canonical_tags[0]
    
    print(f"Selected canonical tag: {canonical_tag['_id']} | {canonical_tag['name']} | Articles: {canonical_tag.get('article_count', 0)}")
    
    # Gather all tags to merge
    tags_to_merge = canonical_tags[1:]  # Skip the selected canonical tag
    
    # Add alternative language versions if provided
    if alt_names:
        for alt in alt_names:
            alt_tags = list(db.tags.find({"name": alt}))
            tags_to_merge.extend(alt_tags)
    
    if not tags_to_merge:
        print("No duplicate tags to merge")
        return
    
    print(f"Found {len(tags_to_merge)} tags to merge into canonical tag")
    
    # Merge translations from all tags
    all_translations = canonical_tag.get('translations', {}).copy()
    
    # IDs of tags being merged
    merged_tag_ids = [str(tag['_id']) for tag in tags_to_merge]
    
    # Collect all translations
    for tag in tags_to_merge:
        translations = tag.get('translations', {})
        for lang, trans in translations.items():
            if lang not in all_translations or not all_translations[lang]:
                all_translations[lang] = trans
    
    # Update canonical tag with all translations
    db.tags.update_one(
        {"_id": canonical_tag['_id']},
        {"$set": {"translations": all_translations}}
    )
    
    # Find all articles with these tag IDs
    articles_to_update = []
    total_affected = 0
    
    for tag_id in merged_tag_ids:
        articles = list(db.articles.find({"tag_ids": tag_id}))
        articles_to_update.extend(articles)
        total_affected += len(articles)
    
    print(f"Found {total_affected} articles to update")
    
    # Update articles to use the canonical tag ID
    canonical_id_str = str(canonical_tag['_id'])
    
    for article in articles_to_update:
        article_id = article['_id']
        tag_ids = article.get('tag_ids', [])
        
        # Skip if already has canonical tag
        if canonical_id_str in tag_ids:
            continue
        
        # Replace merged tag IDs with canonical one
        new_tag_ids = [tag_id for tag_id in tag_ids if tag_id not in merged_tag_ids]
        new_tag_ids.append(canonical_id_str)
        
        # Update article
        db.articles.update_one(
            {"_id": article_id},
            {"$set": {"tag_ids": new_tag_ids}}
        )
    
    # Delete the merged tags
    for tag in tags_to_merge:
        db.tags.delete_one({"_id": tag['_id']})
    
    # Update article count for canonical tag
    new_count = db.articles.count_documents({"tag_ids": canonical_id_str})
    db.tags.update_one(
        {"_id": canonical_tag['_id']},
        {"$set": {"article_count": new_count}}
    )
    
    print(f"Successfully merged tags. Canonical tag now has {new_count} articles.")

def merge_all_duplicate_tags():
    """Merge all known duplicate tags"""
    for canonical, alternatives in TAGS_TO_MERGE:
        merge_tag_group(canonical, alternatives)

def main():
    """Main function to run the tag merging process"""
    print("=" * 60)
    print("LangRead Tag Merger")
    print("=" * 60)
    
    # Show duplicates first
    find_duplicate_tags()
    
    # Ask user if they want to proceed with merge
    proceed = input("\nDo you want to merge duplicate tags? (y/n): ")
    
    if proceed.lower() == 'y':
        merge_all_duplicate_tags()
        print("\nAll duplicate tags have been merged successfully.")
    else:
        print("\nTag merging cancelled.")

if __name__ == "__main__":
    main()
