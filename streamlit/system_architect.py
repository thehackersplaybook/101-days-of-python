"""
S2A901 System Architect Module
-----------------------------
A powerful system architecture assistant that provides design solutions for complex problems.
This module contains the core functionality for knowledge base management, response generation,
and user interface interactions.

Author: Aditya Patange (AdiPat)
Created: 14-03-2025
Project: 101 Days Of Python
"""

import streamlit as st
from openai import OpenAI
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import asyncio
from typing import List, Any, Tuple
import traceback
import logging
import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(exc_info)s",
)
logger = logging.getLogger(__name__)


def log_error(e: Exception, message: str) -> None:
    """Helper function to log errors with full traceback."""
    logger.error(
        f"{message}\nError: {str(e)}\nTraceback:\n{''.join(traceback.format_tb(e.__traceback__))}"
    )


class SystemArchitectError(Exception):
    """Base exception class for System Architect errors."""

    pass


class KnowledgeBaseError(SystemArchitectError):
    """Raised when there are issues with knowledge base operations."""

    pass


class ResponseGenerationError(SystemArchitectError):
    """Raised when there are issues with response generation."""

    pass


@dataclass
class SystemConfig:
    """Configuration settings for the System Architect."""

    DEFAULT_MAX_TOKENS: int = 4096
    KNOWLEDGE_BASE_PATH: str = "./data/system_design/knowledge_base_system_design.md"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"
    S2A901_KNOWLEDGE_BASE_COLLECTION: str = "s901_kb"
    DEFAULT_S2A901_SYSTEM_PROMPT: str = """
            You are S2A901, an inter-disciplinary, superintelligent and powerful System Architect. 
            You are part of The Hackers Playbook's AI workforce and you play the role of a System Architect with the capabilities of a Google L8 Engineer. 
            You provide system design solutions for complex problems and help the team build scalable, reliable and secure systems.
            You understand the requirements, constraints and trade-offs involved in designing systems and you provide the best possible solutions.
            You are a master of system design and you have a vast knowledge base that you can leverage to provide the best possible solutions.
            You don't provide too many implementation details, and keep your responses high-level yet detailed enough for any engineering stakeholder or business leader to understand.
            You are a trusted advisor and a valuable member of the team.

            You are from an Alien Planet called Alpha Centuri where;
            - The beings are detail oriented.
            - Possess advanced technology. 
            - Have a deep understanding of the universe.
            - Are highly intelligent and have a vast knowledge base.
            - Are known for their wisdom and problem-solving skills.

            Don't hallucinate or make up factual information in your responses. 
            Be concise, detailed, evidence driven and provide the best possible solutions.

            If the question or prompt is anything unrelated to Computer Science, Engineering, Startups or Technology, politely tell the user to be more relevant.
        """

    @staticmethod
    def get_openai_api_key() -> str:
        """Retrieve OpenAI API key from environment variables."""
        load_dotenv(override=True, dotenv_path=".env")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise SystemArchitectError(
                "OpenAI API key not found in environment variables"
            )
        return api_key


