import streamlit as st
from google import genai
from google.genai import types
import os
import json

st.title('Chat with Google Gemini')

# --- 2. STRUCTURED CONTEXT (Sidebar Persona) ---
persona = st.sidebar.selectbox("Model Persona", ["General Assistant", "Software Architect", "Car expert"])
system_map = {
    "General Assistant": "You are a helpful, polite assistant.",
    "Software Architect": "You are a senior architect working in Information Technology field.",
    "Car expert": "You are a subject matter expert on cars."
}

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    st.chat_message(message['role'])
    st.markdown(message['content'])

# React to user input
prompt = st.chat_input('Ask anything')
if prompt:
    # Display user message in chat message container
    st.chat_message('user')
    st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

if prompt:
    # Call Gemini API
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    try:
        with st.spinner("Gemini is thinking..."):
            # --- PARSING & STRUCTURE ---
            response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_map[persona] + " Answer in less than 100 words and do not make response unnecessarily long.",
                response_mime_type="application/json",
                response_schema={
                    # all responses will be in this format
                    "type": "OBJECT",
                    "properties": {
                        "llm_response": {"type": "STRING"}
                    }
                }
            ))
        data = json.loads(response.text)

        # Display LLM response in chat message container
        st.chat_message('assistant')
        st.markdown(data['llm_response'])
        # Add LLM response message to chat history
        st.session_state.messages.append({"role": "assistant", "content": data['llm_response']})

        # --- TOKEN TRACKING ---
        usage = response.usage_metadata
        st.sidebar.divider()
        st.sidebar.subheader("Token Usage")
        st.sidebar.info(f"Total Tokens: {usage.total_token_count}")
        st.sidebar.write(f"Input: {usage.prompt_token_count} | Output: {usage.candidates_token_count}")

    except Exception as ex:
        st.error(f"An error occurred - {ex}")