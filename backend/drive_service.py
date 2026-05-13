import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
_drive_service = None

def get_drive_service():
    global _drive_service
    if _drive_service is not None:
        return _drive_service
        
    email = os.environ.get("GOOGLE_SERVICE_ACCOUNT_EMAIL")
    private_key = os.environ.get("GOOGLE_PRIVATE_KEY")
    
    if not email or not private_key:
        raise ValueError("Google Service Account credentials missing in .env")
        
    private_key = private_key.replace('\\n', '\n')
    
    credentials = service_account.Credentials.from_service_account_info(
        {
            "client_email": email,
            "private_key": private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=SCOPES
    )
    
    _drive_service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
    return _drive_service

def search_files(query: str, folder_id: str = None) -> list:
    """Search Google Drive for files matching the query."""
    try:
        service = get_drive_service()
        
        q = query
        if folder_id:
            # Ensure it only searches within the specified folder
            q = f"('{folder_id}' in parents) and ({query})"
            
        results = service.files().list(
            q=q,
            pageSize=20,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)",
            spaces='drive'
        ).execute()
        
        return results.get('files', [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise

def get_folder_analytics(folder_id: str) -> dict:
    try:
        service = get_drive_service()
        
        # Get folder metadata
        folder = service.files().get(
            fileId=folder_id,
            fields="id, name, webViewLink"
        ).execute()
        
        # Get all files for analytics (simplification for sample size)
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=1000,
            fields="files(mimeType)"
        ).execute()
        
        files = results.get('files', [])
        total_files = len(files)
        
        type_counts = {}
        for f in files:
            t = f.get('mimeType', 'unknown')
            type_counts[t] = type_counts.get(t, 0) + 1
            
        return {
            "folder": folder,
            "totalFiles": total_files,
            "typeCounts": type_counts
        }
    except Exception as error:
        print(f"An error occurred getting analytics: {error}")
        raise
