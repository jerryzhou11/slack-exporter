#!/usr/bin/env python3
import os
import sys
import requests
import json
from timeit import default_timer
from datetime import datetime
import argparse
from dotenv import load_dotenv
from pathvalidate import sanitize_filename
from time import sleep

# when rate-limited, add this to the wait time
ADDITIONAL_SLEEP_TIME = 2
MAX_RETRIES = 10  # Maximum number of retries for rate limiting

env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.isfile(env_file):
    load_dotenv(env_file)

# slack api (OAuth 2.0) now requires auth tokens in HTTP Authorization header
try:
    HEADERS = {"Authorization": "Bearer %s" % os.environ["SLACK_USER_TOKEN"]}
except KeyError:
    print("Missing SLACK_USER_TOKEN in environment variables")
    sys.exit(1)

def _get_data(url, params):
    return requests.get(url, headers=HEADERS, params=params)

def get_data(url, params):
    """Improved rate-limiting with maximum retries"""
    attempt = 0
    
    while attempt < MAX_RETRIES:
        r = _get_data(url, params)
        attempt += 1
        
        if r.status_code != 429:
            return r
        else:
            retry_after = int(r.headers["Retry-After"])
            sleep_time = retry_after + ADDITIONAL_SLEEP_TIME
            print(f"Rate-limited. Retrying after {sleep_time} seconds ({attempt}/{MAX_RETRIES}).")
            sleep(sleep_time)
    
    print(f"ERROR: Max retries ({MAX_RETRIES}) exceeded. Giving up.")
    sys.exit(1)

def get_at_cursor(url, params, cursor=None):
    if cursor is not None:
        params["cursor"] = cursor

    r = get_data(url, params)

    if r.status_code != 200:
        print(f"ERROR: {r.status_code} {r.reason}")
        sys.exit(1)

    d = r.json()

    if d["ok"] is False:
        print(f"I encountered an error: {d}")
        sys.exit(1)

    next_cursor = None
    if "response_metadata" in d and "next_cursor" in d["response_metadata"]:
        next_cursor = d["response_metadata"]["next_cursor"]
        if str(next_cursor).strip() == "":
            next_cursor = None

    return next_cursor, d

def paginated_get(url, params, combine_key=None):
    next_cursor = None
    result = []
    page_count = 0
    
    while True:
        page_count += 1
        print(f"Fetching page {page_count}...")
        
        next_cursor, data = get_at_cursor(url, params, cursor=next_cursor)
        
        try:
            if combine_key is None:
                result.extend(data)
            else:
                result.extend(data[combine_key])
        except KeyError as e:
            print(f"Something went wrong: {e}")
            sys.exit(1)

        print(f"Page {page_count}: Got {len(data.get(combine_key, data))} items. Total so far: {len(result)}")
        
        if next_cursor is None:
            break

    return result

def channel_history(channel_id, oldest=None, latest=None):
    params = {
        "channel": channel_id,
        "limit": 200,
    }

    if oldest is not None:
        params["oldest"] = oldest
    if latest is not None:
        params["latest"] = latest

    return paginated_get(
        "https://slack.com/api/conversations.history",
        params,
        combine_key="messages",
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", help="Directory in which to save output files")
    parser.add_argument("--ch", help="Channel ID to export")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--fr", help="Unix timestamp for earliest message", type=str)
    parser.add_argument("--to", help="Unix timestamp for latest message", type=str)

    args = parser.parse_args()
    
    if not args.ch:
        print("Please specify a channel ID with --ch")
        sys.exit(1)
    
    if not args.o:
        print("Please specify an output directory with -o")
        sys.exit(1)
    
    print(f"Starting export of channel {args.ch}")
    print(f"Time range: {args.fr} to {args.to}" if args.fr or args.to else "Full history")
    
    start_time = default_timer()
    
    # Get channel history
    ch_hist = channel_history(args.ch, oldest=args.fr, latest=args.to)
    
    end_time = default_timer()
    duration = int(end_time - start_time)
    
    print(f"Export completed in {duration} seconds")
    print(f"Total messages: {len(ch_hist)}")
    
    # Save to file
    ts = str(datetime.strftime(datetime.now(), "%Y-%m-%d_%H%M%S"))
    out_dir_parent = os.path.abspath(os.path.expanduser(os.path.expandvars(args.o)))
    out_dir = os.path.join(out_dir_parent, f"slack_export_{ts}")
    
    os.makedirs(out_dir, exist_ok=True)
    
    if args.json:
        filename = f"channel_{args.ch}.json"
    else:
        filename = f"channel_{args.ch}.txt"
    
    full_filepath = os.path.join(out_dir, filename)
    print(f"Writing output to {full_filepath}")
    
    with open(full_filepath, mode="w", encoding="utf-8") as f:
        if args.json:
            json.dump(ch_hist, f, indent=4)
        else:
            # Simple text format
            for msg in ch_hist:
                if msg.get('type') == 'message' and 'text' in msg:
                    timestamp = datetime.fromtimestamp(float(msg['ts'])).strftime('%Y-%m-%d %H:%M:%S')
                    text = msg['text'].replace('\n', ' ')
                    f.write(f"[{timestamp}] {text}\n\n")
    
    print("Export completed successfully!") 