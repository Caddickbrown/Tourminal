"""
Constants for the Daily Journal application.
"""

from enum import Enum
from typing import Final

# File paths and directories
DEFAULT_JOURNAL_DIR: Final[str] = "~/journal/daily"
DEFAULT_BACKUP_DIR: Final[str] = "~/journal/backups"
DEFAULT_SETTINGS_FILE: Final[str] = "~/.daily_journal_settings.json"
DEFAULT_EXPORT_DIR: Final[str] = "~/journal/exports"

# Date and time formats
DEFAULT_DATE_FORMAT: Final[str] = "%Y-%m-%d"
TIMESTAMP_FORMAT: Final[str] = "[%Y-%m-%d %H:%M:%S] "

# File extensions
JOURNAL_EXTENSION: Final[str] = ".md"
TEXT_EXTENSION: Final[str] = ".txt"
HTML_EXTENSION: Final[str] = ".html"
PDF_EXTENSION: Final[str] = ".pdf"

# Tag prefixes
DEFAULT_TAG_PREFIXES: Final[list[str]] = ["#", "@"]

# UI Constants
class MenuOptions(Enum):
    """Menu option constants"""
    NEW_BLANK_ENTRY = "New Blank Entry"
    NEW_TEMPLATE_ENTRY = "New Template Entry"
    EDIT_TODAY = "Edit Today"
    VIEW_ENTRIES = "View Entries"
    SEARCH_ENTRIES = "Search Entries"
    EXPORT_ENTRIES = "Export Entries"
    IMPORT_ENTRIES = "Import Entries"
    BACKUP = "Backup"
    SETTINGS = "Settings"
    HELP = "Help"
    QUIT = "Quit"

class ExportFormats(Enum):
    """Export format constants"""
    TEXT = "text"
    HTML = "html"
    PDF = "pdf"

class ThemeOptions(Enum):
    """Theme option constants"""
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"

# Keyboard shortcuts
class Shortcuts(Enum):
    """Keyboard shortcut constants"""
    NEW_ENTRY = "Ctrl+N"
    TEMPLATE_ENTRY = "Ctrl+T"
    EDIT_TODAY = "Ctrl+O"
    SEARCH = "Ctrl+F"
    BACKUP = "Ctrl+B"
    SETTINGS = "Ctrl+S"
    HELP = "Ctrl+H"
    QUIT = "Ctrl+Q"
    SAVE = "Ctrl+S"
    COPY = "Ctrl+C"
    DELETE = "Ctrl+D"

# Status messages
class Messages(Enum):
    """Status message constants"""
    ENTRY_ADDED = "Entry added successfully!"
    ENTRY_SAVED = "Entry saved successfully!"
    BACKUP_CREATED = "Backup created successfully!"
    EXPORT_SUCCESS = "Export completed successfully!"
    IMPORT_SUCCESS = "Import completed successfully!"
    SETTINGS_SAVED = "Settings saved successfully!"
    OPERATION_CANCELLED = "Operation cancelled."
    NO_ENTRIES_FOUND = "No entries found."
    ERROR_OCCURRED = "An error occurred."

# Error messages
class Errors(Enum):
    """Error message constants"""
    FILE_NOT_FOUND = "File not found"
    PERMISSION_DENIED = "Permission denied"
    INVALID_SETTINGS = "Invalid settings"
    EXPORT_FAILED = "Export failed"
    IMPORT_FAILED = "Import failed"
    BACKUP_FAILED = "Backup failed" 