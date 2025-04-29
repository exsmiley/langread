# Lingogi Scripts

This directory contains utility scripts for the Lingogi language learning platform. These scripts help with various tasks including article fetching, content processing, database maintenance, and system management.

## Running Scripts

All scripts should be run from the project root directory with the following pattern:

```bash
python scripts/script_name.py [arguments]
```

For example:
```bash
python scripts/test_full_workflow.py
```

## Script Categories

### System Management

| Script | Description |
|--------|-------------|
| `kill_servers.py` | Stops running Lingogi services (API, frontend, database) |
| `restart_servers.py` | Restarts Lingogi services |
| `setup_env.py` | Sets up the environment for development |
| `test_env_setup.py` | Tests if the environment is properly configured |
| `run_tests.py` | Runs automated tests for the application |

### Article Management

| Script | Description |
|--------|-------------|
| `fetch_one_article.py` | Fetches a single article for testing |
| `test_full_workflow.py` | Demonstrates end-to-end content fetching and rewriting workflow |
| `check_article_count.py` | Counts articles in the database |
| `check_article_data.py` | Inspects article data in the database |
| `analyze_articles.py` | Analyzes article content and metrics |
| `assess_article_difficulty.py` | Evaluates the difficulty level of articles |

### Tag Management

| Script | Description |
|--------|-------------|
| `check_tags.py` | Checks tags in the database |
| `create_initial_tags.py` | Creates initial tags for article classification |
| `create_sample_tags.py` | Creates sample tags for testing |
| `debug_tag_counts.py` | Debugs tag count issues |
| `merge_duplicate_tags.py` | Merges duplicate tags in the database |
| `normalize_tag_languages.py` | Normalizes tag languages |
| `retag_all_articles.py` | Retags all articles in the database |
| `retag_articles.py` | Retags specific articles |
| `test_tag_generator.py` | Tests the tag generation system |
| `update_tag_translations.py` | Updates translations for tags |

### Image Processing

| Script | Description |
|--------|-------------|
| `check_article_images.py` | Checks if articles have associated images |
| `check_image_status.py` | Checks the status of image generation |
| `download_article_images.py` | Downloads images for articles |
| `generate_and_save_images.py` | Generates and saves images for articles |
| `generate_article_images.py` | Generates images for articles using AI |
| `save_dalle_images.py` | Saves DALL-E generated images |
| `update_article_images.py` | Updates article images |

### Content Processing

| Script | Description |
|--------|-------------|
| `check_rewriting.py` | Checks rewriting status of articles |
| `fix_remaining_articles.py` | Fixes issues in articles that need attention |
| `trigger_rewrite.py` | Triggers rewriting of articles to different difficulty levels |

### Debugging & Development

| Script | Description |
|--------|-------------|
| `check_db.py` | Checks database connection and content |
| `debug_articles_api.py` | Debugs the articles API |
| `path_helper.py` | Helper module to resolve paths for scripts |
| `update_script_paths.py` | Updates script paths for compatibility |

## Examples

### Basic Usage Examples

**Testing the complete article workflow:**
```bash
python scripts/test_full_workflow.py
```

**Checking database connection:**
```bash
python scripts/check_db.py
```

**Stopping all services:**
```bash
python scripts/kill_servers.py --all
```

### Advanced Usage Examples

**Retagging articles with specific parameters:**
```bash
python scripts/retag_articles.py --limit 10 --language ko
```

**Generating images for articles:**
```bash
python scripts/generate_article_images.py --count 5
```

## Development Notes

- All scripts use the `path_helper.py` module to ensure they can find the necessary modules regardless of where they're run from
- Scripts that interact with the database require MongoDB to be running
- Many scripts require environment variables (like `OPENAI_API_KEY`) to be set in the `.env` file
