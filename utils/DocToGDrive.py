import json
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# ----------------------------------------
# CONFIGURATION
# ----------------------------------------
# Path to the input JSON file containing transactions grouped by filename
INPUT_JSON_PATH = "INFO/processed_output.json"

# Chunking parameters: number of transactions per chunk and overlap size
CHUNK_SIZE = 10  # Adjust this as needed
OVERLAP = 1      # Adjust this as needed

# Output directory to store individual chunk text files
OUTPUT_DIR = "output_chunks"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Google Drive configuration
# You can set this as an environment variable or directly assign the value here.
GDRIVE_FOLDER_ID = os.environ.get("GDRIVEFOLDERID", "YOUR_GOOGLE_DRIVE_FOLDER_ID")
CREDENTIALS_FILE = "credentials.json"

def chunk_transactions_by_count(table, chunk_size, overlap):
    """
    Splits a list of transactions into chunks based on count.
    Each chunk is a dictionary with a sequential index and a text representation.
    """
    chunks = []
    num_trans = len(table)
    chunk_index = 1
    start = 0
    while start < num_trans:
        end = min(start + chunk_size, num_trans)
        chunk_transactions = table[start:end]
        chunk_text = f"Transaction Chunk {chunk_index}\n" + "-"*40 + "\n"
        for trans in chunk_transactions:
            trans_line = (
                f"Date: {trans.get('Date')}, "
                f"Particulars: {trans.get('Particulars')}, "
                f"Deposit: {trans.get('Deposit')}, "
                f"Withdrawal: {trans.get('Withdrawal')}, "
                f"Balance: {trans.get('Balance')}\n"
            )
            chunk_text += trans_line
        chunks.append({
            "chunk_index": chunk_index,
            "chunk_text": chunk_text
        })
        if end == num_trans:
            break
        start += chunk_size - overlap
        chunk_index += 1
    return chunks

def save_chunks_as_files(chunks, output_dir="temp_chunks"):
    """
    Saves each chunk as an individual text file in output_dir.
    Returns a list of file paths.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_paths = []
    for chunk in chunks:
        file_name = f"transactions_chunk_{chunk['chunk_index']}.txt"
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(chunk["chunk_text"])
        file_paths.append(file_path)
    return file_paths

# --- Google Drive Upload Function ---
def upload_file_to_gdrive(file_path, folder_id, credentials_file):
    """
    Uploads the specified file to Google Drive in the given folder.
    Uses a service account for authentication.
    """

    credentials = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)
    
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype="text/plain")
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    
    print(f"Uploaded {os.path.basename(file_path)} (File ID: {uploaded_file.get('id')})")

def grivePipe(table):
    """
    Given a transaction table (list of transactions), this function:
      1. Chunks the transactions by count.
      2. Saves each chunk as an individual text file.
      3. Uploads each file to Google Drive.
    """
    chunks = chunk_transactions_by_count(table, CHUNK_SIZE, OVERLAP)
    print(f"Created {len(chunks)} chunks from the transaction table.")
    file_paths = save_chunks_as_files(chunks, output_dir="temp_chunks")
    print(f"Saved {len(file_paths)} chunk files.")
    for file_path in file_paths:
        upload_file_to_gdrive(file_path, GDRIVE_FOLDER_ID, CREDENTIALS_FILE)
        # Delete the file after upload
        try:
            os.remove(file_path)
            print(f"Deleted local file: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")


# # ----------------------------------------
# # CHUNKING FUNCTION
# # ----------------------------------------
# def chunk_transactions_by_file(json_path, chunk_size, overlap):
#     """
#     Reads a JSON file where keys are filenames and values are lists of transactions.
#     For each file, splits the transactions into chunks (with overlap) and returns a list
#     of chunk dictionaries containing:
#       - "file": originating filename,
#       - "chunk_index": sequential chunk number,
#       - "chunk_text": text content of the chunk.
#     """
#     with open(json_path, "r", encoding="utf-8") as f:
#         data = json.load(f)
        
#     print(data)

