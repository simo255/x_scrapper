from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
)
import creds
import requests
import json
import X_CONSTANTS as C
import random
import time


# Twitter API Setup
AUTH_BEARER = creds.authBearer
X_CSRF = creds.csrfToken
X_COOKIES = creds.cookies

TWITTER_USER = ""


# Variables for request
variables = {
    "rawQuery": f"(from:{TWITTER_USER})",
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
last_tweet_id = None


# Function to fetch the latest tweet ID
def fetch_data(url, headers):
    global last_tweet_id  # Use the global variable to store the previous tweet ID

    response = requests.get(url, headers=headers)

    # Handle rate limits
    rateLimitReset = int(response.headers.get("x-rate-limit-reset", ""))
    xRateRemaining = int(response.headers.get("x-rate-limit-remaining", ""))

    wait_time = max(0, rateLimitReset - int(time.time()))
    minutes, seconds = divmod(wait_time, 60)
    print(
        f"remaining rate: {xRateRemaining}. Will reset in {minutes} min and {seconds} sec."
    )

    if response.status_code != 200:
        wait_time = max(0, rateLimitReset - int(time.time()))
        minutes, seconds = divmod(wait_time, 60)
        print("status code : " + str(response.status_code))
        print(
            f"Rate limit exceeded. Please try again in {minutes} min and {seconds} sec."
        )
        return None  # Return None if the rate limit is exceeded

    data = response.json()

    instructions = (
        data.get("data", {})
        .get("search_by_raw_query", {})
        .get("search_timeline", {})
        .get("timeline", {})
        .get("instructions", [])[0]
    )

    if instructions:
        entries = instructions.get("entries", [])
        if entries:
            entryId = entries[0].get("entryId", "")
            tweetId = entryId.split("-")
            new_tweet_id = tweetId[1]

            if new_tweet_id != last_tweet_id:
                last_tweet_id = new_tweet_id
                print(f"new tweet {new_tweet_id}")
                return new_tweet_id

    # Return None if no new tweet ID or any error occurs
    return None


async def send_message(context: CallbackContext):

    new_tweet_id = fetch_data(url, headers)
    if new_tweet_id:
        # Send the tweet as a message
        tweet = f"https://twitter.com/{TWITTER_USER}/status/{new_tweet_id}"

        await context.bot.send_message(chat_id=creds.CHAT_ID, text=tweet)

async def startup_message(context: CallbackContext):
    await context.bot.send_message(chat_id=creds.CHAT_ID, text="Bot has started successfully!")



def main():

    token = creds.TELEGRAM_TOKEN

    application = Application.builder().token(token).build()
    application.job_queue.run_once(startup_message, 0)
    application.add_handler(CommandHandler("start", send_message))

    delay = random.uniform(20, 30)

    application.job_queue.run_repeating(send_message, interval=delay, first=0)

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
