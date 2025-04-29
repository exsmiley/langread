from path_helper import setup_path
# Add project root to Python path
setup_path()

import asyncio
import sys
import os
from pprint import pprint

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.utils.tag_generator import tag_generator

async def test_multi_language_tags():
    """Test tag generation for articles in multiple languages"""
    
    # Test articles in different languages
    test_cases = [
        {
            "language": "en",
            "title": "Climate Change Impact on Global Weather Patterns",
            "content": "Scientists have observed significant changes in global weather patterns attributed to climate change. Rising temperatures have led to more frequent extreme weather events including hurricanes, floods, and droughts. The latest IPCC report warns that without immediate action to reduce carbon emissions, the situation could worsen dramatically in the coming decades."
        },
        {
            "language": "es",
            "title": "España celebra el Festival de Cine de San Sebastián",
            "content": "La ciudad de San Sebastián acoge esta semana su prestigioso festival internacional de cine. El evento, que celebra su 72ª edición, contará con la presencia de destacados directores y actores del panorama cinematográfico mundial. Entre las películas más esperadas se encuentra el último trabajo del director Pedro Almodóvar."
        },
        {
            "language": "fr",
            "title": "Nouvelle exposition au Louvre: l'art de la Renaissance italienne",
            "content": "Le musée du Louvre présente une exposition exceptionnelle dédiée aux chefs-d'œuvre de la Renaissance italienne. Les visiteurs pourront admirer des œuvres rares de Léonard de Vinci, Michel-Ange et Raphaël, certaines jamais exposées en France auparavant. L'exposition met en lumière l'évolution des techniques artistiques et l'influence culturelle de cette période historique."
        },
        {
            "language": "ja",
            "title": "東京オリンピックの新たな開催日程が発表",
            "content": "国際オリンピック委員会は、東京オリンピックの新たな開催日程を正式に発表しました。世界中のアスリートたちは、この大会に向けてトレーニングを続けています。日本政府は、安全な大会運営のための対策を強化しています。"
        },
        {
            "language": "unknown",
            "title": "Klimawandel und seine Auswirkungen auf Europa",
            "content": "Der Klimawandel wirkt sich zunehmend auf das Wetter in Europa aus. Wissenschaftler beobachten häufigere Extremwetterereignisse wie Hitzewellen, Überschwemmungen und Dürren. Die Europäische Union hat sich verpflichtet, bis 2050 klimaneutral zu werden, um die schlimmsten Auswirkungen zu vermeiden."
        }
    ]
    
    print("\n===== TESTING MULTI-LANGUAGE TAG GENERATION =====\n")
    
    for i, test_case in enumerate(test_cases, 1):
        language = test_case["language"]
        title = test_case["title"]
        content = test_case["content"]
        
        print(f"\nTest Case {i}: {language} language article")
        print(f"Title: {title}")
        print("Content: " + content[:100] + "...")
        
        # Generate tags
        tags = await tag_generator.generate_tags(title, content, language)
        
        print("\nGenerated Tags:")
        pprint(tags)
        print("-" * 80)
    
    print("\nTest completed.")

if __name__ == "__main__":
    asyncio.run(test_multi_language_tags())
