import streamlit as st
import openai
import os
from dotenv import load_dotenv
import json
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
DEFAULT_OPENAI_MODEL = "gpt-4"

def get_recipes_from_ingredients(ingredients, item, cuisine, num_recipes=5):
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
    num_columns = 3  
    columns = st.columns(num_columns)
    
    for idx, recipe in enumerate(recipes):
        col = columns[idx % num_columns]  
        with col:
            st.subheader(f"🍽️ Recipe {idx + 1}: {recipe.get('name', 'Unnamed Recipe')}")
            st.write("**Ingredients:**")
            for ingredient in recipe.get('ingredients', []):
                st.write(f"- {ingredient}")
            
            if "additional_ingredients" in recipe and recipe["additional_ingredients"]:
                st.write("**Additional Items:**")
                for add_ingredient in recipe.get('additional_ingredients', []):
                    st.write(f"- {add_ingredient}")
            
            st.write("**Instructions:**")
            for step_num, step in enumerate(recipe.get('steps', []), 1):
                st.write(f"{step_num}. {step}")

            st.markdown("---") 

def main():
    st.set_page_config(page_title="Modern Recipe Generator", layout="wide")
    st.title("🍳 Recipe Generator")
    st.write("Generate delicious recipes based on your ingredients with AI.")

    ingredients = st.text_input("🎤 Ingredients (comma-separated)")
    item = st.text_input("🍽️ Your preferred dish")
    cuisine = st.selectbox("🍝 Your preferred cuisine", [
        "Italian", "French", "Mexican", "Indian", "Chinese", "Japanese", "Thai", "Greek", "Turkish", "Moroccan", "Brazilian", "Korean", "Vietnamese", "Spanish", "Lebanese", "American", "Caribbean", "Russian", "German", "Ethiopian"
    ])
    num_recipes = st.slider("Number of recipes to generate", 1, 10, 5)

    if st.button("Generate Recipes"):
        if len(item.split()) > 2:
            st.warning("Please enter only one dish name. Avoid listing multiple items.")
        elif not item:
            st.warning("Please enter your preferred dish")
        elif not ingredients:
            st.warning("Please enter ingredients.")
        elif ',' not in ingredients:
            st.warning("Please separate ingredients with commas.")
        else:
            with st.spinner("Generating recipes..."):
                recipes = get_recipes_from_ingredients(ingredients, item, cuisine, num_recipes)
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
