import streamlit as st
import openai
from dotenv import load_dotenv
import os
import traceback
from openai import OpenAI, OpenAIError
import base64
load_dotenv(verbose=True, override=True, dotenv_path=".env")


anime_style = [
  {"studio": "Ghibli", "prompt": "Transform this image to Studio Ghibli style with soft colors, nature-filled scenery, and magical atmosphere.", "helper": "Whimsical, nature-loving worlds seen in *Spirited Away* and *My Neighbor Totoro*."},
  {"studio": "Mappa", "prompt": "Transform this image to MAPPA style with intense detail, dramatic shadows, and cinematic action energy.", "helper": "High-intensity visuals from anime like *Attack on Titan* and *Jujutsu Kaisen*."},
  {"studio": "Kyoto_Animation", "prompt": "Transform this image to Kyoto Animation style with soft lighting, delicate facial expressions, and warm slice-of-life vibes.", "helper": "Emotional, beautiful scenes from *Clannad* and *Violet Evergarden*."},
  {"studio": "Ufotable", "prompt": "Transform this image to Ufotable style with glowing effects, dynamic poses, and high-contrast anime lighting.", "helper": "Stylized, cinematic flair from *Demon Slayer*."},
  {"studio": "Bones", "prompt": "Transform this image to Studio Bones style with sharp lines, stylish characters, and bold action scenes.", "helper": "Stylish and energetic action seen in *My Hero Academia* and *Mob Psycho 100*."},
  {"studio": "Wit_Studio", "prompt": "Transform this image to Wit Studio style with clean compositions, powerful framing, and vivid animation depth.", "helper": "Polished storytelling seen in *Vinland Saga* and *The Ancient Magus' Bride*."},
  {"studio": "Madhouse", "prompt": "Transform this image to Madhouse style with sharp edges, moody tones, and psychological tension.", "helper": "Gritty, intense animation like *Death Note* and *One Punch Man* (S1)."},
  {"studio": "Toei_Animation", "prompt": "Transform this image to Toei Animation style with bright colors, classic anime look, and energetic vibes.", "helper": "Old-school anime charm from *Dragon Ball* and *One Piece*."},
  {"studio": "Sunrise", "prompt": "Transform this image to Sunrise style with mecha elements, sci-fi backgrounds, and heroic postures.", "helper": "Legendary mecha sagas like *Gundam* and *Code Geass*."},
  {"studio": "Trigger", "prompt": "Transform this image to Studio Trigger style with exaggerated features, bold colors, and wild expressions.", "helper": "Over-the-top visuals from *Kill la Kill* and *Promare*."},
  {"studio": "Production_ig", "prompt": "Transform this image to Production I.G style with cyberpunk tones, clean linework, and futuristic settings.", "helper": "Futuristic cyber-aesthetics from *Ghost in the Shell*."},
  {"studio": "Cloverworks", "prompt": "Transform this image to CloverWorks style with modern anime detail, soft shadows, and appealing character design.", "helper": "Modern, polished anime like *Spy x Family* and *The Promised Neverland*."},
  {"studio": "A1_Pictures", "prompt": "Transform this image to A-1 Pictures style with polished look, vibrant colors, and fantasy undertones.", "helper": "Colorful, detailed anime like *Sword Art Online* and *Fairy Tail*."},
  {"studio": "Pierrot", "prompt": "Transform this image to Studio Pierrot style with classic shonen vibe, bold outlines, and high-energy action.", "helper": "Long-running hits like *Naruto* and *Bleach*."},
  {"studio": "David_Production", "prompt": "Transform this image to David Production style with bold poses, wild color palettes, and comic-style shading.", "helper": "Iconic visuals from *JoJo’s Bizarre Adventure*."},
  {"studio": "Liden_Films", "prompt": "Transform this image to Liden Films style with raw grit, strong contrast, and powerful close-ups.", "helper": "Stylized drama in shows like *Tokyo Revengers*."},
  {"studio": "Silver_Link", "prompt": "Transform this image to Silver Link style with vivid school life tones, colorful characters, and fantasy sparkle.", "helper": "Fantasy-infused school anime like *Kokoro Connect*."},
  {"studio": "Studio_Deen", "prompt": "Transform this image to Studio Deen style with vintage anime tones and expressive emotional storytelling.", "helper": "Classic emotional styles seen in *Fate/stay night (2006)* and *Higurashi*."}
]



