import requests
import json
import time
import scripts.creds as creds
import argparse

import random

# Base URL
BASE_URL = "https://x.com/i/api/graphql/fnkladLRj_7bB0PwaOtymA/SearchTimeline"
AUTH_BEARER = creds.authBearer
X_CSRF = creds.csrfToken
X_COOKIES = creds.cookies

TEXT = ""
MAX_TWEETS = 20
MIN_FAVS = 6
MIN_REPLIES = 0
SINCE_DATE = "2024-11-25"
UNTIL_DATE = ""


def constructQuery():
    query_params = {
        "min_faves": MIN_FAVS if MIN_FAVS > 0 else None,
        "min_replies": MIN_REPLIES if MIN_REPLIES > 0 else None,
        "since": SINCE_DATE or None,
        "until": UNTIL_DATE or None,
    }
    # Build the query
    query = " ".join(
        [TEXT]
        + [f"{key}:{value}" for key, value in query_params.items() if value is not None]
    )
    return query

# Existing variables
variables = {
    "rawQuery": constructQuery(),
    "count": 22,
    "querySource": "typed_query",
    "product": "Latest",
    "cursor": "",
}

# Existing features
features = {
    "profile_label_improvements_pcf_label_in_post_enabled": False,
    "rweb_tipjar_consumption_enabled": True,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "premium_content_api_read_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "responsive_web_grok_analyze_button_fetch_trends_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False,
    "creator_subscriptions_quote_tweet_preview_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "rweb_video_timestamps_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
}

encoded_variables = json.dumps(variables)
encoded_features = json.dumps(features)
url = f"{BASE_URL}?variables={requests.utils.quote(encoded_variables)}&features={requests.utils.quote(encoded_features)}"

headers = {
    "Authorization": "Bearer " + AUTH_BEARER,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "x-csrf-token": X_CSRF,
    "Cookie": X_COOKIES,
}



def fetch_data(url, headers):
    all_results = []
    while len(all_results) < MAX_TWEETS:

        response = requests.get(url, headers=headers)
        data = response.json()

        entries = (
            data.get("data", {})
            .get("search_by_raw_query", {})
            .get("search_timeline", {})
            .get("timeline", {})
            .get("instructions", [])
        )
        if entries:
            for instruction in entries:
                for entry in instruction.get("entries", []):
                    tweet = (
                        entry.get("content", {})
                        .get("itemContent", {})
                        .get("tweet_results", {})
                        .get("result", {})
                        .get("legacy", {})
                    )
                    user = (
                        entry.get("content", {})
                        .get("itemContent", {})
                        .get("tweet_results", {})
                        .get("result", {})
                        .get("core", {})
                        .get("user_results", {})
                        .get("result", {})
                        .get("legacy", {})
                    )
                    if tweet and user:
                        all_results.append(
                            {
                                "quote_count": tweet.get("quote_count", 0),
                                "reply_count": tweet.get("reply_count", 0),
                                "retweet_count": tweet.get("retweet_count", 0),
                                "favorite_count": tweet.get("favorite_count", 0),
                                "full_text": tweet.get("full_text", ""),
                                "name": user.get("name", ""),
                                "screen_name": user.get("screen_name", ""),
                                "created_at": tweet.get("created_at", ""),
                            }
                        )

        last_entry = (
            data.get("data", {})
            .get("search_by_raw_query", {})
            .get("search_timeline", {})
            .get("timeline", {})
            .get("instructions", [{}])[0]
            .get("entries", [])
        )
        if last_entry:
            cursor = last_entry[-1].get("content", {}).get("value", "")
        else:
            break

        if cursor == "":
            last_entry = (
                data.get("data", {})
                .get("search_by_raw_query", {})
                .get("search_timeline", {})
                .get("timeline", {})
                .get("instructions", [{}])[-1]
                .get("entry", {})
            )
            cursor = last_entry.get("content", {}).get("value", "")

        delay = random.uniform(1, 3)
        time.sleep(delay)

        if cursor:
            # Use the bottom cursor to get newer results
            variables["cursor"] = cursor

            encoded_variables = json.dumps(variables)
            url = f"{BASE_URL}?variables={requests.utils.quote(encoded_variables)}&features={requests.utils.quote(encoded_features)}"
        else:

            break  # No more pages, exit the loop

    return all_results



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrap tweets")
    parser.add_argument("-f", type=str, default="tweets.json", help="filename")
    args = parser.parse_args()
    result_data = fetch_data(url, headers)
    
    with open(f"../data/{args.f}.json", "w") as json_file:
        json.dump(result_data, json_file, indent=4)

