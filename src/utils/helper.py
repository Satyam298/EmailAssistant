import os 
import json
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


def authenticate_gmail():
    """
    Handle Gmail Authentication for both local and Streamlit Cloud environments
    """
    try:
        using_secrets = False
        try:
            if "client_id" in st.secrets:       # if runs on streamlit cloud
                using_secrets = True         
        except Exception:                       # if runs on local machine
            using_secrets = False

        # Build credentials structure
        if using_secrets:
            redirect_uri_local = st.secrets.get("redirect_uri_local")
            redirect_uri_cloud = st.secrets.get("redirect_uri_cloud")
            redirect_uris = [redirect_uri_local, redirect_uri_cloud]
            
            credentials_dict = {
                "web": {
                    "client_id": st.secrets["client_id"],
                    "project_id": st.secrets["project_id"],
                    "auth_uri": st.secrets["auth_uri"], 
                    "token_uri": st.secrets["token_uri"],
                    "client_secret": st.secrets["client_secret"],
                    "redirect_uris": redirect_uris
                }
            }
            
            os.makedirs("credentials", exist_ok=True)        
            cred_path = "credentials/temp_credentials.json"    # file exists temporarily in session memory
            with open(cred_path, "w") as f:
                json.dump(credentials_dict, f)
        else: 
            # Local credentials file
            cred_path = "credentials/credentials.json"
            with open(cred_path, "r") as f:
                credentials_dict = json.load(f)
            redirect_uris = credentials_dict.get("web", {}).get("redirect_uris", [])


        # Check if we already have valid credentials
        # auto authentication, doesn't need to go through full OAuth flow again
        if os.path.exists("credentials/gmail_token.json"):
            try:
                creds = Credentials.from_authorized_user_file("credentials/gmail_token.json")
            
                # Refresh if expired
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    with open("credentials/gmail_token.json", "w") as token:
                        token.write(creds.to_json())

                    st.session_state["gmail_creds"] = creds
                    st.session_state["auth_status"] = True
                    st.success("Successfully authenticated with Gmail!")
                    return creds

                # If valid, use existing credentials
                elif creds and creds.valid:
                    st.session_state["gmail_creds"] = creds
                    st.session_state["auth_status"] = True
                    st.success("Already authenticated with Gmail!")
                    return creds
                
            except ValueError as e:
                # Token file is corrupted or missing refresh_token
                st.warning("Existing credentials are invalid. Please authenticate again.")
                os.remove("credentials/gmail_token.json")


        # Determine environment and choose redirect URI
        if using_secrets:
            if st.secrets.get("environment") == "cloud":
                chosen_redirect_uri = redirect_uri_cloud
            elif "client_id" in st.secrets:
                chosen_redirect_uri = redirect_uri_cloud
            else: 
                chosen_redirect_uri = redirect_uri_local
        else:
            chosen_redirect_uri = redirect_uris[0] if redirect_uris else "http://localhost:8501"
        

        # Create OAuth flow with the chosen redirect URI
        flow = Flow.from_client_secrets_file(
            cred_path,
            scopes=[
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.compose"
            ],
            redirect_uri=chosen_redirect_uri
        )

        # Get authorization URL
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        # Store state and flow in session for later verification
        st.session_state['oauth_state'] = state
        st.session_state['oauth_flow'] = flow

        # Check if we have an authorization code in URL params
        query_params = st.query_params
        
        if 'code' in query_params:
            auth_code = query_params['code']
            
            # Get the flow from session
            if 'oauth_flow' in st.session_state:
                flow = st.session_state['oauth_flow']
                
                try:
                    # Exchange code for credentials
                    flow.fetch_token(code=auth_code)
                    creds = flow.credentials

                    # Save credentials
                    with open("credentials/gmail_token.json", "w") as token:
                        token.write(creds.to_json())

                    st.session_state["gmail_creds"] = creds
                    st.session_state["auth_status"] = True
                    
                    # Clear query params and oauth session data
                    st.query_params.clear()
                    if 'oauth_flow' in st.session_state:
                        del st.session_state['oauth_flow']
                    if 'oauth_state' in st.session_state:
                        del st.session_state['oauth_state']
                    
                    st.success("Successfully authenticated with Gmail!")
                    st.rerun()
                    
                    return creds
                except Exception as token_error:
                    st.error(f"Failed to exchange code for token: {token_error}")
                    st.info("Please try authenticating again.")
                    # Clear oauth data
                    if 'oauth_flow' in st.session_state:
                        del st.session_state['oauth_flow']
                    return None
            else:
                st.error("OAuth session expired. Please authenticate again.")
                return None
        else:
            # Show authorization instructions
            st.markdown("### Gmail Authentication Required")
            st.write("To use this app, you need to authorize access to your Gmail account.")
            
            # Display the authorization URL as a clickable link
            st.markdown(f"**[Click here to authorize Gmail access]({auth_url})**")
            
            st.info("After authorizing, you'll be redirected back to this app automatically.")
            
            # Debug info
            with st.expander("Debug Info (check this first!)"):
                st.write(f"**Redirect URI being used:** `{chosen_redirect_uri}`")
                st.write(f"**Environment detected:** {'Streamlit Cloud' if using_secrets else 'Local Development'}")
                st.write(f"**Credentials path:** `{cred_path}`")
                
                # Show first part of auth URL to verify redirect_uri parameter
                if 'redirect_uri=' in auth_url:
                    redirect_param = auth_url.split('redirect_uri=')[1].split('&')[0]
                    from urllib.parse import unquote
                    st.write(f"**Actual redirect_uri in auth URL:** `{unquote(redirect_param)}`")
            
            return None
            
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None