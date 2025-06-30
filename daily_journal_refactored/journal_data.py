"""
Core data layer for the Daily Journal application.
Handles all data operations including file I/O, settings, and entry management.
"""

import os
import json
import re
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from constants import (
    DEFAULT_JOURNAL_DIR, DEFAULT_BACKUP_DIR, DEFAULT_SETTINGS_FILE,
    DEFAULT_DATE_FORMAT, TIMESTAMP_FORMAT, JOURNAL_EXTENSION,
    DEFAULT_TAG_PREFIXES, ExportFormats, ThemeOptions
)


@dataclass
class JournalEntry:
    """Represents a single journal entry"""
    title: str
    content: str
    tags: str
    date: str
    filename: str
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JournalEntry':
        """Create entry from dictionary"""
        return cls(**data)


@dataclass
class JournalStats:
    """Statistics for journal entries"""
    total_entries: int
    total_words: int
    total_files: int
    date_range: Tuple[str, str]
    most_used_tags: List[Tuple[str, int]]


class Settings:
    """Manages application settings"""
    
    def __init__(self, settings_file: str = DEFAULT_SETTINGS_FILE):
        self.settings_file = os.path.expanduser(settings_file)
        self._settings = self._load_default_settings()
        self.load()
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default settings"""
        return {
            "journal_directory": os.path.expanduser(DEFAULT_JOURNAL_DIR),
            "backup_directory": os.path.expanduser(DEFAULT_BACKUP_DIR),
            "export_directory": os.path.expanduser("~/journal/exports"),
            "default_editor": "nano",
            "date_format": DEFAULT_DATE_FORMAT,
            "auto_save": True,
            "auto_backup": True,
            "auto_detect_tags": True,
            "tag_prefixes": DEFAULT_TAG_PREFIXES,
            "merge_detected_tags": True,
            "theme": ThemeOptions.SYSTEM.value,
            "font_family": "Consolas",
            "font_size": 11,
            "window_width": 1200,
            "window_height": 800,
        }
    
    def load(self) -> None:
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    file_settings = json.load(f)
                    self._settings.update(file_settings)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load settings: {e}")
    
    def save(self) -> None:
        """Save settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value"""
        self._settings[key] = value
    
    def reset_to_defaults(self) -> None:
        """Reset settings to defaults"""
        self._settings = self._load_default_settings()
        self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Get all settings as dictionary"""
        return self._settings.copy()


