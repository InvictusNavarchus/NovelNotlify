"""
WebNovel scraper for extracting novel metadata and chapter information
"""

import httpx
import logging
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
import time

from ..database.models import NovelMetadata, Chapter, Volume
from ..config import config
from ..utils import format_catalog_url

logger = logging.getLogger(__name__)


class WebNovelScraper:
    """Scraper for WebNovel website"""
    
    def __init__(self):
        """Initialize the scraper with httpx client"""
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        try:
            await self.client.aclose()
        except Exception as e:
            logger.warning(f"Error closing HTTP client: {e}")
            # Don't re-raise as this could mask other exceptions
    
    async def scrape_novel_metadata(self, novel_id: str) -> Optional[NovelMetadata]:
        """
        Scrape complete novel metadata from WebNovel
        
        Args:
            novel_id: The novel ID
            
        Returns:
            NovelMetadata object if successful, None otherwise
        """
        try:
            catalog_url = f"{config.webnovel_base_url}/book/{novel_id}/catalog"
            logger.info(f"Scraping novel metadata from: {catalog_url}")
            
            response = await self.client.get(catalog_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic novel information
            novel_title = self._extract_novel_title(soup)
            author = self._extract_author(soup)
            cover_url = self._extract_cover_url(soup)
            
            # Extract latest chapter information
            latest_chapter = self._extract_latest_chapter(soup)
            
            # Extract volumes and chapters
            volumes = self._extract_volumes_and_chapters(soup)
            
            if not novel_title or not latest_chapter:
                logger.error(f"Failed to extract essential data for novel {novel_id}")
                return None
            
            metadata = NovelMetadata(
                novel_id=novel_id,
                novel_title=novel_title,
                author=author,
                cover_url=cover_url,
                latest_chapter=latest_chapter,
                volumes=volumes,
                last_updated=time.time()
            )
            
            logger.info(f"Successfully scraped metadata for novel: {novel_title}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to scrape novel metadata for {novel_id}: {e}")
            return None
    
    def _extract_novel_title(self, soup: BeautifulSoup) -> str:
        """Extract novel title from the page"""
        title_element = soup.select_one('h1.auto_height')
        if title_element:
            return title_element.get_text(strip=True)
        
        # Fallback selectors
        title_element = soup.select_one('h1')
        if title_element:
            return title_element.get_text(strip=True)
        
        logger.warning("Could not extract novel title")
        return "Untitled"
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract author name from the page"""
        author_element = soup.select_one('address .c_primary')
        if author_element:
            return author_element.get_text(strip=True)
        
        # Fallback selectors
        author_element = soup.select_one('[data-test="author"] a, .author a, .author-name')
        if author_element:
            return author_element.get_text(strip=True)
        
        logger.warning("Could not extract author name")
        return "Unknown Author"
    
    def _extract_cover_url(self, soup: BeautifulSoup) -> str:
        """Extract cover image URL from the page"""
        cover_element = soup.select_one('div._sd img')
        if cover_element and cover_element.get('src'):
            return cover_element['src']
        
        # Fallback selectors
        cover_element = soup.select_one('.book-cover img, .cover img, img[alt*="cover"]')
        if cover_element and cover_element.get('src'):
            return cover_element['src']
        
        logger.warning("Could not extract cover URL")
        return ""
    
    def _extract_latest_chapter(self, soup: BeautifulSoup) -> Optional[Chapter]:
        """Extract latest chapter information from the page"""
        try:
            latest_chapter_container = soup.select_one('.det-con-intro')
            if not latest_chapter_container:
                # Try alternative selectors
                latest_chapter_container = soup.select_one('.latest-chapter, .last-chapter')
            
            if latest_chapter_container:
                latest_chapter_anchor = latest_chapter_container.select_one('a.lst-chapter')
                if not latest_chapter_anchor:
                    latest_chapter_anchor = latest_chapter_container.select_one('a')
                
                if latest_chapter_anchor:
                    title = latest_chapter_anchor.get_text(strip=True)
                    url = latest_chapter_anchor.get('href', '')
                    
                    # Extract publication date
                    published_element = latest_chapter_container.select_one('small.c_s')
                    if not published_element:
                        published_element = latest_chapter_container.select_one('small, .date, .time')
                    
                    published = published_element.get_text(strip=True) if published_element else 'Unknown'
                    
                    return Chapter(
                        chapter_number=None,  # Will be extracted from chapter list
                        title=title,
                        url=url,
                        published=published,
                        is_locked=False
                    )
            
            # Fallback: try to get from chapter list
            first_chapter = soup.select_one('ol.content-list > li:first-child a')
            if first_chapter:
                return Chapter(
                    chapter_number=None,
                    title=first_chapter.get_text(strip=True),
                    url=first_chapter.get('href', ''),
                    published='Unknown',
                    is_locked=False
                )
            
            logger.warning("Could not extract latest chapter")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting latest chapter: {e}")
            return None
    
    def _extract_volumes_and_chapters(self, soup: BeautifulSoup) -> List[Volume]:
        """Extract volumes and chapters from the page"""
        volumes = []
        
        try:
            # Find all volume containers
            volume_elements = soup.select('.volume-item')
            
            if not volume_elements:
                # If no volume structure, treat as single volume
                chapters = self._extract_chapters_from_container(soup)
                if chapters:
                    volumes.append(Volume(
                        volume_title="Main Volume",
                        chapters=chapters
                    ))
            else:
                # Process each volume
                for volume_element in volume_elements:
                    volume_title = self._extract_volume_title(volume_element)
                    chapters = self._extract_chapters_from_container(volume_element)
                    
                    if chapters:  # Only add volumes with chapters
                        volumes.append(Volume(
                            volume_title=volume_title,
                            chapters=chapters
                        ))
            
            logger.info(f"Extracted {len(volumes)} volumes with total chapters: {sum(len(v.chapters) for v in volumes)}")
            
        except Exception as e:
            logger.error(f"Error extracting volumes and chapters: {e}")
        
        return volumes
    
    def _extract_volume_title(self, volume_element) -> str:
        """Extract volume title from volume element"""
        title_element = volume_element.select_one('h4')
        if title_element:
            return title_element.get_text(strip=True)
        
        # Fallback
        title_element = volume_element.select_one('.volume-title, .volume-name, h1, h2, h3')
        if title_element:
            return title_element.get_text(strip=True)
        
        return "Untitled Volume"
    
    def _extract_chapters_from_container(self, container) -> List[Chapter]:
        """Extract chapters from a container (volume or main page)"""
        chapters = []
        
        try:
            # Find chapter list items
            chapter_elements = container.select('ol.content-list > li')
            
            if not chapter_elements:
                # Fallback selectors
                chapter_elements = container.select('.chapter-list li, .content-list li, .chapter-item')
            
            for chapter_element in chapter_elements:
                chapter = self._extract_single_chapter(chapter_element)
                if chapter:
                    chapters.append(chapter)
            
        except Exception as e:
            logger.error(f"Error extracting chapters from container: {e}")
        
        return chapters
    
    def _extract_single_chapter(self, chapter_element) -> Optional[Chapter]:
        """Extract a single chapter from its element"""
        try:
            anchor = chapter_element.select_one('a')
            if not anchor:
                return None
            
            # Extract chapter number
            chapter_number = None
            number_element = anchor.select_one('._num')
            if number_element:
                try:
                    chapter_number = int(number_element.get_text(strip=True))
                except (ValueError, TypeError):
                    pass
            
            # Extract title
            title_element = anchor.select_one('strong')
            if not title_element:
                title_element = anchor
            title = title_element.get_text(strip=True)
            
            # Extract URL
            url = anchor.get('href', '')
            
            # Extract publication date
            published_element = anchor.select_one('small')
            published = published_element.get_text(strip=True) if published_element else 'Unknown Date'
            
            # Check if chapter is locked
            is_locked = bool(anchor.select_one('svg._icon use[href="#i-lock"], svg._icon use[xlink\\:href="#i-lock"]'))
            
            return Chapter(
                chapter_number=chapter_number,
                title=title,
                url=url,
                published=published,
                is_locked=is_locked
            )
            
        except Exception as e:
            logger.error(f"Error extracting single chapter: {e}")
            return None
    
    async def quick_check_latest_chapter(self, novel_id: str) -> Optional[Chapter]:
        """
        Quick check for latest chapter without full scraping
        
        Args:
            novel_id: The novel ID
            
        Returns:
            Latest chapter if found, None otherwise
        """
        try:
            catalog_url = f"{config.webnovel_base_url}/book/{novel_id}/catalog"
            response = await self.client.get(catalog_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_latest_chapter(soup)
            
        except Exception as e:
            logger.error(f"Failed to quick check latest chapter for {novel_id}: {e}")
            return None
