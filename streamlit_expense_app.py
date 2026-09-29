import json
import pandas as pd
import streamlit as st

from openai import OpenAI
from dotenv import load_dotenv

from tools import (
    get_expenses,
    add_expense,
    update_expense,
    delete_expense
)

# ---------------------------------------------------------
# Setup
# ---------------------------------------------------------

load_dotenv()

client = OpenAI()
MODEL_NAME = "gpt-5.6-sol"

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="SpendWise AI",
    page_icon="💰",
    layout="wide"
)

# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .sub-title {
        font-size: 16px;
        color: #888888;
        margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        background-color: rgba(128,128,128,0.06);
        border: 1px solid rgba(128,128,128,0.15);
        padding: 15px;
        border-radius: 12px;
    }

    .delete-card {
        background-color: rgba(255, 75, 75, 0.06);
        border: 1px solid rgba(255, 75, 75, 0.35);
        padding: 18px;
        border-radius: 12px;
        margin-top: 10px;
        margin-bottom: 16px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Tool Definitions
# ---------------------------------------------------------

mytools = [
    {
        "type": "function",
        "name": "get_expenses",
        "description": "Get all expenses.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "add_expense",
        "description": "Add a new expense.",
        "parameters": {
            "type": "object",
            "properties": {
                "expense_date": {
                    "type": "string",
                    "description": "Expense date in YYYY-MM-DD format."
                },
                "category": {
                    "type": "string",
                    "description": "Expense category."
                },
                "description": {
                    "type": "string",
                    "description": "Expense description."
                },
                "amount": {
                    "type": "number",
                    "description": "Expense amount."
                },
                "payment_method": {
                    "type": "string",
                    "description": "Payment method."
                }
            },
            "required": [
                "expense_date",
                "category",
                "description",
                "amount",
                "payment_method"
            ]
        }
    },
    {
        "type": "function",
        "name": "update_expense",
        "description": "Update an existing expense.",
        "parameters": {
            "type": "object",
            "properties": {
                "expense_id": {
                    "type": "integer",
                    "description": "Expense ID to update."
                },
                "expense_date": {
                    "type": "string",
                    "description": "Expense date in YYYY-MM-DD format."
                },
                "category": {
                    "type": "string",
                    "description": "Expense category."
                },
                "description": {
                    "type": "string",
                    "description": "Expense description."
                },
                "amount": {
                    "type": "number",
                    "description": "Expense amount."
                },
                "payment_method": {
                    "type": "string",
                    "description": "Payment method."
                }
            },
            "required": [
                "expense_id",
                "expense_date",
                "category",
                "description",
                "amount",
                "payment_method"
            ]
        }
    },
    {
        "type": "function",
        "name": "delete_expense",
        "description": "Delete an expense.",
        "parameters": {
            "type": "object",
            "properties": {
                "expense_id": {
                    "type": "integer",
                    "description": "Expense ID to delete."
                }
            },
            "required": [
                "expense_id"
            ]
        }
    }
]

# ---------------------------------------------------------
# Tool Mapping
# ---------------------------------------------------------

tool_mapping = {
    "get_expenses": get_expenses,
    "add_expense": add_expense,
    "update_expense": update_expense,
    "delete_expense": delete_expense
}

# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

if "response_id" not in st.session_state:
    st.session_state.response_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_delete" not in st.session_state:
    st.session_state.pending_delete = None

if "pending_delete_call_id" not in st.session_state:
    st.session_state.pending_delete_call_id = None

if "pending_delete_response_id" not in st.session_state:
    st.session_state.pending_delete_response_id = None

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">💰 SpendWise AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Your conversational AI-powered personal expense tracker'
    '</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Read Expense Data
# ---------------------------------------------------------

try:
    expenses_df = get_expenses()

except Exception as error:
    expenses_df = pd.DataFrame()
    st.error(f"Unable to read expense data: {error}")

# ---------------------------------------------------------
# Dashboard Metrics
# ---------------------------------------------------------

if not expenses_df.empty:

    total_expense = expenses_df["Amount"].sum()
    transaction_count = len(expenses_df)
    average_expense = expenses_df["Amount"].mean()
    highest_expense = expenses_df["Amount"].max()

else:

    total_expense = 0
    transaction_count = 0
    average_expense = 0
    highest_expense = 0


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💵 Total Expenses",
        f"${total_expense:,.2f}"
    )

with col2:
    st.metric(
        "🧾 Transactions",
        f"{transaction_count:,}"
    )

with col3:
    st.metric(
        "📊 Average Expense",
        f"${average_expense:,.2f}"
    )

