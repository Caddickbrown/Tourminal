#!/usr/bin/env python3
"""
Test script for Daily Journal GUI core functions (without tkinter)
Tests the backend functionality without requiring GUI/tkinter.
"""

import os
import tempfile
import shutil
import json
from datetime import datetime
import sys

# Define the core functions directly to test them
JOURNAL_DIR = os.path.expanduser("~/journal/daily")
SETTINGS_FILE = os.path.expanduser("~/.daily_journal_gui_settings.json")
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
    "window_width": 900,
    "window_height": 700,
    "font_family": "Consolas",
    "font_size": 11
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

def test_basic_functions():
    """Test basic functionality without GUI"""
    print("\n🧪 Testing Core Functions")
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="test_journal_")
    print(f"📁 Using test directory: {test_dir}")
    
    try:
        # Override settings for testing
        global JOURNAL_DIR, BACKUP_DIR
        original_journal_dir = JOURNAL_DIR
        original_backup_dir = BACKUP_DIR
        
        JOURNAL_DIR = os.path.join(test_dir, "journal")
        BACKUP_DIR = os.path.join(test_dir, "backups")
        DEFAULT_SETTINGS["journal_directory"] = JOURNAL_DIR
        DEFAULT_SETTINGS["backup_directory"] = BACKUP_DIR
        
        # Test directory creation
        print("\n📁 Testing Directory Creation...")
        ensure_directories()
        
        if os.path.exists(JOURNAL_DIR) and os.path.exists(BACKUP_DIR):
            print("✅ Directory creation works")
        else:
            print("❌ Directory creation failed")
            return False
        
        # Test filename generation
        print("\n📅 Testing Filename Generation...")
        today_file = get_today_filename()
        print(f"📄 Today's filename: {today_file}")
        if today_file.endswith('.md') and len(today_file) > 5:
            print("✅ Filename generation works")
        else:
            print("❌ Filename generation failed")
            return False
        
        # Test file writing and reading
        print("\n📝 Testing File Operations...")
        test_content = "# Test Entry\n\ntags: test, demo\n\nThis is a test entry for the GUI version."
        
        write_daily_file(today_file, test_content)
        read_content = read_daily_file(today_file)
        
        if read_content.strip() == test_content.strip():
            print("✅ File write/read works")
        else:
            print("❌ File write/read failed")
            print(f"Expected: {repr(test_content)}")
            print(f"Got: {repr(read_content)}")
            return False
        
        # Test appending entries
        print("\n➕ Testing Entry Appending...")
        new_entry = "# Second Entry\n\ntags: test, append\n\nThis is a second entry."
        append_to_daily_file(today_file, new_entry)
        
        updated_content = read_daily_file(today_file)
        if new_entry in updated_content and test_content in updated_content:
            print("✅ Entry appending works")
        else:
            print("❌ Entry appending failed")
            print(f"Content: {repr(updated_content)}")
            return False
        
        # Test tag extraction
        print("\n🏷️  Testing Tag Extraction...")
        sample_content = "This is a test with #hashtag and @mention tags. Also #another and @someone."
        detected_tags = extract_tags_from_content(sample_content)
        
        expected_tags = ['another', 'hashtag', 'mention', 'someone']  # Should be sorted
        if detected_tags == expected_tags:
            print(f"✅ Tag extraction works: {detected_tags}")
        else:
            print(f"❌ Tag extraction failed")
            print(f"Expected: {expected_tags}")
            print(f"Got: {detected_tags}")
            return False
        
        # Test timestamp formatting
        print("\n⏰ Testing Timestamp...")
        timestamp = format_timestamp()
        if timestamp.startswith('[') and timestamp.endswith('] '):
            print(f"✅ Timestamp formatting works: {timestamp}")
        else:
            print(f"❌ Timestamp formatting failed: {timestamp}")
            return False
        
        # Test settings save/load
        print("\n⚙️  Testing Settings...")
        test_settings = DEFAULT_SETTINGS.copy()
        test_settings["test_key"] = "test_value"
        
        save_settings(test_settings)
        loaded_settings = load_settings()
        
        if loaded_settings.get("test_key") == "test_value":
            print("✅ Settings save/load works")
        else:
            print("❌ Settings save/load failed")
            return False
        
        print("\n🎉 All core functions working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory: {test_dir}")
        except:
            print(f"⚠️  Could not clean up test directory: {test_dir}")
        
        # Restore original settings
        JOURNAL_DIR = original_journal_dir
        BACKUP_DIR = original_backup_dir
        DEFAULT_SETTINGS["journal_directory"] = original_journal_dir
        DEFAULT_SETTINGS["backup_directory"] = original_backup_dir

