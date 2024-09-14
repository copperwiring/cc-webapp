import streamlit as st
from openai import OpenAI
from PIL import Image
import streamlit as st

st.set_page_config(page_title="DALL.E 3 Image Generation")

OPENAI_KEY = st.secrets["OPENAI_KEY"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

def generate_image(image_description):
  client = OpenAI(api_key=OPENAI_KEY)
  response = client.images.generate(
  model="dall-e-3",
  prompt=f"{image_description}",
  size="1024x1024",
  quality="standard",
  n=1,
  )

  img_url = response.data[0].url
  return img_url


st.title('CC-T2I')
# st.subheader("Powered by OpenAI and Streamlit")

import streamlit as st

# Initialize session state variables if they don't exist
if "prolific_id" not in st.session_state:
    st.session_state["prolific_id"] = ""
if "disable_prolific_id" not in st.session_state:
    st.session_state["disable_prolific_id"] = False
if "disable_confirm_id" not in st.session_state:
    st.session_state["disable_confirm_id"] = False
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "disable_prompt_input" not in st.session_state:
    st.session_state["disable_prompt_input"] = False
if "disable_generate_button" not in st.session_state:
    st.session_state["disable_generate_button"] = False
if "image_generated" not in st.session_state:
    st.session_state["image_generated"] = False
if "breakfast_description" not in st.session_state:
    st.session_state["breakfast_description"] = ""
if "prompt_description" not in st.session_state:
    st.session_state["prompt_description"] = ""
if "generated_image" not in st.session_state:
    st.session_state["generated_image"] = None

# Define the callback function for the Submit button
def submit_callback():
    st.session_state["disable_prolific_id"] = True
    st.session_state["disable_confirm_id"] = True
    st.session_state["submitted"] = True

# Define the callback function for the Generate Image button
def generate_image_callback():
    st.session_state["disable_prompt_input"] = True
    st.session_state["disable_generate_button"] = True
    st.session_state["image_generated"] = True
    # Assume generate_image is a function that returns an image object
    st.session_state["generated_image"] = generate_image(st.session_state["prompt_description"])


# Placeholder function for image generation
def generate_image(prompt):
    client = OpenAI()
    response = client.images.generate(
    model="dall-e-3",
    prompt=f"{prompt}",
    size="1024x1024",
    quality="standard",
    n=1)

    img_url = response.data[0].url
    return img_url

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
    'Is the entered Prolific ID correct? Uncheck the box to edit it.',
    key="confirm_id",
    disabled=st.session_state["disable_confirm_id"]
)

if confirmation and prolific_id:
    # Use the on_click parameter to set the callback
    st.button('Submit', on_click=submit_callback)

    if st.session_state["submitted"]:
        st.warning("You will not be able to change your Prolific ID after this point.")
        st.write("Instructions")

        st.write("Describe in words the image that comes to your mind when you think of your breakfast in your country")
        # Text input for Breakfast Description
        breakfast_description = st.text_input(
            'Breakfast Description',
            value=st.session_state["breakfast_description"]
        )
        st.session_state["breakfast_description"] = breakfast_description

        if breakfast_description:
            st.warning("Once you enter your prompt and press enter, you will not be able to change it.")

            # Text input for Prompt Description
            prompt_description = st.text_input(
                'Enter your prompt',
                key="prompt",
                value=st.session_state["prompt_description"],
                disabled=st.session_state["disable_prompt_input"]
            )
            st.session_state["prompt_description"] = prompt_description

            if prompt_description:
                # Generate Image button with callback
                st.button(
                    'Generate Image',
                    on_click=generate_image_callback,
                    disabled=st.session_state["disable_generate_button"]
                )

                if st.session_state["image_generated"]:
                    # Display the generated image
                    st.image(st.session_state["generated_image"])
        else:
            st.warning("Please enter a description for your breakfast.")
else:
    st.info("Please enter and confirm your Prolific ID to proceed.")




# img_description = st.text_input('Image Desription')

# if st.button('Generate Image'):
#     generated_img = generate_image(img_description)
#     st.image(generated_img)