western_style = [
  {"studio": "Pixar", "prompt": "Transform this image to Pixar style with high-quality 3D look, emotional tone, and expressive characters.", "helper": "Heartwarming and detailed 3D animation from *Toy Story* and *Inside Out*."},
  {"studio": "Disney", "prompt": "Transform this image to Disney style with fairytale charm, clean animation, and magical lighting.", "helper": "Classic princess magic from *Frozen* and *Tangled*."},
  {"studio": "Dreamworks", "prompt": "Transform this image to DreamWorks style with playful poses, exaggerated expressions, and cinematic flair.", "helper": "Stylish fun seen in *Shrek* and *How to Train Your Dragon*."},
  {"studio": "Illumination", "prompt": "Transform this image to Illumination style with bright, minimal 3D design and fun, cartoonish vibe.", "helper": "Simple, humorous animation like *Despicable Me* and *Minions*."},
  {"studio": "Blue_sky", "prompt": "Transform this image to Blue Sky style with smooth 3D models, icy palettes, and expressive animals.", "helper": "Quirky 3D charm from *Ice Age* and *Rio*."},
  {"studio": "Sony_pictures", "prompt": "Transform this image to Sony Pictures Animation style with bold outlines, comic-style effects, and dynamic angles.", "helper": "Animated comic brilliance like *Into the Spider-Verse*."},
  {"studio": "Laika", "prompt": "Transform this image to Laika style with eerie stop-motion texture, gothic tone, and detailed settings.", "helper": "Stop-motion artistry from *Coraline* and *ParaNorman*."},
  {"studio": "Nickelodeon", "prompt": "Transform this image to Nickelodeon style with quirky characters, bright colors, and humorous charm.", "helper": "Bold and unique cartoons like *Avatar: The Last Airbender* and *SpongeBob*."},
  {"studio": "Cartoon_network", "prompt": "Transform this image to Cartoon Network style with experimental 2D animation and creative exaggeration.", "helper": "Playful and surreal styles from *Adventure Time* and *Ben 10*."},
  {"studio": "Warner_bros", "prompt": "Transform this image to Warner Bros Animation style with classic cartoon energy, expressive faces, and bold slapstick.", "helper": "Golden-age cartoon style like *Looney Tunes*."},
  {"studio": "Aardman", "prompt": "Transform this image to Aardman Animations style with claymation look, UK humor, and textured handmade charm.", "helper": "British clay animation like *Wallace & Gromit*."},
  {"studio": "Titmouse", "prompt": "Transform this image to Titmouse style with edgy adult humor, sharp lines, and chaotic animation energy.", "helper": "Alternative adult animation like *The Midnight Gospel*."},
  {"studio": "Bento_Box", "prompt": "Transform this image to Bento Box style with satirical adult humor, minimal linework, and flat comedy scenes.", "helper": "Sitcom-style cartoons like *Bob’s Burgers*."},
  {"studio": "Mercury_Filmworks", "prompt": "Transform this image to Mercury Filmworks style with smooth vector lines, vibrant flat color, and clean animation aesthetics.", "helper": "High-quality 2D visuals from *The Lion Guard*."},
  {"studio": "Spindlehorse", "prompt": "Transform this image to SpindleHorse style with gothic cartoon horror, surreal humor, and sharp contrast.", "helper": "Dark humor and gothic tones in *Hazbin Hotel* and *Helluva Boss*."},
  {"studio": "ShadowMachine", "prompt": "Transform this image to ShadowMachine style with adult satire, gritty surrealism, and detailed textures.", "helper": "Emotional adult stories like *BoJack Horseman*."}
]


