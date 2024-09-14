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

prolific_id = st.text_input('Enter your Prolific ID', disabled=("prolific_id" in st.session_state and st.session_state.get("disable_prolific_id", False)))

confirmation = st.checkbox('Is the entered Prolific ID correct? Uncheck the box to edit it.', key="confirm_id", disabled=st.session_state.get("disable_confirm_id", False))

if confirmation and prolific_id:
    if st.button('Submit'):
        st.session_state['prolific_id'] = prolific_id
        st.session_state["disable_prolific_id"] = True
        st.session_state["disable_confirm_id"] = True
        st.experimental_rerun()
        # Blurring the text input and checkbox by disabling them permanently after submission
        st.text_input('Enter your Prolific ID', value=prolific_id, disabled=True)
        st.checkbox('Is the entered Prolific ID correct?', value=True, disabled=True)
        st.write("Instructions")
        st.warning("You will not be able to change your Prolific ID after this point.")
        
        st.write("Describe in words the image that comes to your mind when you think of your breakfast in your country")
        breakfast_description = st.text_input('Breakfast Description')
        
        if breakfast_description:
            st.warning("Once you enter your prompt and press enter, you will not be able to change it.")
            prompt_description = st.text_input('Enter your prompt', key="prompt", on_change=lambda: st.session_state.pop("prompt", None))
        else:
            st.warning("Please enter a description for your breakfast.")
    else:
        st.warning("Please verify your Prolific ID and confirm. Once you submit, you will not be able to change your Prolific ID.")



# img_description = st.text_input('Image Desription')

# if st.button('Generate Image'):
#     generated_img = generate_image(img_description)
#     st.image(generated_img)





