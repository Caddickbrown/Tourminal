# Daily Journal - Terminal Journal Application

A powerful, feature-rich terminal-based journal application built with Python and curses. Perfect for daily journaling with multiple entries per day, search functionality, and a clean terminal interface.

## Features

### 📝 **Entry Management**
- **Multiple entries per day** - All entries from the same day are stored in one file
- **Individual entry viewing** - Browse and read specific entries across all days
- **Entry-based editing** - Edit individual entries directly
- **Automatic date/time stamps** - Entries are automatically timestamped
- **Tag support** - Add tags to organize your entries

### 🔍 **Advanced Search**
- **Search Entries** - Find and read specific entries by title, tags, or content
- **Search Entries to Edit** - Find and edit specific entries directly
- **Search Daily Files** - Search through entire daily files
- **Match highlighting** - See exactly where your search terms were found

### 📖 **Reading & Viewing**
- **Read Daily Files** - View entire day's journal with scrolling
- **Read Journal Entry** - Browse individual entries across all days
- **Scrollable content** - Navigate through long entries easily
- **Non-wrapping scrolling** - Natural reading experience

### ✏️ **Editing**
- **Terminal-based editor** - Full-featured text editor within the terminal
- **External editor support** - Use your preferred external editor
- **Edit Today's Journal** - Quick access to today's entries
- **Edit by Date** - Select specific dates to edit
- **Edit Individual Entries** - Edit specific entries directly

### ⚙️ **Settings & Configuration**
- **Customizable journal directory** - Store journals anywhere
- **Date format customization** - Choose your preferred date format
- **Editor preferences** - Set your default external editor
- **Auto-save options** - Configure automatic saving behavior

## Installation

### Prerequisites
- Python 3.6 or higher
- Terminal with curses support (most Unix-like systems and Windows with WSL)

### Setup
1. **Clone or download** the `daily_journal.py` file
2. **Make it executable** (optional):
   ```bash
   chmod +x daily_journal.py
   ```
3. **Run the application**:
   ```bash
   python daily_journal.py
   ```

## Usage

### Starting the Application
```bash
python daily_journal.py
```

### Main Menu Navigation
- **Arrow Keys** - Navigate through menu options
- **Enter/Space** - Select option
- **ESC** - Go back/Exit

### Creating New Entries

#### Terminal Entry (Recommended)
1. Select **"New Entry (Terminal)"** or press **Ctrl+N**
2. Enter a title (pre-filled with current date/time)
3. Add tags (comma-separated)
4. Type your entry content
5. Press **Ctrl+D** when finished

#### External Editor Entry
1. Select **"New Entry (Editor)"**
2. Enter title and tags
3. Your preferred editor will open
4. Write your entry and save

### Reading Entries

#### Read Individual Entries
1. Select **"Read Journal Entry"**
2. Browse through all entries across all days
3. Select an entry to read
4. Use arrow keys to scroll through content
5. Press **ESC** to return

#### Read Daily Files
1. Select **"Read Daily File"**
2. Choose a specific date
3. View all entries for that day
4. Scroll through the entire day's content

### Searching

#### Search to Read
1. Select **"Search Entries"** or press **Ctrl+F**
2. Enter your search term
3. Browse matching entries
4. Select an entry to read it

#### Search to Edit
1. Select **"Search Entries to Edit"**
2. Enter your search term
3. Browse matching entries
4. Select an entry to edit it directly

### Editing

#### Edit Individual Entries
1. Select **"Edit Journal Entry"**
2. Browse and select an entry
3. Use the terminal editor:
   - **Arrow keys** - Move cursor
   - **Ctrl+Left/Right** - Move by words
   - **Ctrl+A/E** - Move to line start/end
   - **Backspace/Delete** - Delete characters
   - **Ctrl+S** - Save changes
   - **Ctrl+Q** - Quit without saving

#### Edit Today's Journal
1. Select **"Edit Today's Journal (Terminal)"** or press **Ctrl+O**
2. Edit today's entries directly

