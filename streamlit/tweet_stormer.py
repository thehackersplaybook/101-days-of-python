import streamlit as st
import os
import traceback
from typing import Union
from pydantic import BaseModel
from dotenv import load_dotenv
import tweepy
import requests
import time
import datetime
from openai import OpenAI
from openai._exceptions import OpenAIError


load_dotenv(override=True, dotenv_path=".env")

## constants
DEFAULT_OPENAI_MODEL = "gpt-4o"

class Tweet(BaseModel):
    content: str

class GenerateTweetResponse(BaseModel):
    tweets: list[Tweet]


def validate_openai_key(openai_key: str) -> bool:
    """
    Validates the OpenAI API key by making a test request using the OpenAI v1 API.
    
    Args:
        openai_key (str): The OpenAI API key to validate.
        
    Returns:
        bool: True if the key is valid, False otherwise.
    """
    if not openai_key:
        return False
    try:
        OpenAI(api_key=openai_key).models.list()
        return True
    except OpenAIError:
        return False
    except Exception as e:
        print(f"Unexpected issue during API key validation: {e}")
        traceback.print_exc()
        return False



def generate_system_prompt(context: str, tweet_context: str, tweet_number: int) -> str:
    """
    Generates the system prompt for the tweet generation.

    Args:
        context (str): The context for the tweets.
        tweet_context (str): The description of the tweets.
        tweet_number (int): The number of tweets to generate.

    Returns:        
        str: The system prompt.
    """

    return f"""
    You are a highly skilled social media assistant specializing in crafting engaging, concise, and impactful tweets.

    Generate {tweet_number} professional tweets based on the following information:

    Context: {context}
    Tweet Description: {tweet_context}
    If the context requires a brief mention, keep the tweet concise and engaging. However, if the context needs detailed explanation, structure the tweet to clearly convey key insights while maintaining readability and impact.

    Ensure each tweet is unique, follows best practices for social media engagement, and maintains a professional yet accessible tone. Keep tweets within 280 characters, incorporating relevant hashtags, compelling CTAs, and avoiding repetition. Align language with the provided context for maximum clarity and engagement.
    """


def generate_tweets(
    context: str, tweet_context: str, tweet_number: int, openai_key: str
) -> Union[GenerateTweetResponse, None]:
    """
    Generates tweets based on the given context and tweet description."

    Args:
        context (str): The context for the tweets.
        tweet_context (str): The description of the tweets.
        tweet_number (int): The number of tweets to generate.
        
    Returns:
        Union[GenerateTweetResponse, None]: The generated tweets.
    """

    try:
         # Validate the key
        if not validate_openai_key(openai_key):
            raise ValueError("Invalid OpenAI API key. Please check and try again.")
        
        # Create an OpenAI client instance
        openai_client = OpenAI(api_key=openai_key)
        
        # Generate the system prompt
        system_prompt = generate_system_prompt(context, tweet_context, tweet_number)

        # Call the OpenAI API to generate tweets
        response = openai_client.responses.create(
            model=DEFAULT_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Context: {context}\nTweet Context: {tweet_context}\n Generate {tweet_number} tweets.",
                },
            ],
        )
        # Extract messages from the response
        tweets_list = [Tweet(content=choice.message.content.strip()) for choice in response.choices]

        return GenerateTweetResponse(tweets=tweets_list)
    
    except Exception as e:
        print(f"Failed to generate tweets. Error: {str(e)}")
        traceback.print_exc()
        return None


def refine_tweet(tweet: Tweet, refine_prompt: str, openai_key: str, context="") -> Union[Tweet, None]:
    """
    Refines the given tweet based on the provided refine prompt.

    Args:
        tweet (Tweet): The tweet to refine.
        refine_prompt (str): The refine prompt.
        context (str): The context for the tweet.
        
    Returns:        
        Union[Tweet, None]: The refined tweet.
    """

    try:
         # Validate key
        if not validate_openai_key(openai_key):
            raise ValueError("Invalid OpenAI API key. Please check and try again.")

        # Create OpenAI client
        openai_client = OpenAI(api_key=openai_key)

        # Generate the system prompt
        system_prompt = (
            "Refine the tweet strictly based on the provided instructions, enhancing clarity, engagement, and impact while maintaining a 280-character limit. Ensure precision, readability, and alignment with the given input without introducing additional context."
        )

        # Call the OpenAI API to refine the tweet
        response = openai_client.responses.create(
            model=DEFAULT_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Context: {context}\nOriginal Tweet: {tweet.content}\nRefinement Instructions: {refine_prompt}",
                },
            ],
        )

         # Return the refined tweet
        refined_text = response.choices[0].message.content.strip()
        return Tweet(content=refined_text)
    
    except Exception as e:
        print(f"Failed to refine tweet. Error: {str(e)}")
        traceback.print_exc()
        return None

