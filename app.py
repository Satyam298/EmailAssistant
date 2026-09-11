import os  
import streamlit as st  
from src.assistant_builder import GmailAssistant  
from src.utils.helper import authenticate_gmail  

# Page configuration  
st.set_page_config(page_title="Gmail Assistant",  
                   page_icon="📧",  
                   layout="wide",  
                   initial_sidebar_state="expanded")  

# Custom CSS for chatbot-style messages  
st.markdown("""
    <style>
    .user-message {
        background-color: #0078ff; 
        color: white;
        padding: 10px;
        border-radius: 10px;
        max-width: 60%;
        margin-left: auto;
        text-align: right;
        font-size: 16px;
        margin-top: 30px;
    }
    .assistant-message {
        background-color: #f1f1f1;
        color: black;
        padding: 10px;
        border-radius: 10px;
        max-width: 70%;
        margin-right: auto;
        text-align: left;
        font-size: 16px;
        margin-top: 15px;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 30px;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():  
    if "chat_history" not in st.session_state:  
        st.session_state.chat_history = []  
    if "auth_status" not in st.session_state:  
        st.session_state.auth_status = False  
    if "current_query" not in st.session_state:  
        st.session_state.current_query = ""
    
    # Initialize agent ONLY after authentication
    if st.session_state.auth_status and "agent" not in st.session_state:
        try:
            with st.spinner("Initializing Gmail Assistant..."):  
                st.session_state.agent = GmailAssistant.setup_gmail_agent()
            st.success("Gmail Assistant initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize Gmail Assistant: {e}")


def handle_query(query: str):  
    """Handle query and update chat history"""  
    try:
        # Check if agent is initialized
        if "agent" not in st.session_state:
            st.error("Gmail Assistant is not initialized. Please authenticate first.")
            return None
        
        # Add user query to chat history  
        st.session_state.chat_history.append({'role': 'user', 'content': query})  

        # Get response  
        response = GmailAssistant.perform_task(agent=st.session_state.agent, task=query)  

        # Add response to chat history  
        if response:  
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})  

        return response    

    except Exception as e:  
        st.error(f"Error processing request: {str(e)}")
        # Add error to chat history so user can see it
        st.session_state.chat_history.append({
            'role': 'assistant', 
            'content': f"Sorry, I encountered an error: {str(e)}"
        })
        return None  


def main():  
    initialize_session_state()  

    # Display logo and title in one line using columns
    col1, col2 = st.columns([0.1, 0.9])

    with col1:
        st.image("static/gmail-logo-64px.png")  

    with col2:
       st.title("Gmail Assistant")
    
    st.caption("AI-powered assistant to manage your emails effortlessly.")  

    # Sidebar for authentication and quick actions  
    with st.sidebar:  
        st.header("🔑 Authentication")  
        
        # Show authentication status
        if st.session_state.auth_status:
            st.success("✅ Authenticated")
            if st.button("Re-authenticate / Switch Account"):
                # Clear credentials from session state
                if "gmail_creds" in st.session_state:
                    del st.session_state["gmail_creds"]
                if "agent" in st.session_state:
                    del st.session_state["agent"]
                
                # CRITICAL: Delete the token file to force new OAuth flow
                token_path = "credentials/gmail_token.json"
                if os.path.exists(token_path):
                    os.remove(token_path)
                
                st.session_state.auth_status = False
                st.info("Credentials cleared. Click 'Authenticate with Gmail' to sign in with a different account.")
                st.rerun()
        else:
            auth_button = st.button("Authenticate with Gmail")
            if auth_button:  
                creds = authenticate_gmail()  
                if creds:
                    st.rerun()

        # Only show quick actions if authenticated
        if st.session_state.auth_status:
            st.header("⚡ Quick Actions")  
            quick_actions = {  
                "📩 Get latest emails": "Get me the latest 3 emails and summarize them in under 200 words.",  
                "📧 Get unread emails": "Get me the latest 5 unread emails and summarize them in under 100 words.",
                "🔍 Search emails by keyword": "Search for emails related to 'invoice'.",
                "📅 Get emails by date": "Get me all emails received on 2025-06-04.",
                "📨 Send an email": "Send an email to example@gmail.com with subject 'Meeting' and content 'Let's meet tomorrow at 10 AM'"  
            }  
            
            selected_action = st.radio("Choose an action:", quick_actions.keys())  

            if st.button("Run Quick Action"):  
                st.session_state.current_query = quick_actions[selected_action]
                st.rerun()

    # Display chat history if authenticated  
    if not st.session_state.auth_status:  
        st.info("Please authenticate with Gmail using the sidebar to continue.")  
    else:  
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for message in st.session_state.chat_history:  
            if message['role'] == 'user':  
                st.markdown(f'<div class="user-message"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)  
            else:  
                st.markdown(f'<div class="assistant-message"><b>Assistant:</b> {message["content"]}</div>', unsafe_allow_html=True)  

        st.markdown('</div>', unsafe_allow_html=True)

    # Input for new queries  
    query = st.text_input("Enter your task",  
                          placeholder="Example: 'Find emails from Amazon in the last week' or 'Draft a reply to the latest email from my boss'",  
                          value=st.session_state.current_query,
                          disabled=not st.session_state.auth_status)  

    if st.button("Run Task", disabled=not st.session_state.auth_status):  
        if not st.session_state.auth_status:  
            st.warning("⚠️ Please authenticate with Gmail first.")  
        elif query:
            with st.spinner("Processing your request..."):  
                handle_query(query)  
            st.session_state.current_query = ""  
            st.rerun()
        else:
            st.warning("Please enter a task.")

if __name__ == "__main__":  
    main()