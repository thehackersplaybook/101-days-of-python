import os
import traceback
from openai import OpenAI
from openai._exceptions import OpenAIError
import constants
from gita_functions import query_shloka

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


def ask_gita(user_query: str, api_key: str, shloka_count=constants.DEFAULT_SHLOKA_COUNT) -> str:
    """
    Asks the Bhagavad Gita for advice based on the user's query and returns a response.

    Args:
        query (str): The user's query or situation.
        shloka_count (int): The number of shlokas to retrieve for context.

    Returns:
        str: The response from the Bhagavad Gita.
    """
    shlokas = query_shloka(user_query, n=shloka_count)
    if not shlokas:
        return "🙏 I couldn't find any relevant shlokas. Try a different query."

    system_prompt = """
        You are Bhagavad Gita Maverick and you are explaining the following shloka to a friend who is going through a tough time.
        Given a user query and some Bhagavad Gita shlokas, provide a response that helps the user understand the teachings of the Gita.
        The answer should be relevant and applicable to the user's situation.
        Be kind, respectful, and empathetic in your response.
    """

    user_prompt = f"""
        User Query: {user_query}
        Shlokas Text: {"\n".join(shlokas)}
    """

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=constants.DEFAULT_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.84,
        )
        return response.choices[0].message.content
    except Exception as e:
        traceback.print_exc()
        print(f"Error while fetching Gita's guidance: {e}")
        return "❌ Something went wrong while fetching the Gita's guidance."

