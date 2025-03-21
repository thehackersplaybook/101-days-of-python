from dotenv import load_dotenv
from anthropic import Anthropic
from mem0 import MemoryClient
from uuid import uuid4
import os

load_dotenv(dotenv_path=".env", override=True)

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
mem0_api_key = os.environ.get("MEM0_API_KEY")

if not (anthropic_api_key and mem0_api_key):
    print("API keys not found in environment variables.")
    print("Please add the following keys to your environment variables:")
    print("- ANTHROPIC_API_KEY")
    print("- MEM0_API_KEY")
    raise ValueError("API keys not found in environment variables.")

ai = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)
memory = MemoryClient(api_key=os.environ.get("MEM0_API_KEY"))


def get_chat_response(prompt: str, user_id: str) -> str:
    """
    Get a response from the chatbot using the given prompt.

    Args:
        prompt (str): The prompt to use for the chatbot.
        user_id (str): The user ID to use for the chatbot.

    Returns:
        str: The response from the chatbot.
    """

    relevant_memories = memory.search(query=prompt, user_id=user_id, limit=3)
    memories_text = "\n".join(f"- {entry['memory']}" for entry in relevant_memories)
    system_prompt = f"You are a helpful AI. Answer the question based on query and memories.\nUser Memories:\n{memories_text}"
    user_message = prompt
    messages = [
        {"role": "user", "content": user_message},
    ]
    memory.add(f"""User: {user_message}""", user_id=user_id)
    response = ai.messages.create(
        system=system_prompt,
        messages=messages,
        model="claude-3-5-sonnet-latest",
        max_tokens=2048,
    )
    assistant_response = response.content[0].text

    # Create new memories from the conversation
    memory.add(f"""Assistant: {assistant_response}""", user_id=user_id)

    return assistant_response


def run_chatbot() -> None:
    """
    Runs a simple chatbot that responds to user input.

    Args:
        None

    Returns:
        None
    """
    
    user_id = str(uuid4())
    print("Hello! I am a simple chatbot.")
    print("You can ask me anything, and I will try to respond.")
    print("If you wish to end the chat, type 'exit' or just let me know.")
    print()

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        response = get_chat_response(user_input, user_id)
        print(f"Bot: {response}")


if __name__ == "__main__":
    run_chatbot()
