import streamlit as st
from openai import OpenAI
import uuid
import json
import os
import sqlite3

# Set up OpenAI client
ip = os.environ.get('LLAMACPP_IP')
client = OpenAI(base_url=f"http://{ip}/v1", api_key="fake")

# SQLite database file
DB_FILE = 'chat_sessions.db'

# Function to get a database connection
def get_db_connection():
    # Use detect_types to automatically convert TEXT to datetime
    conn = sqlite3.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
    # Ensure the connection uses UTF-8 encoding
    conn.text_factory = str
    return conn

# Initialize database
def init_db():
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS sessions
                         (id TEXT PRIMARY KEY, name TEXT, messages TEXT)''')
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"An error occurred while initializing the database: {e}")

# Function to create a new session
def create_session():
    try:
        session_id = str(uuid.uuid4())
        session_name = f"New Conversation {len(st.session_state.sessions) + 1}"
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO sessions (id, name, messages) VALUES (?, ?, ?)",
                      (session_id, session_name, json.dumps([])))
            conn.commit()
        st.session_state.sessions.append({"id": session_id, "name": session_name, "messages": []})
        st.session_state.current_session = session_id
    except sqlite3.Error as e:
        st.error(f"An error occurred while creating a new session: {e}")

# Function to delete a session
def delete_session(session_id):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
        st.session_state.sessions = [s for s in st.session_state.sessions if s['id'] != session_id]
        if st.session_state.current_session == session_id:
            st.session_state.current_session = None
    except sqlite3.Error as e:
        st.error(f"An error occurred while deleting the session: {e}")

# Function to save sessions to database
def save_sessions():
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            for session in st.session_state.sessions:
                c.execute("UPDATE sessions SET name = ?, messages = ? WHERE id = ?",
                          (session['name'], json.dumps(session['messages'], ensure_ascii=False), session['id']))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"An error occurred while saving sessions: {e}")

# Function to load sessions from database
def load_sessions():
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id, name, messages FROM sessions")
            rows = c.fetchall()
        st.session_state.sessions = [
            {"id": row[0], "name": row[1], "messages": json.loads(row[2])}
            for row in rows
        ]
    except sqlite3.OperationalError as e:
        st.error(f"Database error: {e}. Please check if the database file exists and is accessible.")
    except sqlite3.IntegrityError as e:
        st.error(f"Data integrity error: {e}. There might be duplicate or invalid data in the database.")
    except json.JSONDecodeError as e:
        st.error(f"JSON decoding error: {e}. The messages in the database might be corrupted.")
    except Exception as e:
        st.error(f"An unexpected error occurred while loading sessions: {e}")

# Function to ensure unique session names
def get_unique_session_name(name):
    existing_names = {session['name'] for session in st.session_state.sessions}
    if name not in existing_names:
        return name
    i = 1
    while f"{name} ({i})" in existing_names:
        i += 1
    return f"{name} ({i})"

# Initialize session state
st.session_state.setdefault('sessions', [])
st.session_state.setdefault('current_session', None)
st.session_state.setdefault('temperature', 1.0)

# Initialize database and load sessions on app start
init_db()
load_sessions()

# Optimize session loading for large numbers of sessions
if len(st.session_state.sessions) > 100:
    st.warning("You have a large number of sessions. Consider archiving old sessions to improve performance.")

# Sidebar
st.sidebar.title("Chat Sessions")

# Create new session button
if st.sidebar.button("New Chat"):
    create_session()
    save_sessions()

# Session selection
for session in st.session_state.sessions:
    col1, col2, col3 = st.sidebar.columns([3, 1, 1])
    with col1:
        if st.button(session['name'], key=f"select_{session['id']}"):
            st.session_state.current_session = session['id']
    with col2:
        if st.button("🗑️", key=f"delete_{session['id']}"):
            delete_session(session['id'])
            save_sessions()
    with col3:
        if st.button("✏️", key=f"edit_{session['id']}"):
            new_name = st.text_input("New name", value=session['name'], key=f"input_{session['id']}")
            if st.button("Save", key=f"save_{session['id']}"):
                session['name'] = new_name
                save_sessions()

# Temperature slider
st.sidebar.title("Settings")
st.session_state.temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 1.0, 0.1)

# Main chat interface
st.title("")

if st.session_state.current_session is not None:
    current_session = next(s for s in st.session_state.sessions if s['id'] == st.session_state.current_session)
    
    # Display chat history
    for message in current_session['messages']:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Chat input
    if prompt := st.chat_input():
        # Add user message to chat history
        current_session['messages'].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # If this is the first message, rename the session
        if len(current_session['messages']) == 1:
            new_name = prompt.strip()[:7] if len(prompt.strip()) > 7 else prompt.strip()
            new_name = get_unique_session_name(new_name)
            current_session['name'] = new_name
            # Update session name in the database
            try:
                with get_db_connection() as conn:
                    c = conn.cursor()
                    c.execute("UPDATE sessions SET name = ? WHERE id = ?",
                              (new_name, current_session['id']))
                    conn.commit()
            except sqlite3.OperationalError as e:
                st.error(f"Database error while updating session name: {e}")
            except sqlite3.IntegrityError as e:
                st.error(f"Data integrity error while updating session name: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred while updating the session name: {e}")

        # Generate AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in client.chat.completions.create(
                model="mistral-large-123b",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in current_session['messages']
                ],
                stream=True,
                temperature=st.session_state.temperature,
            ):
                content = chunk.choices[0].delta.content
                if content is not None:
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        # Add AI response to chat history
        current_session['messages'].append({"role": "assistant", "content": full_response})
        save_sessions()
        
        # Force a rerun to update the sidebar with the new session name
        st.rerun()
else:
    st.write("Please create or select a chat session to start.")
