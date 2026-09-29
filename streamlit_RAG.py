
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from ingestion import create_embeddings
import chromadb
import sqlite3
import uuid
from datetime import datetime

# =========================================================
# App setup
# =========================================================
load_dotenv()

st.set_page_config(
    page_title="PolicyWise AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

client = OpenAI()

dbclient = chromadb.PersistentClient("./chroma_db")
collection = dbclient.get_or_create_collection(
    "CompanyPolicies",
    configuration={"hnsw": {"space": "cosine"}}
)

CHAT_DB = "rag_chat_history.db"


# =========================================================
# SQLite helpers
# =========================================================
def get_conn():
    conn = sqlite3.connect(CHAT_DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                response_id TEXT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()


def create_chat(first_question):
    chat_id = str(uuid.uuid4())
    now = datetime.now().isoformat(timespec="seconds")

    title = first_question.strip().replace("\n", " ")
    if len(title) > 42:
        title = title[:42] + "..."

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO chats (
                chat_id,
                title,
                created_at,
                updated_at,
                response_id
            )
            VALUES (?, ?, ?, ?, NULL)
            """,
            (chat_id, title, now, now)
        )
        conn.commit()

    return chat_id


def get_chats():
    # Only return chats that actually contain messages.
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT
                c.chat_id,
                c.title,
                c.updated_at
            FROM chats c
            WHERE EXISTS (
                SELECT 1
                FROM messages m
                WHERE m.chat_id = c.chat_id
            )
            ORDER BY c.updated_at DESC
            LIMIT 20
            """
        ).fetchall()


def get_messages(chat_id):
    if not chat_id:
        return []

    with get_conn() as conn:
        return conn.execute(
            """
            SELECT role, content
            FROM messages
            WHERE chat_id = ?
            ORDER BY id
            """,
            (chat_id,)
        ).fetchall()


def add_message(chat_id, role, content):
    now = datetime.now().isoformat(timespec="seconds")

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO messages (
                chat_id,
                role,
                content,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (chat_id, role, content, now)
        )

        conn.execute(
            """
            UPDATE chats
            SET updated_at = ?
            WHERE chat_id = ?
            """,
            (now, chat_id)
        )

        conn.commit()


def get_response_id(chat_id):
    if not chat_id:
        return None

    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT response_id
            FROM chats
            WHERE chat_id = ?
            """,
            (chat_id,)
        ).fetchone()

        return row["response_id"] if row else None


def set_response_id(chat_id, response_id):
    if not chat_id:
        return

    now = datetime.now().isoformat(timespec="seconds")

    with get_conn() as conn:
        conn.execute(
            """
            UPDATE chats
            SET response_id = ?,
                updated_at = ?
            WHERE chat_id = ?
            """,
            (response_id, now, chat_id)
        )
        conn.commit()


def delete_chat(chat_id):
    if not chat_id:
        return

    with get_conn() as conn:
        conn.execute(
            "DELETE FROM messages WHERE chat_id = ?",
            (chat_id,)
        )
        conn.execute(
            "DELETE FROM chats WHERE chat_id = ?",
            (chat_id,)
        )
        conn.commit()


# =========================================================
# RAG
# =========================================================
def retrieve_context(user_query, n_results=3):
    query_embedding = create_embeddings(user_query)

    related_docs = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )

    documents = related_docs.get("documents", [[]])[0]

    return "\n\n".join(documents)


def ask_rag(chat_id, user_query):
    context = retrieve_context(user_query)

    prompt = f"""
You are a helpful company policy assistant.

Answer the user's question using ONLY the retrieved company-policy context below.

User question:
{user_query}

Retrieved context:
{context}

Instructions:
- Give a direct and natural answer.
- Do not invent policy details.
- If the answer is not supported by the retrieved context, say:
  "I don't have enough context to answer that from the available company policies."
- Keep the answer concise unless the user asks for more detail.
"""

    previous_response_id = get_response_id(chat_id)

    request_args = {
        "model": "gpt-5.6-sol",
        "input": prompt
    }

    if previous_response_id:
        request_args["previous_response_id"] = previous_response_id

    response = client.responses.create(**request_args)

    set_response_id(chat_id, response.id)

    return response.output_text


# =========================================================
# Styling
# =========================================================
st.markdown(
    """
    <style>
        .block-container {
            max-width: 1120px;
            padding-top: 3.2rem !important;
            padding-bottom: 6rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.18);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem;
        }

        .app-title {
            font-size: 2.25rem;
            line-height: 1.2;
            font-weight: 750;
            margin-top: 0.25rem;
            margin-bottom: 0.35rem;
        }

        .app-subtitle {
            font-size: 1.05rem;
            color: #777777;
            margin-bottom: 2rem;
        }

        .sidebar-heading {
            font-size: 0.8rem;
            font-weight: 700;
            color: #777777;
            margin-top: 1.25rem;
            margin-bottom: 0.45rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        [data-testid="stChatMessage"] {
            border-radius: 16px;
        }

        [data-testid="stChatInput"] {
            margin-bottom: 0.75rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# Initialize app state
# =========================================================
init_db()

if "active_chat_id" not in st.session_state:
    # None means a clean, unsaved New Chat.
    st.session_state.active_chat_id = None


# =========================================================
# Sidebar
# =========================================================
with st.sidebar:
    st.markdown("## 💬 PolicyWise AI")

    if st.button(
        "＋ New chat",
        use_container_width=True,
        type="primary"
    ):
        # Do not insert a blank chat into SQLite.
        st.session_state.active_chat_id = None
        st.rerun()

    st.markdown(
        '<div class="sidebar-heading">Recent chats</div>',
        unsafe_allow_html=True
    )

    chats = get_chats()

    if chats:
        for chat in chats:
            if st.button(
                chat["title"],
                key=f"chat_{chat['chat_id']}",
                use_container_width=True
            ):
                st.session_state.active_chat_id = chat["chat_id"]
                st.rerun()
    else:
        st.caption("No recent chats yet.")

    st.divider()

    if st.session_state.active_chat_id:
        if st.button(
            "🗑️ Delete current chat",
            use_container_width=True
        ):
            delete_chat(st.session_state.active_chat_id)
            st.session_state.active_chat_id = None
            st.rerun()


# =========================================================
# Main content
# =========================================================
st.markdown(
    '<div class="app-title">Company Policy Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="app-subtitle">Ask questions across your company policies.</div>',
    unsafe_allow_html=True
)

chat_id = st.session_state.active_chat_id
messages = get_messages(chat_id)


# =========================================================
# Welcome screen
# =========================================================
# Use native Streamlit markdown inside a bordered container.
# This avoids raw HTML such as <br> or <b> appearing as text.
if not messages:
    with st.container(border=True):
        st.markdown("### What can I help you find?")
        st.markdown(
            """
Try questions such as:

- How many vacation days can employees carry forward?
- What is the remediation target for critical vulnerabilities?
- What is the policy for using generative AI tools?
- What are the remote-work security requirements?
            """
        )


# =========================================================
# Existing messages
# =========================================================
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =========================================================
# User input
# =========================================================
user_query = st.chat_input(
    "Ask a question about company policies..."
)

if user_query:

    # Create the chat only when the first question is actually sent.
    if not st.session_state.active_chat_id:
        st.session_state.active_chat_id = create_chat(user_query)

    chat_id = st.session_state.active_chat_id

    add_message(
        chat_id,
        "user",
        user_query
    )

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching company policies..."):
            try:
                answer = ask_rag(
                    chat_id,
                    user_query
                )

                st.markdown(answer)

                add_message(
                    chat_id,
                    "assistant",
                    answer
                )

            except Exception as exc:
                st.error(
                    f"Something went wrong: {exc}"
                )

    # Refresh so the new chat title appears immediately in Recent Chats.
    st.rerun()
