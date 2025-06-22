"""
Utility functions for the Novel Notify bot
"""

import re
import logging
from typing import Optional, Tuple
from urllib.parse import urlparse, parse_qs

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def extract_novel_id_from_url(url: str) -> Optional[str]:
    """
    Extract novel ID from WebNovel URL
    
    Supports both formats:
    - https://www.webnovel.com/book/title_id
    - https://www.webnovel.com/book/id
    
    Args:
        url: WebNovel URL
        
    Returns:
        Novel ID if found, None otherwise
    """
    try:
        parsed = urlparse(url.strip())
        if not parsed.netloc or 'webnovel.com' not in parsed.netloc:
            return None
            
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2 or path_parts[0] != 'book':
            return None
            
        book_identifier = path_parts[1]
        
        # Extract ID from the end of the identifier (after last underscore)
        if '_' in book_identifier:
            novel_id = book_identifier.split('_')[-1]
        else:
            novel_id = book_identifier
            
        # Validate that it's a numeric ID
        if novel_id.isdigit():
            return novel_id
            
        return None
        
    except Exception as e:
        logger.error(f"Error extracting novel ID from URL {url}: {e}")
        return None


def format_novel_url(novel_id: str) -> str:
    """
    Format a WebNovel URL using novel ID
    
    Args:
        novel_id: The novel ID
        
    Returns:
        Formatted WebNovel URL
    """
    return f"https://www.webnovel.com/book/{novel_id}"


def format_catalog_url(novel_id: str) -> str:
    """
    Format a WebNovel catalog URL using novel ID
    
    Args:
        novel_id: The novel ID
        
    Returns:
        Formatted WebNovel catalog URL
    """
    return f"https://www.webnovel.com/book/{novel_id}/catalog"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be safe for use as a filename
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized[:100]  # Limit length


def format_time_ago(timestamp: float) -> str:
    """
    Format timestamp as human-readable time ago
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Human-readable time string
    """
    import time
    
    now = time.time()
    diff = int(now - timestamp)
    
    if diff < 60:
        return f"{diff} seconds ago"
    elif diff < 3600:
        minutes = diff // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < 86400:
        hours = diff // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = diff // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length with ellipsis
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
