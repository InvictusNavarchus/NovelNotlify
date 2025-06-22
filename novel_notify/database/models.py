"""
Database models for the Novel Notify bot
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import time


@dataclass
class Chapter:
    """Represents a novel chapter"""
    chapter_number: Optional[int]
    title: str
    url: str
    published: str
    is_locked: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'chapter_number': self.chapter_number,
            'title': self.title,
            'url': self.url,
            'published': self.published,
            'is_locked': self.is_locked
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chapter':
        """Create from dictionary"""
        return cls(
            chapter_number=data.get('chapter_number'),
            title=data['title'],
            url=data['url'],
            published=data['published'],
            is_locked=data.get('is_locked', False)
        )


@dataclass
class Volume:
    """Represents a novel volume"""
    volume_title: str
    chapters: List[Chapter] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'volume_title': self.volume_title,
            'chapters': [chapter.to_dict() for chapter in self.chapters]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Volume':
        """Create from dictionary"""
        return cls(
            volume_title=data['volume_title'],
            chapters=[Chapter.from_dict(ch) for ch in data.get('chapters', [])]
        )


@dataclass
class NovelMetadata:
    """Complete novel metadata"""
    novel_id: str
    novel_title: str
    author: str
    cover_url: str
    latest_chapter: Chapter
    volumes: List[Volume] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'novel_id': self.novel_id,
            'novel_title': self.novel_title,
            'author': self.author,
            'cover_url': self.cover_url,
            'latest_chapter': self.latest_chapter.to_dict(),
            'volumes': [volume.to_dict() for volume in self.volumes],
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NovelMetadata':
        """Create from dictionary"""
        return cls(
            novel_id=data['novel_id'],
            novel_title=data['novel_title'],
            author=data['author'],
            cover_url=data['cover_url'],
            latest_chapter=Chapter.from_dict(data['latest_chapter']),
            volumes=[Volume.from_dict(vol) for vol in data.get('volumes', [])],
            last_updated=data.get('last_updated', time.time())
        )
    
    def get_latest_chapter_info(self) -> str:
        """Get formatted latest chapter information"""
        return f"{self.latest_chapter.title} - {self.latest_chapter.published}"
    
    def get_total_chapters(self) -> int:
        """Get total number of chapters across all volumes"""
        return sum(len(volume.chapters) for volume in self.volumes)


@dataclass
class UserSubscription:
    """Represents a user's subscription to a novel"""
    user_id: int
    novel_id: str
    added_at: float = field(default_factory=time.time)
    last_notified_chapter: Optional[str] = None
    notifications_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'novel_id': self.novel_id,
            'added_at': self.added_at,
            'last_notified_chapter': self.last_notified_chapter,
            'notifications_enabled': self.notifications_enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSubscription':
        """Create from dictionary"""
        return cls(
            user_id=data['user_id'],
            novel_id=data['novel_id'],
            added_at=data.get('added_at', time.time()),
            last_notified_chapter=data.get('last_notified_chapter'),
            notifications_enabled=data.get('notifications_enabled', True)
        )
