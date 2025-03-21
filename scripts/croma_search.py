import traceback
import os
import argparse
import requests
from dotenv import load_dotenv
import asyncio
from openai import OpenAI
from pydantic import BaseModel
import re
from markdownify import markdownify as md
from firecrawl import FirecrawlApp
from browser_use import Agent
from langchain_openai import ChatOpenAI


DEFAULT_SEARCH_PAGE_THRESHOLD = 18000

load_dotenv(dotenv_path=".env", override=True)

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))


class StructuredCromaSearchItem(BaseModel):
    name: str
    price: str
    url: str


class StructuredCromaSearchResults(BaseModel):
    products: list[StructuredCromaSearchItem]


def extract_product_urls_from_markdown(markdown_content: str) -> list:
    """
    Extract all product page URLs from the given markdown content using regex.

    Args:
        markdown_content (str): The markdown content.

    Returns:
        list: A list of product page URLs.
    """

    product_urls = re.findall(
        r"https://www\.croma\.com[^\s]+/p/[^\s]+", markdown_content
    )
    filtered_urls = []
    for url in product_urls:
        if "adm_" in url:
            url = re.sub(r"adm_", "", url)
        if not url.split("/")[-1].startswith("ph"):
            filtered_urls.append(url)
    print(f"Filtered URLS found: {len(filtered_urls)}.")
    return filtered_urls


def search_croma(query: str) -> list[str]:
    """
    Search for products on Croma that match the query.

    Args:
        query (str): The search query.

    Returns:
        list[str]: A list of products that match the query.
    """

    try:
        url = "https://www.croma.com/search?q=" + requests.utils.quote(query)
        app = firecrawl
        scrape_result = app.scrape_url(url=url, params={"formats": ["markdown"]})
        result_markdown = scrape_result.get("markdown", "")
        urls = extract_product_urls_from_markdown(markdown_content=result_markdown)
        return urls
    except Exception as e:
        print(f"Error searching Croma: {e}")
        traceback.print_exc()
        return []


class ProductDetails(BaseModel):
    name: str
    price: str
    features: list[str]
    discontinued: bool
    description: str


async def scrape_product_details(url: str) -> ProductDetails | None:
    """
    Scrape the product details from the given URL.

    Args:
        url (str): The URL of the product.

    Returns:
        ProductDetails | None: The product details.
    """

    try:
        agent = Agent(
            llm=ChatOpenAI(model="gpt-4o"),
            task=f"Go to {url} and extract the product details, features, description, discontinued, and all other necessary details related to the product. Ignore other details not relevant to the product.",
        )
        result = await agent.run()
        markdown_data = result.final_result()
        reduced_text = markdown_data

        response = openai.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant for structuring data.",
                },
                {
                    "role": "user",
                    "content": f"Given the product details, return a JSON object with the product name, price, features, discontinued, and description. Markdown Data: {reduced_text}",
                },
            ],
            response_format=ProductDetails,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"Error scraping product details: {e}")
        traceback.print_exc()
        return {}


async def scrape_all_product_details(
    product_urls: list[str],
) -> list[ProductDetails]:
    """
    Scrape the product details from the given list of products.

    Args:
        products (list): The list of products.

    Returns:
        list[ProductDetails]: The list of product details.
    """

    product_details = []
    for url in product_urls:
        print(f"Scraping product details for: {url}")
        details = await scrape_product_details(url=url)
        product_details.append(details)
        print(f"Scraped product details for: {details.name}")
    return product_details


def recommend_product(query: str, product_details: list[ProductDetails]) -> str:
    """
    Recommend a product based on the given product details.

    Args:
        query (str): The search query.
        product_details (list[ProductDetails]): The product details.

    Returns:
        str: The recommendation message.
    """

    try:
        total_product_info = ""
        for product in product_details:
            product_info = f"""
                \n
                _______________________________________________________
                Product Name: {product.name}
                Price: {product.price}
                Features: {', '.join(product.features)}
                Discontinued: {product.discontinued}
                Description: {product.description}
                _______________________________________________________
            """
            total_product_info += product_info
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant for recommending products.",
                },
                {
                    "role": "user",
                    "content": f"Given the product details, recommend the best product based on the Query ['{query}']. Product Details: {total_product_info}",
                },
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error recommending product: {e}")
        traceback.print_exc()
        return "Sorry, failed to recommend a product."


async def main():
    """
    The main function that searches for products on Croma.

    Args:
        None

    Returns:
        None
    """

    parser = argparse.ArgumentParser(description="Search for products on Croma.")
    parser.add_argument("--query", type=str, required=True, help="The search query.")
    args = parser.parse_args()
    products = search_croma(query=args.query)
    print("________\nProducts Found:\n", len(products))
    top_5_products = products[:5]
    product_details = await scrape_all_product_details(product_urls=top_5_products)
    product_recommendation = recommend_product(
        query=args.query, product_details=product_details
    )
    print("________\nProduct Recommendation:\n", product_recommendation)


if __name__ == "__main__":
    asyncio.run(main())
