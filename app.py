import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000/api"

st.set_page_config(page_title="TailorTalk Drive Assistant", page_icon="💬", layout="wide")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Please paste a Google Drive folder link in the sidebar to get started."}]
if "folder_id" not in st.session_state:
    st.session_state.folder_id = None
if "analytics" not in st.session_state:
    st.session_state.analytics = None

# Sidebar for configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    folder_url = st.text_input("Google Drive Folder URL", placeholder="https://drive.google.com/drive/folders/...")
    
    if st.button("Connect Folder"):
        if folder_url:
            with st.spinner("Connecting..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/connect", json={"url": folder_url})
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.folder_id = data["folder_id"]
                        st.session_state.analytics = data["analytics"]
                        st.success("Connected successfully!")
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"Connected to folder: **{data['analytics']['folder']['name']}**. What would you like to find?"
                        })
                    else:
                        st.error(f"Failed to connect: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection failed. Make sure the backend server is running. Error: {str(e)}")
        else:
            st.warning("Please enter a URL")

    # Display Analytics if connected
    if st.session_state.analytics:
        st.subheader("📊 Folder Analytics")
        analytics = st.session_state.analytics
        st.write(f"**Total Files:** {analytics['totalFiles']}")
        
        if analytics['typeCounts']:
            st.write("**File Types:**")
            for ftype, count in analytics['typeCounts'].items():
                short_type = ftype.split('.')[-1]
                st.caption(f"- {short_type}: {count}")

# Main Chat Interface
st.title("💬 TailorTalk Drive Assistant")
st.caption("Your intelligent Google Drive exploration partner. Connect a folder to begin.")
st.divider()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display files if they are in the message
        if "files" in message and message["files"]:
            for file in message["files"]:
                with st.expander(f"📄 {file['name']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Type:** {file.get('mimeType', 'Unknown')}")
                        st.write(f"**Modified:** {file.get('modifiedTime', 'Unknown')}")
                    with col2:
                        st.markdown(f"[🔗 Open File]({file.get('webViewLink', '#')})")

# Chat input
if prompt := st.chat_input("Ask for files (e.g., 'Find all PDFs')"):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            try:
                # Prepare chat history format for backend
                chat_history = [
                    {"role": "user" if m["role"] == "user" else "model", "text": m["content"]} 
                    for m in st.session_state.messages[:-1] # Exclude current prompt
                ]
                
                payload = {
                    "message": prompt,
                    "folder_id": st.session_state.folder_id,
                    "chat_history": chat_history
                }
                
                response = requests.post(f"{API_BASE_URL}/chat", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.markdown(data["text"])
                    
                    # Display files if any
                    files = data.get("files")
                    if files:
                        for file in files:
                            with st.expander(f"📄 {file['name']}"):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**Type:** {file.get('mimeType', 'Unknown')}")
                                    st.write(f"**Modified:** {file.get('modifiedTime', 'Unknown')}")
                                with col2:
                                    st.markdown(f"[🔗 Open File]({file.get('webViewLink', '#')})")
                    
                    # Append to history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": data["text"],
                        "files": files
                    })
                else:
                    st.error(f"Error from server: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Failed to communicate with backend. Make sure the FastAPI server is running on port 8000. Error: {str(e)}")