def handle_rate_limits(response)-> bool:
    """
    Handles rate limits for the OpenAI API.

    Args:
        response (Response): The response object from the OpenAI API.
        
    Returns:        
        bool: True if the rate limit was handled, False otherwise.
    """

    try:
        reset_time = int(response.headers.get("x-rate-limit-reset", time.time()))
        remaining_requests = int(response.headers.get("x-rate-limit-remaining", 0))

        current_time = int(time.time())
        remaining_time = reset_time - current_time  
        reset_time_str = datetime.datetime.utcfromtimestamp(reset_time).strftime('%Y-%m-%d %H:%M:%S UTC')

        if remaining_requests > 0:
            print(f"✅ Remaining Requests: {remaining_requests}. You can retry now.")
            return True

        if remaining_time < 30:
            print(f"⏳ Rate limit exceeded. Retrying in {remaining_time} seconds...")
            time.sleep(remaining_time)
            return True
        else:
            print(f"⚠️ Rate limit exceeded. Reset at: {reset_time_str}. Try again later.")
            return False

    except AttributeError:
        print("❌ Response object does not have headers attribute.")
        return False
    except KeyError as e:
        print(f"❌ Missing expected header: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Failed to check rate limits: {str(e)}")
        return False

def get_rate_limit_status(client)-> tuple:
    """
    Gets the rate limit status for the OpenAI API.

    Args:
        client (Client): The OpenAI client.
        
    Returns:        
        tuple: The remaining requests and reset time.
    """

    try:
        rate_limit_status = client.get_rate_limit_status()
        remaining_requests = rate_limit_status["resources"]["statuses"]["/statuses/update"]["remaining"]
        reset_time_unix = rate_limit_status["resources"]["statuses"]["/statuses/update"]["reset"]
        
        reset_time_str = datetime.datetime.utcfromtimestamp(reset_time_unix).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        return remaining_requests, reset_time_str
    except Exception as e:
        print(f"⚠️ Failed to fetch rate limit status: {str(e)}")
        return None, None


def post_tweet(tweet_content: str, api_key, api_secret, access_token, access_secret) -> bool:
    """
    Posts a tweet to Twitter.

    Args:
        tweet_content (str): The content of the tweet.
        api_key (str): The API key for the Twitter API.
        api_secret (str): The API secret for the Twitter API.
        access_token (str): The access token for the Twitter API.
        access_secret (str): The access secret for the Twitter API.
        
    Returns:        
        bool: True if the tweet was posted successfully, False otherwise.
    """     

    try:
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )

        response = client.create_tweet(text=tweet_content)

        print("🚀 API Response:", response)

        if hasattr(response, "errors") and response.errors:
            print(f"❌ API Error: {response.errors}")
            return False

        if response and response.data and "id" in response.data:
            tweet_id = response.data["id"]
            print(f"✅ Tweet posted successfully! ID: {tweet_id}")

            time.sleep(5) 
            try:
                rate_limits = client.get_rate_limits()
                tweet_limit = rate_limits["tweet"]["remaining"]
                reset_time = rate_limits["tweet"]["reset"]

                print(f"🔄 Remaining Tweets: {tweet_limit}")
                print(f"⏳ Rate Limit Resets At: {reset_time}")
            except Exception as e:
                print(f"⚠️ Failed to fetch rate limit status: {str(e)}")

            return True
        else:
            print("❌ Failed to post tweet.")
            return False

    except tweepy.TweepyException as e:
        print(f"❌ Error posting tweet: {str(e)}")
        return False

                

tweets_generated = []

if st.session_state.get("tweets_generated") is None:
    st.session_state["tweets_generated"] = tweets_generated


