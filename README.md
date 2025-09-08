# AI Data Analysis Assistant

A beautiful, intuitive Streamlit frontend for AI-powered data analysis with comprehensive file upload, data preview, and intelligent query capabilities.

## Features

### 📁 File Upload Section
- **Multi-format support**: Excel (.xlsx, .xls) and CSV files
- **Drag-and-drop interface**: Modern file drop zone with visual feedback
- **File validation**: Size limits and format checking
- **Progress indicators**: Real-time upload status and success/error messages
- **File metadata**: Display file size, type, and basic information

### 👁️ Data Preview Section
- **File/sheet selector**: Choose which uploaded file to preview
- **Configurable rows**: Specify number of rows to display (1-100)
- **Responsive tables**: Clean, formatted data display
- **Dataset information**: Shape, column names, and data types
- **Download functionality**: Export preview data as CSV

### 🤖 AI Query Interface
- **Natural language queries**: Ask questions about your data in plain English
- **Example prompts**: Quick-select buttons with common questions
- **File context**: Select which dataset to query against
- **Loading states**: Spinner animations and progress indicators
- **Formatted responses**: Clean display of AI insights

### 📚 Query History Panel
- **Persistent history**: All queries saved with timestamps
- **Search functionality**: Filter history by query or response content
- **Rerun capability**: Click to re-execute previous queries
- **Recent queries**: Display last 10 queries for quick access
- **Clear history**: Option to reset query history

### 💬 Feedback System
- **Thumbs up/down**: Quick feedback on AI responses
- **Text comments**: Optional detailed feedback
- **Feedback tracking**: Store and display user feedback
- **Confirmation messages**: Visual feedback on submission

## Design Features

### 🎨 Visual Design
- **Modern theme**: Professional blue and white color scheme
- **Custom CSS**: Enhanced styling with gradients and shadows
- **Responsive layout**: Works on different screen sizes
- **Interactive elements**: Hover effects and smooth transitions
- **Icons and emojis**: Visual cues for better UX

### 📱 Layout Structure
- **Multi-column layout**: Responsive design using Streamlit columns
- **Expandable sections**: Organized content with collapsible panels
- **Sidebar navigation**: Easy access to history and settings
- **Tab organization**: Clean separation of different functionalities
- **Header section**: Prominent app title and description

### 🔧 User Experience
- **Tooltips and help**: Contextual information throughout the app
- **Progress indicators**: Visual feedback for long operations
- **Error handling**: Clear error messages and validation feedback
- **Confirmation dialogs**: Safe destructive actions
- **Loading states**: Spinners and progress bars for better UX

## Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   streamlit run app.py
   ```
4. **Open your browser** to `http://localhost:8501`

## Usage

### Getting Started
1. **Upload Files**: Drag and drop or select Excel/CSV files
2. **Preview Data**: Select a file and specify rows to display
3. **Ask Questions**: Use the AI query interface to get insights
4. **Review History**: Check previous queries in the sidebar
5. **Provide Feedback**: Rate AI responses to improve the system

### Example Questions
- "What are the main trends in this data?"
- "Show me correlations between variables"
- "Summarize the key insights"
- "What patterns do you see?"
- "Are there any outliers?"
- "Describe the data distribution"

### File Requirements
- **Supported formats**: .xlsx, .xls, .csv
- **Maximum file size**: 200MB per file
- **Multiple files**: Upload and analyze multiple datasets
- **Data validation**: Automatic format checking and error handling

## Technical Implementation

### Backend Integration
The app includes placeholder functions for backend integration:
- `upload_and_process_files()`: File processing and validation
- `get_data_preview()`: Data preview functionality
- `query_ai()`: AI query processing
- `save_query_history()`: History management
- `submit_feedback()`: Feedback collection

### State Management
- **Session state**: Persistent data across interactions
- **File storage**: Uploaded files maintained in memory
- **Query history**: All queries saved with metadata
- **User preferences**: Settings and display options

### Security Features
- **File size limits**: Clear display of upload restrictions
- **Format validation**: Only supported file types accepted
- **Session management**: Automatic cleanup and timeout handling
- **Privacy notices**: Clear data handling information

## Customization

### Styling
- **CSS variables**: Easy color scheme modification
- **Component styling**: Customizable button and card designs
- **Layout options**: Flexible column and spacing configurations
- **Theme integration**: Compatible with Streamlit themes

### Functionality
- **Backend integration**: Replace placeholder functions with real APIs
- **AI model**: Connect to your preferred AI service
- **Data processing**: Customize file handling and validation
- **Export options**: Add additional download formats

## Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **openpyxl**: Excel file reading
- **xlrd**: Legacy Excel support
- **streamlit-extras**: Enhanced UI components
- **plotly**: Interactive visualizations
- **numpy**: Numerical computing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions, issues, or feature requests, please open an issue in the repository or contact the development team.

---

**Built with ❤️ using Streamlit**
