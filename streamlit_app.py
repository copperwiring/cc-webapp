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

prolific_id = st.text_input('Enter your Prolific ID')
if st.button('Submit') and prolific_id:
    confirmation = st.checkbox('Is the entered Prolific ID correct?')
    if confirmation:
        st.write("Instructions")
        st.warning("You will not be able to change your Prolific ID after this point.")
    else:
        st.warning("Please verify your Prolific ID and confirm. Once you confirm, you will not be able to change your Prolific ID.")

    st.write("Describe in words the image that comes to your mind when you think of your breakfast in your country")
    breakfast_description = st.text_input('Breakfast Description')

    if not breakfast_description:
        st.warning("Please enter a description for your breakfast.")
    else:
        st.warning("Once you enter your prompt and press enter, you will not be able to change it.")
        prompt_description = st.text_input('Enter your prompt', key="prompt", on_change=lambda: st.session_state.pop("prompt", None))



# img_description = st.text_input('Image Desription')

# if st.button('Generate Image'):
#     generated_img = generate_image(img_description)
#     st.image(generated_img)





