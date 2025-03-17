import os
import json
from dotenv import load_dotenv
from composio_openai import ComposioToolSet, Action
from openai import OpenAI
import traceback

load_dotenv(dotenv_path=".env", override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Replace with your OpenAI API key
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY") # Replace with your Composio API key
AUTHOR_ID = os.getenv("AUTHOR_ID") # Replace with your LinkedIn Author ID, To find your author ID, check out the request_test.py file in the scripts folder 

if not OPENAI_API_KEY or not COMPOSIO_API_KEY or not AUTHOR_ID:
    raise ValueError("Missing API keys or AUTHOR_ID. Ensure you have set the OPENAI_API_KEY and COMPOSIO_API_KEY in your .env file.")


openai_client = OpenAI(api_key=OPENAI_API_KEY) 
composio_toolset = ComposioToolSet(api_key=COMPOSIO_API_KEY)

post_content = {
    "post": {
        "author": AUTHOR_ID, # Replace with your LinkedIn Author ID
        "commentary": (
           #Insert your LinkedIn post content here. Be sure to include the key insights and a strong call to action.
        ),
        "visibility": "PUBLIC"
    }
}


def create_linkedin_post(post_content: dict) -> dict | None:
    """
    Creates a LinkedIn post using Composio's LinkedIn tool.

    Args:
        post_content (dict): A dictionary containing the post content.
    
    Returns:
        dict: The response from the LinkedIn tool.
    """

    if not post_content:
        raise ValueError("❌ Post content cannot be empty!")
    
    try :
        print("Creating LinkedIn post...")

        tools = composio_toolset.get_tools(actions=[Action.LINKEDIN_CREATE_LINKED_IN_POST]) 

        SYSTEM_PROMPT = """
        You are an expert in writing engaging and professional LinkedIn posts. 
        Craft a compelling LinkedIn post using the provided details while ensuring:
        ✅ Clarity, impact, and readability.
        ✅ A structured format with an engaging introduction, key insights, and a strong call to action.
        ✅ A professional yet conversational tone to maximize audience engagement.
        """

        response = openai_client.chat.completions.create(
        model="gpt-4o",
        tools=tools,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},   
            {"role": "user", "content": f"POST_CONTENT: {json.dumps(post_content, indent=2)}"},
        ],
    )
        result = composio_toolset.handle_tool_calls(response)
        if not result:
            print("❌ API returned an empty response!")   

        print("✅ LinkedIn post created successfully!")
        return result
    
    except Exception as e:
        print(f"❌ Error creating LinkedIn post: {str(e)}")
        traceback.print_exc()
        return None
        
if __name__ == "__main__":
    response = create_linkedin_post(post_content)
    if response:
        print("✅ LinkedIn post created successfully!")
    else:
        print("🚨 FAILED TO CREATE LINKEDIN POST")


