import os
# from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import json


def process_pdfs(data_folder, fileName=None):
    """Process PDFs in the given folder. If fileName is provided, process only that file."""
    pdf_text_data = {}

    if fileName:  # Process only the given file
        file_path = os.path.join(data_folder, fileName)
        if fileName.endswith(".pdf") and os.path.exists(file_path):
            loader = PyPDFLoader(file_path)
            pages = loader.load()

            pages_text = [page.page_content for page in pages]
            splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=100)
            split_pages_text = [splitter.split_text(page) for page in pages_text]

            pdf_text_data[fileName] = split_pages_text
    else:  # Process all PDFs in the folder
        for filename in os.listdir(data_folder):
            if filename.endswith(".pdf"):
                file_path = os.path.join(data_folder, filename)

                loader = PyPDFLoader(file_path)
                pages = loader.load()

                pages_text = [page.page_content for page in pages]
                splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=100)
                split_pages_text = [splitter.split_text(page) for page in pages_text]

                pdf_text_data[filename] = split_pages_text

    return pdf_text_data

if __name__ == "__main__":
    data_folder = "INFO/data"
    result = process_pdfs(data_folder)
    
    # Save output to a JSON file
    with open("INFO/output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    print("Processing complete. Extracted text saved to output.json.")
