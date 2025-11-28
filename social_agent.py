import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import gspread
from google.oauth2.service_account import Credentials
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
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    if "GOOGLE_CREDENTIALS" in st.secrets:
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        sheet = gc.open("SocialMediaPlans").sheet1
        sheets_enabled = True
        st.success("Google Sheets connected! Auto-save ON")
except Exception as e:
    st.warning(f"Sheets error: {e}")

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

st.set_page_config(page_title="Sochh-ial Agent by Athira", page_icon="rocket", layout="centered")

st.title("Sochh-ial Agent :)")
st.markdown("### Save time & boost engagement with AI-generated viral post ideas :)")

st.info("""
**Project Overview :**  
This is an AI-powered Social Media Content Generator built using Google Gemini 2.5 Flash, LangChain, and Streamlit.  
It instantly creates YouTube/Instagram/TikTok ideas with captions, best posting times, and hashtags which can be downloaded.(Data is also stored in Google Sheets for backend)
Perfect for creators, brands, and marketers.
""")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("**Enter your Niche/Topic**")
    topic = st.text_input("Enter your Niche/Topic", placeholder="e.g. fitness, coffee, pets, study motivation", label_visibility="collapsed")
with col2:
    st.markdown("**Number of ideas**")
    num = st.selectbox("Number of ideas", [1, 2, 3, 4, 5], index=2, label_visibility="collapsed")

if st.button("Generate Viral Posts", type="primary", use_container_width=True):
    if not topic.strip():
        st.error("Please enter a topic!")
    else:
        with st.spinner("Creating your viral content plan..."):
            result = chain.invoke({"topic": topic, "num": num})

        st.balloons()
        st.success(f"Here are your {num} post ideas!")

        blocks = [b.strip() for b in result.split("\n\n") if b.strip()]
        for i, block in enumerate(blocks[:num], 1):
            lines = [l.strip() for l in block.split("\n")]
            idea_desc = next((l.split("Idea:")[1].strip() for l in lines if "Idea:" in l), "Great idea")
            caption = next((l.split("Caption:")[1].strip() for l in lines if "Caption:" in l), "Amazing caption!")
            best_time = next((l.split("Best time:")[1].strip() for l in lines if "Best time:" in l), "Any time")
            hashtags = next((l.split("Hashtags:")[1].strip() for l in lines if "Hashtags:" in l), "")

            with st.container(border=True):
                st.markdown(f"**Idea {i}:** {idea_desc}")
                st.markdown(f"**{caption}**")
                st.caption(f"Best time: {best_time}  •  {hashtags}")

        if sheets_enabled and sheet:
            try:
                clean_text = result.replace("\n", " | ")
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), topic, clean_text[:10000]])
                st.toast("Saved to Google Sheets!", icon="✅")
            except Exception as e:
                st.error(f"Save failed: {e}")
        else:
            st.info("Auto-save disabled — add GOOGLE_CREDENTIALS in Secrets to enable")

        st.download_button("Download Full Plan", data=result, file_name=f"{topic.replace(' ', '_')}_social_plan.txt", mime="text/plain", use_container_width=True)

st.markdown("---")
st.caption("Athira TP • Built with Google Gemini + Streamlit")