import streamlit as st
from openai import OpenAI
from PIL import Image
import streamlit as st

st.set_page_config(page_title="DALL.E 3 Image Generation")

OPENAI_KEY = st.secrets["OPENAI_KEY"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


st.title('CC-T2I')

# Your image generation function
def generate_image(prompt):
    client = OpenAI(api_key=OPENAI_KEY)
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    img_url = response.data[0].url
    return img_url

# Initialize session state variables if they don't exist
if "prolific_id" not in st.session_state:
    st.session_state["prolific_id"] = ""
if "disable_prolific_id" not in st.session_state:
    st.session_state["disable_prolific_id"] = False
if "disable_confirm_id" not in st.session_state:
    st.session_state["disable_confirm_id"] = False
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "disable_submit_button" not in st.session_state:
    st.session_state["disable_submit_button"] = False
if "disable_breakfast_input" not in st.session_state:
    st.session_state["disable_breakfast_input"] = False
if "breakfast_submitted" not in st.session_state:
    st.session_state["breakfast_submitted"] = False
if "breakfast_description" not in st.session_state:
    st.session_state["breakfast_description"] = ""
if "breakfast_submit_show" not in st.session_state:
    st.session_state["breakfast_submit_show"] = False
if "image_generated" not in st.session_state:
    st.session_state["image_generated"] = False
if "prompt_description" not in st.session_state:
    st.session_state["prompt_description"] = ""
if "generated_image" not in st.session_state:
    st.session_state["generated_image"] = None


# Define the callback function for the Submit button
def submit_callback():
    st.session_state["disable_prolific_id"] = True
    st.session_state["disable_confirm_id"] = True
    st.session_state["submitted"] = True
    st.session_state["disable_submit_button"] = True

# Define the callback function for the Breakfast Description Submit button
def submit_breakfast_callback():
    st.session_state["disable_breakfast_input"] = True
    st.session_state["breakfast_submitted"] = True

def onchange_breakfast_description_callback(value):
    if len(value) > 10:
        st.session_state["breakfast_submit_show"] = True

# Define the callback function for the Generate Image button
def generate_image_callback():
    st.session_state["disable_prompt_input"] = True
    st.session_state["disable_generate_button"] = True
    st.session_state["image_generated"] = True
    # Use your actual image generation logic here
    st.session_state["generated_image"] = generate_image(st.session_state["prompt_description"])



# Text input for Prolific ID
prolific_id = st.text_input(
    'Enter your Prolific ID',
    value=st.session_state["prolific_id"],
    disabled=st.session_state["disable_prolific_id"]
)

# Update the Prolific ID in session state
st.session_state["prolific_id"] = prolific_id

# Checkbox for confirmation
confirmation = st.checkbox(
    'Continue with Profilic ID? You can not change it later',
    key="confirm_id",
    disabled=st.session_state["disable_confirm_id"]
)

if confirmation and prolific_id:
    # Use the on_click parameter to set the callback
    st.button('Submit', on_click=submit_callback, disabled=st.session_state["disable_submit_button"])

    if st.session_state["submitted"]:
        st.warning("You will not be able to change your Prolific ID after this point.")
        st.write("Instructions")

        st.write("Write some keywords that describe your breakfast in your country. For example: shot of espresso, croissant, orange juice, reading the newspaper, etc.")
        
        # Text input for Breakfast Description
        breakfast_description = st.text_area(
            'Enter your description here',
            value=st.session_state["breakfast_description"],
            disabled=st.session_state["disable_breakfast_input"]        )
        st.session_state["breakfast_description"] = breakfast_description

        if breakfast_description:
            st.warning("Once you submit your breakfast description, you will not be able to change it.")
            # Submit button for Breakfast Description
            st.button('Submit Breakfast Description', on_click=submit_breakfast_callback, disabled= st.session_state["breakfast_submitted"])
        else:
            st.info("Breakfast description submitted and cannot be changed.")

        # Proceed only if breakfast description is submitted
        if st.session_state["breakfast_submitted"]:
            st.warning("Once you enter your prompt and press enter, you will not be able to change it.")

            # Text input for Prompt Description
            prompt_description = st.text_input(
                'Enter your prompt',
                key="prompt",
                value=st.session_state["prompt_description"],
                # disabled=st.session_state["disable_prompt_input"]
            )
            st.session_state["prompt_description"] = prompt_description

            if prompt_description:
                # Generate Image button with callback
                st.button(
                    'Generate Image',
                    on_click=generate_image_callback,
                    # disabled=st.session_state["disable_generate_button"]
                )

                if st.session_state["image_generated"]:
                    # Display the generated image
                    st.image(st.session_state["generated_image"])
else:
    st.info("Please enter and confirm your Prolific ID to proceed.")
