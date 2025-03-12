import os
import sys

# Add the parent directory to Python path so we can import pickleball.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def split_and_clean(text):
    """Split text by commas and remove whitespace from each item."""
    if not text:
        return []
    return [item.strip() for item in text.split(',')]
