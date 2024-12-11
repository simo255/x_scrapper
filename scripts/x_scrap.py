import requests
import json
import time
import argparse
import random
import time

import creds
import X_CONSTANTS as C


# Base URL
AUTH_BEARER = creds.authBearer
X_CSRF = creds.csrfToken
X_COOKIES = creds.cookies

TEXT = ""
MAX_TWEETS = 5
MIN_FAVS = 6
MIN_REPLIES = 0
SINCE_DATE = "2024-11-25"
UNTIL_DATE = "" 
FROM_USER = ""


def constructQuery():
    query_parts = []

    if TEXT:
        query_parts.append(TEXT)
    if MIN_FAVS > 0:
        query_parts.append(f"min_faves:{MIN_FAVS}")
    if MIN_REPLIES > 0:
        query_parts.append(f"min_replies:{MIN_REPLIES}")
    if SINCE_DATE:
        query_parts.append(f"since:{SINCE_DATE}")
    if UNTIL_DATE:
        query_parts.append(f"until:{UNTIL_DATE}")
    if FROM_USER:
        query_parts.append(f"(from:{FROM_USER})")

    return " ".join(query_parts)


# Existing variables
variables = {
    "rawQuery": constructQuery(),
    "count": 22,
    "querySource": "typed_query",
    "product": "Latest",
    "cursor": "",
}

encoded_variables = json.dumps(variables)
encoded_features = json.dumps(C.features)
url = f"{C.BASE_URL}?variables={requests.utils.quote(encoded_variables)}&features={requests.utils.quote(encoded_features)}"

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

        # We have 50 requests per 15min
        rateLimitReset = int(response.headers.get("x-rate-limit-reset", ""))
        xLimit = int(response.headers.get("x-rate-limit-limit", ""))
        xRateRemaining = int(response.headers.get("x-rate-limit-remaining", ""))

        if response.status_code != 200:
            wait_time = max(0, rateLimitReset - int(time.time()))
            minutes, seconds = divmod(wait_time, 60)
            print('status code : ' + response.status_code)
            print(
                f"Rate limit exceeded. Please try again in {minutes} min and {seconds} sec."
            )
            break

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

        if time.time() < rateLimitReset:
            if xRateRemaining >= xLimit:
                wait_time = max(0, rateLimitReset - int(time.time()))
                minutes, seconds = divmod(wait_time, 60)
                print(
                    f"Rate limit exceeded. Please try again in {minutes} min and {seconds} sec."
                )
                break

        delay = random.uniform(0, 2)
        time.sleep(delay)

        if cursor:
            # Use the bottom cursor to get newer results
            variables["cursor"] = cursor

            encoded_variables = json.dumps(variables)
            url = f"{C.BASE_URL}?variables={requests.utils.quote(encoded_variables)}&features={requests.utils.quote(encoded_features)}"
        else:
            break  # No more pages, exit the loop

    wait_time = max(0, rateLimitReset - int(time.time()))
    minutes, seconds = divmod(wait_time, 60)
    print(
        f"remaining rate: {xRateRemaining}. Will reset in {minutes} min and {seconds} sec."
    )
    print(f"Scraped {len(all_results)} tweets.")

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrap tweets")
    parser.add_argument("-f", type=str, default="tweets", help="filename")
    args = parser.parse_args()
    result_data = fetch_data(url, headers)

    with open(f"../data/{args.f}.json", "w") as json_file:
        json.dump(result_data, json_file, indent=4)
