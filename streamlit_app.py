import streamlit as st
from openai import OpenAI
from PIL import Image
import streamlit as st
from supabase import create_client, Client
import base64

st.cache_data.clear()
st.cache_resource.clear()

st.set_page_config(page_title="T2I Image Generation")

OPENAI_KEY = st.secrets["OPENAI_KEY"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]   

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)    

st.title('Culture Specific Image Generation Task')

task_name = "breakfast"

st.markdown("---"*20)

# Write instructions numbered list
st.write("Instructions")
st.write(f" Goal: To generate images of 'your {task_name}' using an image generation tool.")
st.write("1. Browser compatibility: This task is best done on Chrome or Edge.")
st.write("2. Please disable work VPN as it may give HTTPS errors. If you are on a university wifi, please use your mobile data to avoid firewall issues.")
st.write("3. One part of task involves writing text in native language, please use a computer keyboard that supports your native language OR use your mobile phone with native language keyboard.")
st.write("4. Do not forget to write your Prolific ID in the first step and make sure to confirm it. Once you confirm it, you will not be able to change it.")
st.write("5. There is no word limit in the text input fields. You can write as much as you want.")
st.write("6. If webapp crashes (internet issue, etc), please refresh the page and start again. You will be compensated for your completed responses.")
st.markdown("---"*20)

prefix_prompt = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS: "
# Your image generation function
def generate_image(prompt):
    client = OpenAI(api_key=OPENAI_KEY)
    response = client.images.generate(
        model="dall-e-3",
        prompt=prefix_prompt + prompt,
        size="1024x1024",
        quality="standard",
        response_format="b64_json",
        n=1
    )

    img_b64 = response.data[0].b64_json
    bytes_decoded = base64.b64decode(img_b64)
    image_path_on_supastorage = str(st.session_state["prolific_id"]) + "/"+ task_name + "/" + str(st.session_state["variation_iterator"])+".jpg"
    bucket_name = "images"
    supabase.storage.from_(bucket_name).upload(file=bytes_decoded,path=image_path_on_supastorage, file_options={"content-type": "image/jpeg", "upsert": 'true'})
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
if f"disable_{task_name}_input" not in st.session_state:   # to enable/disbale text input for {task_name} description
    st.session_state[f"disable_{task_name}_input"] = False
if f"{task_name}_submitted" not in st.session_state:       # flag to see if {task_name} description is submitted
    st.session_state[f"{task_name}_submitted"] = False
if f"{task_name}_description_txt" not in st.session_state: # to store {task_name} description text   
    st.session_state[f"{task_name}_description_txt"] = ""
# if "{task_name}_submit_show" not in st.session_state:
#     st.session_state["{task_name}_submit_show"] = False
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
    st.session_state["prompt_list"] = [None] * 12
if "openai_revised_prompts" not in st.session_state:
    st.session_state["openai_revised_prompts"] = [None] * 12
if "imgurls" not in st.session_state:
    st.session_state["imgurls"] = [None] * 12

# success message
if "success_message" not in st.session_state:
    st.session_state["success_message"] = False


# Define the callback function for the Submit button
def submit_callback():
    st.session_state["disable_prolific_id"] = True
    st.session_state["disable_confirm_id"] = True
    st.session_state["id_and_buttonclick_done"] = True
    st.session_state["disable_submit_button"] = True


# Define the callback function for the {task_name} Description Submit button
# def submit_breakfast_callback():
#     st.session_state[f"disable_{task_name}_input"] = True
#     st.session_state[f"{task_name}_submitted"] = True

# Define the callback function for the Generate Image button
def generate_image_callback():
    st.session_state["disable_prompt_input"] = True
    # st.session_state["disable_generate_button"] = True
    st.session_state["image_generated"] = True
    # Use your actual image generation logic here
    st.session_state["generated_image"] = generate_image(st.session_state["prompt_description"])
    st.session_state["show_thumbs"] = True


