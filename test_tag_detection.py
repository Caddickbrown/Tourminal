#!/usr/bin/env python3
"""
Test script to demonstrate tag autodetection functionality
"""

def extract_tags_from_content(content, tag_prefixes=None):
    """Extract tags from content using specified prefixes"""
    if not content or not tag_prefixes:
        return []
    
    if tag_prefixes is None:
        tag_prefixes = ["#", "@"]
    
    print(f"DEBUG: tag_prefixes = {tag_prefixes}")
    
    tags = set()
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        print(f"DEBUG: Processing line {line_num}: '{line}'")
        
        # Split line into words and check each word
        words = line.split()
        for word in words:
            print(f"DEBUG: Checking word: '{word}'")
            for prefix in tag_prefixes:
                if word.startswith(prefix):
                    print(f"DEBUG: Word '{word}' starts with prefix '{prefix}'")
                    # Extract the tag (remove prefix and any trailing punctuation)
                    tag = word[len(prefix):]
                    print(f"DEBUG: Extracted tag: '{tag}'")
                    # Remove common punctuation that might follow the tag
                    tag = tag.rstrip('.,;:!?')
                    print(f"DEBUG: After punctuation removal: '{tag}'")
                    # Only add if it's a valid tag (not empty and contains at least one alphanumeric character)
                    if tag and any(c.isalnum() for c in tag):
                        print(f"DEBUG: Adding tag: '{tag.lower()}'")
                        tags.add(tag.lower())
                    else:
                        print(f"DEBUG: Tag '{tag}' rejected (empty or no alphanumeric chars)")
                    break  # Only match one prefix per word
    
    print(f"DEBUG: Final tags: {sorted(list(tags))}")
    return sorted(list(tags))

def merge_tags(existing_tags, detected_tags):
    """Merge existing tags with detected tags, avoiding duplicates"""
    if not existing_tags:
        return ", ".join(detected_tags)
    if not detected_tags:
        return existing_tags
    
    # Parse existing tags
    existing_tag_list = [tag.strip().lower() for tag in existing_tags.split(',') if tag.strip()]
    
    # Combine and deduplicate
    all_tags = existing_tag_list + detected_tags
    unique_tags = []
    seen = set()
    
    for tag in all_tags:
        if tag not in seen:
            unique_tags.append(tag)
            seen.add(tag)
    
    return ", ".join(unique_tags)

def main():
    print("Tag Autodetection Test")
    print("=" * 50)
    
    # Test content with various tags
    test_content = """This is a test entry with some tags.

I'm working on a #project today and meeting with @john and @sarah.
The meeting is about #work and #planning.

Some thoughts on #ideas and #goals for the future.
Also discussing #health and #fitness plans.

End of entry with #final tag."""
    
    print("Test content:")
    print(test_content)
    print()
    
    # Test with default prefixes
    print("Testing with default prefixes (# and @):")
    detected_tags = extract_tags_from_content(test_content)
    print(f"Detected tags: {detected_tags}")
    print()
    
    # Test merging
    existing_tags = "existing, tags"
    merged_tags = merge_tags(existing_tags, detected_tags)
    print(f"Existing tags: {existing_tags}")
    print(f"Merged tags: {merged_tags}")
    print()
    
    # Test with different prefixes
    print("Testing with different prefixes:")
    test_prefixes = ["$", "!", "&"]
    for prefix in test_prefixes:
        test_tags = extract_tags_from_content(test_content, [prefix])
        print(f"{prefix}: {test_tags if test_tags else 'none'}")
    print()
    
    # Test edge cases
    print("Testing edge cases:")
    edge_cases = [
        "#tag",           # Simple tag
        "#tag123",        # Tag with numbers
        "#tag-name",      # Tag with hyphen
        "#tag_name",      # Tag with underscore
        "#tag!",          # Tag with punctuation
        "#",              # Just prefix
        "#!",             # Prefix with punctuation only
        "not-a-tag",      # No prefix
        "@user@domain",   # Multiple @ symbols
    ]
    
    for case in edge_cases:
        tags = extract_tags_from_content(case)
        print(f"'{case}' -> {tags}")

if __name__ == "__main__":
    main() 