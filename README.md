# DocuVerse  
DocuVerse is a document analysis tool that allows users to upload PDF/DOCX files, generate summaries in different formats, and ask context-based questions about the document. Built with modern NLP and AI technologies, it simplifies document comprehension and interaction.  

App Link: https://docuverse-kvrxhzujikwqqqkokjqqjm.streamlit.app/

If App in sleep mode please wake it up using the button you see on the web-page.
---

## ✨ Features  
- **Document Upload**: Supports PDF and DOCX files.  
- **AI-Powered Summarization**:  
  - Toggle between **paragraph summaries** and **bullet-point summaries**.  
  - Extracts key information efficiently.  
- **Contextual Q&A**: Ask questions related to the uploaded document and get precise answers.  
- **User-Friendly Interface**: Clean and intuitive UI for seamless interaction.  

---

## 🛠️ Tech Stack  
- **Backend**: Python, Flask, LangChain,  HuggingFace, GroqCloud    
- **Frontend**: Streamlit 
- **NLP/ML**: Llama3-8b-8192, Transformers, PyPDF2, python-docx, 
- **Utilities**: dotenv, FAISS (vector storage)  

---

## 🚀 Quick Start  

### Prerequisites  
- Python 3.8+  
- Groq Cloud API key ([get it here](https://console.groq.com/docs/quickstart)  

### Installation  
1. **Clone the repository**:  
   ```bash  
   git clone https://github.com/Kratik-Rathi/DocuVerse.git  
   cd DocuVerse  
   ```  

2. **Set up a virtual environment**:  
   ```bash  
   python -m venv venv  
   source venv/bin/activate  # Linux/Mac  
   venv\Scripts\activate    # Windows  
   ```  

3. **Install dependencies**:  
   ```bash  
   pip install -r requirements.txt  
   ```  

4. **Configure environment variables**:  
   Create a `.env` file in the root directory and add:  
   ```env  
   GROQ_API_KEY=="your-api-key-here"  
   ```  

### Usage  
1. **Run the streamlit app**:  
   ```bash  
   streamlit run app,py  
   ```  

2. **Upload a document**:  
   - Click "Upload" and select a PDF/DOCX file.  

3. **Generate a summary**:  
   - Toggle between paragraph/bullet-point formats.  

4. **Ask questions**:  
   - Type questions in the chat-style interface for instant answers.  

---

## 🔍 How It Works  
1. **Document Processing**:  
   - Text extraction from PDF/DOCX using `PyPDF2` and `python-docx`.  
   - Chunking text for efficient processing.  

2. **Summarization**:  
   - Leverages Llama3-8b-8192 model on GroqCloud to generate summaries in the desired format.  

3. **Q&A System**:  
   - Uses LangChain and FAISS vector storage for semantic search.  

---

## 📄 License  
Distributed under the MIT License. See `LICENSE` for details.  


---

**Note**:  
Replace `your-api-key-here` in the `.env` file with your actual Groq API key.  