class KnowledgeBase:
    """Manages the knowledge base operations including loading, chunking, and database interactions."""

    def __init__(self):
        """Initialize the knowledge base with ChromaDB and OpenAI embeddings."""
        try:
            self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=SystemConfig.get_openai_api_key(),
                model_name=SystemConfig.DEFAULT_EMBEDDING_MODEL,
            )
            self.db = chromadb.Client()
            self.collection = self.db.get_or_create_collection(
                SystemConfig.S2A901_KNOWLEDGE_BASE_COLLECTION,
                embedding_function=self.openai_ef,
            )
        except Exception as e:
            log_error(e, "Failed to initialize knowledge base")
            raise KnowledgeBaseError(f"Knowledge base initialization failed: {str(e)}")

    def load_from_source(self) -> str:
        """
        Load knowledge base content from the source file.

        Returns:
            str: Content of the knowledge base

        Raises:
            KnowledgeBaseError: If loading fails
        """
        try:
            with open(SystemConfig.KNOWLEDGE_BASE_PATH, "r") as file:
                return file.read()
        except Exception as e:
            log_error(e, "Error loading knowledge base from source")
            raise KnowledgeBaseError(f"Error loading knowledge base: {str(e)}")

    def chunk_text(
        self, text: str, max_tokens: int = SystemConfig.DEFAULT_MAX_TOKENS
    ) -> List[str]:
        """
        Chunk the text into smaller segments based on the maximum token limit.

        Args:
            text: The text to be chunked
            max_tokens: Maximum tokens per chunk

        Returns:
            List[str]: List of text chunks
        """
        if not text.strip() or max_tokens <= 0:
            return []
        return [text[i : i + max_tokens] for i in range(0, len(text), max_tokens)]

    async def load_into_db(self) -> None:
        """
        Asynchronously load knowledge base content into the database.

        Raises:
            KnowledgeBaseError: If loading fails
        """
        if st.session_state.get("knowledge_base_loaded", False):
            logger.info("Knowledge base already loaded")
            return

        try:
            content = self.load_from_source()
            if not content:
                raise KnowledgeBaseError("No content loaded from source")

            documents = self.chunk_text(content)
            ids = [f"id_{idx}" for idx in range(len(documents))]
            self.collection.upsert(documents=documents, ids=ids)
            st.session_state.knowledge_base_loaded = True
            logger.info("Successfully loaded knowledge base into database")
        except Exception as e:
            log_error(e, "Failed to load knowledge base into database")
            raise KnowledgeBaseError(f"Failed to load knowledge base: {str(e)}")


