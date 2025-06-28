# Daily Journal - Terminal Journal Application

A powerful, feature-rich terminal-based journaling application built with Python and curses. Perfect for daily journaling with multiple entries per day, advanced search functionality, export capabilities, and a clean terminal interface.

![Daily Journal](https://img.shields.io/badge/version-1.1-blue) ![Python](https://img.shields.io/badge/python-3.6+-green) ![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey) ![License](https://img.shields.io/badge/license-open--source-brightgreen)

## ✨ Features Overview

### 📝 **Writing & Entry Management**
- **Multiple Writing Modes**: Terminal editor with real-time word count, external editor support
- **Multiple Entries Per Day**: All entries from the same day stored in one organized file
- **Entry Templates**: 6 pre-built templates for different journaling needs
- **Auto-Tag Detection**: Intelligent tag extraction with configurable prefixes (#, @)
- **Individual Entry Access**: Read, edit, and manage specific entries independently
- **Automatic Timestamps**: Entries automatically timestamped with customizable formats

### 🔍 **Advanced Search & Organization**
- **Basic Search**: Find entries by title, content, or tags with match highlighting
- **Advanced Search Suite**:
  - **Date Range Search**: Filter entries between specific dates
  - **Tag-Only Search**: Search exclusively by tags with flexible matching
  - **Content Length Search**: Filter by word count (short/medium/long/custom)
  - **Regular Expression Search**: Power user pattern matching
- **Enhanced Results**: Entry previews and multiple action options (read, edit, copy)

### 🏷️ **Tag Management & Analytics**
- **Auto-Tag Detection**: Configurable prefixes with intelligent extraction
- **Tag Statistics**: Comprehensive analytics including usage counts and trends
- **Tag Viewing**: Browse all tags with scrollable interface
- **Most Used Tags**: Frequency ranking and analysis
- **Tag Operations**: Foundation for rename, merge, and cleanup (coming soon)

### 📤📥 **Export & Import System**
- **Export Formats**:
  - **PDF**: Professional formatting with fallback generation tools
  - **HTML**: Beautiful responsive design with CSS styling
  - **Text**: Clean, readable plain text format
- **Export Filters**: All entries, date ranges, or by specific tags
- **Import Sources**:
  - **Text Files**: Import plain text as journal entries
  - **Markdown Files**: Intelligent entry detection and parsing
  - **JSON**: Structured data with title/content/tags
  - **Batch Import**: Process entire directories automatically

### 📊 **Analytics & Statistics**
- **Writing Statistics**: Total words, entries, files with detailed breakdowns
- **Recent Activity**: Monitor writing frequency and habits (last 7 days)
- **Real-time Tracking**: Word count during writing, live statistics in status bar
- **Usage Analytics**: Entry patterns, tag usage, and writing insights

### 💾 **Backup & Settings**
- **Automatic Backups**: Files backed up before changes with configurable frequency
- **Manual Backup**: Create backups on demand with progress feedback
- **Settings Management**: Export/import configuration, customizable preferences
- **Debug Tools**: Comprehensive debugging suite for troubleshooting

### 🎮 **User Experience**
- **Keyboard Shortcuts**: Platform-specific shortcuts with Mac/Linux/Windows support
- **Status Bar**: Real-time information about current file and statistics
- **Help System**: Built-in help overlay (Ctrl+H) with shortcut reference
- **Cross-platform**: Clipboard integration, file operations, terminal compatibility

## 🚀 Installation

### Prerequisites
- **Python 3.6 or higher**
- **Terminal with curses support** (most Unix-like systems and Windows with WSL)

### Quick Install

1. **Clone or download** the `daily_journal.py` file:
   ```bash
   git clone <repository-url>
   cd daily-journal
   ```

2. **Run the application**:
   ```bash
   python3 daily_journal.py
   ```

3. **Test the installation** (optional):
   ```bash
   python3 test_tag_detection.py
   ```

### Dependencies
The application uses only **Python standard library** modules:
- `curses` - Terminal interface
- `os`, `shutil` - File operations  
- `json` - Settings management
- `datetime` - Date handling
- `subprocess` - External editor support
- `re` - Regular expressions for search

**No external dependencies required** for core functionality.

## 📖 Usage Guide

### Quick Start

1. **Launch the application**:
   ```bash
   python3 daily_journal.py
   ```

2. **Create your first entry**:
   - Press `Ctrl+N` for a blank entry, or
   - Press `Ctrl+T` to use a template
   - Enter a title (auto-filled with current timestamp)
   - Add tags (optional, supports auto-detection)
   - Write your content
   - Press `Ctrl+D` when finished

3. **Navigate the interface**:
   - Use ↑/↓ arrow keys to navigate menus
   - Press Enter or Space to select options
   - Press ESC to go back or cancel
   - Press `Ctrl+H` for help at any time

### Writing Entries

#### **Blank Entry (Quick)**
- **Shortcut**: `Ctrl+N`
- **Use for**: Quick thoughts, daily notes, spontaneous writing
- **Features**: Real-time word count, auto-timestamps, tag detection

#### **Template Entry (Structured)**
- **Shortcut**: `Ctrl+T`
- **Available Templates**:
  - **Daily Reflection**: Morning/evening thoughts with gratitude prompts
  - **Meeting Notes**: Structured meeting documentation with action items
  - **Ideas**: Creative thoughts and brainstorming with categorization
  - **Goals**: Goal setting and progress tracking with milestones
  - **Learning**: Study notes and insights with knowledge tracking
  - **Gratitude**: Daily gratitude practice with reflection prompts

#### **External Editor**
- **Use for**: Longer entries, complex formatting
- **Editors**: nano, vim, VS Code, any configured editor
- **Features**: Full editor capabilities, automatic import

### Advanced Search

#### **Basic Search** (`Ctrl+F`)
- Search across titles, content, and tags
- Match highlighting shows exactly where terms were found
- Entry previews in results

#### **Advanced Search Menu**
Access comprehensive search options:

1. **Date Range Search**:
   ```
   Start date: 2024-01-01
   End date: 2024-01-31
   Optional keyword: meeting
   ```

2. **Tag-Only Search**:
   ```
   Tags to find: work, project, important
   ```

3. **Content Length Search**:
   - **Short**: < 100 words
   - **Medium**: 100-500 words  
   - **Long**: > 500 words
   - **Custom**: Specify exact range

4. **Regular Expression Search**:
   ```
   Pattern: \b(goal|objective|target)\b
   ```

### Export & Import

#### **Export Options**
Access via main menu → "📤 Export Entries":

1. **Export All Entries**:
   - **PDF**: Professional document with styling
   - **HTML**: Web-ready format with responsive design
   - **Text**: Plain text for maximum compatibility

2. **Export Date Range**:
   - Specify start and end dates
   - Include optional keyword filtering
   - All formats available

3. **Export by Tags**:
   - Filter by specific tags
   - Comma-separated tag list
   - Flexible matching

#### **Import Options**
Access via main menu → "📥 Import Entries":

1. **Text Files**: Import any `.txt` file as a journal entry
2. **Markdown Files**: Auto-detect existing journal format vs. new content
3. **JSON Export**: Import structured data with title/content/tags
4. **Batch Import**: Process entire directories of files

#### **Export Directory**
- **Default**: `~/journal/exports`
- **Configurable**: Change in Settings → Export Directory
- **Auto-created**: Directory created automatically if needed

### Tag Management

#### **Viewing Tags**
- **All Tags**: Browse complete tag list with scroll navigation
- **Tag Statistics**: View usage counts, averages, and analytics
- **Most Used Tags**: See frequency ranking with usage counts

#### **Auto-Tag Detection**
- **Configurable Prefixes**: Default `#` and `@`, customizable in settings
- **Auto-Merge**: Detected tags merged with manually entered tags
- **Settings Control**: Enable/disable detection, customize behavior

#### **Tag Analytics**
- Total unique tags count
- Total tag usage across all entries  
- Average tags per entry
- Top 10 most used tags with frequencies

### Statistics & Analytics

Access via main menu → "📊 Journal Statistics":

#### **Overview Statistics**
- **Total Files**: Number of daily journal files
- **Total Entries**: Count of individual entries
- **Total Words**: Cumulative word count across all entries
- **Recent Activity**: Writing frequency in last 7 days

#### **Real-time Tracking**
- **Status Bar**: Live file and entry counts
- **Word Count**: Real-time counting during writing
- **Writing Progress**: Track daily writing habits

### File Management

#### **File Structure**
```
~/journal/daily/               # Main journal files
├── 2024-01-15.md             # Daily files with multiple entries
├── 2024-01-16.md
└── 2024-01-17.md

~/journal/backups/            # Automatic backups
├── backup_20240115_143022/   # Full backup folders
├── 20240115_143022_2024-01-15.md  # Individual file backups
└── ...

~/journal/exports/            # Export output
├── journal_export_all_20240115_143022.pdf
├── journal_export_work_tags_20240115_143022.html
└── ...
```

#### **Entry Format**
Each daily file contains multiple entries:

```markdown
# [2024-01-15 14:30:00] Morning Reflection

tags: reflection, morning, gratitude

This morning I'm feeling grateful for...

## Today's Goals
- [ ] Complete project documentation
- [ ] Review team feedback
- [ ] Plan evening routine

# [2024-01-15 18:45:10] Work Meeting Notes

tags: work, meeting, project-alpha

**Meeting**: Project Alpha Review
**Attendees**: John, Sarah, Mike
**Date**: 2024-01-15

## Action Items
- [ ] Update project timeline
- [ ] Schedule follow-up meeting
- [ ] Share meeting notes with team
```

## ⚙️ Configuration

### Settings Menu
Access with `Ctrl+S` or through the main menu:

#### **Core Settings**
- **Journal Directory**: Where your journal files are stored
- **Backup Directory**: Where backups are saved  
- **Export Directory**: Where exported files are saved
- **Default Editor**: External editor for Editor Mode
- **Date Format**: How dates are formatted in filenames

#### **Advanced Settings**
- **Auto Backup**: Enable/disable automatic backups
- **Backup Frequency**: Daily, weekly, or monthly backups
- **Auto-Save Interval**: Automatic saving frequency (seconds)
- **Tag Detection**: Enable auto-detection of tags
- **Tag Prefixes**: Configurable tag markers (#, @, etc.)
- **Mac Keyboard Shortcuts**: Platform-specific shortcuts

#### **Display Settings**
- **Show Word Count**: Real-time word counting
- **Show Entry Count**: Entry count in status bar
- **Confirm Delete**: Confirmation dialogs for destructive actions

### Default Settings
```json
{
  "journal_directory": "~/journal/daily",
  "backup_directory": "~/journal/backups", 
  "export_directory": "~/journal/exports",
  "default_editor": "nano",
  "date_format": "%Y-%m-%d",
  "auto_backup": true,
  "backup_frequency": "daily",
  "auto_detect_tags": true,
  "tag_prefixes": ["#", "@"],
  "merge_detected_tags": true,
  "mac_keyboard_shortcuts": true,
  "auto_save_interval": 300,
  "show_word_count": true,
  "show_entry_count": true,
  "confirm_delete": true
}
```

### Settings Export/Import
- **Export**: Settings → "Export Settings" (saves to `~/daily_journal_settings_export.json`)
- **Import**: Settings → "Import Settings" (loads from `~/daily_journal_settings_export.json`)

## ⌨️ Keyboard Shortcuts

### Global Shortcuts
| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+N` | New Blank Entry | Quick entry creation |
| `Ctrl+T` | New Template Entry | Structured entry with templates |
| `Ctrl+O` | Edit Today's Journal | Quick access to today's entries |
| `Ctrl+F` | Search Entries | Basic search functionality |
| `Ctrl+B` | Create Backup | Manual backup creation |
| `Ctrl+S` | Settings | Open settings menu |
| `Ctrl+H` | Help | Show help overlay |
| `ESC` | Go Back/Cancel | Navigation and cancellation |

### Navigation
| Key | Action |
|-----|--------|
| `↑/↓` | Navigate menus |
| `Enter/Space` | Select option |
| `Page Up/Down` | Scroll by page |
| `Home/End` | Jump to start/end |

### Writing Mode
| Shortcut | Action |
|----------|--------|
| `Ctrl+D` | Finish Entry | Complete and save entry |
| `Ctrl+S` | Save | Save current changes |
| `Ctrl+Q` | Quit | Exit without saving |
| `Ctrl+A/E` | Line Start/End | Move cursor to line boundaries |
| `Ctrl+Left/Right` | Word Navigation | Move by words |

### Platform-Specific
- **macOS**: Optimized shortcuts that don't conflict with system shortcuts
- **Linux**: Standard terminal shortcuts
- **Windows**: WSL-compatible shortcuts

## 🛠️ Advanced Features

### Debug Tools
Access via Settings → Debug Tools:

- **Journal Directory Info**: Analyze journal folder and files
- **Parse Entries Debug**: Test entry parsing and detection
- **Tag Detection Test**: Validate tag auto-detection
- **Keyboard Shortcuts Test**: Verify platform-specific shortcuts
- **Create Test File**: Generate sample content for testing

### Performance Optimization
- **Lazy Loading**: Efficient handling of large entry collections
- **Caching**: Smart caching for frequently accessed data
- **Memory Management**: Optimized memory usage for long sessions

### Cross-Platform Features
- **Clipboard Integration**: Copy entries to system clipboard
- **File Manager Integration**: Open journal folder in system file manager
- **Terminal Compatibility**: Works across different terminal emulators

## 📋 Tips & Best Practices

### Organizing Your Journal

#### **Effective Tagging**
- **Use consistent tag naming**: `work`, `personal`, `health`
- **Leverage auto-detection**: Write `#meeting` or `@project` naturally
- **Multiple tags per entry**: `work, meeting, project-alpha, quarterly-review`
- **Tag analytics**: Review most-used tags to refine your system

#### **Entry Templates Usage**
- **Daily Reflection**: Start/end of day routine
- **Meeting Notes**: Professional documentation
- **Ideas**: Capture creative thoughts with context
- **Goals**: Track progress with measurable outcomes
- **Learning**: Document insights and knowledge
- **Gratitude**: Build positive habits with structured prompts

#### **Search Strategies**
- **Date Range**: Find entries from specific time periods
- **Tag Combinations**: Use multiple tags for precise filtering
- **Content Length**: Find quick notes vs. detailed entries
- **Regex Patterns**: Advanced users can use complex pattern matching

### Efficient Workflows

#### **Daily Routine**
1. **Morning**: Use Daily Reflection template
2. **Throughout day**: Quick blank entries (`Ctrl+N`) for thoughts
3. **Meetings**: Meeting Notes template for documentation
4. **Evening**: Review day with Gratitude template

#### **Weekly Review**
1. **Search last 7 days**: Use date range search
2. **Review tag usage**: Check tag statistics
3. **Export important entries**: Create backups of key insights
4. **Clean up**: Review and organize older entries

#### **Monthly Archive**
1. **Export month's entries**: Use date range export to PDF/HTML
2. **Backup settings**: Export configuration
3. **Review analytics**: Check writing statistics and patterns
4. **Update templates**: Refine templates based on usage

### Advanced Usage

#### **Power User Features**
- **Regex Search**: Complex pattern matching for advanced queries
- **Batch Import**: Migrate from other journaling apps
- **Tag Analytics**: Understand writing patterns and habits
- **Export Automation**: Regular exports for backup and sharing

#### **Integration with Other Tools**
- **File Sync**: Use cloud storage for journal directory
- **External Editors**: Integrate with VS Code, Obsidian, etc.
- **Automation**: Script regular backups and exports
- **Data Analysis**: Export to analyze writing patterns

## 🚦 Troubleshooting

### Common Issues

#### **Installation Problems**
```bash
# If python command not found
python3 daily_journal.py

# Check Python version
python3 --version
```

#### **Permission Issues**
```bash
# Make executable
chmod +x daily_journal.py

# Check journal directory permissions
ls -la ~/journal/
```

#### **Terminal Display Issues**
- **Resize terminal**: Ensure adequate window size (80x24 minimum)
- **Terminal compatibility**: Use modern terminal emulator
- **Unicode support**: Ensure terminal supports UTF-8

#### **Keyboard Shortcuts Not Working**
- **Terminal conflicts**: Some terminals intercept certain Ctrl combinations
- **Mac users**: Enable Mac keyboard shortcuts in settings
- **Alternative**: Use menu navigation instead of shortcuts

#### **Export Issues**
```bash
# PDF export requirements (optional)
pip install weasyprint
# OR
sudo apt install wkhtmltopdf
# OR ensure Chrome/Chromium installed for headless PDF generation
```

#### **Import/Export Errors**
- **File permissions**: Ensure read/write access to export directory
- **File encoding**: Use UTF-8 encoding for text files
- **Large files**: Memory limitations for very large imports

### Debug Information
Access comprehensive debugging via Settings → Debug Tools:
- View journal directory structure
- Test entry parsing functionality  
- Validate tag detection
- Check keyboard shortcut compatibility

### Getting Help
- Press `Ctrl+H` in the application for quick help
- Check Settings → Debug Tools for detailed diagnostics
- Review error messages in the status bar
- Test with Settings → Create Test File for validation

## 🏗️ Development

### Requirements
- **Python 3.6+**
- **curses library** (included with Python)
- **Standard library only** (no external dependencies)

### Architecture
```
daily_journal.py (4200+ lines)
├── Core Functions (file I/O, settings)
├── UI Components (menus, input, display)
├── Entry Management (parsing, templates)
├── Search System (basic, advanced, regex)
├── Export/Import System (PDF, HTML, text)
├── Tag Management (detection, analytics)
├── Statistics & Analytics
├── Backup System
└── Debug Tools
```

### Key Functions
- `main_menu()` - Main application loop and navigation
- `new_entry_with_template()` - Entry creation with template support
- `advanced_search_menu()` - Comprehensive search functionality
- `export_entries_menu()` - Export system with multiple formats
- `tag_management_menu()` - Tag analytics and management
- `parse_entries_from_content()` - Entry parsing and detection

### Testing
```bash
# Test tag detection
python3 test_tag_detection.py

# Debug mode (if implemented)
python3 daily_journal.py --debug
```

## 📊 Version History

### v1.1 (Current) - Major Feature Release
- ✅ **Export/Import System**: PDF, HTML, text export with filtering
- ✅ **Advanced Search**: Date range, tag, content length, regex search
- ✅ **Tag Management**: Auto-detection, analytics, statistics
- ✅ **Enhanced Templates**: 6 pre-built templates with customization
- ✅ **Platform Optimization**: Mac keyboard shortcuts, cross-platform features
- ✅ **Debug Tools**: Comprehensive debugging and validation suite

### v1.0 - Initial Release
- ✅ **Core Journaling**: Entry creation, editing, reading
- ✅ **Basic Search**: Title, content, tag search
- ✅ **File Management**: Daily files, backup system
- ✅ **Settings**: Configuration and customization
- ✅ **Terminal UI**: Curses-based interface with navigation

### Planned v1.2
- [ ] **Auto-Save**: Configurable auto-save during editing
- [ ] **Saved Searches**: Persistent search query storage
- [ ] **Enhanced Tag Operations**: Rename, merge, delete tags
- [ ] **Spell Check**: Basic spell checking in terminal editor

## 🤝 Contributing

### Areas for Contribution
- **Export Enhancements**: Additional format support (JSON, CSV)
- **Import Sources**: Day One, Journey, Obsidian integration
- **Performance**: Optimization for large datasets
- **Platform Support**: Windows native compatibility improvements
- **Documentation**: Screenshots, tutorials, video guides

### Development Guidelines
- **Python Standard Library Only**: Maintain zero-dependency core
- **Cross-Platform**: Ensure compatibility across Unix-like systems
- **Terminal Focus**: Preserve terminal-based simplicity
- **User Experience**: Prioritize ease of use and accessibility

## 📄 License

This project is open source. Feel free to modify and distribute as needed.

## 🙏 Acknowledgments

- Built with Python's built-in `curses` library for terminal interface
- Inspired by the need for a powerful yet simple terminal journaling solution
- Designed for daily use by writers, developers, thinkers, and anyone who values reflection
- Community-driven development with focus on user needs and feedback

---

**Happy Journaling! 📝✨**

*A terminal application that grows with your thoughts, powered by simplicity and enhanced by sophistication.*

**For questions, suggestions, or bug reports, please open an issue or contact the development team.**