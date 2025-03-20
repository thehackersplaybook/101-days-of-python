from mcp.server.fastmcp import FastMCP
from auxknow import AuxKnow, AuxKnowAnswer
from dotenv import load_dotenv
import os

load_dotenv(override=True, dotenv_path=".env")

mcp = FastMCP("auxknow_mcp")

auxknow = AuxKnow(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
    fast_mode=True,
)


def format_response(question: str, response: AuxKnowAnswer) -> str:
    """
    Formats the response from the AuxKnow Answer Engine.

    Args:
        question (str): The question being asked
        response (AuxKnowAnswer): The response from the AuxKnow Answer Engine.

    Returns:
        str: The formatted response including question, answer and citations.
    """
    formatted_response = f"Question: {question}\nAnswer:{response.answer}\n"
    if response.citations:
        formatted_response += "Citations:\n"  # Fixed typo here
        for citation in response.citations:
            formatted_response += f"- {citation}\n"
    return formatted_response


@mcp.tool()
async def ask_auxknow_answer_engine(question: str, context: str = "") -> str:
    """Asks AuxKnow Answer Engine a question and returns the answer with citations.

    Args:
        question (str): The question to ask the AuxKnow Answer Engine.
        context (str, optional): The context to provide to the AuxKnow Answer Engine. Defaults to "".

    Returns:
        str: The answer to the question with citations.
    """
    response = auxknow.ask(question=question, context=context)
    return format_response(question, response)


if __name__ == "__main__":
    print("AuxKnow MCP is running!")
    mcp.run(transport="stdio")
