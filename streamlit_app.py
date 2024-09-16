import streamlit as st
from openai import OpenAI
from PIL import Image
import streamlit as st
from supabase import create_client, Client
import base64
from streamlit_feedback import streamlit_feedback

st.cache_data.clear()
st.cache_resource.clear()

st.set_page_config(page_title="T2I Image Generation")

OPENAI_KEY = st.secrets["OPENAI_KEY"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]   

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)    

st.title('Culture Specific Image Generation Task')




st.markdown("---"*20)
# Write instructions numbered list
st.write("Instructions")
st.write("1. Browser compatibility: This task is best done on Chrome or Edge.")
st.write("2. Please disable VPN as it may give HTTPS errors.")
st.write("3. Since this task involves writing text in native language, please use a keyboard that supports your native language OR use your mobile phone")
st.write("4. Do not forget to write your Prolific ID in the first step and make sure to confirm it. Once you confirm it, you will not be able to change it.")
st.write("5. There is no word limit in the text input fields. You can write as much as you want.")
st.markdown("---"*20)


# Your image generation function
def generate_image(prompt):
    client = OpenAI(api_key=OPENAI_KEY)
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        response_format="b64_json",
        n=1
    )

    img_b64 = response.data[0].b64_json
    bytes_decoded = base64.b64decode(img_b64)
    image_path_on_supastorage = str(st.session_state["prolific_id"]) + "/"+ str(st.session_state["variation_iterator"])+".jpg"
    bucket_name = "images"
    supabase.storage.from_(bucket_name).upload(file=bytes_decoded,path=image_path_on_supastorage, file_options={"content-type": "image/jpeg"})
    db_image_url = supabase.storage.from_(bucket_name).get_public_url(image_path_on_supastorage)

    st.session_state["imgurls"][st.session_state["variation_iterator"]] = db_image_url
    st.session_state["openai_revised_prompts"][st.session_state["variation_iterator"]] = response.data[0].revised_prompt
    st.session_state["variation_iterator"] += 1
    return db_image_url

def update_db(feedback_text, satisfaction, appropriateness):
    """
    Update the existing record in the database with satisfaction, appropriateness and comments
    """
    data = [{
        "satisfaction": satisfaction,
        "appropriateness": appropriateness,
        "feedback": feedback_text
    }]

    supabase_table_response = (
        supabase.table("cc-t2i-test-attempts")
        .upsert({"prolific_id": st.session_state["prolific_id"], "data": data})
        .execute()
    )

    return supabase_table_response


# Initialize session state variables if they don't exist

if "prolific_id" not in st.session_state:
    st.session_state["prolific_id"] = ""
if "disable_prolific_id" not in st.session_state:       # to disable text input for prolific id
    st.session_state["disable_prolific_id"] = False
if "disable_confirm_id" not in st.session_state:        # to disbale checkbox where user confirms to continue with prolific id
    st.session_state["disable_confirm_id"] = False
if "disable_submit_button" not in st.session_state:     # to disable submit button after it is clicked using the callback
    st.session_state["disable_submit_button"] = False  
if "id_and_buttonclick_done" not in st.session_state:   # flag to see if prolificid + idconfirmation + submit button is clicked
    st.session_state["id_and_buttonclick_done"] = False
if "disable_breakfast_input" not in st.session_state:   # to enable/disbale text input for breakfast description
    st.session_state["disable_breakfast_input"] = False
if "breakfast_submitted" not in st.session_state:       # flag to see if breakfast description is submitted
    st.session_state["breakfast_submitted"] = False
if "breakfast_description_txt" not in st.session_state: # to store breakfast description text   
    st.session_state["breakfast_description_txt"] = ""
# if "breakfast_submit_show" not in st.session_state:
#     st.session_state["breakfast_submit_show"] = False
if "image_generated" not in st.session_state:            # flag to see if image is being generated
    st.session_state["image_generated"] = False
if "prompt_description" not in st.session_state:         # to store prompt description text
    st.session_state["prompt_description"] = ""
if "generated_image" not in st.session_state:            # to store generated image
    st.session_state["generated_image"] = None
if  "disable_generate_button" not in st.session_state:
    st.session_state["disable_generate_button"] = False
if "enable_feedback" not in st.session_state:
    st.session_state["enable_feedback"] = False
if "variation_iterator" not in st.session_state:
    st.session_state["variation_iterator"] = 0
if "show_thumbs" not in st.session_state:
    st.session_state["show_thumbs"] = False

# all data to be saved
if "prompt_list" not in st.session_state:
    st.session_state["prompt_list"] = [None] * 10
if "openai_revised_prompts" not in st.session_state:
    st.session_state["openai_revised_prompts"] = [None] * 10
if "imgurls" not in st.session_state:
    st.session_state["imgurls"] = [None] * 10


# Define the callback function for the Submit button
def submit_callback():
    st.session_state["disable_prolific_id"] = True
    st.session_state["disable_confirm_id"] = True
    st.session_state["id_and_buttonclick_done"] = True
    st.session_state["disable_submit_button"] = True


# Define the callback function for the Breakfast Description Submit button
def submit_breakfast_callback():
    st.session_state["disable_breakfast_input"] = True
    st.session_state["breakfast_submitted"] = True

# def onchange_breakfast_description_callback(value):
#     if len(value) > 10:
#         st.session_state["breakfast_submit_show"] = True

