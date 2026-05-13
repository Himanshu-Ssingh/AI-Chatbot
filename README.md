# TailorTalk Drive Assistant

A clean and powerful conversational AI agent that searches and discovers files within your Google Drive using natural language.

## Architecture
**Input:** Drive folder link
**Output:** AI assistant searches that folder and returns a cleanly formatted list of files (name, type, date, and clickable link).

This project runs entirely on **Streamlit**, integrating **LangChain** and **Google Drive API** in a clean, single-file architecture.

---

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables (`.env`)
Create a `.env` file in the root directory and add your credentials:
```env
GEMINI_API_KEY="your_gemini_api_key"
GOOGLE_SERVICE_ACCOUNT_EMAIL="your-service-account@your-project.iam.gserviceaccount.com"
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

### 3. How to share folder with service account
Google Drive will only allow the AI to search folders that are explicitly shared with the Service Account.
1. Open Google Drive.
2. Right-click the folder you want the AI to search.
3. Click **Share**.
4. In the "Add people and groups" field, paste your `GOOGLE_SERVICE_ACCOUNT_EMAIL`.
5. Give it "Viewer" access and click **Send**.

### 4. How to use dynamic folder links
You don't need to hardcode the folder ID in the code! 
1. Open the Streamlit App.
2. In the "Enter Google Drive Folder Link" text box, paste the full URL of your Google Drive folder (e.g., `https://drive.google.com/drive/folders/1qkx58...`).
3. The app will dynamically extract the ID, connect, and lock the AI's search context to that specific folder.

---

## Example Usage

1. Run the app:
   ```bash
   streamlit run app.py
   ```
2. Paste the folder link: `https://drive.google.com/drive/folders/1qkx58doSeYrcLjHPDysJyVJ36PsSqqIt`
3. Ask the AI: 
   - *"Find all PDFs about AI"*
   - *"Do we have any spreadsheets from last week?"*
   - *"Search for a file containing the word 'TailorTalk'"*

The AI will output cleanly formatted results like:
> **Report_AI.pdf**
> - **Type:** `application/pdf`
> - **Modified Date:** 2024-05-13
> - **Link:** [Click here to open Drive Link](https://...)