#### Edit by Date
1. Select **"Edit Journal by Date (Terminal)"**
2. Choose a specific date
3. Edit all entries for that day

### File Management

#### Delete Daily Files
1. Select **"Delete Daily File"**
2. Choose a date to delete
3. Confirm deletion (entire day's journal will be deleted)

## File Structure

### Journal Files
- **Location**: `~/journal/daily/` (configurable)
- **Format**: `YYYY-MM-DD.md`
- **Content**: Markdown format with individual entries

### Entry Format
```markdown
# [2024-01-15 14:30:00] Entry Title

tags: tag1, tag2, tag3

Entry content goes here.
This can be multiple lines.

## Subheadings work too

- Lists work
- Multiple entries per day
- All in one file
```

### Settings File
- **Location**: `~/.daily_journal_settings.json`
- **Purpose**: Stores user preferences and configuration

## Configuration

### Settings Menu
Access via **"Settings"** in the main menu:

- **Journal Directory** - Change where journals are stored
- **Default Editor** - Set your preferred external editor
- **Date Format** - Customize date display format
- **Filename Format** - Choose file naming style
- **Auto Save** - Configure automatic saving

### Default Settings
```json
{
  "journal_directory": "~/journal/daily",
  "default_editor": "nano",
  "date_format": "%Y-%m-%d",
  "filename_format": "daily",
  "auto_save": true
}
```

## Keyboard Shortcuts

### Main Menu
- **Ctrl+N** - New Entry (Terminal)
- **Ctrl+O** - Edit Today's Journal (Terminal)
- **Ctrl+F** - Search Entries

### Navigation
- **↑/↓** - Navigate menus
- **Enter/Space** - Select option
- **ESC** - Go back/Exit

### Editor
- **Arrow Keys** - Move cursor
- **Ctrl+Left/Right** - Move by words
- **Ctrl+A/E** - Move to line start/end
- **Ctrl+S** - Save
- **Ctrl+Q** - Quit without saving
- **Ctrl+D** - Finish writing entry (when creating new entry)

### Reading
- **↑/↓** - Scroll up/down
- **Page Up/Down** - Scroll by page
- **ESC** - Exit reader

## Tips & Best Practices

### Organizing Entries
- **Use descriptive titles** - Makes searching easier
- **Add relevant tags** - Helps with organization and search
- **Multiple entries per day** - Perfect for different thoughts/events
- **Consistent formatting** - Makes reading easier

### Efficient Workflow
1. **Quick entries** - Use "New Entry (Terminal)" for fast thoughts
2. **Longer entries** - Use "New Entry (Editor)" for detailed writing
3. **Finding entries** - Use search functions to locate specific content
4. **Editing** - Use "Search Entries to Edit" for quick modifications

### Search Strategies
- **Search by tags** - Use consistent tag naming
- **Search by content** - Find entries with specific words/phrases
- **Search by title** - Use descriptive titles for easy finding

## Troubleshooting

### Common Issues

#### "No journal entries found"
- Create your first entry using "New Entry (Terminal)"
- Check the journal directory in Settings

#### "Permission denied"
- Check file permissions in your journal directory
- Ensure you have write access to the directory

#### "Editor not found"
- Set a different default editor in Settings
- Ensure your preferred editor is installed

#### Curses display issues
- Ensure your terminal supports curses
- Try resizing your terminal window
- Use a different terminal emulator if needed

### Debug Tools
Access via **Settings → Debug Journal Info**:
- View journal directory information
- Check file permissions
- List all journal files

## Development

### Requirements
- Python 3.6+
- curses library (included with Python)

### File Structure
```
daily_journal.py          # Main application
README.md                 # This file
```

### Key Functions
- `main_menu()` - Main application loop
- `new_entry()` - Create new entries
- `parse_entries_from_content()` - Parse entries from files
- `search_individual_entries()` - Search functionality
- `edit_entry()` - Entry editing
- `display_entry_content()` - Entry viewing

## License

This project is open source. Feel free to modify and distribute as needed.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

**Happy Journaling! 📖✨** 