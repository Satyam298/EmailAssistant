# import os 
# import sys
# from typing import List
# from textwrap import dedent
# from dataclasses import dataclass

# from agno.agent import Agent, RunResponse
# from agno.models.huggingface import HuggingFace
# from agno.models.groq import Groq
# from agno.tools.gmail import GmailTools

# from src.utils.exception import CustomException

# from dotenv import load_dotenv
# load_dotenv()

# HF_TOKEN = os.getenv("HF_TOKEN_MISTRAL")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
# GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


# @dataclass
# class GmailAssistant():
#     """
#     Initializes and return a Gmail Assistant
#     Executing tasks using the assistant
#     """

#     def setup_gmail_agent()->Agent:
#         try:
#             agent = Agent(name="Gmail Agent",
#                         model=Groq(id="llama-3.3-70b-versatile"), #llama-3.3-70b-versatile, llama-3.1-8b-instant
#                                    #response_format={"type": "json_object"}), 
#                         #model=HuggingFace(id="mistralai/Mistral-7B-v0.1"),
#                         tools=[GmailTools()],
#                         description=dedent("""\
#                                             You are an AI-powered Gmail assistant that can read, search, send, and manage emails.
#                                             Your role is to assist users in handling their Gmail efficiently.
#                                             Your expertise includes:
#                                             1. Reading emails with attention to detail.
#                                             2. Sending emails with structured content.
#                                             3. Searching emails using keywords, date, or sender.
#                                             4. Managing emails effectively."""),
#                         instructions=dedent("""\
#                                             Instructions for handling tasks:

#                                             1. **Reading Emails**:
#                                                 - Return details in the format:
#                                                   - **Sender Email**: {email of sender}
#                                                   - **Summary**: {brief but comprehensive summary}
#                                                   - **Received Time**: {converted IST timestamp}
#                                                 - Convert UTC time to IST (UTC+5:30).

#                                             2. **Sending Emails**:
#                                                 - Ensure the recipient email is valid.
#                                                 - Format:
#                                                   - **Subject**: {clear and brief}
#                                                   - **Content**: {all necessary details}
#                                                   - **Signature**: "Best Regards"

#                                             3. **Searching Emails**:
#                                                 - Search by:
#                                                   - **Email ID**
#                                                   - **Email Content**
#                                                   - **Date**
#                                                 - Look in both **Inbox and Spam**.
#                                                 - Include both received and sent emails.

#                                             4. **Fetching Latest Emails**:
#                                                 - When using get_latest_emails tool, always pass count as a NUMBER, not a string.
#                                                 - Return a numbered list:
#                                                   - **Sender Email**
#                                                   - **Brief Summary**
#                                                   - **Received Time** (in IST)
#                                                 - Sort by latest first. 

#                                             5. **Fetching Emails from a Specific User**:
#                                                 - Search all emails from a given sender.
#                                                 - Convert received time to IST.
#                                                 - Return a numbered list sorted by date (latest first).
                                            
#                                             IMPORTANT: When calling tools, ensure all numeric parameters are passed as numbers, not strings."""),
#                         add_history_to_messages=False,
#                         reasoning=False,
#                         structured_outputs=False,
#                         show_tool_calls=True,
#                         debug_mode=True,
#                         markdown=True)

#             return agent
        
#         except Exception as e:
#             raise CustomException(e, sys)
    
    
#     def perform_task(agent: Agent, task: str)->str:
#         try:
#             # # Get the streamed response
#             # response_stream: Iterator[RunResponse] = agent.run(task, stream=True)
            
#             # # Collect and format the streamed content
#             # full_response = []
#             # for chunk in response_stream:
#             #     full_response.append(chunk.content)
#             #     # Print each chunk in real-time (for terminal)
#             #     pprint_run_response(chunk, markdown=True)
            
#             # return "".join(full_response)
#             response: RunResponse = agent.run(task)
#             return response.content

#         except Exception as e:
#             raise CustomException(e, sys)
        

import os 
import sys
from typing import List
from textwrap import dedent
from dataclasses import dataclass

