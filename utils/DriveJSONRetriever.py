import os
import io
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2 import service_account
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Configuration – replace these with your actual values
CREDENTIALS_FILE = 'credentials.json'
TARGET_FOLDER_ID = '1oL0fn813sIKLt16_fmFSqXcwgG4OjXDI'  # The ID of the folder containing the file
TARGET_FILE_NAME = 'filtered_transactions.json'             # The name of the file to retrieve
NEW_FILE_NAME = 'filtered_transactions.json'        # The name for a new uploaded file (if needed)

def get_drive_service(credentials_file: str):
    """Initializes and returns a Google Drive service."""
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=credentials)

def search_file_by_name(file_name: str, parent_folder_id: str = None) -> str:
    """
    Searches for a file by name (and optionally parent folder) and returns its file ID.

    Args:
        file_name (str): The name of the file to search for.
        parent_folder_id (str): Optional; The ID of the parent folder to narrow the search.

    Returns:
        str: The file ID of the found file, or None if not found.
    """
    service = get_drive_service(CREDENTIALS_FILE)
    query = f"name = '{file_name}'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print(f"No file found with name '{file_name}' in folder '{parent_folder_id if parent_folder_id else 'root'}'.")
        return None
    if len(items) > 1:
        print(f"Warning: Multiple files found with name '{file_name}' in folder '{parent_folder_id if parent_folder_id else 'root'}'. Using the first one.")
    return items[0]['id']

def retrieve_data_from_gdrive(file_name: str, folder_id=TARGET_FOLDER_ID) -> dict or None:
    """
    Retrieves data from a JSON file within a specified Google Drive folder.

    Args:
        file_name (str): The name of the file to retrieve.
        folder_id (str): The ID of the folder containing the file.

    Returns:
        dict or None: Parsed JSON data from the file, or None if the file is not found.
    """
    file_id = search_file_by_name(file_name, folder_id)
    if file_id:
        return download_file_from_gdrive_by_id(file_id)
    return None

def download_file_from_gdrive_by_id(file_id: str) -> dict:
    """
    Downloads a JSON file from Google Drive using its file ID.

    Args:
        file_id (str): The ID of the file to download.

    Returns:
        dict: Parsed JSON data from the downloaded file.
    """
    service = get_drive_service(CREDENTIALS_FILE)
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download progress: {int(status.progress() * 100)}%")
    fh.seek(0)
    data = json.load(fh)
    return data

def delete_file_by_name_in_folder(file_name: str):
    """
    Deletes a file with the given name within the specified Google Drive folder.
    """
    service = get_drive_service(CREDENTIALS_FILE)
    file_id_to_delete = search_file_by_name(file_name, TARGET_FOLDER_ID)
    if file_id_to_delete:
        try:
            service.files().delete(fileId=file_id_to_delete).execute()
            print(f"Successfully deleted file '{file_name}' (ID: {file_id_to_delete}) from folder '{TARGET_FOLDER_ID}'.")
        except Exception as e:
            print(f"An error occurred while deleting file '{file_name}': {e}")
    else:
        print(f"File '{file_name}' not found in folder '{TARGET_FOLDER_ID}'.")

def upload_file_to_gdrive(file_data, file_name: str) -> dict:
    """
    Uploads JSON data as a file to Google Drive.

    Returns:
        dict: The uploaded file's metadata.
    """
    service = get_drive_service(CREDENTIALS_FILE)
    # Write the JSON data to a temporary file
    temp_file = file_name
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(file_data, f, indent=4)

    file_metadata = {
        "name": file_name,
        "parents": [TARGET_FOLDER_ID]
    }
    media = MediaFileUpload(temp_file, mimetype="application/json")
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"Uploaded file '{file_name}' with ID: {file.get('id')} to folder '{TARGET_FOLDER_ID}'.")
    os.remove(temp_file)
    return file

def upload_my_file(file_name: str, file_data):
    """
    Uploads a file to Google Drive and deletes the old one if it exists.
    """
    delete_file_by_name_in_folder(file_name)
    upload_file_to_gdrive(file_data, file_name)