custom_styles = [
  {"studio": "Custom_Retro_80s", "prompt": "Transform this image to retro 80s style with neon glow, VHS textures, and cyberpunk city vibes.", "helper": "Neon-lit synthwave and VHS aesthetics from retro-futuristic media."},
  {"studio": "Custom_Noir_Style", "prompt": "Transform this image to noir style with moody black & white tones, film grain, and detective atmosphere.", "helper": "Classic noir films like *Sin City* or *The Maltese Falcon*."},
  {"studio": "Custom_Watercolor", "prompt": "Transform this image to a watercolor painting with soft edges, brush strokes, and pastel colors.", "helper": "Delicate, artistic renderings using watercolor textures."},
  {"studio": "Custom_Low_Poly", "prompt": "Transform this image to low poly art style with geometric shapes, flat shading, and stylized simplicity.", "helper": "Stylized minimalist 3D visuals found in mobile or indie games."},
  {"studio": "Custom_Paper_Cutout", "prompt": "Transform this image to paper cutout style with layered textures and handmade paper effects.", "helper": "Crafted look similar to stop-motion or storybook visuals."}
]


video_game_styles = [
  {"studio": "FromSoftware", "prompt": "Transform this image to FromSoftware game style with gothic architecture, dark fantasy, and eerie atmosphere.", "helper": "Dark RPGs like *Dark Souls* and *Elden Ring* with haunting scenery."},
  {"studio": "Nintendo", "prompt": "Transform this image to Nintendo style with vibrant colors, joyful vibe, and cartoon-like characters.", "helper": "Playful, cheerful worlds like *Mario* and *Zelda*."},
  {"studio": "CD_Projekt_Red", "prompt": "Transform this image to CD Projekt Red style with realistic characters, medieval fantasy tone, and immersive landscapes.", "helper": "Rich fantasy worlds like *The Witcher 3*."},
  {"studio": "Blizzard", "prompt": "Transform this image to Blizzard style with fantasy armor, magical elements, and polished 3D fantasy.", "helper": "Epic fantasy visuals from *World of Warcraft* and *Overwatch*."},
  {"studio": "Capcom", "prompt": "Transform this image to Capcom style with arcade aesthetics, strong characters, and anime-influenced proportions.", "helper": "Dynamic action games like *Street Fighter* and *Devil May Cry*."},
  {"studio": "Valve", "prompt": "Transform this image to Valve style with gritty realism, sci-fi dystopia, and immersive lighting.", "helper": "Realistic world-building from *Half-Life* and *Portal*."}
]


comic_book_styles = [
  {"studio": "Marvel_Comics", "prompt": "Transform this image to Marvel Comics style with bold outlines, dynamic poses, and superhero energy.", "helper": "Colorful heroes and action-packed visuals from *Spider-Man* and *X-Men*."},
  {"studio": "DC_Comics", "prompt": "Transform this image to DC Comics style with darker tones, heroic silhouettes, and gothic cities.", "helper": "Moody and iconic heroes from *Batman* and *Justice League*."},
  {"studio": "Manga_Style", "prompt": "Transform this image to black and white manga style with dramatic linework and expressive paneling.", "helper": "Traditional Japanese comics like *One Piece* and *Naruto*."},
  {"studio": "Webtoon", "prompt": "Transform this image to Webtoon style with vertical scroll layout, bright color palettes, and romantic flair.", "helper": "Colorful digital comics like *Lore Olympus* and *Omniscient Reader*."},
  {"studio": "Indie_Comic", "prompt": "Transform this image to indie comic style with experimental textures, alternative aesthetics, and raw emotions.", "helper": "Visually unique graphic novels like *Saga* and *Monstress*."}
]




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
    
