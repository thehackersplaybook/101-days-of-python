#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Boilerplate: This block goes into every notebook.
# It sets up the environment, installs the requirements, and checks for the required environment variables.

from IPython.display import clear_output
import os

requirements_installed = False
max_retries = 3
retries = 0
REQUIRED_ENV_VARS = ["OPENAI_API_KEY"]


def install_requirements():
    """
    Installs the requirements from requirements.txt file
    
    Args:
        None
        
    Returns:        
        None
    """

    global requirements_installed, retries
    if requirements_installed:
        print("Requirements already installed.")
        return

    print("Installing requirements...")
    install_status = os.system("pip install -r requirements.txt")
    if install_status == 0:
        print("Requirements installed successfully.")
        requirements_installed = True
    else:
        print("Failed to install requirements.")
        if retries < max_retries:
            print("Retrying...")
            retries += 1
            return install_requirements()
        exit(1)
    return


install_requirements()
clear_output()
print("🚀 Setup complete. Continue to the next cell.")


# In[2]:


from dotenv import load_dotenv

def setup_env():
    """
    Sets up the environment variables
    
    Args:
        None
        
    Returns:        
        None
    """

    def check_env(env_var):
        """
        Checks if the environment variable is set
        
        Args:
            env_var (str): The environment variable to check
            
        Returns:        
            None
        """
        
        value = os.getenv(env_var)
        if value is None:
            print(f"Please set the {env_var} environment variable.")
            exit(1)
        else:
            print(f"{env_var} is set.")

    load_dotenv(override=True, dotenv_path="../.env")

    variables_to_check = REQUIRED_ENV_VARS

    for var in variables_to_check:
        check_env(var)

    print("Environment variables are set.")


setup_env()


# In[3]:


import requests

def downloader(book_name):
    """
    Downloads a PDF file from Google Books
    
    Args:
        book_name (str): The name of the book to download
        
    Returns:        
        None
    """
    query = book_name.replace(" ", "+")
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url).json()
    if response["totalItems"] > 0:
        print(f"Found {response['totalItems']} results for {book_name}")

        try:
            pdf_link = response["items"][0]["accessInfo"]["pdf"]["acsTokenLink"]
            print(f"Downloading {book_name} from Google Books...")
            pdf_file = f"{book_name.replace(' ','_')}.pdf"
            pdf_content = requests.get(pdf_link).content
            with open(pdf_file, "wb") as f:
                f.write(pdf_content)
            return pdf_file
        except:
            print("Error: Failed to download the PDF file.")


# In[4]:


import pdfplumber

def extract_text(pdf_file)-> str:
    """
    Extracts text from a PDF file
    
    Args:
        pdf_file (str): The path to the PDF file
        
    Returns:        
        str: The extracted text
    """

    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
        return text


# In[5]:


import openai

DEFAULT_MODEL = "gpt-4-turbo"

SYSTEM_PROMPT = """
You are an advanced AI book summarizer designed to generate highly detailed, structured, and professional book summaries in Markdown format.

Your task is to produce comprehensive book summaries that capture the **key ideas, chapter-wise breakdowns, important quotes, page references (if available)**, and **actionable insights** from books across various genres, including non-fiction, self-help, academic, business, history, and literature.

### Summary Guidelines:
- Provide a **chapter-by-chapter summary** with the chapter number and title.
- Use a clear **Markdown format** with proper headings (`#`, `##`, `###`) and bullet points.
- Highlight the **main idea** of each chapter in bold.
- Include **key takeaways, insights, or lessons** at the end of each chapter.
- Use **direct quotes** with proper citation (e.g., "Quote text" — Page 34).
- Mention **page references** when available (if PDF or EPUB contains page numbers).
- Provide the book's **market value insights** (target audience, why this book is important).
- At the end of the summary, generate a **Final Summary Section** with your intelligence.
    - Key Ideas Recap
    - Pros and Cons of the Book
    - Best Quotes
    - Who Should Read This Book
    - Market Value
    - Available Platforms (e.g., Amazon, Google Books, Audible, etc.)
"""

def summarize_text(prompt)-> str:
    """
    Summarizes a text using OpenAI's GPT-4 model
    
    Args:
        prompt (str): The text to be summarized
        
    Returns:        
        str: The summarized text
    """

    try:
        response = openai.chat.completions.create(
        model = DEFAULT_MODEL,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role":"user", "content": f"Summarize this book chapter-wise:\n{prompt}"}
        ]
    )
        return response.choices[0].message.content
    except Exception as e:
         return "Not Available"


# In[23]:


