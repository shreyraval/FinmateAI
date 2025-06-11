# FinMateAI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FinMateAI is an intelligent financial management assistant that helps users analyze their bank statements and gain valuable insights into their spending habits. By leveraging AI and machine learning, FinMateAI provides personalized budget advice and spending analytics to help users make better financial decisions.

## 🌟 Features

- **Bank Statement Analysis**: Upload and analyze PDF or CSV bank statements
- **Smart Transaction Categorization**: Automatically categorizes transactions into meaningful categories
- **Spending Analytics**: Visual breakdown of spending patterns by category
- **Personalized Budget Advice**: AI-powered recommendations for better financial management
- **Interactive Dashboard**: User-friendly interface with real-time data visualization
- **Multi-Format Support**: Handles PDF, CSV, and XLSX file formats

## 🛠️ Tech Stack

### Frontend
- Streamlit (Web Interface)
- Plotly (Data Visualization)
- Pandas (Data Processing)

### Backend
- FastAPI (REST API)
- LangChain (AI/ML Integration)
- OpenAI (Natural Language Processing)
- PDF Plumber (PDF Processing)

### Infrastructure
- Python 3.8+
- Render (Deployment)

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/FinMateAI.git
cd FinMateAI
```

2. Install frontend dependencies:
```bash
cd frontend
pip install -r requirements.txt
```

3. Install backend dependencies:
```bash
cd ../backend
pip install -r requirements.txt
```

### Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. Start the frontend application:
```bash
cd frontend
streamlit run streamlit_app.py
```

3. Open your browser and navigate to `http://localhost:8501`

## 📝 Usage

1. Upload your bank statement (PDF or CSV format)
2. Wait for the analysis to complete
3. View your transaction breakdown and spending patterns
4. Read personalized budget advice
5. Use the insights to make informed financial decisions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Shrey Raval - Initial work

## 🙏 Acknowledgments

- OpenAI for providing the AI capabilities
- The open-source community for the amazing tools and libraries