#     chunks = []
#     for file_name, transactions in data.items():
#         num_trans = len(transactions)
#         chunk_index = 1  # start chunk numbering at 1 for each file
#         start = 0
#         while start < num_trans:
#             end = min(start + chunk_size, num_trans)
#             chunk_transactions = transactions[start:end]
#             # Build text with a header including file and chunk info
#             chunk_text = f"File: {file_name} | Chunk: {chunk_index}\n"
#             chunk_text += "-" * 40 + "\n"
#             for trans in chunk_transactions:
#                 trans_line = (
#                     f"Date: {trans.get('Date')}, "
#                     f"Particulars: {trans.get('Particulars')}, "
#                     f"Deposit: {trans.get('Deposit')}, "
#                     f"Withdrawal: {trans.get('Withdrawal')}, "
#                     f"Balance: {trans.get('Balance')}\n"
#                 )
#                 chunk_text += trans_line
#             chunk_text += "\n"
#             chunks.append({
#                 "file": file_name,
#                 "chunk_index": chunk_index,
#                 "chunk_text": chunk_text
#             })
#             if end == num_trans:
#                 break
#             # Update start pointer for next chunk (with overlap)
#             start += chunk_size - overlap
#             chunk_index += 1
#             print(f"Chunk {chunk_index} created for file '{file_name}' with transactions {start} to {end}.")

#     return chunks

# # ----------------------------------------
# # SAVE EACH CHUNK AS AN INDIVIDUAL TEXT FILE
# # ----------------------------------------
# def save_chunks_as_files(chunks, output_dir):
#     """
#     For each chunk, creates an individual text file in the specified output directory.
#     The filename is generated from the original filename and the chunk index.
    
#     Returns a list of file paths created.
#     """
#     file_paths = []
#     for chunk in chunks:
#         base_name = os.path.splitext(chunk["file"])[0]  # Remove extension if any
#         file_name = f"{base_name}_chunk_{chunk['chunk_index']}.txt"
#         file_path = os.path.join(output_dir, file_name)
#         with open(file_path, "w", encoding="utf-8") as f:
#             f.write(chunk["chunk_text"])
#         file_paths.append(file_path)
#     return file_paths

# # ----------------------------------------
# # UPLOAD A SINGLE FILE TO GOOGLE DRIVE
# # ----------------------------------------
# def upload_file_to_gdrive(file_path, folder_id, credentials_file):
#     """
#     Uploads the specified file to Google Drive within the given folder.
#     Uses a service account for authentication.
#     """
#     credentials = service_account.Credentials.from_service_account_file(
#         credentials_file,
#         scopes=["https://www.googleapis.com/auth/drive"]
#     )
#     service = build("drive", "v3", credentials=credentials)
    
#     file_metadata = {
#         "name": os.path.basename(file_path),
#         "parents": [folder_id]
#     }
#     media = MediaFileUpload(file_path, mimetype="text/plain")
#     uploaded_file = service.files().create(
#         body=file_metadata,
#         media_body=media,
#         fields="id"
#     ).execute()
    
#     print(f"Uploaded {os.path.basename(file_path)} (File ID: {uploaded_file.get('id')})")

# # ----------------------------------------
# # MAIN PIPELINE EXECUTION
# # ----------------------------------------
# def grivePipe():
#     # Step 1: Read and chunk the transactions by file.
#     chunks = chunk_transactions_by_file(INPUT_JSON_PATH, CHUNK_SIZE, OVERLAP)
#     print(f"Created {len(chunks)} chunks from the input JSON.")

#     # Step 2: Save each chunk as an individual text file in OUTPUT_DIR.
#     file_paths = save_chunks_as_files(chunks, OUTPUT_DIR)
#     print(f"Saved {len(file_paths)} text files in '{OUTPUT_DIR}' directory.")

#     # Step 3: Upload each text file to the specified Google Drive folder.
#     for file_path in file_paths:
#         upload_file_to_gdrive(file_path, GDRIVE_FOLDER_ID, CREDENTIALS_FILE)