class Journal:
    """Manages journal entries and file operations"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.journal_dir = Path(self.settings.get("journal_directory"))
        self.backup_dir = Path(self.settings.get("backup_directory"))
        self.export_dir = Path(self.settings.get("export_directory"))
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def get_today_filename(self) -> str:
        """Get filename for today's journal"""
        date_str = datetime.now().strftime(self.settings.get("date_format"))
        return f"{date_str}{JOURNAL_EXTENSION}"
    
    def get_journal_files(self) -> List[str]:
        """Get list of all journal files"""
        try:
            files = [f.name for f in self.journal_dir.glob(f"*{JOURNAL_EXTENSION}")]
            return sorted(files, reverse=True)
        except OSError:
            return []
    
    def read_file(self, filename: str) -> str:
        """Read content from a journal file"""
        filepath = self.journal_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except (IOError, OSError):
            return ""
    
    def write_file(self, filename: str, content: str) -> bool:
        """Write content to a journal file"""
        filepath = self.journal_dir / filename
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except (IOError, OSError):
            return False
    
    def append_to_file(self, filename: str, entry_content: str) -> bool:
        """Append entry content to a journal file"""
        existing_content = self.read_file(filename)
        if existing_content:
            new_content = existing_content + "\n\n" + entry_content
        else:
            new_content = entry_content
        return self.write_file(filename, new_content)
    
    def create_entry(self, title: str, content: str, tags: str = "", 
                    use_timestamp: bool = True) -> bool:
        """Create a new journal entry"""
        today_file = self.get_today_filename()
        
        # Format entry
        entry_lines = []
        if title:
            entry_lines.append(f"# {title}")
            entry_lines.append("")
        
        if use_timestamp:
            timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            entry_lines.append(f"{timestamp}{content}")
        else:
            entry_lines.append(content)
        
        # Add tags at the end
        if tags:
            tag_list = [tag.strip() for tag in tags.split() if tag.strip()]
            if tag_list:
                entry_lines.append("")
                entry_lines.append(f"{' '.join([f'@{tag}' for tag in tag_list])}")
        
        entry_content = "\n".join(entry_lines) + "\n"
        return self.append_to_file(today_file, entry_content)
    
    def extract_tags_from_content(self, content: str) -> List[str]:
        """Extract tags from content using configured prefixes"""
        if not content:
            return []
        
        tag_prefixes = self.settings.get("tag_prefixes", DEFAULT_TAG_PREFIXES)
        tags = set()
        lines = content.split('\n')
        
        for line in lines:
            words = line.split()
            for word in words:
                for prefix in tag_prefixes:
                    if word.startswith(prefix):
                        tag = word[len(prefix):].rstrip('.,;:!?')
                        if tag and any(c.isalnum() for c in tag):
                            tags.add(tag.lower())
                        break
        return sorted(list(tags))
    
    def parse_entries_from_content(self, content: str, filename: str) -> List[JournalEntry]:
        """Parse individual entries from file content"""
        entries = []
        lines = content.split('\n')
        current_entry = JournalEntry(
            title="", content="", tags="", 
            date=filename.replace(JOURNAL_EXTENSION, ''),
            filename=filename
        )
        
        for line in lines:
            if line.startswith('[20') and ']' in line:  # Timestamp line
                if current_entry.content:  # Save previous entry
                    # Extract tags from the end of content
                    content_text = current_entry.content.strip()
                    tags = self._extract_tags_from_end_of_content(content_text)
                    current_entry.content = content_text
                    current_entry.tags = tags
                    entries.append(current_entry)
                    current_entry = JournalEntry(
                        title="", content="", tags="", 
                        date=filename.replace(JOURNAL_EXTENSION, ''),
                        filename=filename
                    )
                
                # Extract content after timestamp
                timestamp_end = line.find(']') + 1
                content_part = line[timestamp_end:].strip()
                if content_part:
                    current_entry.content = content_part
                    current_entry.timestamp = line[:timestamp_end]
            elif line.startswith('# ') and not current_entry.title:
                current_entry.title = line[2:].strip()
            elif line.strip() and not line.startswith('**Tags:**'):
                if current_entry.content:
                    current_entry.content += "\n" + line
                else:
                    current_entry.content = line
        
        # Add last entry
        if current_entry.content:
            content_text = current_entry.content.strip()
            tags = self._extract_tags_from_end_of_content(content_text)
            current_entry.content = content_text
            current_entry.tags = tags
            entries.append(current_entry)
        
        return entries
    
    def _extract_tags_from_end_of_content(self, content: str) -> str:
        """Extract tags from the end of content in @tag format"""
        if not content:
            return ""
        
        lines = content.split('\n')
        tags = []
        
        # Look for @tags at the end of the content
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if this line contains @tags
            words = line.split()
            line_tags = []
            for word in words:
                if word.startswith('@'):
                    tag = word[1:].rstrip('.,;:!?')
                    if tag and any(c.isalnum() for c in tag):
                        line_tags.append(tag.lower())
            
            if line_tags:
                # Found tags, add them and stop looking
                tags.extend(reversed(line_tags))
                break
            elif line.startswith('#'):
                # Found a header, stop looking
                break
            else:
                # This line doesn't contain tags, stop looking
                break
        
        return ", ".join(reversed(tags))
    
    def get_all_entries(self) -> List[JournalEntry]:
        """Get all entries from all journal files"""
        all_entries = []
        files = self.get_journal_files()
        
        for filename in files:
            content = self.read_file(filename)
            if content:
                entries = self.parse_entries_from_content(content, filename)
                all_entries.extend(entries)
        
        return all_entries
    
    def search_entries(self, query: str, case_sensitive: bool = False) -> List[JournalEntry]:
        """Search entries by content, title, and tags"""
        all_entries = self.get_all_entries()
        results = []
        
        if not case_sensitive:
            query = query.lower()
        
        for entry in all_entries:
            search_text = f"{entry.title} {entry.content} {entry.tags}"
            if not case_sensitive:
                search_text = search_text.lower()
            
            if query in search_text:
                results.append(entry)
        
        return results
    
    def search_by_tags(self, target_tags: List[str]) -> List[JournalEntry]:
        """Search entries by specific tags"""
        all_entries = self.get_all_entries()
        results = []
        
        for entry in all_entries:
            if entry.tags:
                entry_tags = [tag.strip().lower() for tag in entry.tags.split(',')]
                # Check if any target tags match entry tags
                if any(target_tag in entry_tags for target_tag in target_tags):
                    results.append(entry)
        
        return results
    
    def get_statistics(self) -> JournalStats:
        """Get journal statistics"""
        all_entries = self.get_all_entries()
        files = self.get_journal_files()
        
        total_words = sum(len(entry.content.split()) for entry in all_entries)
        
        # Get date range
        dates = [entry.date for entry in all_entries if entry.date]
        date_range = (min(dates), max(dates)) if dates else ("", "")
        
        # Get most used tags
        tag_counts = {}
        for entry in all_entries:
            if entry.tags:
                for tag in entry.tags.split(','):
                    tag = tag.strip().lower()
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        most_used_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return JournalStats(
            total_entries=len(all_entries),
            total_words=total_words,
            total_files=len(files),
            date_range=date_range,
            most_used_tags=most_used_tags
        )
    
    def create_backup(self, filename: Optional[str] = None) -> bool:
        """Create a backup of journal files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if filename:
                backup_name = f"backup_{filename}_{timestamp}"
            else:
                backup_name = f"backup_full_{timestamp}"
            
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Copy all journal files
            for journal_file in self.journal_dir.glob(f"*{JOURNAL_EXTENSION}"):
                shutil.copy2(journal_file, backup_path / journal_file.name)
            
            return True
        except (OSError, IOError):
            return False
    
    def get_word_count(self, content: str) -> int:
        """Get word count from content"""
        return len(content.split()) 