import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.theme import Theme

load_dotenv(dotenv_path=".env", override=True)

# Define custom theme for rich
custom_theme = Theme(
    {
        "title": "bold orange1",
        "banner": "bold orange1",
        "assistant": "bold cyan",
        "user": "bold green",
    }
)

console = Console(theme=custom_theme)


async def main() -> None:
    """
    Sets up the chatbot and runs the chatbot in a loop.

    Demonstrates the Open AI Realtime API.

    Args:
        None

    Returns:
        None
    """
    
    client = AsyncOpenAI()
    console.print("Realtime Life Coach Chatbot", style="title")
    console.print("=" * 30, style="banner")
    console.print("Type a message to get a response.", style="banner")
    console.print("Type 'exit' to stop the chatbot.", style="banner")
    console.print("=" * 30, style="banner")

    instructions = f"""
        You are Mato Nui, a Life Coach with decades of experience. 
        The client will chat with you about their life and ask for advice.
        You will provide guidance and support to help them navigate their challenges.
        You can also ask questions to learn more about the client's situation.
        The goal is to help the client achieve their personal growth and well-being.
        Remember to be empathetic, understanding, and encouraging in your responses.
    """

    message = "Introduce yourself to the user and get to know them."

    async with client.beta.realtime.connect(
        model="gpt-4o-realtime-preview",
    ) as connection:
        await connection.session.update(
            session={"modalities": ["text"], "instructions": instructions}
        )

        while True:
            await connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": message}],
                }
            )
            await connection.response.create()

            async for event in connection:
                if event.type == "response.text.delta":
                    console.print(event.delta, style="assistant", end="")

                elif event.type == "response.text.done":
                    console.print()

                elif event.type == "response.done":
                    break

            message = console.input("[user]You: [/user]")

            if message.lower() == "exit":
                break


asyncio.run(main())
