import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)


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
    print("Realtime chatbot started. Type a message to get a response.")
    print("Type 'exit' to stop the chatbot.")

    message = "Say hello!"

    async with client.beta.realtime.connect(
        model="gpt-4o-realtime-preview"
    ) as connection:
        await connection.session.update(session={"modalities": ["text"]})

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
                    print(event.delta, flush=True, end="")

                elif event.type == "response.text.done":
                    print()

                elif event.type == "response.done":
                    break

            message = input("You: ")

            if message.lower() == "exit":
                break


asyncio.run(main())
