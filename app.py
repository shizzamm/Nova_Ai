import os
import requests
import streamlit as st
from dotenv import load_dotenv

# LOAD CSS
def load_css():
    with open("style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# Move this to the very top to prevent Streamlit configuration errors
st.set_page_config(
    page_title="Nova AI",
    page_icon="🧠",
    layout="wide"
)

try:
    load_css()
except:
    pass

# LOAD ENV VARIABLES
load_dotenv()

# Force override token loading
HF_TOKEN = os.getenv("HF_TOKEN") or "PASTE_YOUR_NEW_TOKEN_HERE_IF_ENV_FAILS"

# CONFIGURABLE VARIABLES: Dynamic architecture routing
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"

# Clean up trailing slashes in environment strings to prevent double slashes in concatenation
base_url = API_BASE_URL.rstrip("/")
API_URL = f"{base_url}/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# SIDEBAR
st.sidebar.title("🚀 Nova AI")
page = st.sidebar.radio("Navigation", ["Dashboard", "AI Assistant", "To-Do List", "Notes"])

# DEBUG LOGGING IN SIDEBAR
st.sidebar.markdown("---")
st.sidebar.markdown("**Current Engine Config:**")
st.sidebar.code(f"Base: {API_BASE_URL}\nModel: {MODEL_NAME}")

# STORE TASKS
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# AI ASSISTANT PAGE
if page == "AI Assistant":
    st.title("🤖 Nova AI Assistant")
    user_input = st.text_input("Talk with Nova AI")

    if st.button("Send"):
        if user_input.strip() == "":
            st.warning("Please type something")
        else:
            ai_response = ""
            api_success = False

            # --- LIVE ENDPOINT REQUEST DEBUGGER ---
            # with st.expander("🔍 DYNAMIC CONFIGURATION LOGS", expanded=True):
            #     st.write(f"**Full API Target Endpoint:** `{API_URL}`")
            #     st.write(f"**Selected Model Target:** `{MODEL_NAME}`")
            #     st.write(f"**Token Verification:** `...{HF_TOKEN[-6:] if (HF_TOKEN and len(HF_TOKEN) > 6) else 'MISSING OR PLACEHOLDER'}`")

            # TRY CHAT ROUTER COMPLETIONS
            try:
                payload = {
                    "model": MODEL_NAME,
                    "messages": [{"role": "user", "content": user_input}],
                    "max_tokens": 150
                }
                
                response = requests.post(
                    API_URL,
                    headers=headers,
                    json=payload,
                    timeout=15
                )

                # --- EXPLICIT FIREWALL METADATA LOGGER ---
                if response.status_code != 200:
                    st.error(f"🌐 Server Returned Gateway Error Status: {response.status_code}")
                    st.write(f"**True destination that generated the 403 error block:** `{response.url}`")
                    st.write("**Response Server Body Content:**")
                    st.code(response.text)

                response.raise_for_status()
                result = response.json()

                if isinstance(result, dict) and "choices" in result and len(result["choices"]) > 0:
                    ai_response = result["choices"][0]["message"]["content"]
                    api_success = True
                else:
                    raise Exception("Unexpected API JSON layout.")

            except requests.exceptions.RequestException as req_err:
                st.sidebar.error("Network Request Failed")
            except Exception as e:
                st.sidebar.error(f"Error parsing response: {str(e)}")

            # FALLBACK
            if not api_success:
                st.info("🔄 Falling back to local responses...")
                if "hello" in user_input.lower():
                    ai_response = "Hello buddy 👋"
                else:
                    ai_response = f"Nova AI fallback mode activated. The server framework blocked the connection profile to model: {MODEL_NAME}."

            st.success(ai_response)

# Remaining pages kept simple to preserve structural navigation
else:
    st.title(f"🧠 Nova {page}")
    st.write(f"Section structure for '{page}' is active and operational.")
