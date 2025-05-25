import streamlit as st
import requests
import pandas as pd

st.title("FinMateAI – Upload Bank Statement")

uploaded = st.file_uploader("Choose a PDF or CSV file")

if uploaded:
    with st.spinner("Analyzing your statement..."):
        response = requests.post(
            "https://finmateai.onrender.com/analyze/",
            files={"file": (uploaded.name, uploaded.getvalue())}
        )

    try:
        response_json = response.json()

        if "transactions" in response_json:
            df = pd.DataFrame(response_json["transactions"])

            st.success("✅ Statement processed successfully.")
            st.subheader("📄 Transaction Breakdown")
            st.dataframe(df)

            # Safety check for expected columns
            if "Category" not in df.columns or "Amount" not in df.columns:
                st.error("❗ Missing expected 'Category' or 'Amount' column.")
                st.stop()

            st.subheader("📊 Spending by Category")
            st.bar_chart(df.groupby("Category")["Amount"].sum().abs())

            st.subheader("💡 Personalized Budget Advice")
            st.markdown(response_json["advice"])

        else:
            st.error(f"⚠️ Error: {response_json.get('error', 'Unknown issue')}")

    except Exception as e:
        st.error(f"❌ Something went wrong: {str(e)}")

