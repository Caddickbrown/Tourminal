#!/usr/bin/env python3
"""
Daily Journal GUI - PyQt6-based Journal Application
A professional GUI version of the daily journal with native cross-platform compatibility.
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
import subprocess
import platform
from typing import Optional, Dict, List, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QPushButton, QLabel, QLineEdit, QTextEdit, 
    QListWidget, QListWidgetItem, QDialog, QMessageBox, 
    QFileDialog, QCheckBox, QGroupBox, QSplitter, QFrame,
    QScrollArea, QSizePolicy, QTabWidget, QTextBrowser, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence, QPalette, QColor

# Configuration - reuse from original
JOURNAL_DIR = os.path.expanduser("~/journal/daily")
SETTINGS_FILE = os.path.expanduser("~/.daily_journal_pyqt6_settings.json")
BACKUP_DIR = os.path.expanduser("~/journal/backups")

DEFAULT_SETTINGS = {
    "journal_directory": JOURNAL_DIR,
    "backup_directory": BACKUP_DIR,
    "default_editor": "nano",
    "date_format": "%Y-%m-%d",
    "auto_save": True,
    "auto_backup": True,
    "auto_detect_tags": True,
    "tag_prefixes": ["#", "@"],
    "merge_detected_tags": True,
    "window_width": 1200,
    "window_height": 800,
    "font_family": "Consolas",
    "font_size": 11,
    "theme": "system"
}

def load_settings():
    """Load settings from file"""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return {**DEFAULT_SETTINGS, **json.load(f)}
    except:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except:
        pass

def ensure_directories():
    """Ensure journal and backup directories exist"""
    settings = load_settings()
    os.makedirs(settings["journal_directory"], exist_ok=True)
    os.makedirs(settings["backup_directory"], exist_ok=True)

def get_today_filename():
    """Get filename for today's journal"""
    settings = load_settings()
    date_str = datetime.now().strftime(settings["date_format"])
    return f"{date_str}.md"

def get_daily_files():
    """Get list of daily journal files"""
    ensure_directories()
    settings = load_settings() 
    try:
        files = [f for f in os.listdir(settings["journal_directory"]) if f.endswith('.md')]
        return sorted(files, reverse=True)
    except:
        return []

