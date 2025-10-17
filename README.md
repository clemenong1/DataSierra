# DataSierra - AI-Powered Data Analysis Platform

DataSierra is a modern, clean, and well-architected web application that allows users to upload CSV and Excel files and get intelligent insights using OpenAI's GPT models. Built with a clean architecture and object-oriented design, the system provides advanced data analysis, visualization suggestions, and code generation capabilities.

## 🚀 Features

### Core Functionality
- **Multi-format Uploads: Supports CSV, XLSX, and XLS files
- **AI-Powered Insights: Analyze data using OpenAI GPT-4o and PandasAI
- **Natural Language Queries: Ask questions like “What’s the average sales by region?”
- **Multi-file & Cross-dataset Analysis: Compare and correlate multiple datasets
- **Smart Visualizations: Auto-generate charts and graphs from queries
- **Code Generation: Get ready-to-use pandas code snippets
- **Conversation Memory: Maintains context across multiple queries

### Advanced Analytics
- **Data Quality Assessment: Detect missing values, outliers, and anomalies
- **Statistical Insights: Summaries, correlations, and trends
- **Business Intelligence: Actionable recommendations and insights
- **Visualization Suggestions: Recommended charts with example code

### Tech Stack
- **Frontend: Streamlit (modern and responsive interface)
- **Backend: FastAPI (RESTful API with rate limiting & robust error handling)
- **Performance: Optimized data processing, caching, and scalable architecture

## 🚀 Usage

### Streamlit Web App

1. **Start the Streamlit app**:
   ```bash
   # Use Python 3.11 for full functionality
   python3.11 -m streamlit run app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Upload your files** and start asking questions!

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
