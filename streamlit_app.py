import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from sqldb import execute_query, get_table_schema


load_dotenv()

TABLE_NAME = "Sales.SalesOrderDetail"
MODEL_NAME = "gpt-5.6-sol"


st.set_page_config(
    page_title="QueryPilot",
    page_icon="🧠",
    layout="wide",
)

st.title("QueryPilot")
st.caption("Ask questions about your database and generate executable SQL.")


if not os.getenv("OPENAI_API_KEY"):
    st.warning(
        "OPENAI_API_KEY is not set. Add it to your .env file."
    )


def is_safe_query(query):
    query = query.strip().lower()
    return query.startswith("select")


# Initialize schema + chat history only once
if "chat_history" not in st.session_state:

    with st.spinner("Reading table schema..."):
        schema = get_table_schema(TABLE_NAME)

    st.session_state.chat_history = [
        {
            "role": "developer",
            "content": f"""
You are a SQL assistant.

Generate MSSQL queries using only the schema below:

{schema}

Rules:
- Return SQL only
- Do not explain
- Use valid MSSQL syntax
- Generate SELECT queries only
"""
        }
    ]


# Display previous user/assistant messages
for message in st.session_state.chat_history:

    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])

    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.code(message["content"], language="sql")


# Chat input
question = st.chat_input(
    "Ask a question about your database..."
)


if question:

    # Display user's question
    with st.chat_message("user"):
        st.write(question)

    # Add user message to conversation history
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    try:

        client = OpenAI()

        with st.spinner("Generating SQL..."):

            response = client.responses.create(
                model=MODEL_NAME,
                input=st.session_state.chat_history
            )

            sql = response.output_text.strip()


        # Store assistant response
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": sql
            }
        )


        # Display assistant response
        with st.chat_message("assistant"):

            st.code(sql, language="sql")

            if not is_safe_query(sql):

                st.error(
                    "Blocked: Only SELECT queries are allowed."
                )

            else:

                with st.spinner(
                    "Running SQL against AdventureWorks..."
                ):

                    results = execute_query(sql)


                st.dataframe(
                    results,
                    width="stretch"
                )

                st.caption(
                    f"{len(results):,} row(s) returned"
                )


    except Exception as error:

        st.error(
            f"The request could not be completed: {error}"
        )