def generate_markdown(title, metadata, summary)-> str:
    """
    Generate a detailed book summary in Markdown format.

    Args:
        title (str): The title of the book.
        metadata (dict): A dictionary containing the book metadata.
        summary (str): The summary of the book.

    Returns:
        str: The generated Markdown content.
    """

    missing_info = summarize_text(f"""
Book: {title}
Generate the following details:
- Author
- Published Year
- Genre
- Key Ideas Recap
- Pros and Cons
- Best Quotes
- Who Should Read This Book
- Market Value
""")

    def extract_info(section, fallback)-> str:
        """
        Extracts information from the summary based on the specified section.

        Args:
            section (str): The section to extract information from.
            fallback (str): The fallback value if the information is not found.

        Returns:
            str: The extracted information.
        """

        try:
            return missing_info.split(f"{section}:")[1].split('\n')[0].strip()
        except (IndexError, AttributeError):
            return fallback

    md = f"""
# {title}
**Author:** {metadata.get('authors', extract_info('Author', 'Unknown Author'))}  
**Published Year:** {metadata.get('publishedDate', extract_info('Published Year', 'Unknown Year'))}  
**Genre:** {metadata.get('Categories', extract_info('Genre', 'Unknown Genre'))}  
**Market Value:** {metadata.get('Market Value', extract_info('Market Value', 'Not Available'))}  

## Summary
{summary}

## Final Summary
### Key Ideas Recap
{extract_info('Key Ideas Recap', 'Not Available')}

### Pros and Cons
**Pros:**
{extract_info('Pros and Cons', 'Not Available').split('Cons:')[0]}  

**Cons:**
{extract_info('Cons', 'Not Available')}

### Best Quotes
{extract_info('Best Quotes', 'Not Available')}

### Who Should Read This Book?
{extract_info('Who Should Read This Book', 'Not Available')}

### Market Value
- Amazon: {metadata.get('amazon', summarize_text(f"What is the market value of the book {title} on Amazon?"))}
- Google Books: {metadata.get('Platform', summarize_text(f"What is the market value of the book {title} on Google Books?"))}
- Audible: {metadata.get('audible', summarize_text(f"What is the market value of the book {title} on Audible?"))}
"""
    return md


# In[24]:


import requests

def get_book_metadata(book_name)-> dict:
    """
    Retrieves metadata for a book from Google Books API.

    Args:
        book_name (str): The name of the book.

    Returns:
        dict: A dictionary containing the book metadata.
    """

    query = book_name.replace(" ", "+")
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url).json()

    try:
        if response["totalItems"] > 0:
            book = response['items'][0]['volumeInfo']
            sale_info = response['items'][0].get("saleInfo", {})

            metadata = {
                "Title": book.get("title", "Not Available"),
                "Author": ", ".join(book.get("authors", ["Not Available"])),
                "Pages": book.get("pageCount", "Not Available"),
                "Market Value": sale_info.get("retailPrice", {}).get("amount", "Not Available"),
                "Currency": sale_info.get("retailPrice", {}).get("currencyCode", ""),
                "Platform": "Google Books",
                "Published Date": book.get("publishedDate", "Not Available"),
                "Ratings": book.get("averageRating", "Not Available"),
                "Book Continuation": "Yes" if "seriesInfo" in book else "No",
                "Preview Link": book.get("previewLink", "Not Available"),
                "Publisher": book.get("publisher", "Not Available"),
                "Categories": ", ".join(book.get("categories", ["Not Available"])),
                "Language": book.get("language", "Not Available").upper(),
                "Thumbnail": book["imageLinks"]["thumbnail"] if "imageLinks" in book else "Not Available"
            }

            # Adding Currency Symbol
            if metadata["Market Value"] != "Not Available":
                metadata["Market Value"] = f"{metadata['Market Value']} {metadata['Currency']}"

            return metadata

        else:
            return {
                "Title": "Not Found",
                "Author": "Not Found",
                "Pages": "Not Available",
                "Market Value": "Not Available",
                "Platform": "Not Available",
                "Published Date": "Not Available",
                "Ratings": "Not Available",
                "Book Continuation": "Not Available",
                "Preview Link": "Not Available",
                "Publisher": "Not Available",
                "Categories": "Not Available",
                "Language": "Not Available"
            }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "Title": "Not Found",
            "Author": "Not Found",
            "Pages": "Not Available",
            "Market Value": "Not Available",
            "Platform": "Not Available",
            "Published Date": "Not Available",
            "Ratings": "Not Available",
            "Book Continuation": "Not Available",
            "Preview Link": "Not Available",
            "Publisher": "Not Available",
            "Categories": "Not Available",
            "Language": "Not Available"
        }


# In[ ]:


if __name__ == "__main__":
    os.system("jupyter nbconvert --to script book_summarizer.ipynb && move book_summarizer.py streamlit/")
    print("Conversion Complete ✅")
    print("Launching Streamlit App...")

    os.system("streamlit run streamlit/app.py")
    exit()  # Stop recursion

