#!/usr/bin/env python3
import csv
import re
from collections import defaultdict

def show_theme_examples(csv_file):
    """Show specific feedback quotes for each theme"""
    
    # Read the CSV file
    feedbacks = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            feedbacks.append(row['feedback_text'])
    
    # Define themes and keywords (same as analyze_feedback.py)
    themes = {
        'source filtering/blocking': [
            'block', 'filter', 'source', 'sources', 'unfollow', 'follow', 'trust', 'untrust',
            'clickbait', 'sensational', 'bias', 'biased', 'unreliable', 'reliable'
        ],
        'location/local news': [
            'location', 'local', 'country', 'region', 'area', 'geographic', 'location-based',
            'near me', 'my area', 'my country', 'uk', 'us', 'canada', 'australia'
        ],
        'language/localization': [
            'language', 'translate', 'translation', 'localization', 'british english',
            'spanish', 'french', 'german', 'korean', 'chinese', 'japanese'
        ],
        'personalization/customization': [
            'personalize', 'customize', 'preferences', 'settings', 'tailor', 'individual',
            'my interests', 'my preferences', 'follow topics', 'follow categories'
        ],
        'content quality': [
            'quality', 'accurate', 'factual', 'reliable', 'trustworthy', 'credible',
            'fake news', 'misinformation', 'fact-check', 'verify'
        ],
        'user interface/UX': [
            'interface', 'ui', 'ux', 'design', 'layout', 'navigation', 'user experience',
            'easy to use', 'intuitive', 'clean', 'modern', 'interface'
        ],
        'notification settings': [
            'notification', 'alert', 'push', 'email', 'reminder', 'frequency',
            'too many', 'too few', 'timing', 'schedule'
        ],
        'offline reading': [
            'offline', 'download', 'save', 'bookmark', 'read later', 'cached',
            'no internet', 'airplane mode', 'download for offline'
        ],
        'sharing features': [
            'share', 'social', 'twitter', 'facebook', 'instagram', 'whatsapp',
            'send to', 'export', 'copy link', 'share with friends'
        ],
        'search functionality': [
            'search', 'find', 'lookup', 'query', 'keyword', 'topic search',
            'search bar', 'search function', 'find articles'
        ],
        'reading experience': [
            'read', 'reading', 'font', 'text size', 'dark mode', 'light mode',
            'reading time', 'summarize', 'summary', 'key points'
        ],
        'app performance': [
            'slow', 'fast', 'performance', 'speed', 'loading', 'crash', 'bug',
            'lag', 'responsive', 'smooth', 'optimization'
        ],
        'content variety': [
            'variety', 'diverse', 'different', 'more content', 'categories',
            'topics', 'subjects', 'range', 'selection'
        ],
        'pricing/subscription': [
            'free', 'paid', 'subscription', 'premium', 'cost', 'price', 'money',
            'upgrade', 'pro', 'premium features'
        ]
    }
    
    # Collect examples for each theme
    theme_examples = defaultdict(list)
    
    for feedback in feedbacks:
        feedback_lower = feedback.lower()
        
        for theme, keywords in themes.items():
            for keyword in keywords:
                if keyword.lower() in feedback_lower:
                    theme_examples[theme].append(feedback)
                    break  # Only add once per theme per feedback
    
    # Show examples for top themes
    top_themes = [
        'location/local news',
        'pricing/subscription', 
        'user interface/UX',
        'source filtering/blocking',
        'reading experience',
        'content quality',
        'app performance',
        'content variety',
        'language/localization',
        'sharing features'
    ]
    
    for theme in top_themes:
        print(f"\n{'='*80}")
        print(f"🎯 {theme.upper()}")
        print(f"{'='*80}")
        print(f"Total mentions: {len(theme_examples[theme])}")
        
        # Show 5 specific examples
        for i, example in enumerate(theme_examples[theme][:5], 1):
            print(f"\n{i}. {example}")
        
        if len(theme_examples[theme]) > 5:
            print(f"\n... and {len(theme_examples[theme]) - 5} more examples")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 show_examples.py <feedback_csv_file>")
        sys.exit(1)
    
    show_theme_examples(sys.argv[1]) 