# Define the callback function for the Generate Image button
def generate_image_callback():
    st.session_state["disable_prompt_input"] = True
    # st.session_state["disable_generate_button"] = True
    st.session_state["image_generated"] = True
    # Use your actual image generation logic here
    st.session_state["generated_image"] = generate_image(st.session_state["prompt_description"])
    st.session_state["show_thumbs"] = True



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

    if st.session_state["id_and_buttonclick_done"]:
        st.warning("You will not be able to change your Prolific ID after this point.")
        st.write("Instructions")

        st.write("""Write some keywords that describe your breakfast in your country. Someone from France might write the following phrases: "shot of espresso, croissant, orange juice, reading the newspaper", while someone from Scotland might write "cup of tea, bowl of porridge, listening to morning radio".""")
        
        # Text input for Breakfast Description
        breakfast_description = st.text_area(
            'Enter your description here',
            value=st.session_state["breakfast_description_txt"],
            disabled=st.session_state["disable_breakfast_input"])
        
        st.session_state["breakfast_description_txt"] = breakfast_description

        if breakfast_description:
            st.warning("Once you submit your breakfast description, you will not be able to change it.")
            # Submit button for Breakfast Description
            st.button('Submit Breakfast Description', on_click=submit_breakfast_callback, disabled=st.session_state["breakfast_submitted"])
        else:
            st.info("Breakfast description submitted and cannot be changed.")

        # Proceed only if breakfast description is submitted
        if st.session_state["breakfast_submitted"]:
            st.warning("Once you enter your prompt and press enter, you will not be able to change it.")

            # Text input for Prompt Description
            prompt_description_val = st.text_area(
                'Now, you are going to use an image generation tool. You are tasked to describe your breakfast in your country. You can use the keywords above as a reference. Please write a sentence below. You are allowed to expand, edit or add to these sentences later to improve the image. This is your prompt',
                key="prompt",
                value=st.session_state["prompt_description"],
            )
            st.session_state["prompt_description"] = prompt_description_val
            st.session_state["prompt_list"][st.session_state["variation_iterator"]] = prompt_description_val

            if prompt_description_val:
                # Generate Image button with callback
                st.button(
                    'Generate Image',
                    on_click=generate_image_callback,
                    # disabled=st.session_state["disable_generate_button"]
                )
                st.warning("Please wait for the image to load. It may take a few seconds.")

                # st.spinner("Generating image...Please wait.")
                if st.session_state["image_generated"]:
                    # Display the generated image
                    st.image(st.session_state["generated_image"])

                    st.write("Image generated successfully! If you don't see it yet, please wait for a few seconds.")


                st.spinner("Please wait for the image to load.")

                if st.session_state["variation_iterator"] > 0 and st.session_state["show_thumbs"] == False:
                    st.info("""
                            1. As you are unhappy with the generated image, we need to generate it again to get a better image. 
                            2. Scroll up to the prompt text box and edit it.
                            3. Click on the 'Generate Image' button again to generate a new image.
                            4. It could be a new prompt or a slight variation of the previous prompt.
                            """)
                    
                def _thumbscallback():
                    option = st.session_state['thumbs_option']
                    st.write(option)
                    if option == "👎":
                        st.session_state["show_thumbs"] = False

                if st.session_state["show_thumbs"]:
                    option = st.selectbox(
                        "Are you satisfied with the generated image?",
                        ("None", "👍", "👎"),
                        index=None,
                        key='thumbs_option',  # Add a unique key
                        on_change=_thumbscallback,
                        placeholder="Select an option")

                    
                    # res = st.radio("Are you satisfied with the generated image?", ["thumbs_down", "thumbs_up"],
                    #          disabled=st.session_state["enable_feedback"])
                    st.warning("Only select the thumbs up when you are finally satisfied with the image and think it is closest to your mental picture of your breakfast. If you are not satisfied, please select thumbs down and edit your prompt.")

                    
                    if option == "👎":
                        option = "None"
                        st.session_state["show_thumbs"] = False
                    elif option == "👍":
                        st.session_state["enable_feedback"] = True

                        feedback_text = st.text_area("Please provide feedback on the generated image", height=100)
                        st.write(feedback_text)

                        # Add slider for satisfaction
                        satisfaction = st.slider("How well does this image represent your mental picture of your breakfast?", 0, 10, 5)
                        st.info("0: Not satisfied, 5: No strong feelings, 10: Very satisfied")

                        # Draw a line
                        st.markdown("---"*20)


                        # Add slider for appropriateness
                        appropriateness = st.slider("How appropriate is the generated image for the prompt?", 0, 10, 5)
                        st.info("0: Absolutely not appropriate, 5: Could be appropriate in some contexts but also not appropriate in others, 10: Absolutely appropriate")

                        submissions = []
                        for prompt, imgurl, openai_revised_prompt in zip(st.session_state["prompt_list"], st.session_state["imgurls"], st.session_state["openai_revised_prompt_list"]):
                            submissions.append({
                                "prompt": prompt,
                                "imgurl": imgurl,
                                "openai_revised_prompt": openai_revised_prompt,
                            })


                        def finalsubmit_response():
                            data = {
                            "prolific_id": st.session_state["prolific_id"],
                            "breakfast_description_txt": st.session_state["breakfast_description_txt"],
                            "submissions": submissions,
                            "satisfaction": satisfaction,
                            "appropriateness": appropriateness
                            }

                            supabase_table_response = (
                                supabase.table("cc-t2i-test-attempts")
                                .upsert({"prolific_id": st.session_state["prolific_id"], "data": data})
                                .execute()
                            )

                        st.button('Submit Response', on_click=finalsubmit_response, disabled=st.session_state["disable_submit_button"])
else:
    st.info("Please enter and confirm your Prolific ID to proceed.")