def main():
    """The main function to run the Tweet Stormer app."""
    st.set_page_config(page_title="Tweet Stormer 🚀", page_icon="🐦", layout="wide")

    st.title("🚀 Tweet Stormer 🐦")

    st.caption(
        "Tweet Stormer is a Twitter Bot that generates Tweets based on a given context."
    )

    # Setup API Key
    with st.sidebar:
        st.title("⚙️ Configuration")
    
    with st.sidebar.expander("🔑 OpenAI and Twitter API Credentials"):
        openai_key = st.text_input("Enter your OpenAI API Key:", type="password", key="api_key_input_sidebar",placeholder="sk-XXXXXXXXXXXXXXXXXXXXXXXXXX", help="Get your API key from https://platform.openai.com/signup")
        user_api_key = st.text_input("X API Key", type="password", placeholder="Enter your X API Key", key="user_api", help="Get your API key from https://developer.twitter.com/en/docs/twitter-api/getting-started")
        user_api_secret = st.text_input("X API Secret", type="password", placeholder="Enter your X API Secret", key="user_api_secret", help="Get your API secret from https://developer.twitter.com/en/docs/twitter-api/getting-started")
        user_access_token = st.text_input("Access Token", type="password", placeholder="Enter your Access Token", key="user_access_token", help="Get your access token from https://developer.twitter.com/en/docs/twitter-api/getting-started")
        user_access_secret = st.text_input("Access Secret", type="password", placeholder="Enter your Access Secret", key="user_access_secret", help="Get your access secret from https://developer.twitter.com/en/docs/twitter-api/getting-started")
        st.markdown("---")

        col1, col2 = st.columns(2)

        # Spinner for validating the API key
        if col1.button("💾 Save API Keys"):
            if not openai_key or not user_api_key or not user_api_secret or not user_access_token or not user_access_secret:
                st.warning("❌ Please fill in all fields before saving.")
            else:
                with st.spinner("⏳ Validating API key..."):
                    is_valid = validate_openai_key(openai_key)
                if is_valid:
                    st.toast("API keys saved successfully! ✅")
                else:
                    st.toast("Invalid OpenAI API key. Please check and try again. ❌")

        if col2.button("🔄 Reset API Keys"):
            with st.spinner("Resetting API key..."):
                openai_key = ""
                user_api_key = ""
                user_api_secret = ""
                user_access_token = ""
                user_access_secret = ""
                st.success("OpenAI key reset successfully!")

    context = st.sidebar.text_input(
        "📝 Context", placeholder="Enter your context here..."
    )

    tweet_context = st.sidebar.text_area(
        "📝 Tweet Description", placeholder="Describe your tweet context here..."
    )

    tweet_number = st.sidebar.slider(
        "🔢 Number of Tweets", min_value=1, max_value=10, value=1
    )

    st.sidebar.markdown("---")

    tweets = st.session_state.tweets_generated

    col1, col2 = st.sidebar.columns(2)
    if col1.button("🔄 Generate Tweets"):
        if not openai_key:
            st.warning("❌ Please enter a valid OpenAI API key before generating tweets.")
        elif not user_api_key or not user_api_secret or not user_access_token or not user_access_secret:
            st.warning("❌ Please enter valid X API credentials before generating tweets.")
        else:
            if not context or not tweet_context or not tweet_number:
                st.warning("❌ Please fill in all fields before generating tweets.")
            else:
                with st.spinner("⏳ Generating tweets..."):
                    tweets_response = generate_tweets(context, tweet_context, tweet_number, openai_key)

                    if not tweets_response:
                        st.error("❌ Failed to generate tweets. Please try again.")
                    else:
                        for key in list(st.session_state.keys()):
                            if key.startswith("post_status_"):
                                del st.session_state[key]

                        st.session_state.tweets_generated = tweets_response.tweets
                        st.rerun()

    if col2.button("🧹 Clear Tweets"):
        st.session_state.tweets_generated = []
        for key in list(st.session_state.keys()):
            if key.startswith("post_status_") or key.startswith("refine_"):
                del st.session_state[key]
        st.success("🧼 Cleared generated tweets.")
        st.rerun()


    if tweets and len(tweets) > 0:
        st.success("✅ Tweets Generated Successfully!")

        for idx, tweet in enumerate(tweets):
            column1, column2 = st.columns([1, 0.2])
            column1.markdown(f"🐦 {tweet.content}")

            post_key = f"post_status_{idx}"
            
            if st.session_state.get(post_key, False):
                column2.success("✅ Tweet Posted!")
            else:
                post_tweet_button = column2.button("🚀 Post Tweet", key=f"post_tweet_{idx}")

                if post_tweet_button:
                    if not all([user_api_key, user_api_secret, user_access_token, user_access_secret]):
                        st.error("❌ Please enter valid X API credentials before posting.")
                    else:
                        success = post_tweet(tweet.content, user_api_key, user_api_secret, user_access_token, user_access_secret)
                        if success:
                            st.session_state[post_key] = True
                            st.success("✅ Tweet Posted Successfully!")
                            st.rerun()
                        else:
                            column2.error("❌ Failed to post tweet.")

            column1, column2 = st.columns([1, 2])
            refine_input_prompt = column1.text_input(
                "🔧 Refine Tweet",
                placeholder="Instructions to refine the tweet.",
                key=f"refine_input_{idx}",
            )
            refine_button = column1.button("🔧 Refine Tweet", key=f"refine_{idx}")
            column2.markdown("")
            st.markdown("---")
                
            if refine_button:
                refined_tweet = refine_tweet(tweet, refine_input_prompt, openai_key, context)
                if refined_tweet:
                    st.session_state.tweets_generated[idx] = refined_tweet
                    post_key = f"post_status_{idx}"
                    if post_key in st.session_state:
                        del st.session_state[post_key]
                    
                    st.success("✅ Tweet Refined Successfully!")
                    st.rerun()

if __name__ == "__main__":
    main()