def read_daily_file(filename):
    """Read a daily journal file"""
    settings = load_settings()
    filepath = os.path.join(settings["journal_directory"], filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def write_daily_file(filename, content):
    """Write content to a daily journal file"""
    settings = load_settings()
    filepath = os.path.join(settings["journal_directory"], filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def append_to_daily_file(filename, entry_content):
    """Append a new entry to a daily journal file"""
    existing_content = read_daily_file(filename)
    if existing_content:
        new_content = existing_content + "\n\n" + entry_content
    else:
        new_content = entry_content
    write_daily_file(filename, new_content)

def extract_tags_from_content(content, tag_prefixes=None):
    """Extract tags from content using specified prefixes"""
    if not content:
        return []
    if tag_prefixes is None:
        settings = load_settings()
        tag_prefixes = settings.get("tag_prefixes", ["#", "@"])
    
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

def format_timestamp():
    """Get formatted timestamp for entries"""
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")

class EntryDialog(QDialog):
    """Dialog for creating/editing journal entries"""
    
    def __init__(self, parent=None, title="New Entry", content="", tags="", entry_title=""):
        super().__init__(parent)
        self.result: Optional[Dict[str, str]] = None
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(900, 700)
        
        # Center the dialog
        screen = self.screen()
        if screen:
            self.setGeometry(
                (screen.size().width() - 900) // 2,
                (screen.size().height() - 700) // 2,
                900, 700
            )
        
        # If no entry_title provided, include the date like in the original
        if not entry_title:
            current_datetime = format_timestamp()
            entry_title = f"{current_datetime}"
        
        self.create_widgets(entry_title, tags, content)
        
        # Focus on title entry and move cursor to end
        self.title_entry.setFocus()
        self.title_entry.setCursorPosition(len(entry_title))
    
    def create_widgets(self, entry_title, tags, content):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Entry Title:")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        self.title_entry = QLineEdit()
        self.title_entry.setPlaceholderText("Enter entry title...")
        self.title_entry.setText(entry_title)
        layout.addWidget(self.title_entry)
        
        # Tags
        tags_label = QLabel("Tags:")
        tags_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(tags_label)
        
        self.tags_entry = QLineEdit()
        self.tags_entry.setPlaceholderText("Enter tags separated by spaces...")
        self.tags_entry.setText(tags)
        layout.addWidget(self.tags_entry)
        
        # Content
        content_label = QLabel("Content:")
        content_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(content_label)
        
        self.content_text = QTextEdit()
        self.content_text.setPlainText(content)
        layout.addWidget(self.content_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save Entry")
        self.save_btn.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px;")
        self.save_btn.clicked.connect(self.save_entry)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 16px;")
        self.cancel_btn.clicked.connect(self.cancel)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Connect Enter key to save
        self.title_entry.returnPressed.connect(self.save_entry)
    
    def save_entry(self):
        """Save the entry"""
        title = self.title_entry.text().strip()
        tags = self.tags_entry.text().strip()
        content = self.content_text.toPlainText().strip()
        
        if not content:
            QMessageBox.critical(self, "Error", "Content cannot be empty.")
            return
        
        # Only use explicitly entered tags, not auto-detected ones
        settings = load_settings()
        if settings.get("auto_detect_tags", True):
            detected_tags = extract_tags_from_content(content)
            if detected_tags:
                # Show tag detection feedback but don't add them to tags
                QMessageBox.information(self, "Tags Detected", 
                    f"Auto-detected tags in content: {', '.join(detected_tags)}\n"
                    f"Explicitly entered tags: {tags}\n"
                    f"Note: Auto-detected tags remain in content, only explicit tags appear at bottom.")
        
        # Format entry with only explicitly entered tags at the end
        entry_lines = []
        
        if title:
            entry_lines.append(f"# {title}")
            entry_lines.append("")
        
        entry_lines.append(content)
        
        # Add only explicitly entered tags at the end
        if tags:
            tag_list = [tag.strip() for tag in tags.split() if tag.strip()]
            if tag_list:
                entry_lines.append("")
                entry_lines.append(f"{' '.join([f'@{tag}' for tag in tag_list])}")
        
        entry_content = "\n".join(entry_lines)
        
        self.result = {
            "title": title,
            "tags": tags,
            "content": content,
            "entry_content": entry_content
        }
        
        self.accept()
    
    def cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.reject()

class SearchDialog(QDialog):
    """Dialog for searching journal entries"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setWindowTitle("Search Entries")
        self.setModal(True)
        self.resize(800, 600)
        
        # Center the dialog
        screen = self.screen()
        if screen:
            self.setGeometry(
                (screen.size().width() - 800) // 2,
                (screen.size().height() - 600) // 2,
                800, 600
            )
        
        self.search_results = []
        self.create_widgets()
    
    def create_widgets(self):
        layout = QVBoxLayout()
        
        # Search frame
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout()
        
        # Search input
        search_label = QLabel("Search:")
        search_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        search_layout.addWidget(search_label)
        
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Enter search terms...")
        search_layout.addWidget(self.search_entry)
        
        # Search options
        options_layout = QHBoxLayout()
        self.case_sensitive_check = QCheckBox("Case Sensitive")
        options_layout.addWidget(self.case_sensitive_check)
        options_layout.addStretch()
        
        self.search_btn = QPushButton("Search")
        self.search_btn.setStyleSheet("background-color: #007bff; color: white; padding: 8px 16px;")
        self.search_btn.clicked.connect(self.perform_search)
        options_layout.addWidget(self.search_btn)
        
        search_layout.addLayout(options_layout)
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Results
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.view_selected)
        results_layout.addWidget(self.results_list)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.view_btn = QPushButton("View Selected")
        self.view_btn.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px;")
        self.view_btn.clicked.connect(self.view_selected)
        button_layout.addWidget(self.view_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 16px;")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Connect Enter key to search
        self.search_entry.returnPressed.connect(self.perform_search)
    
    def perform_search(self):
        """Perform the search"""
        query = self.search_entry.text().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a search term.")
            return
        
        # Clear previous results
        self.results_list.clear()
        self.search_results = []
        
        settings = load_settings()
        
        # Search through all journal files
        files = get_daily_files()
        for filename in files:
            content = read_daily_file(filename)
            if content:
                entries = self.parse_entries_from_content(content, filename)
                for entry in entries:
                    search_text = f"{entry['title']} {entry['content']} {entry['tags']}"
                    if not self.case_sensitive_check.isChecked():
                        search_text = search_text.lower()
                        query = query.lower()
                    
                    if query in search_text:
                        self.search_results.append(entry)
                        # Create display text
                        display_text = f"{entry['title']} - {entry['date']}"
                        if entry['tags']:
                            display_text += f" [{entry['tags']}]"
                        item = QListWidgetItem(display_text)
                        self.results_list.addItem(item)
        
        if not self.search_results:
            self.results_list.addItem("No results found.")
    
    def parse_entries_from_content(self, content, filename):
        """Parse individual entries from file content"""
        entries = []
        lines = content.split('\n')
        current_entry = {"title": "", "content": "", "tags": "", "date": filename.replace('.md', '')}
        
        for line in lines:
            if line.startswith('[20') and ']' in line:  # Timestamp line
                if current_entry["content"]:  # Save previous entry
                    # Extract tags from the end of content
                    content_text = current_entry["content"].strip()
                    tags = self.extract_tags_from_end_of_content(content_text)
                    current_entry["content"] = content_text
                    current_entry["tags"] = tags
                    entries.append(current_entry.copy())
                    current_entry = {"title": "", "content": "", "tags": "", "date": filename.replace('.md', '')}
                
                # Extract content after timestamp
                timestamp_end = line.find(']') + 1
                content_part = line[timestamp_end:].strip()
                if content_part:
                    current_entry["content"] = content_part
            elif line.startswith('# ') and not current_entry["title"]:
                current_entry["title"] = line[2:].strip()
            elif line.strip() and not line.startswith('**Tags:**'):
                if current_entry["content"]:
                    current_entry["content"] += "\n" + line
                else:
                    current_entry["content"] = line
        
        # Add last entry
        if current_entry["content"]:
            # Extract tags from the end of content
            content_text = current_entry["content"].strip()
            tags = self.extract_tags_from_end_of_content(content_text)
            current_entry["content"] = content_text
            current_entry["tags"] = tags
            entries.append(current_entry)
        
        return entries
    
    def extract_tags_from_end_of_content(self, content):
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
                tags.extend(reversed(line_tags))  # Reverse to maintain order
                break
            elif line.startswith('#'):
                # Found a header, stop looking
                break
            else:
                # This line doesn't contain tags, stop looking
                break
        
        return ", ".join(reversed(tags))  # Reverse again to get original order
    
    def view_selected(self):
        """View the selected result"""
        current_row = self.results_list.currentRow()
        if 0 <= current_row < len(self.search_results):
            entry = self.search_results[current_row]
            if self.parent_widget and hasattr(self.parent_widget, 'show_file_content'):
                self.parent_widget.show_file_content(entry['date'] + '.md', entry['content'], readonly=True)
        else:
            QMessageBox.information(self, "Info", "No result selected.")

class SettingsDialog(QDialog):
    """Dialog for application settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 500)
        
        # Center the dialog
        screen = self.screen()
        if screen:
            self.setGeometry(
                (screen.size().width() - 600) // 2,
                (screen.size().height() - 500) // 2,
                600, 500
            )
        
        self.settings = load_settings()
        self.create_widgets()
    
    def create_widgets(self):
        layout = QVBoxLayout()
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Journal Directory
        dir_group = QGroupBox("Journal Directory")
        dir_layout = QVBoxLayout()
        
        dir_layout.addWidget(QLabel("Journal Directory:"))
        
        dir_input_layout = QHBoxLayout()
        self.dir_entry = QLineEdit()
        self.dir_entry.setText(self.settings["journal_directory"])
        dir_input_layout.addWidget(self.dir_entry)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_journal_dir)
        dir_input_layout.addWidget(self.browse_btn)
        
        dir_layout.addLayout(dir_input_layout)
        dir_group.setLayout(dir_layout)
        scroll_layout.addWidget(dir_group)
        
        # Backup Directory
        backup_group = QGroupBox("Backup Directory")
        backup_layout = QVBoxLayout()
        
        backup_layout.addWidget(QLabel("Backup Directory:"))
        self.backup_entry = QLineEdit()
        self.backup_entry.setText(self.settings["backup_directory"])
        backup_layout.addWidget(self.backup_entry)
        
        backup_group.setLayout(backup_layout)
        scroll_layout.addWidget(backup_group)
        
        # Editor Settings
        editor_group = QGroupBox("Editor Settings")
        editor_layout = QVBoxLayout()
        
        editor_layout.addWidget(QLabel("Default Editor:"))
        self.editor_entry = QLineEdit()
        self.editor_entry.setText(self.settings["default_editor"])
        editor_layout.addWidget(self.editor_entry)
        
        editor_layout.addWidget(QLabel("Date Format:"))
        self.date_entry = QLineEdit()
        self.date_entry.setText(self.settings["date_format"])
        editor_layout.addWidget(self.date_entry)
        
        editor_group.setLayout(editor_layout)
        scroll_layout.addWidget(editor_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.auto_save_check = QCheckBox("Auto Save")
        self.auto_save_check.setChecked(self.settings["auto_save"])
        options_layout.addWidget(self.auto_save_check)
        
        self.auto_backup_check = QCheckBox("Auto Backup")
        self.auto_backup_check.setChecked(self.settings["auto_backup"])
        options_layout.addWidget(self.auto_backup_check)
        
        self.auto_detect_tags_check = QCheckBox("Auto Detect Tags")
        self.auto_detect_tags_check.setChecked(self.settings["auto_detect_tags"])
        options_layout.addWidget(self.auto_detect_tags_check)
        
        options_group.setLayout(options_layout)
        scroll_layout.addWidget(options_group)
        
        # Appearance Settings
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout()
        
        appearance_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        current_theme = self.settings.get("theme", "system").capitalize()
        if current_theme == "System":
            self.theme_combo.setCurrentText("System")
        elif current_theme == "Light":
            self.theme_combo.setCurrentText("Light")
        elif current_theme == "Dark":
            self.theme_combo.setCurrentText("Dark")
        appearance_layout.addWidget(self.theme_combo)
        
        appearance_group.setLayout(appearance_layout)
        scroll_layout.addWidget(appearance_group)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px;")
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.setStyleSheet("background-color: #ffc107; color: black; padding: 8px 16px;")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 16px;")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def browse_journal_dir(self):
        """Browse for journal directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Journal Directory", self.settings["journal_directory"])
        if directory:
            self.dir_entry.setText(directory)
    
    def save_settings(self):
        """Save the settings"""
        self.settings.update({
            "journal_directory": self.dir_entry.text(),
            "backup_directory": self.backup_entry.text(),
            "default_editor": self.editor_entry.text(),
            "date_format": self.date_entry.text(),
            "auto_save": self.auto_save_check.isChecked(),
            "auto_backup": self.auto_backup_check.isChecked(),
            "auto_detect_tags": self.auto_detect_tags_check.isChecked(),
            "theme": self.theme_combo.currentText().lower()
        })
        
        save_settings(self.settings)
        QMessageBox.information(self, "Success", "Settings saved successfully!")
        self.accept()
    
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        self.settings = DEFAULT_SETTINGS.copy()
        save_settings(self.settings)
        QMessageBox.information(self, "Success", "Settings reset to defaults!")
        self.accept()

class FileViewerDialog(QDialog):
    """Dialog for viewing/editing file content"""
    
    def __init__(self, parent=None, filename="", content="", readonly=False):
        super().__init__(parent)
        self.setWindowTitle(f"{'View' if readonly else 'Edit'}: {filename}")
        self.setModal(True)
        self.resize(800, 600)
        
        # Center the dialog
        screen = self.screen()
        if screen:
            self.setGeometry(
                (screen.size().width() - 800) // 2,
                (screen.size().height() - 600) // 2,
                800, 600
            )
        
        self.filename = filename
        self.create_widgets(content, readonly)
    
    def create_widgets(self, content, readonly):
        layout = QVBoxLayout()
        
        # Content text area
        self.text_area = QTextEdit()
        self.text_area.setPlainText(content)
        if readonly:
            self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)
        
        # Buttons
        if not readonly:
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            self.save_btn = QPushButton("Save")
            self.save_btn.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px;")
            self.save_btn.clicked.connect(self.save_file)
            button_layout.addWidget(self.save_btn)
            
            layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_file(self):
        """Save the file"""
        new_content = self.text_area.toPlainText()
        write_daily_file(self.filename, new_content)
        QMessageBox.information(self, "Success", "File saved successfully!")
        self.accept()

class DailyJournalPyQt6(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Load settings
        self.settings = load_settings()
        
        # Configure window
        self.setWindowTitle("Daily Journal - PyQt6")
        self.setGeometry(100, 100, self.settings["window_width"], self.settings["window_height"])
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QHBoxLayout(central_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - File list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File list title
        file_title = QLabel("Journal Files")
        file_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        left_layout.addWidget(file_title)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.view_selected_file)
        # Connect single selection
        self.file_list.itemSelectionChanged.connect(self.show_selected_file_in_editor)
        left_layout.addWidget(self.file_list)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Main content
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Quick Actions
        actions_title = QLabel("Quick Actions")
        actions_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        right_layout.addWidget(actions_title)
        
        # Quick action buttons
        actions_layout = QGridLayout()
        
        self.new_entry_btn = QPushButton("New Entry")
        self.new_entry_btn.setStyleSheet("QPushButton { padding: 12px; font-size: 12px; }")
        self.new_entry_btn.clicked.connect(self.new_entry)
        actions_layout.addWidget(self.new_entry_btn, 0, 0)
        
        self.edit_today_btn = QPushButton("Edit Today")
        self.edit_today_btn.setStyleSheet("QPushButton { padding: 12px; font-size: 12px; }")
        self.edit_today_btn.clicked.connect(self.edit_today)
        actions_layout.addWidget(self.edit_today_btn, 0, 1)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.setStyleSheet("QPushButton { padding: 12px; font-size: 12px; }")
        self.search_btn.clicked.connect(self.search_entries)
        actions_layout.addWidget(self.search_btn, 0, 2)
        
        self.view_btn = QPushButton("View Selected")
        self.view_btn.setStyleSheet("QPushButton { padding: 12px; font-size: 12px; }")
        self.view_btn.clicked.connect(self.view_selected_file)
        actions_layout.addWidget(self.view_btn, 1, 0)
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.setStyleSheet("QPushButton { padding: 12px; font-size: 12px; }")
        self.edit_btn.clicked.connect(self.edit_selected_file)
        actions_layout.addWidget(self.edit_btn, 1, 1)
        
        self.external_btn = QPushButton("External Editor")
        self.external_btn.setStyleSheet("QPushButton { padding: 12px; font-size: 12px; }")
        self.external_btn.clicked.connect(self.open_external_editor)
        actions_layout.addWidget(self.external_btn, 1, 2)
        
        right_layout.addLayout(actions_layout)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")
        right_layout.addWidget(self.status_label)
        
        # Settings button
        settings_btn = QPushButton("Settings")
        settings_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 16px;")
        settings_btn.clicked.connect(self.show_settings)
        right_layout.addWidget(settings_btn)
        
        # --- New: Inline file editor below status/settings ---
        self.inline_filename_label = QLabel("")
        self.inline_filename_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addWidget(self.inline_filename_label)
        
        self.inline_editor = QTextEdit()
        self.inline_editor.setPlaceholderText("Select a file to view and edit its content here...")
        self.inline_editor.setFont(QFont(self.settings.get("font_family", "Consolas"), self.settings.get("font_size", 11)))
        right_layout.addWidget(self.inline_editor)
        
        self.inline_save_btn = QPushButton("Save Changes")
        self.inline_save_btn.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px;")
        self.inline_save_btn.clicked.connect(self.save_inline_editor)
        right_layout.addWidget(self.inline_save_btn)
        self.inline_editor.setEnabled(False)
        self.inline_save_btn.setEnabled(False)
        self.inline_filename_label.setVisible(False)
        
        right_layout.addStretch()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 900])
        
        # Create menu bar
        self.create_menu()
        
        # Initial load
        self.refresh_file_list()
        self.update_status()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_file_list)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def create_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()
        if menubar is None:
            return
        
        # File menu
        file_menu = menubar.addMenu('File')
        if file_menu is None:
            return
        
        new_action = QAction('New Entry', self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_entry)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        if tools_menu is None:
            return
        
        search_action = QAction('Search', self)
        search_action.setShortcut(QKeySequence.StandardKey.Find)
        search_action.triggered.connect(self.search_entries)
        tools_menu.addAction(search_action)
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
    
    def update_status(self):
        """Update status bar"""
        files = get_daily_files()
        today_file = get_today_filename()
        has_today = today_file in files
        
        status_text = f"Files: {len(files)} | Today: {'✓' if has_today else '✗'}"
        self.status_label.setText(status_text)
    
    def refresh_file_list(self):
        """Refresh the file list"""
        self.file_list.clear()
        files = get_daily_files()
        today_file = get_today_filename()
        
        for filename in files:
            display_name = filename.replace('.md', '')
            if filename == today_file:
                display_name += " (Today)"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, filename)
            self.file_list.addItem(item)
        
        self.update_status()
    
    def new_entry(self):
        """Create a new journal entry"""
        dialog = EntryDialog(self, "New Entry")
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.result:
            today_file = get_today_filename()
            append_to_daily_file(today_file, dialog.result["entry_content"])
            self.refresh_file_list()
            QMessageBox.information(self, "Success", "Entry added successfully!")
    
    def view_selected_file(self):
        """View the selected file"""
        current_item = self.file_list.currentItem()
        if current_item:
            filename = current_item.data(Qt.ItemDataRole.UserRole)
            content = read_daily_file(filename)
            dialog = FileViewerDialog(self, filename, content, readonly=True)
            dialog.exec()
        else:
            QMessageBox.information(self, "Info", "No file selected.")
    
    def edit_selected_file(self):
        """Edit the selected file"""
        current_item = self.file_list.currentItem()
        if current_item:
            filename = current_item.data(Qt.ItemDataRole.UserRole)
            content = read_daily_file(filename)
            dialog = FileViewerDialog(self, filename, content, readonly=False)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_file_list()
        else:
            QMessageBox.information(self, "Info", "No file selected.")
    
    def edit_today(self):
        """Edit today's journal"""
        today_file = get_today_filename()
        content = read_daily_file(today_file)
        dialog = FileViewerDialog(self, today_file, content, readonly=False)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_file_list()
    
    def show_file_content(self, filename, content, readonly=False):
        """Show file content in a dialog"""
        dialog = FileViewerDialog(self, filename, content, readonly)
        dialog.exec()
    
    def search_entries(self):
        """Open search dialog"""
        dialog = SearchDialog(self)
        dialog.exec()
    
    def open_external_editor(self):
        """Open external editor"""
        current_item = self.file_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Info", "No file selected.")
            return
        
        filename = current_item.data(Qt.ItemDataRole.UserRole)
        filepath = os.path.join(self.settings["journal_directory"], filename)
        
        try:
            subprocess.Popen([self.settings["default_editor"], filepath])
            QMessageBox.information(self, "Success", f"Opened {filename} in {self.settings['default_editor']}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open editor: {e}")
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reload settings
            self.settings = load_settings()
            # Apply theme immediately
            theme = self.settings.get("theme", "system")
            apply_theme(QApplication.instance(), theme)
    
    def show_selected_file_in_editor(self):
        current_item = self.file_list.currentItem()
        if current_item:
            filename = current_item.data(Qt.ItemDataRole.UserRole)
            content = read_daily_file(filename)
            self.inline_filename_label.setText(f"Editing: {filename}")
            self.inline_editor.setPlainText(content)
            self.inline_editor.setEnabled(True)
            self.inline_save_btn.setEnabled(True)
            self.inline_filename_label.setVisible(True)
        else:
            self.inline_filename_label.setText("")
            self.inline_editor.clear()
            self.inline_editor.setEnabled(False)
            self.inline_save_btn.setEnabled(False)
            self.inline_filename_label.setVisible(False)

    def save_inline_editor(self):
        current_item = self.file_list.currentItem()
        if current_item:
            filename = current_item.data(Qt.ItemDataRole.UserRole)
            new_content = self.inline_editor.toPlainText()
            write_daily_file(filename, new_content)
            QMessageBox.information(self, "Success", f"Saved changes to {filename}")
            self.refresh_file_list()
    
    def closeEvent(self, event):
        """Handle window closing"""
        # Save window size
        self.settings["window_width"] = self.width()
        self.settings["window_height"] = self.height()
        save_settings(self.settings)
        event.accept()

def apply_theme(app, theme="system"):
    """Apply theme to the application"""
    if theme == "dark":
        # Dark theme palette
        dark_palette = QPalette()
        
        # Set dark colors
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(dark_palette)
        
        # Set dark stylesheet for additional styling
        app.setStyleSheet("""
            QMainWindow {
                background-color: #353535;
                color: #ffffff;
            }
            QWidget {
                background-color: #353535;
                color: #ffffff;
            }
            QTextEdit, QLineEdit {
                background-color: #191919;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QTextEdit:focus, QLineEdit:focus {
                border: 1px solid #2a82da;
            }
            QPushButton {
                background-color: #555555;
                color: #ffffff;
                border: 1px solid #777777;
                border-radius: 3px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QListWidget {
                background-color: #191919;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                alternate-background-color: #252525;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:selected {
                background-color: #2a82da;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #444444;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #555555;
                background-color: #191919;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #2a82da;
                background-color: #2a82da;
            }
            QScrollBar:vertical {
                background-color: #353535;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QComboBox {
                background-color: #191919;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox:focus {
                border: 1px solid #2a82da;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #191919;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #2a82da;
            }
        """)
        
    elif theme == "light":
        # Light theme - use system default
        app.setPalette(app.style().standardPalette())
        app.setStyleSheet("")
        
    else:  # system theme
        # Use system theme - no custom styling
        app.setPalette(app.style().standardPalette())
        app.setStyleSheet("")

def main():
    """Main function"""
    ensure_directories()
    
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Load settings and apply theme
    settings = load_settings()
    theme = settings.get("theme", "system")
    apply_theme(app, theme)
    
    # Create and show main window
    window = DailyJournalPyQt6()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 