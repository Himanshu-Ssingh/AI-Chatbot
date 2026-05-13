from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from backend.drive_service import search_files
import os
import json

@tool
def search_google_drive(query: str, folder_id: str = None) -> str:
    """
    Search for files in Google Drive folder using a search query string.
    The query follows Google Drive API v3 search syntax.
    Returns a JSON string of matched files.
    """
    try:
        files = search_files(query, folder_id)
        if not files:
            return json.dumps({"message": "No files found matching the query."})
        return json.dumps({"files": files})
    except Exception as e:
        return json.dumps({"error": str(e)})


def run_agent(user_message: str, folder_id: str = None, chat_history: list = None) -> dict:
    if not chat_history:
        chat_history = []
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=api_key,
        temperature=0
    )
    
    # We use a simple bind_tools for the agent setup
    # Because we need the folder_id inside the tool, we can wrap the tool logic
    # Or just pass folder_id explicitly if we let LLM know about it,
    # but the simplest way is to inject it dynamically or let LLM pass None and we handle it.
    
    # Redefine tool dynamically to inject folder_id
    @tool
    def search_drive_for_user(query: str) -> str:
        """
        Search for files in Google Drive using a search query string (Drive API v3 syntax).
        Examples of query:
        - "mimeType='application/pdf' and fullText contains 'AI'"
        - "name contains 'report'"
        """
        print(f"DEBUG: Executing Drive Query -> {query}", flush=True)
        try:
            files = search_files(query, folder_id)
            if not files:
                return json.dumps({"message": "No files found matching the query."})
            return json.dumps({"files": files})
        except Exception as e:
            return json.dumps({"error": str(e)})

    llm_with_tools = llm.bind_tools([search_drive_for_user])
    
    messages = [
        SystemMessage(content=f"""You are the TailorTalk File Discovery Assistant.
Your goal is to help users find files in their Google Drive.

Convert natural language into valid Google Drive API 'q' queries.
IMPORTANT: DO NOT include 'in parents' or any folder IDs in your query. The system handles folder scoping automatically.
Examples:
- "Find AI PDFs" -> "mimeType='application/pdf' and fullText contains 'AI'"
- "Find report files" -> "name contains 'report'"
- "Show image files" -> "mimeType contains 'image/'"
Use the search_drive_for_user tool to search.""")
    ]
    
    for msg in chat_history:
        if msg.get('role') == 'user':
            messages.append(HumanMessage(content=msg.get('text')))
        elif msg.get('role') == 'model':
            messages.append(AIMessage(content=msg.get('text')))
            
    messages.append(HumanMessage(content=user_message))
    
    response = llm_with_tools.invoke(messages)
    
    # Check if tool was called
    tool_calls = response.tool_calls
    files_context = None
    
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call['name'] == 'search_drive_for_user':
                query = tool_call['args']['query']
                tool_output = search_drive_for_user.invoke(tool_call)
                
                output_str = tool_output.content if hasattr(tool_output, "content") else str(tool_output)
                
                # Performance Optimization: Skip the second LLM call to save time!
                parsed_output = json.loads(output_str)
                if "files" in parsed_output:
                    files_context = parsed_output["files"]
                    return {
                        "text": "Here are the files I found in your Drive:",
                        "files": files_context
                    }
                else:
                    return {
                        "text": "I couldn't find any files matching your request in this folder.",
                        "files": None
                    }
    
    return {
        "text": response.content,
        "files": files_context
    }
