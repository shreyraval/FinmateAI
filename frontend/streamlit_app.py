import streamlit as st
import requests

st.title("FinmateAI – Upload Bank Statement")
uploaded = st.file_uploader("Choose PDF or CSV")
if uploaded:
    response = requests.post("https://finmateai.onrender.com/upload/", files={"file": uploaded})
    st.json(response.json())
