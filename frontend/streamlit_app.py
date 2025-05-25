import streamlit as st
import requests
import pandas as pd

# Try to import plotly, but provide fallback if not available
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly is not installed. Some visualizations will be simplified.")

st.title("FinMateAI - Upload Bank Statement")

uploaded = st.file_uploader("Choose PDF or CSV")

if uploaded:
    with st.spinner("Processing..."):
        try:
            files = {"file": uploaded.getvalue()}
            url = "https://finmateai.onrender.com/upload/"
            response = requests.post(url, files={"file": (uploaded.name, uploaded.getvalue())})

            if response.ok:
                data = response.json()
                
                # Display success message
                st.success("File processed successfully!")
                
                # Create DataFrame from transactions
                all_transactions = []
                for category, transactions in data['categorized']['transactions'].items():
                    for transaction in transactions:
                        transaction['category'] = category
                        all_transactions.append(transaction)
                
                df = pd.DataFrame(all_transactions)
                
                # Display transactions
                st.subheader("Transaction Details")
                st.dataframe(df)
                
                # Display summary statistics
                st.subheader("Spending Summary by Category")
                summary_df = pd.DataFrame(data['categorized']['summary']).T
                st.dataframe(summary_df)
                
                # Create spending visualization
                st.subheader("Spending Distribution")
                if PLOTLY_AVAILABLE:
                    # Use Plotly for interactive visualization
                    fig = px.pie(
                        df[df['amount'] < 0],  # Only show expenses
                        values='amount',
                        names='category',
                        title='Spending by Category'
                    )
                    st.plotly_chart(fig)
                else:
                    # Fallback to Streamlit's built-in chart
                    spending_by_category = df[df['amount'] < 0].groupby('category')['amount'].sum().abs()
                    st.bar_chart(spending_by_category)
                
                # Display total spending
                total_spending = abs(df[df['amount'] < 0]['amount'].sum())
                st.metric("Total Spending", f"${total_spending:,.2f}")
                
            else:
                st.error(f"Error: {response.text}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
