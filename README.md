# Gmail Assistant

Natural-language AI agent for Gmail. Read, search, summarize, and send emails through a simple chat interface.

**Live demo:** [gmail-assistant-project.streamlit.app](https://gmail-assistant-project.streamlit.app/)  
(Note: Access requires prior authorization. Contact the owner from your email to request it. The app may take 1–2 minutes to start.)

### Features
- Summarize recent or unread emails
- Search by keyword, sender, or topic
- Compose and send emails
- Quick-action buttons for common tasks
- Secure Google OAuth 2.0 authentication

### Tech Stack
Python · Streamlit · Agno (Phidata) · Groq · Gmail API · Google OAuth 2.0

### Setup
1. Clone the repo  

2. Install dependencies  
   ```bash
   pipenv install
   pipenv shell
   ```

3. Create a `.env` file with:  
   ```
   GROQ_API_KEY=...
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   GOOGLE_PROJECT_ID=...
   GOOGLE_REDIRECT_URI=...
   ```

4. Run  
   ```bash
   streamlit run app.py
   ```

### Usage
Authenticate with Gmail via the sidebar, then chat naturally:

- “Summarize my 3 latest emails in under 100 words”
- “Find recent emails about invoices”
- “Send an email to example@domain.com saying I’m free Wednesday at 4:30 PM”
- “Show the latest email from sender@domain.com”

Quick actions in the sidebar cover the most common requests.