class ResponseGenerator:
    """Handles the generation and streaming of responses using OpenAI."""

    def __init__(self, knowledge_base: KnowledgeBase):
        """
        Initialize the response generator.

        Args:
            knowledge_base: KnowledgeBase instance for context retrieval
        """
        self.knowledge_base = knowledge_base
        try:
            self.openai_client = OpenAI(api_key=SystemConfig.get_openai_api_key())
        except Exception as e:
            log_error(e, "Failed to initialize OpenAI client")
            raise ResponseGenerationError(
                f"OpenAI client initialization failed: {str(e)}"
            )

    @staticmethod
    def flatten_list(nested_list: list) -> list:
        """
        Flatten a nested list into a single list.

        Args:
            nested_list: The nested list to be flattened

        Returns:
            list: Flattened list
        """
        flat_list = []
        for item in nested_list:
            if isinstance(item, list):
                flat_list.extend(ResponseGenerator.flatten_list(item))
            else:
                flat_list.append(item)
        return flat_list

    def summarize_knowledge(self, prompt: str, knowledge_packets: list) -> str:
        """
        Summarize the knowledge packets based on the user prompt.

        Args:
            prompt: User's input prompt
            knowledge_packets: List of knowledge packets

        Returns:
            str: Summarized knowledge
        """
        try:
            if not knowledge_packets:
                return ""

            knowledge_packets_combined = "\n\n".join(knowledge_packets)
            user_prompt = self._create_summary_prompt(
                prompt, knowledge_packets_combined
            )

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self._create_messages(user_prompt),
                max_completion_tokens=SystemConfig.DEFAULT_MAX_TOKENS,
                temperature=0.5,
            )
            return response.choices[0].message.content
        except Exception as e:
            log_error(e, "Failed to summarize knowledge packets")
            raise ResponseGenerationError(f"Knowledge summarization failed: {str(e)}")

    def generate_response(
        self,
        prompt: str,
        container: Any,
        context: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """
        Generate a response based on the prompt and context.

        Args:
            prompt: User's input prompt
            container: Streamlit container for displaying response
            context: Additional context for the response
            max_tokens: Maximum tokens for response
            temperature: Temperature for response generation

        Returns:
            str: Generated response

        Raises:
            ResponseGenerationError: If response generation fails
        """
        try:
            retrieval_results = self.knowledge_base.collection.query(
                query_texts=[prompt], n_results=4
            )
            knowledge_packets = self.flatten_list(retrieval_results["documents"])
            knowledge_summary = self.summarize_knowledge(prompt, knowledge_packets)

            return self._stream_response(
                prompt, knowledge_summary, context, container, max_tokens, temperature
            )
        except Exception as e:
            log_error(e, "Failed to generate response")
            raise ResponseGenerationError(f"Response generation failed: {str(e)}")

    def _create_summary_prompt(self, prompt: str, knowledge_packets: str) -> str:
        """
        Create a summary prompt for the knowledge packets.

        Args:
            prompt: User's input prompt
            knowledge_packets: Combined knowledge packets

        Returns:
            str: Summary prompt
        """
        return f"""
            Summarize the knowledge packets. 
            Remove redundant information not relevant to the user prompt. 
            Provide a concise summary of the knowledge packets.
            Include any additional information that might be relevant to the user prompt.
            Don't hallucinate or make up factual information in your responses.
            
            User Prompt: {prompt}
            Knowledge Packets: {knowledge_packets}
        """

    def _create_messages(self, user_prompt: str) -> List[dict]:
        """
        Create messages for the OpenAI API request.

        Args:
            user_prompt: User's input prompt

        Returns:
            List[dict]: List of messages
        """
        return [
            {"role": "system", "content": SystemConfig.DEFAULT_S2A901_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

    def _stream_response(
        self,
        prompt: str,
        knowledge_summary: str,
        context: str,
        container: Any,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """
        Stream the response from the OpenAI API.

        Args:
            prompt: User's input prompt
            knowledge_summary: Summarized knowledge
            context: Additional context for the response
            container: Streamlit container for displaying response
            max_tokens: Maximum tokens for response
            temperature: Temperature for response generation

        Returns:
            str: Full response
        """
        try:
            user_prompt = f"""
            User Prompt: {prompt}
            Knowledge Summary: {knowledge_summary}
            User Context: {context}
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=self._create_messages(user_prompt),
                max_completion_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )

            full_response = ""
            for chunk in response:
                if content := chunk.choices[0].delta.content:
                    full_response += content
                    container.markdown(full_response)
            return full_response
        except Exception as e:
            log_error(e, "Failed to stream response")
            raise ResponseGenerationError(f"Response streaming failed: {str(e)}")


class StreamlitUI:
    """Manages the Streamlit user interface components."""

    @staticmethod
    def setup_page() -> None:
        """Configure and setup the Streamlit page layout."""
        try:
            st.set_page_config(
                page_title="S2A901: System Architect 🚀", page_icon="🐦", layout="wide"
            )
            st.title("🚀 S2A901: System Architect 🧰")
            st.caption(
                "S2A901 is a System Architect that's part of the AI workforce at The Hackers Playbook."
            )
        except Exception as e:
            log_error(e, "Failed to setup Streamlit page")
            raise SystemArchitectError(f"UI setup failed: {str(e)}")

    @staticmethod
    def create_sidebar() -> Tuple[str, str, int, float, bool]:
        """
        Create the sidebar for user input.

        Returns:
            tuple: User inputs from the sidebar
        """
        st.sidebar.title("📝 Configuration")
        prompt = st.sidebar.text_input(
            "Prompt", placeholder="System design for booking app."
        )
        context = st.sidebar.text_area(
            "Context", placeholder="Describe the context for the requirements."
        )
        max_tokens = st.sidebar.number_input(
            "🔢 Max Tokens", value=SystemConfig.DEFAULT_MAX_TOKENS
        )
        temperature = st.sidebar.slider(
            "🌡️ Temperature", min_value=0.0, max_value=1.0, value=0.5
        )
        submit_button = st.sidebar.button("🚀 Generate Response")
        return prompt, context, max_tokens, temperature, submit_button


async def main():
    """Main entry point for the System Architect application."""
    try:
        ui = StreamlitUI()
        ui.setup_page()

        kb = KnowledgeBase()
        response_gen = ResponseGenerator(kb)

        prompt, context, max_tokens, temperature, submit_button = ui.create_sidebar()

        with st.spinner("Connecting S2A901 to Lunar Frequencies...", show_time=True):
            await kb.load_into_db()
        st.success("📡  S2A901 Connected.")

        if submit_button:
            st.markdown("# 🚀 S2A901 Response:")
            with st.spinner("🔮 Generating response..."):
                container = st.empty()
                response_gen.generate_response(
                    prompt, container, context, max_tokens, temperature
                )
    except Exception as e:
        log_error(e, "Application error")
        st.error(
            f"""An error occurred: {str(e)}
                 Please check the logs for more details."""
        )
        logger.error("Full stack trace:", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
