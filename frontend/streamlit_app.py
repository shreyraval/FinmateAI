import streamlit as st
import requests

st.title("FinMate – Upload Bank Statement")
uploaded = st.file_uploader("Choose PDF or CSV")
if uploaded:
    response = requests.post("http://localhost:8000/upload/", files={"file": uploaded})
    st.json(response.json())
