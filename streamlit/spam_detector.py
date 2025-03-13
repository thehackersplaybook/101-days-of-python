# Import necessary libraries
import streamlit as st
import openai
from dotenv import load_dotenv
import os
import re
from agents import Agent
from agents import Runner
import asyncio


load_dotenv()


api_key = os.getenv('OPENAI_API_KEY')


if not api_key:
    st.error("Error: OPENAI_API_KEY not found in .env file.")
else:
    openai.api_key = api_key

# Function to extract links from email body

def extract_links(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.findall(text)

# Content Agent: Analyzes email content for spam

content_agent= Agent(
    name="Content Agent",
    instructions="You detect whether an email is spam or not based on its content.",
)

# Link Agent: Checks if any links in the email are suspicious

link_agent = Agent(
    name="Link Agent",
    instructions="You check if the email contains suspicious links, like shortened URLs or domains that imitate well-known websites."
)

# Metadata Agent: Analyzes the email's metadata for spam signals

metadata_agent = Agent(
    name="Meta Agent",
    instructions="You monitor and coordinate the workflow between all agents, ensuring smooth collaboration and decision-making."
)

# Judge Agent: Decides if the email is spam based on the votes from other agents

judge_agent = Agent(
    name="Judge Agent",
    instructions="You take the spam score from the Content Agent and Link Agent, then decide whether the email is spam or not.",
    handoffs=[content_agent, link_agent]
)

async def run_content_agent(email):
    result= await Runner.run(content_agent, email["Body"])
    return result.final_output

async def run_link_agent(email):
    links = ', '.join(email['links']) if email['links'] else 'No links found'
    result= await Runner.run(link_agent, links)
    return result.final_output

async def run_metadata_agent(email):
    result= await Runner.run(metadata_agent, email["Subject"])
    return result.final_output

async def run_judge_agent(content_result, link_result, meta_result):
    combined_input = f"Content: {content_result}\nLinks: {link_result}\nMetadata: {meta_result}"
    result = await Runner.run(judge_agent, combined_input)
    return result.final_output


def setup_streamlit_app():
    st.set_page_config(page_title="AI Email Spam Detector", page_icon="💀", layout="wide")
    st.title("⚠️ AI Email Spam Detector")

    st.subheader("📧 Enter Email Details")
    subject = st.text_input("Email Subject", placeholder="Enter email subject here...")
    body = st.text_area("Email Body", placeholder="Paste the email body here...")

    if st.button("Check for Spam"):

        links = extract_links(body)


        st.subheader("🫗 Extracted Links")
        
        if links:
            links_md = "\n".join([f"- 🔗 [{link}]({link})" for link in links])
            st.markdown(links_md)
        else:
            st.markdown("No links found.")


        email = {
            "Subject": subject,
            "Body": body,
            "links": links
        }


        with st.spinner("AI Agents are analyzing the email..."):
            content_result = asyncio.run(run_content_agent(email))
            link_result = asyncio.run(run_link_agent(email))
            metadata_result = asyncio.run(run_metadata_agent(email))
            final_decision = asyncio.run(run_judge_agent(content_result, link_result, metadata_result))

        
        st.subheader("🤖 Agent Responses")
        
        st.markdown("### 📜 **Content Agent**")
        st.markdown(f"{content_result}")
        
        st.markdown("### 🔗 **Link Agent**")
        st.markdown(f"{link_result}")
        
        st.markdown("### 🏷️ **Metadata Agent**")
        st.markdown(f"{metadata_result}")
        
        st.subheader("🎯 Final Decision")
        st.markdown(f"## 🚨 **{final_decision}**")
        
if __name__ == "__main__":
    setup_streamlit_app()
