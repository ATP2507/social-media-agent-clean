
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import gspread
import json
import os
from datetime import datetime


gemini_api_key = st.secrets["GEMINI_API_KEY"]


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=gemini_api_key,
    temperature=0.9
)


sheets_enabled = False
sheet = None
try:
    if "GOOGLE_CREDENTIALS" in st.secrets:
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        gc = gspread.service_account_from_dict(creds_dict)
        sheet = gc.open("SocialMediaPlans").sheet1
        sheets_enabled = True
        st.success("Google Sheets connected! Auto-save ON")
    else:
        cred_path = os.path.join(os.path.dirname(__file__), "google-credentials.json")
        if os.path.exists(cred_path):
            gc = gspread.service_account(filename=cred_path)
            sheet = gc.open("SocialMediaPlans").sheet1
            sheets_enabled = True
            st.success("Google Sheets connected! Auto-save ON")
except Exception as e:
    st.warning(f"Sheets not connected: {e}")


prompt = PromptTemplate.from_template(
    """You are a top social media strategist.
Topic: {topic}

Generate exactly {num} complete post ideas with this exact format:

1. Idea: [short description of the content, 8-12 words]
   Caption: [viral caption with emojis, under 180 chars]
   Best time: [e.g. Wednesday 7 PM]
   Hashtags: #A #B #C #D

2. Idea: ...
   Caption: ...
   Best time: ...
   Hashtags: ...

Start directly with 1. No intro text."""
)

chain = prompt | llm | StrOutputParser()


st.set_page_config(page_title="Social Agent by Athira", page_icon="rocket", layout="centered")
st.title("Sochh -ial Agent 🚀")
st.markdown("### Save timee & boost engagement with AI-generated viral post ideas!")
st.caption("Made with love by **Athira TP**")

col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("Enter your topic", placeholder="e.g. fitness, coffee, pets, study motivation")
with col2:
    num = st.selectbox("Number of ideas", [1, 2, 3, 4, 5], index=2)

if st.button("Generate Viral Posts", type="primary", use_container_width=True):
    if not topic.strip():
        st.error("Please enter a topic!")
    else:
        with st.spinner("Creating your content plan..."):
            result = chain.invoke({"topic": topic, "num": num})

        st.success(f"Here are your {num} post ideas!")

        blocks = [b.strip() for b in result.split("\n\n") if b.strip()]
        for i, block in enumerate(blocks[:num], 1):
            lines = [l.strip() for l in block.split("\n")]
            idea_desc = next((l.split("Idea:")[1].strip() for l in lines if "Idea:" in l), "Great idea")
            caption = next((l.split("Caption:")[1].strip() for l in lines if "Caption:" in l), "Amazing caption!")
            best_time = next((l.split("Best time:")[1].strip() for l in lines if "Best time:" in l), "Any time")
            hashtags = next((l.split("Hashtags:")[1].strip() for l in lines if "Hashtags:" in l), "")

            with st.container():
                st.markdown(f"#### Idea {i}: {idea_desc}")
                st.markdown(f"**{caption}**")
                st.caption(f"Best time: {best_time}  •  {hashtags}")
                st.markdown("---")

        
        if sheets_enabled and sheet:
            try:
                clean_text = result.replace("\n", " | ")
                sheet.append_row([
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    topic,
                    clean_text[:10000]
                ])
                st.toast("Saved to Google Sheets!", icon="✅")
            except Exception as e:
                st.error(f"Save failed: {e}")

        
        st.download_button(
            label="Download Full Plan",
            data=result,
            file_name=f"{topic.replace(' ', '_')}_social_plan.txt",
            mime="text/plain"
        )

st.markdown("---")
st.caption("Happy Posting! 🚀 | Developed by Athira TP")