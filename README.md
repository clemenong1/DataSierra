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

- Python 3.11+
- OpenAI API key
- Required Python packages (see requirements.txt)
- PandasAI (optional but recommended for enhanced analysis)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd DataSierra
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key**:
   Create a `.streamlit/secrets.toml` file in your project root:
   ```bash
   mkdir -p .streamlit
   echo 'openai_api_key = "your_openai_api_key_here"' > .streamlit/secrets.toml
   ```

4. **Test the installation**:
   ```bash
   streamlit run app.py
   ```

## 🚀 Usage

### Option 1: Streamlit Web App (Recommended)

1. **Start the Streamlit app**:
   ```bash
   streamlit run app.py
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

## 📊 Sample Data

Sample datasets are available in the `public/assets/` directory:
- `demo_sales_data.csv` - Sales transaction data
- `demo_customer_data.csv` - Customer information
- `demo_product_data.csv` - Product catalog
- `demo_data.csv` - General sample data

## 🔧 Configuration

Key configuration options in `.streamlit/secrets.toml`:

```toml
# OpenAI Configuration
openai_api_key = "your_openai_api_key_here"
openai_model = "gpt-4o" 

# File Upload Limits (optional)
max_file_size_mb = 200
max_files_per_upload = 10

# Rate Limiting (optional)
openai_requests_per_minute = 60
openai_tokens_per_minute = 150000
```

### Model Selection

- **GPT-4o**: Best quality, higher cost, slower

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

## 🧪 Testing

### Run the Application
```bash
streamlit run app.py
```

### Test Individual Components
```python
from src.services.file.file_service import FileService
from src.services.ai.ai_service import AIService
from src.services.data.data_service import DataService

# Test file processing
file_service = FileService()
processed_files = file_service.process_uploaded_files(files)

# Test AI integration
ai_service = AIService()
response = ai_service.process_query(question, files)

# Test data analysis
data_service = DataService()
analysis = data_service.analyze_data(files)
```

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
- Store API keys in `.streamlit/secrets.toml` (automatically ignored by git)
- Never commit API keys to version control
- Use different keys for development and production

### Rate Limiting
- Built-in rate limiting prevents API quota exhaustion
- Automatic retry with exponential backoff
- Token usage tracking and optimization

### Error Handling
- Comprehensive error handling at all levels
- Graceful degradation when services are unavailable
- Detailed error messages for debugging

## 🚀 Deployment

### Local Development
```bash
# Streamlit app
streamlit run app.py
```

### Production Deployment

1. **Set up production secrets** in `.streamlit/secrets.toml`
2. **Use a production WSGI server** (e.g., Gunicorn)
3. **Configure reverse proxy** (e.g., Nginx)
4. **Set up monitoring and logging**
5. **Configure SSL/TLS certificates**

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**Q: OpenAI API key not working**
A: Check that your API key is valid and has sufficient credits

**Q: Files not uploading**
A: Ensure files are CSV, XLSX, or XLS format and under 200MB

**Q: Rate limit errors**
A: The system includes automatic rate limiting. Wait a moment and try again

**Q: Memory issues with large files**
A: Consider splitting large files or using the API for programmatic access

### Getting Help

- Run the application: `streamlit run app.py`
- Check the logs for detailed error messages
- Review the clean architecture in the `src/` directory

## 🔮 Future Enhancements

- [ ] Database integration for persistent storage
- [ ] Real-time collaboration features
- [ ] Advanced visualization generation
- [ ] Custom model fine-tuning
- [ ] Multi-language support
- [ ] Cloud deployment templates
- [ ] Advanced analytics dashboard
- [ ] Integration with popular BI tools

---

**DataSierra** - Transform your data into actionable insights with the power of AI! 🚀📊