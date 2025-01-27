import docx
from PyPDF2 import PdfReader
import os


def get_files_text(uploaded_files):
    text = ""
    for uploaded_file in uploaded_files:
        split_tup = os.path.splitext(uploaded_file.name)
        file_extension = split_tup[1]
        if file_extension == ".pdf":
            text += get_pdf_text(uploaded_file)
        elif file_extension == ".docx":
            text += get_docx_text(uploaded_file)
    return text


def get_pdf_text(pdf):
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def get_docx_text(file):
    doc = docx.Document(file)
    alltext = []
    for docpara in doc.paragraphs:
        alltext.append(docpara.text)
    text = ' '.join(alltext)
    return text
