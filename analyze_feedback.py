#!/usr/bin/env python3
import csv
import re
from collections import Counter
from datetime import datetime
import json

def analyze_feedback(csv_file):
    """Analyze feedback to find common themes and topics"""
    
    # Read the CSV file
    feedbacks = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            feedbacks.append(row['feedback_text'])
    
    print(f"Analyzing {len(feedbacks)} feedback messages...")
    
    # Define common themes and their keywords
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
    
    # Count theme occurrences
    theme_counts = Counter()
    theme_examples = {}
    
    for feedback in feedbacks:
        feedback_lower = feedback.lower()
        
        for theme, keywords in themes.items():
            for keyword in keywords:
                if keyword.lower() in feedback_lower:
                    theme_counts[theme] += 1
                    if theme not in theme_examples:
                        theme_examples[theme] = []
                    if len(theme_examples[theme]) < 3:  # Keep up to 3 examples
                        theme_examples[theme].append(feedback[:100] + "..." if len(feedback) > 100 else feedback)
                    break  # Only count once per theme per feedback
    
    # Print top 10 themes
    print("\n" + "="*60)
    print("TOP 10 FEEDBACK THEMES (by frequency)")
    print("="*60)
    
    for i, (theme, count) in enumerate(theme_counts.most_common(10), 1):
        percentage = (count / len(feedbacks)) * 100
        print(f"\n{i}. {theme.upper()}")
        print(f"   Mentions: {count} ({percentage:.1f}% of feedback)")
        print(f"   Examples:")
        for j, example in enumerate(theme_examples.get(theme, []), 1):
            print(f"     {j}. {example}")
    
    # Additional analysis
    print(f"\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Total feedback messages analyzed: {len(feedbacks)}")
    print(f"Unique themes identified: {len(theme_counts)}")
    print(f"Most common theme: {theme_counts.most_common(1)[0][0]} ({theme_counts.most_common(1)[0][1]} mentions)")
    
    # Save detailed results to JSON
    results = {
        'total_feedback': len(feedbacks),
        'theme_counts': dict(theme_counts),
        'theme_examples': theme_examples,
        'top_10_themes': [{'theme': theme, 'count': count, 'percentage': (count/len(feedbacks))*100} 
                         for theme, count in theme_counts.most_common(10)]
    }
    
    with open('feedback_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed analysis saved to: feedback_analysis.json")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_feedback.py <feedback_csv_file>")
        sys.exit(1)
    
    analyze_feedback(sys.argv[1]) 