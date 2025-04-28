# LangRead Implementation Plan: Tag-Based Article System

## Overview
This document outlines the plan for redesigning LangRead's article processing and organization system, shifting from article grouping to a tag-based approach.

## Phase 1: Database Schema Updates

### Create Tags Collection
```javascript
// tags collection schema
{
  "_id": ObjectId,
  "name": String, // e.g. "science", "politics"
  "language": String, // e.g. "en", "ko"
  "active": Boolean, // default: false, requires admin approval
  "created_at": ISODate,
  "updated_at": ISODate,
  "article_count": Number // count of articles with this tag
}
```

### Update Article Schema
```javascript
// articles collection schema (additions only)
{
  // existing fields...
  "tags": [String], // array of tag names
  "auto_generated_tags": [String], // original tags before approval/editing
}
```

## Phase 2: Backend API Updates

### 1. Remove Grouping Step
- Modify the bulk fetch operation to skip grouping
- Update rewrite_step to process individual articles

### 2. Add Tag Generation
- Create a new function to analyze article content and generate tags
- LLM-based extraction of topics and themes
- Store both auto-generated tags and approved tags

### 3. Tag Management API
- `GET /api/tags` - List all tags with filtering options
- `POST /api/tags` - Create a new tag
- `PATCH /api/tags/{id}` - Update a tag (including activation)
- `DELETE /api/tags/{id}` - Delete a tag
- `GET /api/tags/stats` - Get tag usage statistics

### 4. Update Article APIs
- Modify article fetch endpoints to include tag filtering
- Add endpoints for updating article tags

## Phase 3: Frontend Updates

### 1. Admin Tag Management UI
- Create a tag management interface for admins
- Include approval workflow
- Tag analytics dashboard

### 2. User-Facing Tag System
- Update article listing to show and filter by tags
- Tag cloud component
- Tag-based article recommendations

### 3. Content Display
- Update article cards to show tags
- Implement tag-based search and filtering

## Implementation Steps

1. **Database Changes**
   - Add tags collection
   - Update article schema

2. **Backend Implementation**
   - Remove grouping code
   - Implement tag generation on article rewrite
   - Create tag management APIs

3. **Frontend Implementation**
   - Admin tag management interface
   - User tag browsing experience
   - Update article components to display tags

4. **Testing**
   - Test tag generation quality
   - Test admin approval workflow
   - Test article filtering by tags

## Timeline Estimate
- Database changes: 1 day
- Backend implementation: 3-4 days
- Frontend implementation: 3-4 days
- Testing and refinement: 2-3 days

Total estimated time: 9-12 days
