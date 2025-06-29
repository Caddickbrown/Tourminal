# Daily Journal GUI

A tkinter-based graphical interface for the Daily Journal application. This is a trial version with core functionality while maintaining the same file format and settings as the terminal version.

## Features

### Core Functionality
- ✅ **Create New Entries**: Write journal entries with title, tags, and content
- ✅ **View Entries**: Read existing journal files and entries
- ✅ **Edit Entries**: Modify journal content in built-in or external editor
- ✅ **Search Entries**: Find entries by content, title, or tags
- ✅ **Auto-Tag Detection**: Automatically detect tags with # and @ prefixes
- ✅ **Settings Management**: Customize journal directory, fonts, and behavior

### GUI Features
- **File List**: Browse all journal files with size information
- **Quick Actions**: Easy access to common operations
- **External Editor Support**: Open files in your preferred text editor
- **Keyboard Shortcuts**: Efficient navigation with hotkeys
- **Status Display**: Real-time information about your journal

## Installation & Requirements

### Requirements
- Python 3.6 or higher
- tkinter (usually included with Python)
- No additional dependencies required

### Running the Application
```bash
python daily_journal_gui.py
```

## Interface Overview

### Main Window
- **Left Panel**: List of all journal files with file sizes
- **Right Panel**: Quick action buttons and status information
- **Menu Bar**: Full access to all features

### Key Components

#### File List
- Shows all `.md` files in your journal directory
- Double-click to view a file
- Use View/Edit buttons for selected files

#### Quick Actions
- **📝 New Entry**: Create a new journal entry
- **✏️ Edit Today**: Open today's journal file for editing
- **🔍 Search**: Search through all entries
- **⚙️ Settings**: Configure the application

## Usage Guide

### Creating Your First Entry
1. Click **"📝 New Entry"** or press `Ctrl+N`
2. Enter a title for your entry
3. Add tags (comma-separated)
4. Write your content in the text area
5. Click **"Save"** to save the entry

### Auto-Tag Detection
The application automatically detects tags in your content:
- Tags starting with `#` (hashtags)
- Tags starting with `@` (mentions)
- Click **"Auto-Detect Tags"** in the entry dialog

### Searching Entries
1. Click **"🔍 Search"** or press `Ctrl+F`
2. Enter your search term
3. Click **"Search"** to find matching entries
4. Double-click results to view entries

### Using External Editor
1. Click **"Open External Editor"** from File menu or press `Ctrl+O`
2. Your default editor will open today's journal file
3. Edit and save in the external editor

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Entry |
| `Ctrl+O` | Open External Editor |
| `Ctrl+F` | Search Entries |
| `Ctrl+,` | Settings |
| `Ctrl+Q` | Exit Application |
| `Ctrl+S` | Save (in dialogs) |

## Settings

Access settings via the menu or `Ctrl+,`:

### Journal Settings
- **Journal Directory**: Where your journal files are stored
- **Date Format**: How dates are formatted in filenames
- **Tag Prefixes**: Characters that indicate tags (default: #, @)

### Display Settings
- **Font Family**: Choose your preferred font
- **Font Size**: Adjust text size
- **Window Size**: Automatically saved

### Behavior Settings
- **Auto-detect Tags**: Automatically find tags in content
- **Merge Detected Tags**: Combine auto-detected with manual tags
- **Auto Backup**: Automatically backup journal files

## File Format

The GUI version uses the same file format as the terminal version:

```markdown
# [2024-01-15 14:30:25] My Entry Title

tags: personal, thoughts, important

This is the content of my journal entry.
I can write multiple paragraphs here.

# [2024-01-15 15:45:10] Another Entry

tags: work, meeting

Another entry in the same day's file.
```

## Compatibility

- **File Compatibility**: Full compatibility with terminal version files
- **Settings**: Uses separate GUI settings file (`.daily_journal_gui_settings.json`)
- **Journal Directory**: Can share the same journal directory with terminal version

## Troubleshooting

### Common Issues

**Application won't start**
- Ensure Python 3.6+ is installed
- Check that tkinter is available: `python -c "import tkinter"`

**Can't see journal files**
- Check the journal directory in Settings
- Ensure the directory exists and contains `.md` files

**External editor not working**
- Check the default editor setting
- Ensure the editor command is in your system PATH

### Default Locations
- **Journal Directory**: `~/journal/daily/`
- **Settings File**: `~/.daily_journal_gui_settings.json`
- **Backup Directory**: `~/journal/backups/`

## Feature Comparison: GUI vs Terminal

| Feature | GUI Version | Terminal Version |
|---------|-------------|------------------|
| Entry Creation | ✅ Dialog-based | ✅ Terminal input |
| File Viewing | ✅ Built-in viewer | ✅ Terminal pager |
| Search | ✅ Dialog with results | ✅ Interactive search |
| External Editor | ✅ One-click open | ✅ Configurable |
| Templates | ❌ Not implemented | ✅ Full support |
| Advanced Search | ❌ Basic only | ✅ Multiple filters |
| Export/Import | ❌ Not implemented | ✅ Multiple formats |
| Tag Management | ❌ Basic only | ✅ Advanced tools |
| Statistics | ❌ Basic info only | ✅ Detailed analytics |

## Planned Improvements

For future versions:
- [ ] Entry templates support
- [ ] Advanced search filters
- [ ] Export functionality
- [ ] Drag-and-drop file management
- [ ] Rich text formatting preview
- [ ] Calendar view integration
- [ ] Tag management tools

## Development Notes

This is a trial GUI version focusing on core functionality. The codebase is designed to be:
- **Lightweight**: Minimal dependencies
- **Compatible**: Works with existing journal files
- **Extensible**: Easy to add new features
- **User-friendly**: Intuitive interface design

## Support

If you encounter issues or have suggestions:
1. Check the troubleshooting section above
2. Verify your Python and tkinter installation
3. Test with the terminal version for comparison
4. Check file permissions for journal directory

---

**Note**: This GUI version is a trial implementation. For full features, consider using the terminal version (`daily_journal.py`) alongside this GUI for the best experience.