with col4:
    st.metric(
        "🔝 Highest Expense",
        f"${highest_expense:,.2f}"
    )

st.divider()

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "🤖 AI Assistant",
        "📋 Expenses",
        "📊 Insights"
    ]
)

# =========================================================
# TAB 1 - AI ASSISTANT
# =========================================================

with tab1:

    st.subheader("Ask SpendWise")

    st.caption(
        "Try: 'Show all my expenses', "
        "'Add a $25 food expense for today', "
        "'Update expense 3', or "
        "'Delete expense 7'."
    )

    # -----------------------------------------------------
    # Display Conversation
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # -----------------------------------------------------
    # Delete Confirmation
    # -----------------------------------------------------

    if st.session_state.pending_delete is not None:

        expense_id = st.session_state.pending_delete

        try:

            current_expenses = get_expenses()

            selected_expense = current_expenses[
                current_expenses["ExpenseID"] == expense_id
            ]

            if not selected_expense.empty:

                expense = selected_expense.iloc[0]

                expense_date = expense["ExpenseDate"]
                category = expense["Category"]
                description = expense["Description"]
                amount = expense["Amount"]
                payment_method = expense["PaymentMethod"]

                st.warning(
                    "⚠️ Please confirm this expense before deletion."
                )

                st.markdown(
                    f"""
                    <div class="delete-card">

                    <b>Expense ID:</b> {expense_id}<br><br>

                    <b>Date:</b> {expense_date}<br>

                    <b>Category:</b> {category}<br>

                    <b>Description:</b> {description}<br>

                    <b>Amount:</b> ${amount:,.2f}<br>

                    <b>Payment Method:</b> {payment_method}

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.error(
                    f"Expense ID {expense_id} was not found."
                )

        except Exception as error:

            st.error(
                f"Unable to load expense details: {error}"
            )

        col_confirm, col_cancel = st.columns(2)

        # -------------------------------------------------
        # Confirm Delete
        # -------------------------------------------------

        with col_confirm:

            if st.button(
                "✅ Confirm Delete",
                type="primary",
                use_container_width=True
            ):

                try:

                    tool_result = delete_expense(
                        expense_id
                    )

                    tool_outputs = [
                        {
                            "type":
                                "function_call_output",

                            "call_id":
                                st.session_state
                                .pending_delete_call_id,

                            "output":
                                str(tool_result)
                        }
                    ]

                    response = client.responses.create(
                        model=MODEL_NAME,
                        input=tool_outputs,

                        previous_response_id=
                            st.session_state
                            .pending_delete_response_id,

                        tools=mytools
                    )

                    st.session_state.response_id = (
                        response.id
                    )

                    final_response = (
                        response.output_text
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content":
                                final_response
                        }
                    )

                    # Clear pending delete state
                    st.session_state.pending_delete = None
                    st.session_state.pending_delete_call_id = None
                    st.session_state.pending_delete_response_id = None

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Delete failed: {error}"
                    )

        # -------------------------------------------------
        # Cancel Delete
        # -------------------------------------------------

        with col_cancel:

            if st.button(
                "❌ Cancel",
                use_container_width=True
            ):

                try:

                    tool_outputs = [
                        {
                            "type":
                                "function_call_output",

                            "call_id":
                                st.session_state
                                .pending_delete_call_id,

                            "output":
                                "Deletion cancelled by the user."
                        }
                    ]

                    response = client.responses.create(
                        model=MODEL_NAME,
                        input=tool_outputs,

                        previous_response_id=
                            st.session_state
                            .pending_delete_response_id,

                        tools=mytools
                    )

                    st.session_state.response_id = (
                        response.id
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content":
                                "Deletion cancelled. "
                                "No expense was removed."
                        }
                    )

                    # Clear pending delete state
                    st.session_state.pending_delete = None
                    st.session_state.pending_delete_call_id = None
                    st.session_state.pending_delete_response_id = None

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Cancel failed: {error}"
                    )

    # -----------------------------------------------------
    # Chat Input
    # -----------------------------------------------------

    user_input = st.chat_input(
        "Ask something about your expenses..."
    )

    if user_input:

        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        try:

            # -------------------------------------------------
            # Initial Model Call
            # -------------------------------------------------

            response = client.responses.create(
                model=MODEL_NAME,
                input=user_input,

                previous_response_id=
                    st.session_state.response_id,

                tools=mytools
            )

            st.session_state.response_id = (
                response.id
            )

            # -------------------------------------------------
            # Tool Calling Loop
            # -------------------------------------------------

            while True:

                tool_outputs = []

                for item in response.output:

                    if item.type == "function_call":

                        tool_name = item.name

                        tool_args = json.loads(
                            item.arguments
                        )

                        # -------------------------------------
                        # DELETE -> WAIT FOR USER CONFIRMATION
                        # -------------------------------------

                        if tool_name == "delete_expense":

                            st.session_state.pending_delete = (
                                tool_args["expense_id"]
                            )

                            st.session_state.pending_delete_call_id = (
                                item.call_id
                            )

                            st.session_state.pending_delete_response_id = (
                                response.id
                            )

                            break

                        # -------------------------------------
                        # Other Tools Execute Normally
                        # -------------------------------------

                        calling_function = (
                            tool_mapping.get(
                                tool_name
                            )
                        )

                        if calling_function is None:

                            raise ValueError(
                                f"Unknown tool: "
                                f"{tool_name}"
                            )

                        tool_result = (
                            calling_function(
                                **tool_args
                            )
                        )

                        # DataFrame conversion
                        if isinstance(
                            tool_result,
                            pd.DataFrame
                        ):

                            tool_result_text = (
                                tool_result
                                .to_string(
                                    index=False
                                )
                            )

                        else:

                            tool_result_text = (
                                str(tool_result)
                            )

                        tool_outputs.append(
                            {
                                "type":
                                    "function_call_output",

                                "call_id":
                                    item.call_id,

                                "output":
                                    tool_result_text
                            }
                        )

                # ---------------------------------------------
                # Waiting for delete confirmation
                # ---------------------------------------------

                if (
                    st.session_state.pending_delete
                    is not None
                ):
                    break

                # ---------------------------------------------
                # No more tool calls
                # ---------------------------------------------

                if not tool_outputs:
                    break

                # ---------------------------------------------
                # Send Tool Results Back
                # ---------------------------------------------

                response = client.responses.create(
                    model=MODEL_NAME,
                    input=tool_outputs,

                    previous_response_id=
                        st.session_state.response_id,

                    tools=mytools
                )

                st.session_state.response_id = (
                    response.id
                )

            # -------------------------------------------------
            # Waiting for Delete Confirmation
            # -------------------------------------------------

            if (
                st.session_state.pending_delete
                is not None
            ):

                st.session_state.messages.append(
                    {
                        "role": "assistant",

                        "content":
                            f"Please confirm deletion "
                            f"of Expense ID "
                            f"{st.session_state.pending_delete}."
                    }
                )

                st.rerun()

            # -------------------------------------------------
            # Final Response
            # -------------------------------------------------

            final_response = (
                response.output_text
            )

            with st.chat_message("assistant"):
                st.markdown(final_response)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": final_response
                }
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Request failed: {error}"
            )

# =========================================================
# TAB 2 - EXPENSE HISTORY
# =========================================================

with tab2:

    st.subheader("Expense History")

    if expenses_df.empty:

        st.info(
            "No expenses found."
        )

    else:

        st.dataframe(
            expenses_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"{len(expenses_df):,} expense records"
        )

# =========================================================
# TAB 3 - INSIGHTS
# =========================================================

with tab3:

    st.subheader("Expense Insights")

    if expenses_df.empty:

        st.info(
            "Add expenses to see insights."
        )

    else:

        # -------------------------------------------------
        # Spending by Category
        # -------------------------------------------------

        category_summary = (
            expenses_df
            .groupby("Category")["Amount"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        st.markdown(
            "### Spending by Category"
        )

        st.bar_chart(
            category_summary
        )

        # -------------------------------------------------
        # Spending by Payment Method
        # -------------------------------------------------

        payment_summary = (
            expenses_df
            .groupby(
                "PaymentMethod"
            )["Amount"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        st.markdown(
            "### Spending by Payment Method"
        )

        st.bar_chart(
            payment_summary
        )

        # -------------------------------------------------
        # Recent Expenses
        # -------------------------------------------------

        st.markdown(
            "### Recent Expenses"
        )

        recent_expenses = (
            expenses_df
            .sort_values(
                "ExpenseDate",
                ascending=False
            )
            .head(5)
        )

        st.dataframe(
            recent_expenses,
            use_container_width=True,
            hide_index=True
        )

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("💰 SpendWise")

    st.caption(
        "AI-powered Expense Tracker"
    )

    st.divider()

    st.markdown(
        """
        **Example Prompts**

        • Show all my expenses

        • How much did I spend?

        • Add a $30 grocery expense today

        • Update expense 5

        • Delete expense 10

        • Show my highest expense
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.response_id = None

        st.session_state.pending_delete = None

        st.session_state.pending_delete_call_id = None

        st.session_state.pending_delete_response_id = None

        st.rerun()