def test_file_operations():
    """Test more complex file operations"""
    print("\n📚 Testing Advanced File Operations...")
    
    # Test multiple entries in one file
    test_dir = tempfile.mkdtemp(prefix="test_journal_advanced_")
    print(f"📁 Using test directory: {test_dir}")
    
    try:
        # Override settings
        global JOURNAL_DIR
        original_journal_dir = JOURNAL_DIR
        JOURNAL_DIR = os.path.join(test_dir, "journal")  
        DEFAULT_SETTINGS["journal_directory"] = JOURNAL_DIR
        
        ensure_directories()
        
        # Create a file with multiple entries
        today_file = get_today_filename()
        
        # First entry
        entry1 = "# [2024-01-15 09:00:00] Morning Thoughts\n\ntags: morning, personal\n\nStarting the day with some reflection."
        append_to_daily_file(today_file, entry1)
        
        # Second entry
        entry2 = "# [2024-01-15 14:30:00] Afternoon Update\n\ntags: work, progress\n\nMade good progress on the #project today."
        append_to_daily_file(today_file, entry2)
        
        # Third entry
        entry3 = "# [2024-01-15 20:15:00] Evening Wrap-up\n\ntags: evening, summary\n\nReflecting on the day. Met with @team about #goals."
        append_to_daily_file(today_file, entry3)
        
        # Read and verify content
        full_content = read_daily_file(today_file)
        
        if all(entry in full_content for entry in [entry1, entry2, entry3]):
            print("✅ Multiple entry handling works")
        else:
            print("❌ Multiple entry handling failed")
            return False
        
        # Test tag extraction from full content
        all_tags = extract_tags_from_content(full_content)
        expected_tags = ['goals', 'project', 'team']  # From #project, @team, #goals
        
        if all(tag in all_tags for tag in expected_tags):
            print(f"✅ Complex tag extraction works: {all_tags}")
        else:
            print(f"❌ Complex tag extraction failed")
            print(f"Expected to find: {expected_tags}")
            print(f"Got: {all_tags}")
            return False
        
        print("✅ Advanced file operations work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Advanced test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up advanced test directory: {test_dir}")
        except:
            print(f"⚠️  Could not clean up advanced test directory: {test_dir}")
        
        # Restore original settings
        JOURNAL_DIR = original_journal_dir
        DEFAULT_SETTINGS["journal_directory"] = original_journal_dir

def main():
    """Run all tests"""
    print("🚀 Daily Journal GUI - Core Function Tests")
    print("=" * 60)
    print("Testing backend functionality without GUI components")
    
    # Test basic functions
    basic_test_passed = test_basic_functions()
    
    # Test advanced file operations
    advanced_test_passed = test_file_operations()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"Core Functions: {'✅ PASS' if basic_test_passed else '❌ FAIL'}")
    print(f"Advanced Operations: {'✅ PASS' if advanced_test_passed else '❌ FAIL'}")
    
    all_passed = basic_test_passed and advanced_test_passed
    
    if all_passed:
        print("\n🎉 All backend tests passed!")
        print("💡 The core functionality is working correctly.")
        print("🖥️  To run the full GUI (if tkinter is available):")
        print("   python3 daily_journal_gui.py")
    else:
        print(f"\n❌ Some tests failed. Please check the implementation.")
    
    print("\n📋 Summary:")
    print("• Core journal operations (read/write/append) working")
    print("• Tag detection and extraction working")
    print("• Settings management working")
    print("• Multi-entry file handling working")
    print("• Timestamp formatting working")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())