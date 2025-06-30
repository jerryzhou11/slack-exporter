#!/usr/bin/env python3
import csv
import json
import os
import sys
from collections import Counter
from openai import OpenAI
from typing import List, Dict

def setup_openai(api_key: str):
    """Setup OpenAI client"""
    return OpenAI(api_key=api_key)

def analyze_feedback_with_llm(feedbacks: List[str], api_key: str) -> Dict:
    """Use LLM to analyze feedback themes"""
    
    client = setup_openai(api_key)
    
    # Split feedback into batches to avoid token limits
    batch_size = 50
    batches = [feedbacks[i:i + batch_size] for i in range(0, len(feedbacks), batch_size)]
    
    all_themes = []
    
    print(f"Analyzing {len(feedbacks)} feedback messages in {len(batches)} batches...")
    
    for i, batch in enumerate(batches):
        print(f"Processing batch {i+1}/{len(batches)}...")
        
        # Create prompt for LLM analysis
        prompt = f"""
        Analyze the following user feedback for a news app called Particle. Identify the main themes, concerns, and feature requests mentioned.

        Feedback samples:
        {json.dumps(batch[:10], indent=2)}

        Please provide:
        1. Top 10 most common themes/topics mentioned
        2. For each theme, provide:
           - A clear theme name
           - Number of mentions (estimate)
           - 3 specific example quotes
           - Brief description of the concern/request

        Format your response as JSON:
        {{
            "themes": [
                {{
                    "name": "theme_name",
                    "mentions": estimated_count,
                    "examples": ["quote1", "quote2", "quote3"],
                    "description": "brief description"
                }}
            ]
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a product analyst specializing in user feedback analysis. Be concise and accurate."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            # Parse LLM response
            content = response.choices[0].message.content
            try:
                # Try to extract JSON from response
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    json_str = content.split("```")[1]
                else:
                    json_str = content
                
                result = json.loads(json_str)
                all_themes.extend(result.get("themes", []))
                
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON from batch {i+1}")
                continue
                
        except Exception as e:
            print(f"Error processing batch {i+1}: {e}")
            continue
    
    # Aggregate themes across batches
    theme_counts = Counter()
    theme_examples = {}
    theme_descriptions = {}
    
    for theme in all_themes:
        name = theme.get("name", "").lower()
        theme_counts[name] += theme.get("mentions", 1)
        
        if name not in theme_examples:
            theme_examples[name] = []
        theme_examples[name].extend(theme.get("examples", []))
        
        if name not in theme_descriptions:
            theme_descriptions[name] = theme.get("description", "")
    
    # Get top 10 themes
    top_themes = theme_counts.most_common(10)
    
    results = {
        "total_feedback": len(feedbacks),
        "theme_counts": dict(theme_counts),
        "theme_examples": {k: v[:5] for k, v in theme_examples.items()},  # Keep top 5 examples
        "theme_descriptions": theme_descriptions,
        "top_10_themes": [
            {
                "theme": theme,
                "count": count,
                "percentage": (count / len(feedbacks)) * 100,
                "description": theme_descriptions.get(theme, ""),
                "examples": theme_examples.get(theme, [])[:3]
            }
            for theme, count in top_themes
        ]
    }
    
    return results

def print_llm_analysis(results: Dict):
    """Print the LLM analysis results"""
    
    print("\n" + "="*80)
    print("🤖 LLM ANALYSIS RESULTS")
    print("="*80)
    
    print(f"\nTotal feedback analyzed: {results['total_feedback']}")
    print(f"Unique themes identified: {len(results['theme_counts'])}")
    
    print("\n" + "="*80)
    print("TOP 10 THEMES (LLM Analysis)")
    print("="*80)
    
    for i, theme_data in enumerate(results['top_10_themes'], 1):
        theme = theme_data['theme']
        count = theme_data['count']
        percentage = theme_data['percentage']
        description = theme_data['description']
        examples = theme_data['examples']
        
        print(f"\n{i}. {theme.upper()}")
        print(f"   Mentions: {count} ({percentage:.1f}% of feedback)")
        print(f"   Description: {description}")
        print(f"   Examples:")
        for j, example in enumerate(examples, 1):
            print(f"     {j}. {example}")
    
    # Save detailed results
    with open('llm_feedback_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed analysis saved to: llm_feedback_analysis.json")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 llm_analyze_feedback.py <feedback_csv_file> <openai_api_key>")
        print("Or set OPENAI_API_KEY environment variable")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("Error: Please provide OpenAI API key as argument or set OPENAI_API_KEY environment variable")
        sys.exit(1)
    
    # Read feedback from CSV
    feedbacks = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            feedbacks.append(row['feedback_text'])
    
    print(f"Loaded {len(feedbacks)} feedback messages")
    
    # Analyze with LLM
    results = analyze_feedback_with_llm(feedbacks, api_key)
    
    # Print results
    print_llm_analysis(results)

if __name__ == "__main__":
    main() 