def image_generator(image: str, prompt: str, openai_key: str, action: str, studio_style: str, number_of_images: str , resolution: str, quality: str,) -> str:
    """
    Generates or transforms an image using OpenAI's GPT-image-1 model.

    Args:
        image (str): The image to be used as a reference (for transformation).
        prompt (str): The text prompt for the image generation.
        openai_key (str): The OpenAI API key.
        action (str): The action to perform ("generate_image" or "transform_image").
        studio_style (str): The style of the image to be generated or transformed.
        number_of_images (str): The number of images to generate.
        resolution (str): The resolution of the generated image.
        quality (str): The quality of the generated image.

    Returns:
        str: The path to the generated or transformed image.
    """
    try:
        # Set OpenAI API key
        openai.api_key = openai_key
        if not openai_key:
            raise ValueError("OpenAI API key is required.")

        output_file = "generated-image.png" if action == "generate_image" else "transformed-image.png"

        # Generate Image
        if action == "generate_image":
            generate_prompt = f"Create an image in the style of {studio_style} with the following prompt: {prompt}"
            response = openai.images.generate(
                model="gpt-image-1",
                prompt=generate_prompt,
                n=number_of_images,
                quality=quality,
                size=resolution,
            )
            image_base64 = response.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)

            with open(output_file, "wb") as f:
                f.write(image_bytes)

        # Transform Image
        elif action == "transform_image":
            transform_prompt = f"Create an image in the style of {studio_style} with the following prompt: {prompt}"
            response = openai.images.edit(
                model="gpt-image-1",
                image=image,
                prompt=transform_prompt,
                size="1024x1024",
                n=1,
            )
            image_base64 = response.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
        
        with open(output_file, "wb") as f:
            f.write(image_bytes)

        return output_file

    except Exception as e:
        print(f"Error in image generation: {e}")
        traceback.print_exc()
        return None


