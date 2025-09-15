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
   # Make sure you're using Python 3.11
   python3.11 --version
   
   # Install dependencies with Python 3.11
   python3.11 -m pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in your project root:
   ```bash
   touch .env
   ```
   
   Add the following variables to your `.env` file:
   ```bash
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Firebase Configuration
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_PRIVATE_KEY_ID=your_firebase_private_key_id
   FIREBASE_PRIVATE_KEY="your_firebase_private_key"
   FIREBASE_CLIENT_EMAIL=your_firebase_client_email
   FIREBASE_CLIENT_ID=your_firebase_client_id
   FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
   FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
   ```

4. **Set up Firebase**:
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Enable Firestore database
   - Go to Project Settings > Service Accounts
   - Generate a new private key and download the JSON file
   - Extract the values from the JSON file and add them to your `.env` file
   - Alternatively, place the downloaded `serviceAccountKey.json` file in your project root

5. **Verify your environment** (optional but recommended):
   ```bash
   # Check Python version and dependencies
   python3.11 check_environment.py
   ```

6. **Test the installation**:
   ```bash
   # Run with Python 3.11 to ensure all features work
   python3.11 -m streamlit run app.py
   ```

## 🚀 Usage

### Option 1: Streamlit Web App (Recommended)

1. **Start the Streamlit app**:
   ```bash
   # Use Python 3.11 for full functionality
   python3.11 -m streamlit run app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Upload your files** and start asking questions!

### Option 2: Programmatic Usage

```python
from src.services.ai.ai_service import AIService
from src.services.file.file_service import FileService

# Initialize services
file_service = FileService()
ai_service = AIService()

# Process your files and ask questions
files = file_service.process_uploaded_files(uploaded_files)
response = ai_service.process_query(
    query="What are the main trends in this data?",
    files=files,
    session_id="my_session"
)

print(response['answer'])
```

## 🔧 Configuration

### Environment Variables (.env file)

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Firebase Configuration
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY_ID=your_firebase_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour_firebase_private_key\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your_firebase_client_email
FIREBASE_CLIENT_ID=your_firebase_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
```

### Firebase Setup Steps

1. **Create Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Create a project"
   - Follow the setup wizard

2. **Enable Firestore**:
   - In your Firebase project, go to "Firestore Database"
   - Click "Create database"
   - Choose "Start in test mode" for development

3. **Generate Service Account Key**:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download the JSON file
   - Extract the values and add them to your `.env` file

4. **Alternative: Use Service Account File**:
   - Place the downloaded `serviceAccountKey.json` in your project root
   - The app will automatically detect and use this file

### Model Selection

- **GPT-4o**: Best quality, higher cost, slower

## 🔧 Troubleshooting

### "LIDA not available" Error

If you see "LIDA not available, using fallback visualization service":

1. **Run the environment checker**:
   ```bash
   python3.11 check_environment.py
   ```

2. **Use Python 3.11**:
   ```bash
   python3.11 -m streamlit run app.py
   ```

3. **Reinstall dependencies with Python 3.11**:
   ```bash
   python3.11 -m pip install -r requirements.txt
   ```

### Firebase Authentication Issues

If you see "Auth not configured":

1. **Add Firebase service account credentials** to your `.env` file
2. **Or place `serviceAccountKey.json`** in your project root
3. **Restart the app** after adding credentials

### General Issues

- **Always use Python 3.11** for this project
- **Check your `.env` file** has all required variables
- **Restart the app** after making configuration changes

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

### Key Components

- **Models**: Typed data structures for better code organization
- **Services**: Business logic separated from UI components
- **UI Components**: Reusable, focused components
- **Pages**: Main page orchestrator
- **Utils**: Styling and utility functions
- **Config**: Centralized configuration management

### System Components

1. **Frontend (Streamlit)**: Modern, responsive user interface
2. **Service Layer**: Clean separation of business logic
3. **Model Layer**: Typed data structures and validation
4. **AI Integration**: OpenAI and PandasAI integration
5. **Session Management**: Conversation memory and context

### Data Flow

```
User Upload → File Service → Data Service → AI Service → Response Processing → UI Display
```

### Key Services

- **FileService**: Handles file processing and validation
- **DataService**: Data analysis and visualization
- **AIService**: OpenAI and PandasAI integration
- **SessionService**: Session and conversation management

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
