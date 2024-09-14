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
if st.button('Show Instructions'):
    st.write("Instructions")



# img_description = st.text_input('Image Desription')

# if st.button('Generate Image'):
#     generated_img = generate_image(img_description)
#     st.image(generated_img)





