import streamlit as st
import openai
import os
from dotenv import load_dotenv
import json
import traceback
from openai import OpenAI
from openai._exceptions import OpenAIError
load_dotenv(verbose=True, override=True, dotenv_path=".env")


#Constants
DEFAULT_OPENAI_MODEL = "gpt-4"

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

def get_recipes_from_ingredients(openai_key, ingredients, item, cuisine, num_recipes=5) -> list:
    """
    Generate recipes based on the provided ingredients and cuisine.

    Args:
        ingredients (str): Comma-separated list of ingredients.
        item (str): The item to be made.
        cuisine (str): The cuisine of the recipe.
        num_recipes (int): The number of recipes to generate.

    Returns:
        list: A list of dictionaries containing the recipe details.
    """

    system_prompt = f"""
Create {num_recipes} unique and authentic {cuisine} recipes using the following core ingredients: {ingredients}.
Generate a high-quality recipe for {item} in {cuisine} style, ensuring that it strictly adheres to the provided ingredients.
If essential sauces, spices, or liquids are missing, intelligently infer and add them under an 'additional_ingredients' section.
Provide the output **strictly** in this JSON format:
[
  {{
    "item_of_choice": "{item}",
    "cuisine": "{cuisine}",
    "name": "Recipe Name",
    "ingredients": ["ingredient1", "ingredient2", ...],
    "additional_ingredients": [provide any additional items here if necessary],
    "steps": ["Step 1", "Step 2", ...]
  }},
  ...
]
Do not include any additional text or explanations.
"""
    try:
        # Set OpenAI API key
        openai.api_key = openai_key
        if not openai_key:
            raise ValueError("OpenAI API key is required.")

        response = openai.chat.completions.create(
            model=DEFAULT_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
            ],
            temperature=0.84,
        )
        recipes = json.loads(response.choices[0].message.content)
        return recipes
    except Exception as e:
        st.error(f"Error fetching recipe data: {e}")
        return None

def display_recipes(recipes):
    """
    Display the generated recipes on the Streamlit app with a visually appealing design.
    
    Args:
        recipes (list): A list of dictionaries containing the recipe details.

    Returns:
        None
    """
    # Set up columns for displaying recipes in a grid
    num_columns = 3
    columns = st.columns(num_columns)

    for idx, recipe in enumerate(recipes):
        col = columns[idx % num_columns]  # Distribute recipes across columns
        with col:
            # Recipe card design with some padding and border
            st.markdown(
                f"""
                <div style="background-color:#f8f8f8; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                    <h3 style="color:#4CAF50; font-size: 20px; text-align:center;">🍽️ {recipe.get('name', 'Unnamed Recipe')}</h3>
                    <h4 style="color:#333; font-size: 16px; margin-bottom: 15px;">**Cuisine**: {recipe.get('cuisine', 'Unknown')}</h4>
                    <h4 style="color:#333; font-size: 16px; margin-bottom: 15px;">**Item of Choice**: {recipe.get('item_of_choice', 'Unknown')}</h4>
                    <hr style="border: 1px solid #ddd; margin-bottom: 15px;">
                    <h4 style="color:#4CAF50; font-size: 18px; margin-bottom: 5px;">Ingredients:</h4>
                    <ul style="list-style-type: none; padding-left: 0;">
            """
            )
            for ingredient in recipe.get('ingredients', []):
                st.markdown(f"<li style='font-size: 14px; color: #555;'>{ingredient}</li>", unsafe_allow_html=True)

            if "additional_ingredients" in recipe and recipe["additional_ingredients"]:
                st.markdown(
                    """
                    <h4 style="color:#4CAF50; font-size: 18px; margin-top: 15px;">Additional Ingredients:</h4>
                    <ul style="list-style-type: none; padding-left: 0;">
                    """
                )
                for add_ingredient in recipe.get('additional_ingredients', []):
                    st.markdown(f"<li style='font-size: 14px; color: #555;'>{add_ingredient}</li>", unsafe_allow_html=True)

            st.markdown(
                """
                </ul>
                <hr style="border: 1px solid #ddd; margin-bottom: 15px;">
                <h4 style="color:#4CAF50; font-size: 18px;">Instructions:</h4>
                <ol style="padding-left: 20px;">
                """
            )
            for step_num, step in enumerate(recipe.get('steps', []), 1):
                st.markdown(f"<li style='font-size: 14px; color: #555;'>{step}</li>", unsafe_allow_html=True)

            st.markdown(
                """
                </ol>
                </div>
                <br>
                """
            )  # End recipe card

            # Add a horizontal line between each recipe for clarity
            st.markdown("<hr style='border: 2px solid #f0f0f0;'>", unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Modern Recipe Generator", layout="wide")
    st.title("🍳 Recipe Generator")
    st.write("Generate delicious recipes based on your ingredients with AI.")

    st.sidebar.header("API Key Management")
    openai_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password", key="api_key_input_sidebar", placeholder="sk-XXXXXXXXXXXXXXXXXXXXXXXXXX", help="Get your API key from https://platform.openai.com/signup")

    col1, col2 = st.sidebar.columns(2)

    with st.sidebar:
        if col1.button("💾 Save API Key"):
            if not openai_key:
                st.warning("❌ Please fill in the API key field before saving.")
            else:
                with st.spinner("⏳ Validating API key..."):
                    is_valid = validate_openai_key(openai_key)
                    if is_valid:
                        st.toast("API key saved successfully! ✅")
                    else:
                        st.toast("Invalid OpenAI API key. Please check and try again. ❌")

        if col2.button("🔄 Reset API Key"):
            if not openai_key :
                st.warning("❌ No API key to reset.")
            else:
                with st.spinner("Resetting API key..."):
                    st.session_state.openai_key = None
                    st.success("OpenAI API key reset successfully!")   


    ingredients = st.text_input("🎤 Ingredients (comma-separated)")
    item = st.text_input("🍽️ Your preferred dish")
    cuisine = st.selectbox("🍝 Your preferred cuisine", [
        "Italian", "French", "Mexican", "Indian", "Chinese", "Japanese", "Thai", "Greek", "Turkish", "Moroccan", "Brazilian", "Korean", "Vietnamese", "Spanish", "Lebanese", "American", "Caribbean", "Russian", "German", "Ethiopian"
    ])
    num_recipes = st.slider("Number of recipes to generate", 1, 10, 5)

    if st.button("Generate Recipes"):
        if not openai_key:
            st.warning("Please enter your OpenAI API key.")
        elif len(item.split()) > 2:
            st.warning("Please enter only one dish name. Avoid listing multiple items.")
        elif not item:
            st.warning("Please enter your preferred dish.")
        elif not ingredients:
            st.warning("Please enter ingredients.")
        elif ',' not in ingredients:
            st.warning("Please separate ingredients with commas.")
        else:
            with st.spinner("Generating recipes..."):
                recipes = get_recipes_from_ingredients(openai_key, ingredients, item, cuisine, num_recipes)
            if recipes:
                st.success("Recipes generated successfully!")
                display_recipes(recipes)



    st.markdown(
        """
        <style>
        .bottom-right {
            position: fixed;
            bottom: 10px;
            right: 15px;
            font-size: 0.9em;
            color: gray;
        }
        </style>
        <div class="bottom-right">
            Made with ⚡ at 'The Hackers Playbook' ©. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
