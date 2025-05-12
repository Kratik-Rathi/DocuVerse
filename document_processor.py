import docx
from PyPDF2 import PdfReader
import os
import pandas as pd


def get_files_text(uploaded_files):
    text = ""
    for uploaded_file in uploaded_files:
        split_tup = os.path.splitext(uploaded_file.name)
        file_extension = split_tup[1].lower()  # To handle .TXT or .Docx etc.

        if file_extension == ".pdf":
            text += get_pdf_text(uploaded_file)
        elif file_extension == ".docx":
            text += get_docx_text(uploaded_file)
        elif file_extension == ".txt":
            text += get_txt_text(uploaded_file)
        elif file_extension == ".xlsx":
            text += get_xlsx_text(uploaded_file)

    return text


def get_pdf_text(pdf):
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""  # In case extract_text() returns None
    return text


def get_docx_text(file):
    doc = docx.Document(file)
    alltext = []
    for docpara in doc.paragraphs:
        alltext.append(docpara.text)
    text = ' '.join(alltext)
    return text


def get_txt_text(file):
    content = file.read()
    if isinstance(content, bytes):
        return content.decode("utf-8", errors="ignore")
    return content


def get_xlsx_text(file):
    text = ""
    try:
        excel_file = pd.read_excel(file, sheet_name=None)  # Read all sheets
        for sheet_name, df in excel_file.items():
            text += f"\nSheet: {sheet_name}\n"
            text += df.to_string(index=False, header=True)
            text += "\n\n"
    except Exception as e:
        text += f"\n[Error reading Excel file: {e}]\n"
    return text

