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

# Configure the page
st.set_page_config(
    page_title="FinMateAI",
    page_icon="💰",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("FinMateAI - Upload Bank Statement")
st.markdown("Upload your bank statement (PDF, CSV, or XLSX) to analyze your spending patterns.")

# File uploader
uploaded = st.file_uploader("Choose a file", type=['pdf', 'csv', 'xlsx'])

if uploaded:
    with st.spinner("Processing your statement..."):
        try:
            # Use environment variable for API URL
            API_URL = "https://finmateai.onrender.com/upload/"
            
            # Prepare the file for upload
            files = {"file": (uploaded.name, uploaded.getvalue())}
            
            # Make the API request
            response = requests.post(API_URL, files=files)

            if response.ok:
                data = response.json()
                
                # Display success message
                st.success("✅ File processed successfully!")
                
                # Create DataFrame from transactions
                all_transactions = []
                for category, transactions in data['categorized']['transactions'].items():
                    for transaction in transactions:
                        transaction['category'] = category
                        all_transactions.append(transaction)
                
                df = pd.DataFrame(all_transactions)
                
                # Create two columns for layout
                col1, col2 = st.columns(2)
                
                with col1:
                    # Display transactions
                    st.subheader("Transaction Details")
                    st.dataframe(df, use_container_width=True)
                
                with col2:
                    # Display summary statistics
                    st.subheader("Spending Summary by Category")
                    summary_df = pd.DataFrame(data['categorized']['summary']).T
                    st.dataframe(summary_df, use_container_width=True)
                
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
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Fallback to Streamlit's built-in chart
                    spending_by_category = df[df['amount'] < 0].groupby('category')['amount'].sum().abs()
                    st.bar_chart(spending_by_category)
                
                # Display total spending
                total_spending = abs(df[df['amount'] < 0]['amount'].sum())
                st.metric("Total Spending", f"${total_spending:,.2f}")
                
            else:
                st.error(f"❌ Error: {response.text}")
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("Please try again or contact support if the issue persists.") 