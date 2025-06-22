#!/usr/bin/env python3
"""
Test script to verify WebNovel scraping functionality
"""

import asyncio
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from novel_notify.scraper import WebNovelScraper
from novel_notify.utils import extract_novel_id_from_url


async def test_scraping():
    """Test the scraping functionality"""
    
    # Test URL
    test_url = "https://www.webnovel.com/book/awakening-the-only-sss-rank-class!-now-even-dragons-obey-me_32382246008650205"
    
    print(f"Testing URL: {test_url}")
    
    # Extract novel ID
    novel_id = extract_novel_id_from_url(test_url)
    print(f"Extracted Novel ID: {novel_id}")
    
    if not novel_id:
        print("❌ Failed to extract novel ID")
        return
    
    # Test scraping
    async with WebNovelScraper() as scraper:
        print("🔄 Scraping novel metadata...")
        metadata = await scraper.scrape_novel_metadata(novel_id)
        
        if metadata:
            print("✅ Scraping successful!")
            print(f"📖 Title: {metadata.novel_title}")
            print(f"✍️ Author: {metadata.author}")
            print(f"📚 Latest Chapter: {metadata.latest_chapter.title}")
            print(f"🔗 Cover URL: {metadata.cover_url}")
            print(f"📊 Total Volumes: {len(metadata.volumes)}")
            print(f"📊 Total Chapters: {metadata.get_total_chapters()}")
        else:
            print("❌ Scraping failed!")


if __name__ == "__main__":
    print("🧪 Testing Novel Notify Bot Scraping...")
    asyncio.run(test_scraping())