import streamlit as st
from agno.agent import Agent, RunResponse
from agno.models.huggingface import HuggingFace
from agno.models.groq import Groq
from agno.tools.gmail import GmailTools

from src.utils.exception import CustomException

from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN_MISTRAL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


@dataclass
class GmailAssistant():
    """
    Initializes and return a Gmail Assistant
    Executing tasks using the assistant
    """

    def setup_gmail_agent()->Agent:
        try:
            # Get credentials from session state
            gmail_creds = st.session_state.get("gmail_creds")
            
            if not gmail_creds:
                raise ValueError("Gmail credentials not found in session state. Please authenticate first.")
            
            agent = Agent(
                name="Gmail Agent",
                model=Groq(id="llama-3.3-70b-versatile"),
                tools=[GmailTools(creds=gmail_creds)],  # Pass credentials using 'creds' parameter
                description=dedent("""\
                    You are an AI-powered Gmail assistant that can read, search, send, and manage emails.
                    Your role is to assist users in handling their Gmail efficiently.
                    Your expertise includes:
                    1. Reading emails with attention to detail.
                    2. Sending emails with structured content.
                    3. Searching emails using keywords, date, or sender.
                    4. Managing emails effectively."""),
                    
                    # CRITICAL: You must ALWAYS use the available tools to perform actions. Never just describe what you would do.
                instructions=dedent("""\
                    Instructions for handling tasks:

                    1. **Reading Emails**:
                        - Use get_latest_emails tool to fetch emails
                        - Return details in the format:
                          - **Sender Email**: {email of sender}
                          - **Summary**: {brief but comprehensive summary}
                          - **Received Time**: {converted IST timestamp}
                        - Convert UTC time to IST (UTC+5:30).

                    2. **Sending Emails**:
                        - Use send_email tool
                        - Ensure the recipient email is valid.
                        - Format:
                          - **Subject**: {clear and brief}
                          - **Content**: {all necessary details}
                          - **Signature**: "Best Regards"

                    3. **Searching Emails**:
                        - Use search_emails or get_emails_by_context tool
                        - Search by:
                          - **Email ID**
                          - **Email Content**
                          - **Date**
                        - Look in both **Inbox and Spam**.
                        - Include both received and sent emails.

                    4. **Fetching Latest Emails**:
                        - ALWAYS use get_latest_emails tool with count as an INTEGER
                        - Example: get_latest_emails(count=3) NOT get_latest_emails(count="3")
                        - Return a numbered list:
                          - **Sender Email**
                          - **Brief Summary**
                          - **Received Time** (in IST)
                        - Sort by latest first. 

                    5. **Fetching Emails from a Specific User**:
                        - Use get_emails_from_user tool
                        - Search all emails from a given sender.
                        - Convert received time to IST.
                        - Return a numbered list sorted by date (latest first).
                                    
                    6. **Fetching Unread Emails**:
                        - ALWAYS use get_unread_emails tool with count as an INTEGER
                        - Example: get_unread_emails(count=5) NOT get_unread_emails(count="5")
                        - Return a numbered list:
                          - **Sender Email**
                          - **Brief Summary**
                          - **Received Time** (in IST)
                        - Sort by latest first.
                    
                    7. **Fetching Emails by Date**:
                        - Use get_emails_by_date tool with proper date format
                        - Date format should be YYYY-MM-DD
                        - Example: get_emails_by_date(start_date="2024-01-01", end_date="2024-01-31")
                        - Return a numbered list with sender, summary, and received time in IST
                    
                    CRITICAL RULES:
                    - ALWAYS call the actual tool functions - never just explain what you would do
                    - All numeric parameters must be integers, not strings
                    - If a tool call fails, report the error and try again with corrected parameters"""),
                    # - Never output raw function syntax like <function=...> - always use proper tool calls
                add_history_to_messages=True,
                reasoning=False,
                structured_outputs=False,
                show_tool_calls=True,
                debug_mode=True,  
                markdown=True)

            return agent
        
        except Exception as e:
            raise CustomException(e, sys)
    
    
    def perform_task(agent: Agent, task: str)->str:
        try:
            response: RunResponse = agent.run(task)
            return response.content

        except Exception as e:
            raise CustomException(e, sys)