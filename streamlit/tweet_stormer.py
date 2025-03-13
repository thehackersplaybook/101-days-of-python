import streamlit as st
import os
import traceback
from typing import Union
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import tweepy

load_dotenv(override=True, dotenv_path=".env")

## constants
DEFAULT_OPENAI_MODEL = "gpt-4o"
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")


class Tweet(BaseModel):
    content: str


class GenerateTweetResponse(BaseModel):
    tweets: list[Tweet]

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET, BEARER_TOKEN]):
    raise ValueError("❌ Missing API credentials. Check your .env file.")


def validate_openai_api_key(openai_api_key: str) -> str:
    if not openai_api_key:
        st.error("❌ OpenAI API Key Not Found in .env File")
        st.stop()


def get_openai_client() -> OpenAI:
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        validate_openai_api_key(openai_api_key)
        return OpenAI(api_key=openai_api_key)
    except Exception as e:
        print(f"Failed to create OpenAI client. Error: {str(e)}")
        traceback.print_exc()


def generate_system_prompt(context: str, tweet_context: str, tweet_number: int) -> str:
    return f"""
    You are a highly skilled social media assistant specializing in crafting engaging, concise, and impactful tweets.

Generate {tweet_number} professional tweets based on the following information:

Context: {context}
Tweet Description: {tweet_context}
If the context requires a brief mention, keep the tweet concise and engaging. However, if the context needs detailed explanation, structure the tweet to clearly convey key insights while maintaining readability and impact.

Ensure each tweet is unique, follows best practices for social media engagement, and maintains a professional yet accessible tone. Keep tweets within 280 characters, incorporating relevant hashtags, compelling CTAs, and avoiding repetition. Align language with the provided context for maximum clarity and engagement.
    """


def generate_tweets(
    context: str, tweet_context: str, tweet_number: int
) -> Union[GenerateTweetResponse, None]:
    """
    Generates tweets based on the given context and tweet description."
    Args:
        context (str): The context for the tweets.
        tweet_context (str): The description of the tweets.
        tweet_number (int): The number of tweets to generate.
    Returns:
        str: The generated tweets.
    """

    try:
        openai_client = get_openai_client()
        system_prompt = generate_system_prompt(context, tweet_context, tweet_number)
        response = openai_client.beta.chat.completions.parse(
            model=DEFAULT_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Context: {context}\nTweet Context: {tweet_context}\n Generate {tweet_number} tweets.",
                },
            ],
            response_format=GenerateTweetResponse,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"Failed to generate tweets. Error: {str(e)}")
        traceback.print_exc()
        return None


def refine_tweet(tweet: Tweet, refine_prompt: str, context="") -> Union[Tweet, None]:
    try:
        openai_client = get_openai_client()
        system_prompt = (
            "Refine the tweet strictly based on the provided instructions, enhancing clarity, engagement, and impact while maintaining a 280-character limit. Ensure precision, readability, and alignment with the given input without introducing additional context."
        )
        response = openai_client.beta.chat.completions.parse(
            model=DEFAULT_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Context: {context}\nOriginal Tweet: {tweet.content}\nRefinement Instructions: {refine_prompt}",
                },
            ],
            response_format=Tweet,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"Failed to refine tweet. Error: {str(e)}")
        traceback.print_exc()
        return None
    
def post_tweet(tweet_content: str, api_key, api_secret, access_token, access_secret, bearer_token) -> bool:
    try:
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
            bearer_token=bearer_token
        )

        response = client.create_tweet(text=tweet_content)

        if response and response.data and "id" in response.data:
            tweet_id = response.data["id"]
            print(f"✅ Tweet posted successfully! ID: {tweet_id}")
            return True
        else:
            print(f"❌ Failed to post tweet. {response}")
            return False
    except Exception as e:
        print(f"❌ Failed to post tweet. Error: {str(e)}")
        traceback.print_exc()
        return False


tweets_generated = []

if st.session_state.get("tweets_generated") is None:
    st.session_state["tweets_generated"] = tweets_generated


def main():
    st.set_page_config(page_title="Tweet Stormer 🚀", page_icon="🐦", layout="wide")

    st.title("🚀 Tweet Stormer 🐦")

    st.caption(
        "Tweet Stormer is a Twitter Bot that generates Tweets based on a given context."
    )

    st.sidebar.title("📝 Configuration")

    with st.sidebar.expander("🔑 Twitter API Credentials"):
        user_api_key = st.text_input("X API Key", type="password")
        user_api_secret = st.text_input("X API Secret", type="password")
        user_access_token = st.text_input("Access Token", type="password")
        user_access_secret = st.text_input("Access Secret", type="password")
        user_bearer_token = st.text_input("Bearer Token", type="password")

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

    if st.sidebar.button("🔄 Generate Tweets"):
        if not context or not tweet_context or not tweet_number:
            st.warning("❌ Please fill in all fields before generating tweets.")
        else:
            tweets_response = generate_tweets(context, tweet_context, tweet_number)

            if not tweets_response:
                st.error("❌ Failed to generate tweets. Please try again.")
            else:
                for key in list(st.session_state.keys()):
                    if key.startswith("post_status_"):
                        del st.session_state[key]

            st.session_state.tweets_generated = tweets_response.tweets
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
                    if not all ([user_api_key, user_api_secret, user_access_token, user_access_secret, user_bearer_token]):
                        st.error("❌ Please enter valid X API credentials before posting.")
                    else:
                        success = post_tweet(tweet.content, user_api_key, user_api_secret, user_access_token, user_access_secret, user_bearer_token)
                        if success:
                            st.session_state[post_key] = True
                            st.success("✅ Tweet Posted Successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to post tweet. Please try again.")

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
                refined_tweet = refine_tweet(tweet, refine_input_prompt, context)
                if refined_tweet:
                    st.session_state.tweets_generated[idx] = refined_tweet
                    post_key = f"post_status_{idx}"
                    if post_key in st.session_state:
                        del st.session_state[post_key]
                    
                    st.success("✅ Tweet Refined Successfully!")
                    st.rerun()

if __name__ == "__main__":
    main()
