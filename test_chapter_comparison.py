#!/usr/bin/env python3
"""
Test script to verify the new chapter comparison functionality
"""

import asyncio
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from novel_notify.scraper import WebNovelScraper
from novel_notify.utils import extract_novel_id_from_url


async def test_chapter_comparison():
    """Test the new chapter comparison functionality"""
    
    # Test URL
    test_url = "https://www.webnovel.com/book/awakening-the-only-sss-rank-class!-now-even-dragons-obey-me_32382246008650205"
    
    print(f"🧪 Testing Chapter Comparison Functionality")
    print(f"📖 Testing URL: {test_url}")
    print("-" * 80)
    
    # Extract novel ID
    novel_id = extract_novel_id_from_url(test_url)
    print(f"📋 Extracted Novel ID: {novel_id}")
    
    if not novel_id:
        print("❌ Failed to extract novel ID")
        return
    
    # Test the new functionality
    async with WebNovelScraper() as scraper:
        print("\n🔍 1. Testing quick_check_latest_chapter...")
        latest_chapter = await scraper.quick_check_latest_chapter(novel_id)
        
        if latest_chapter:
            print("✅ Latest chapter found!")
            print(f"   📚 Title: {latest_chapter.title}")
            print(f"   🔢 Chapter Number: {latest_chapter.chapter_number}")
            print(f"   🔒 Is Locked: {latest_chapter.is_locked}")
            print(f"   📅 Published: {latest_chapter.published}")
        else:
            print("❌ Failed to get latest chapter")
        
        print("\n🔍 2. Testing get_last_free_chapter...")
        last_free_chapter = await scraper.get_last_free_chapter(novel_id)
        
        if last_free_chapter:
            print("✅ Last free chapter found!")
            print(f"   📚 Title: {last_free_chapter.title}")
            print(f"   🔢 Chapter Number: {last_free_chapter.chapter_number}")
            print(f"   🔒 Is Locked: {last_free_chapter.is_locked}")
            print(f"   📅 Published: {last_free_chapter.published}")
        else:
            print("❌ Failed to get last free chapter")
        
        print("\n🔍 3. Testing compare_latest_chapters...")
        comparison = await scraper.compare_latest_chapters(novel_id)
        
        if comparison['latest_chapter'] and comparison['last_free_chapter']:
            print("✅ Chapter comparison completed!")
            print(f"   📊 Has paid chapters: {comparison['has_paid_chapters']}")
            
            if comparison['chapter_difference']:
                print(f"   📈 Chapter difference: {comparison['chapter_difference']} chapters")
            else:
                print("   📈 Chapter difference: Cannot calculate (no chapter numbers)")
            
            print(f"\n   📚 Latest Chapter: {comparison['latest_chapter'].title}")
            print(f"   📚 Last Free Chapter: {comparison['last_free_chapter'].title}")
            
            if comparison['has_paid_chapters']:
                print("\n🔐 This novel has paid chapters! The latest chapter is different from the last free chapter.")
            else:
                print("\n🆓 This novel only has free chapters (or latest chapter is the same as last free chapter).")
        else:
            print("❌ Failed to compare chapters")
        
        print("\n" + "=" * 80)
        print("🎉 Test completed!")


if __name__ == "__main__":
    print("🧪 Testing Novel Notify Bot Chapter Comparison...")
    asyncio.run(test_chapter_comparison())
