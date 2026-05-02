import re
import tempfile
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document


def get_files_text(uploaded_files):
    all_docs = []
    for file in uploaded_files:
        file.seek(0)
        if file.type == "application/pdf":
            text = get_pdf_text(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = get_docx_text(file)
        elif file.type == "text/plain":
            content = file.read()
            text = content.decode("utf-8", errors="ignore")
        elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            text = get_xlsx_text(file)
        else:
            text = "[Unsupported file type]"

        all_docs.append(Document(page_content=text))
        file.seek(0)
    return all_docs


def get_pdf_text(file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        return "\n".join([p.page_content for p in pages])
    except Exception as e:
        return f"[Error reading PDF: {e}]"


def get_docx_text(file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        loader = UnstructuredWordDocumentLoader(tmp_path)
        docs = loader.load()
        return "\n".join([doc.page_content for doc in docs])
    except Exception as e:
        return f"[Error reading DOCX: {e}]"


def get_xlsx_text(file):
    try:
        excel_file = pd.read_excel(file, sheet_name=None)
        text = ""
        for sheet_name, df in excel_file.items():
            text += f"\nSheet: {sheet_name}\n"
            text += df.to_string(index=False, header=True)
            text += "\n"
        return text
    except Exception as e:
        return f"[Error reading Excel file: {e}]"


def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()
