# DocuVerse RAG Application

A powerful document question-answering application built with Streamlit, LangChain, and Milvus vector database.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available for Docker

### Option 1: Using Startup Scripts (Recommended)

**For Windows:**
```bash
start.bat
```

**For Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Docker Commands

1. **Start the services:**
```bash
docker-compose up --build -d
```

2. **Wait for Milvus to be ready (about 30-60 seconds):**
```bash
# Check if Milvus is healthy
curl http://localhost:9091/healthz
```

3. **Access the application:**
- 🌐 **Streamlit App**: http://localhost:8501
- 🔍 **Milvus API**: http://localhost:9091

## 📁 Project Structure

```
DocuVerse Rebuild/
├── app.py                 # Main Streamlit application
├── text_processor.py      # Document processing and vector storage
├── document_processor.py  # File parsing and text extraction
├── model.py              # LLM model initialization
├── conversation.py       # Chat conversation handling
├── utils.py              # Utility functions
├── docker-compose.yml    # Docker services configuration
├── Dockerfile           # Streamlit app container
├── requirements.txt     # Python dependencies
├── start.sh            # Linux/Mac startup script
├── start.bat           # Windows startup script
└── README.md           # This file
```

## Prerequisites
Python 3.8+
Groq Cloud API key: https://console.groq.com/docs/quickstart

## 🔧 Configuration

### Environment Variables

The application uses these environment variables (set in docker-compose.yml):

- `MILVUS_HOST`: Milvus database host (default: localhost)
- `MILVUS_PORT`: Milvus database port (default: 19530)

### Supported File Types

- PDF files (.pdf)
- Word documents (.docx)
- Text files (.txt)
- Excel files (.xlsx)

### Streamlit Secrets & Groq API Setup

For local development or deployment on Streamlit Cloud, you need to configure your **Groq API key** securely.

#### Local Setup
1. Create a hidden folder `.streamlit` in the project root:
   ```bash
   mkdir .streamlit

2. Inside .streamlit, create a file called secrets.toml:
   ```bash 
   GROQ_API_KEY = "your-api-key-here"

## 🛠️ Troubleshooting

### Common Issues

1. **Milvus Connection Failed**
   ```
   ❌ Failed to connect to Milvus: Connection refused
   ```
   **Solution**: Wait for Milvus to fully start (30-60 seconds) or check Docker logs:
   ```bash
   docker-compose logs milvus-standalone
   ```

2. **Port Already in Use**
   ```
   Error: Port 19530 is already in use
   ```
   **Solution**: Stop existing containers and remove volumes:
   ```bash
   docker-compose down -v
   docker-compose up --build -d
   ```

3. **Memory Issues**
   ```
   Out of memory error
   ```
   **Solution**: Increase Docker memory limit to at least 4GB

4. **Collection Creation Failed**
   ```
   Failed to create vector store
   ```
   **Solution**: Check if Milvus is healthy and restart if needed:
   ```bash
   docker-compose restart milvus-standalone
   ```

### Debug Commands

**View all logs:**
```bash
docker-compose logs -f
```

**View specific service logs:**
```bash
docker-compose logs -f milvus-standalone
docker-compose logs -f streamlit-app
```

**Check service status:**
```bash
docker-compose ps
```

**Restart services:**
```bash
docker-compose restart
```

**Complete reset (removes all data):**
```bash
docker-compose down -v
docker-compose up --build -d
```

## 🔍 Health Checks

### Milvus Health
```bash
curl http://localhost:9091/healthz
```

### Streamlit Health
```bash
curl http://localhost:8501/_stcore/health
```

## 📊 Performance Tips

1. **Large Documents**: For documents >10MB, consider splitting them into smaller files
2. **Memory Usage**: Monitor Docker memory usage, especially during document processing
3. **Collection Management**: The app automatically cleans up old collections to prevent conflicts

## 🚀 Development

### Local Development (without Docker)

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start Milvus with Docker:
```bash
docker-compose up milvus-standalone -d
```

3. Run Streamlit app:
```bash
streamlit run app.py
```

### Adding New Features

1. **New File Types**: Add support in `document_processor.py`
2. **New Embedding Models**: Modify `text_processor.py`
3. **UI Changes**: Update `app.py` and related Streamlit components

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Docker logs for error messages
3. Ensure all prerequisites are met
4. Try a complete reset with `docker-compose down -v && docker-compose up --build -d` 