# generate random key using uuid
# Text input for Prolific ID
prolific_id = st.text_input(
    'Enter your Prolific ID',
    value=st.session_state["prolific_id"],
    key = "prolific_id_input",
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

        if st.session_state["id_and_buttonclick_done"]:
            # st.warning("Once you enter your prompt and press enter, you will not be able to change it.")
            st.info("""
                1. Here, you are going to write in your native language.
                2. Native language is the language you speak with your family.
                3. Do not write in English if it is not your native language."""
            )
            # Text input for Prompt Description
            prompt_description_val = st.text_area(
                f"Now, you are going to use an image generation tool. You should describe 'your {task_name}'. You can be as detailed as you want. No word limit. You are allowed to expand, edit or add to these sentences later to improve the image. We will use your description to generate an image.",
                key="prompt",
                value=st.session_state["prompt_description"],
                help="This has to be written in your native language.",
            )
            st.warning("Did you write in your native language? If you can't see Generate Image button, please click anywhere outside the text box.")
            st.session_state["prompt_description"] = prompt_description_val
            st.session_state["prompt_list"][st.session_state["variation_iterator"]] = prompt_description_val

            if prompt_description_val:
                # Generate Image button with callback
                st.button(
                    'Generate Image',
                    on_click=generate_image_callback,
                    help = "You also click anwhere outside the text box to see the generate button",
                    # disabled=st.session_state["disable_generate_button"]
                )
                st.warning("Click Generate Image. Please wait for the image to load. It may take a few seconds.")
                

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
                        f"""Are you sure this is what 'your {task_name}' looks like? Select '👍' if you are happy with it, else select '👎' """,
                        ("None", "👍", "👎"),
                        index=None,
                        key='thumbs_option',  # Add a unique key
                        on_change=_thumbscallback,
                        placeholder="Select an option")

                    
                    # res = st.radio("Are you satisfied with the generated image?", ["thumbs_down", "thumbs_up"],
                    #          disabled=st.session_state["enable_feedback"])
                    st.warning(f"Only select the thumbs up when you are finally satisfied with the image and think it is closest to your mental picture of your {task_name}. If you are not satisfied, please select thumbs down and edit your prompt.")

                    
                    if option == "👎":
                        option = "None"
                        st.session_state["show_thumbs"] = False
                    elif option == "👍":
                        st.session_state["enable_feedback"] = True

                        feedback_text = st.text_area("Please provide feedback on the generated image in 'English' ", height=100, key = "feedback")
                        st.write(feedback_text)

                        # Add slider for satisfaction
                        satisfaction = st.slider(f"How well does this image represent your mental picture of your {task_name}?", 0, 10, 5)
                        st.info("0: Not satisfied, 5: No strong feelings, 10: Very satisfied")

                        # Draw a line
                        st.markdown("---"*20)


                        # Add slider for appropriateness
                        appropriateness = st.slider("How appropriate is the generated image for the prompt?", 0, 10, 5)
                        st.info("0: Absolutely not appropriate, 5: Could be appropriate in some contexts but also not appropriate in others, 10: Absolutely appropriate")

                        # Draw a line
                        st.markdown("---"*20)

                        # Add a text area for the user to enter the above details and save the answers in the database
                        st.write("Thank you!! Finally, please enter the following details:")
                        st.info("Fields are mandatory. Write in 'English' only")
                        # 1. The language they use to speak with their family
                        language_family = st.text_input("The language you use to speak with your family", key = "language_family")
                        # 2. The language they use to speak with their colleagues
                        language_colleagues = st.text_input("The language you use to speak with your colleagues", key = "language_colleagues")
                        # 3. The language their mothers speak
                        language_mothers = st.text_input("The language your mother speaks", key = "language_mothers")
                        # 4. The language their fathers speak
                        language_fathers = st.text_input("The language your father speaks", key = "language_fathers")
                        # 5. The country they were born in
                        country_born = st.text_input("The country you were born in", key = "country_born")
                        # Years they have lived in the country they were born in
                        ques_years_born = f"How many years you have lived in the country you were born in: {country_born}"
                        years_born = st.text_input(ques_years_born, key = "years_born")
                        # 6. The country they currently live in
                        country_live = st.text_input("The country you currently live in", key = "country_live")
                        # 7. How many years they have lived in the country they currently live in. Use the name of the country from previous question in the sentence.
                        ques_years_live = f"How many years you have lived in the country you currently live in: {country_live}"
                        years_live = st.text_input(ques_years_live, key = "years_live")

                        
                        submissions = []
                        for prompt, imgurl, openai_revised_prompt in zip(st.session_state["prompt_list"], st.session_state["imgurls"], st.session_state["openai_revised_prompts"]):
                            submissions.append({
                                "prompt": prompt,
                                "imgurl": imgurl,
                                "openai_revised_prompt": openai_revised_prompt,
                            })



                        def finalsubmit_response():
                            st.session_state["success_message"] = True
                            data = {
                            "prolific_id": st.session_state["prolific_id"],
                            "submissions": submissions,
                            "feedback": feedback_text,
                            "satisfaction": satisfaction,
                            "appropriateness": appropriateness,
                            "language_family": language_family,
                            "language_colleagues": language_colleagues,
                            "language_mothers": language_mothers,
                            "language_fathers": language_fathers,
                            "country_born": country_born,
                            "years_born": years_born,
                            "country_live": country_live,
                            "years_live": years_live
                            }

                            supabase_table_response = (
                                supabase.table("cc-t2i-test-attempts")
                                .upsert({"prolific_id": st.session_state["prolific_id"], "data": data})
                                .execute()
                            )

                        st.button('Submit Response', on_click=finalsubmit_response, disabled = st.session_state["success_message"])
                        st.warning("Please click the submit button to submit your response. Once you submit, you will not be able to change your response.")
                        # Add: Response submitted successfully message
                        if st.session_state["success_message"]:
                            st.success("Response submitted successfully! Thank you for your participation.")
                            st.stop()

else:
    st.info("Please enter and confirm your Prolific ID to proceed.")
