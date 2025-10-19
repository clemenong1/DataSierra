# DataSierra - AI-Powered Data Analysis Platform

DataSierra is a modern, clean, and well-architected web application that allows users to upload CSV and Excel files and get intelligent insights using OpenAI's GPT models. Built with a clean architecture and object-oriented design, the system provides advanced data analysis, visualization suggestions, and code generation capabilities.

## 🚀 Features

### Core Functionality
- **Multi-format Support**: Upload CSV, XLSX, and XLS files
- **AI-Powered Analysis**: Get intelligent insights using OpenAI GPT-4o
- **PandasAI Integration**: Natural language data queries with direct pandas operations
- **Multi-file Processing**: Analyze multiple datasets simultaneously
- **Cross-dataset Analysis**: Compare and analyze relationships between different files
- **Conversation Memory**: Maintain context across multiple queries

### PandasAI Enhanced Features
- **Natural Language Queries**: Ask questions like "What is the average sales by region?"
- **Direct Data Analysis**: Get immediate answers without writing code
- **Smart Visualizations**: Generate charts and graphs from natural language
- **Data Quality Assessment**: Automatic detection of missing values and outliers
- **Code Generation**: Get pandas code snippets for further analysis

### Advanced Features
- **Data Quality Assessment**: Automatic detection of missing values, outliers, and data quality issues
- **Statistical Insights**: Comprehensive statistical analysis with summaries and correlations
- **Business Intelligence**: Actionable business insights and recommendations
- **Code Generation**: Python/pandas code snippets for further analysis
- **Visualization Suggestions**: Recommended charts and plots with code
- **Rate Limiting**: Intelligent API rate limiting and error handling
- **Session Management**: Persistent conversation history and session tracking

### Technical Features
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Streamlit Frontend**: Modern, responsive web interface
- **Error Handling**: Robust error handling and recovery
- **Performance Optimization**: Efficient data processing and caching
- **Scalable Architecture**: Modular design for easy extension

## 📋 Requirements

- **Python 3.11+** (Recommended: Python 3.11.13)
  - LIDA visualization requires Python 3.9+
  - PandasAI works best with Python 3.11+
  - All features tested with Python 3.11
- OpenAI API key
- Firebase project with Firestore enabled
- Required Python packages (see requirements.txt)
- PandasAI (optional but recommended for enhanced analysis)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd DataSierra
   ```

2. **Install dependencies** (use Python 3.11):
   ```bash
   # Make sure you're using Python 3.9+
   python3.11 --version
   
   # Install dependencies with Python 3.9
   python3.11 -m pip install -r requirements.txt
   ```

   Alternatively, you can create a python venv
   ```bash
   python3.11 -m venv .venv
   ```

3. **Set up environment variables**:
   Create a `.env` file in your project root and add your Firebase keys and OpenAI key.
   ```bash
   OPENAI_API_KEY=
   
   # Firebase Configuration (from Service Account JSON)
   FIREBASE_PROJECT_ID=
   FIREBASE_PRIVATE_KEY_ID=
   FIREBASE_PRIVATE_KEY=
   FIREBASE_CLIENT_EMAIL=
   FIREBASE_CLIENT_ID=
   FIREBASE_AUTH_URI=
   FIREBASE_TOKEN_URI=
   ```
   
4. **Set up Firebase**:
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Enable Firestore database
   - Go to Project Settings > Service Accounts
   - Generate a new private key and download the JSON file
   - Extract the values from the JSON file and add them to your `.env` file
   - Alternatively, place the downloaded `serviceAccountKey.json` file in your project root

5. **Set up OpenAI**:
   - Create a new Project at [OpenAI][https://platform.openai.com/]
   - Generate a new API Key
   - Place the API key into the `.env` file

6. **Test the installation**:
   ```bash
   # Run with Python 3.11 to ensure all features work
   python3.11 -m streamlit run app.py
   ```

## 🏗️ Architecture

### Clean Architecture Structure

```
DataSierra/
├── src/                          # Clean source code
│   ├── models/                   # Data models & schemas
│   │   ├── file_models.py       # File-related data models
│   │   ├── query_models.py      # Query request/response models
│   │   └── session_models.py    # Session management models
│   ├── services/                 # Business logic services
│   │   ├── ai/                  # AI service implementations
│   │   ├── data/                # Data processing services
│   │   ├── file/                # File handling services
│   │   ├── ai_service.py        # Main AI service
│   │   ├── data_service.py      # Data analysis service
│   │   ├── file_service.py      # File processing service
│   │   └── session_service.py   # Session management service
│   ├── ui/                       # User interface components
│   │   ├── components/          # Reusable UI components
│   │   │   ├── data_preview.py  # Data preview component
│   │   │   ├── file_upload.py   # File upload component
│   │   │   ├── history.py       # Query history component
│   │   │   └── query_interface.py # Query interface component
│   │   └── pages/               # Page components
│   │       └── main_page.py     # Main application page
│   ├── utils/                    # Utilities & styling
│   │   └── styling.py           # Custom styling utilities
│   └── config.py                # Configuration management
├── public/                       # Static assets
│   └── assets/                  # Sample data files
├── app.py                       # Main application entry point
└── requirements.txt             # Dependencies
```

## 🔒 Security & Best Practices

### API Key Security
- Store API keys in `.env` file (automatically ignored by git)
- Never commit API keys to version control
- Use different keys for development and production
- Keep your Firebase service account keys secure

### Rate Limiting
- Built-in rate limiting prevents API quota exhaustion
- Automatic retry with exponential backoff
- Token usage tracking and optimization

**DataSierra** - Transform your data into actionable insights with the power of AI! 🚀📊