def main():
    st.set_page_config(page_title="Vision Crafter", page_icon=":art:", layout="wide")
    st.title(":art: Vision Crafter")
    st.markdown("VisionCrafter is an AI platform that generates and transforms images into stunning visuals across animation styles, from anime to video games, blending creativity with generative intelligence.")

    st.sidebar.header("Settings")
    
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
    


    # Sidebar title
    st.sidebar.markdown("---")
    st.sidebar.markdown('<div style="font-size: 22px; font-weight: bold; color: #A45A52;">🎨 Select Image Style</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # Combine all style configurations into one expander
    with st.sidebar.expander("🎨 Image Style Configuration", expanded=True):
        # Style selection
        st.radio(
            "Choose the style of the image:",
            ["Anime Style", "Western Animation", "Video Game Style", "Comic Book Style", "Custom Styles"],
            key="style",
        )

        # Dynamically display studio options based on the selected style
        style = st.session_state.style

        if style == "Anime Style":
            studio_options = [studio["studio"] for studio in anime_style]
            st.selectbox("Select Anime Studio:", studio_options, key="studio")

        elif style == "Western Animation":
            studio_options = [studio["studio"] for studio in western_style]
            st.selectbox("Select Western Animation Studio:", studio_options, key="studio")

        elif style == "Video Game Style":
            studio_options = [studio["studio"] for studio in video_game_styles]
            st.selectbox("Select Video Game Studio:", studio_options, key="studio")

        elif style == "Comic Book Style":
            studio_options = [studio["studio"] for studio in comic_book_styles]
            st.selectbox("Select Comic Book Studio:", studio_options, key="studio")

        elif style == "Custom Styles":
            studio_options = [studio["studio"] for studio in custom_styles]
            st.selectbox("Select Custom Style:", studio_options, key="studio")

        else:
            st.error("Invalid style selected. Please choose a valid style.")

    selected_studio_style = st.session_state.get("studio")

    st.sidebar.markdown(
        f'<div style="color: white;margin-left:20px;">You have Selected : <span style="color: #FF2400;">{selected_studio_style}</span></div>',
        unsafe_allow_html=True,
        )

    tab1, tab2 = st.tabs(["Generate Image", "Transform Image"])
    with tab1:
        # Dynamically fetch the selected studio details
        selected_studio = next(
            (studio for studio in anime_style + western_style + custom_styles + video_game_styles + comic_book_styles
             if studio["studio"] == st.session_state.get("studio")), None
        )
        prompt_placeholder = selected_studio["prompt"] if selected_studio else "e.g. Transform this image to animated style with vibrant colors and whimsical characters."
        help_text = selected_studio["helper"] if selected_studio else "e.g. Spirited Away, My Neighbor Totoro"

        action = "generate_image"

        # Text area for entering the prompt
        prompt_input = st.text_area("Enter your prompt:", placeholder=prompt_placeholder, key="generate_prompt", help=help_text)
        number_of_images = st.slider("Number of images to generate:", min_value=1, max_value=10, value=1, step=1, key="num_images")
        resolution = st.selectbox("Select image resolution:", ['auto','1024x1024', '1024x1536', '1536x1024'], key="resolution")
        quality = st.selectbox("Select image quality:", ['auto','low','medium','high'], key="quality")


        # Button to generate the image
        if st.button("Generate Image", key="generate_image"):
            if not openai_key:
                st.error("Please enter a valid OpenAI API key.")
            elif not prompt_input:
                st.error("Please provide a text prompt for image generation.")
            else:
                with st.spinner("Generating image... May take a few moment"):
                    generated_image = image_generator(number_of_images=number_of_images , resolution=resolution, quality=quality, studio_style=selected_studio_style, prompt=prompt_input, openai_key=openai_key, action=action, image=None) 
                    if generated_image:
                        st.success("Image generated successfully!")
                        st.image(generated_image, caption="Generated Image", width=400, channels="RGB")
                        st.download_button("Download Generated Image", data=open(generated_image, "rb"), file_name="generated-image.png", mime="image/png")
                    else:
                        st.error("Failed to generate image. Please try again.")

    with tab2:
            upload_image = st.file_uploader("Select an image to transform", type=["jpg", "jpeg", "png"], key="image_upload")
            if upload_image:
                st.image(upload_image, caption="Uploaded Image", width=250, channels="RGB")
            selected_studio = next((studio for studio in anime_style + western_style + custom_styles + video_game_styles + comic_book_styles if studio["studio"] == st.session_state.get("studio")), None)        
            prompt_placeholder = selected_studio["prompt"] if selected_studio else "e.g. Transform this image to animated style with vibrant colors and whimsical characters."
            help_text = selected_studio["helper"] if selected_studio else "e.g. Spirited Away, My Neighbor Totoro"
            prompt_input = st.text_area("Enter your prompt:", placeholder=prompt_placeholder, key="transform_prompt", help=help_text)
            number_of_images = st.slider("Number of images to generate:", min_value=1, max_value=10, value=1, step=1, key="transform_num_images")
            resolution = st.selectbox("Select image resolution:", ['auto','1024x1024', '1024x1536', '1536x1024'], key="transform_resolution")
            quality = st.selectbox("Select image quality:", ['auto','low','medium','high'], key="transform_quality")
            action = "transform_image"

            if st.button("Transform Image", key="transform_image"):
                if not openai_key :
                    st.error("Please enter a valid OpenAI API key.")
                elif not upload_image:
                    st.error("Please upload an image for image transformation.")
                elif not prompt_input:
                    st.error("Please provide a text prompt for image transformation.")     
                else:
                    with st.spinner("Transforming image... May take a few moment"):
                        transformed_image = image_generator(number_of_images=number_of_images , resolution=resolution, quality=quality, studio_style=selected_studio_style, prompt=prompt_input, openai_key=openai_key, action=action, image=upload_image)
                        col1, col2 = st.columns([3,2])
                        if upload_image:
                            col1.image(upload_image, caption="Uploaded Image", width=500, channels="RGB") 
                        if transformed_image:
                            st.toast("Image transformed successfully!")
                            col2.image(transformed_image, caption="Transformed Image", width=500, channels="RGB")
                            st.download_button("Download Transformed Image", data=open(transformed_image, "rb"), file_name="transformed-image.png", mime="image/png")
                            

if __name__ == "__main__":
    main()