# Data & AI Projects

A hands-on portfolio of **Data Engineering + Generative AI** projects built with Python, OpenAI, SQL Server, ChromaDB, Streamlit, and Azure-oriented data engineering patterns.

This repository showcases practical implementations of:

- Retrieval-Augmented Generation (RAG)
- AI Agents with Tool / Function Calling
- Natural Language to SQL
- RAG Optimization with Hybrid Search and Re-Ranking
- RAG Evaluation
- Conversational AI
- Streamlit-based AI applications

> **Note:** All documents and sample data used in this repository are dummy / non-production examples created for learning and demonstration purposes. No confidential company data, credentials, or proprietary production datasets are included.

---

## Projects

### 1. Enterprise RAG Knowledge Assistant

A conversational RAG application that answers questions from company policy and glossary documents using retrieved context instead of relying only on the LLM's general knowledge.

**Flow**

```text
Documents
   ↓
Text Extraction
   ↓
Recursive Chunking
   ↓
Embeddings
   ↓
Vector Database
   ↓
Semantic / Hybrid Retrieval
   ↓
Re-Ranking
   ↓
LLM
   ↓
Conversational Response
```

**Key capabilities**

- PDF document ingestion
- Recursive text chunking
- Metadata creation
- Embedding generation
- ChromaDB vector storage
- Semantic similarity search
- Conversational history
- Grounded LLM responses
- Hybrid Search
- Re-Ranking
- RAG evaluation
- Streamlit chatbot UI
- New Chat and Recent Chats experience

**RAG evaluation metrics explored**

- Recall
- Contextual Precision
- Contextual Relevance
- Faithfulness
- Answer Relevancy

---

### 2. AI Agent with Tool / Function Calling

An AI-agent implementation where the LLM can select and invoke approved backend Python functions instead of directly performing uncontrolled operations.

**Conceptual flow**

```text
User Request
    ↓
LLM
    ↓
Tool Selection
    ↓
Function Arguments
    ↓
Python Function
    ↓
Backend / Database Operation
    ↓
Tool Result
    ↓
LLM Final Response
```

**Key capabilities**

- OpenAI tool / function calling
- JSON argument handling
- Dynamic tool mapping
- Multi-step tool execution
- Controlled backend actions
- Human-in-the-loop patterns for sensitive operations
- Conversational continuity using response IDs

This pattern can be extended to Data Quality workflows, CRUD applications, operational support, and enterprise automation.

---

### 3. QueryPilot - Natural Language to SQL

A conversational assistant that converts natural-language business questions into SQL and executes them against SQL Server.

**Key capabilities**

- Natural language → SQL
- Schema-grounded prompting
- SQL Server integration
- Query execution
- Conversational results
- Streamlit chat interface

**Example**

```text
User:
Show me the top 5 products by sales.

        ↓

LLM generates schema-aware SQL

        ↓

SQL Server executes query

        ↓

Results returned conversationally
```

---

### 4. AI Expense Tracker

A conversational CRUD application built using OpenAI tool calling, Python, SQL Server, and Streamlit.

**Supported operations**

- View expenses
- Add expenses
- Update expenses
- Delete expenses
- Human confirmation before destructive actions
- Dashboard and category-level insights

---

## Technology Stack

### AI / Generative AI

- OpenAI API
- Large Language Models
- Retrieval-Augmented Generation (RAG)
- AI Agents
- Tool / Function Calling
- Embeddings
- Vector Search
- Hybrid Search
- Re-Ranking
- RAG Evaluation

### Data Engineering

- Python
- SQL
- PySpark
- Azure Data Factory
- Azure Databricks
- Azure SQL
- Azure Synapse Analytics
- ADLS Gen2
- Microsoft Fabric
- Delta Lake

### Application / Storage

- Streamlit
- SQL Server
- ChromaDB
- SQLite
- Git / GitHub

---

## Repository Structure

The exact file structure may evolve as projects are added, but the repository currently contains components such as:

```text
Data_AI_Projects/
│
├── chunking.py
├── ingestion.py
├── retreival.py
├── streamlit_RAG.py
├── main_toolcalling.py
├── tools.py
├── sqlDB.py
├── webtools.py
├── streamlit_app.py
├── streamlit_expense_app.py
├── docs/
├── .gitignore
└── README.md
```

---

## RAG Components

### Chunking

Documents are extracted and split using recursive chunking.

Typical flow:

```text
PDF
 ↓
Extract Text
 ↓
RecursiveCharacterTextSplitter
 ↓
Chunks + Metadata + IDs
```

### Embeddings

Chunks are converted into numerical vector representations using an embedding model.

```text
Chunk
  ↓
Embedding Model
  ↓
Vector
```

### Vector Retrieval

The user question is embedded and compared with stored document vectors.

```text
User Question
      ↓
Query Embedding
      ↓
Vector Search
      ↓
Top-K Relevant Chunks
```

### Grounded Generation

Only the retrieved context is provided to the LLM for generating the final answer.

This reduces hallucination and keeps responses grounded in the indexed knowledge base.

---

## RAG Optimization

The baseline semantic-search RAG pipeline was extended with:

### Hybrid Search

Combines semantic/vector retrieval with keyword-based retrieval to improve coverage for both semantic concepts and exact terms.

### Re-Ranking

Retrieves a broader candidate set first, then reorders the results based on their relevance to the user question before sending the strongest context to the LLM.

```text
Query
  ↓
Retrieve Candidate Chunks
  ↓
Re-Ranker
  ↓
Best Context
  ↓
LLM
```

---

## RAG Evaluation

Evaluation is used to measure both retrieval quality and generation quality.

**Retrieval-focused metrics**

- Recall
- Contextual Precision
- Contextual Relevance

**Generation-focused metrics**

- Faithfulness
- Answer Relevancy

This makes it possible to compare baseline RAG with optimized retrieval approaches such as Hybrid Search and Re-Ranking.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/pc65571/Data_AI_Projects.git
cd Data_AI_Projects
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file locally:

```text
OPENAI_API_KEY=your_openai_api_key
```

Do not commit `.env` to GitHub.

### 6. Run ingestion

```bash
python ingestion.py
```

### 7. Run the RAG application

```bash
streamlit run streamlit_RAG.py
```

---

## Security

The repository intentionally excludes local and sensitive artifacts through `.gitignore`, including:

```text
.env
.venv/
venv/
__pycache__/
*.pyc
chroma_db/
*.db
.vscode/
```

Never commit:

- API keys
- passwords
- database credentials
- private connection strings
- internal company URLs
- confidential documents
- production datasets

---

## Future Enhancements

Potential next steps include:

- Azure AI Search integration
- Metadata filtering
- Query rewriting for conversational RAG
- Automated evaluation pipelines
- RAG observability
- Agent orchestration
- Role-based access control
- Azure-hosted deployment
- Microsoft Teams integration
- Production-grade monitoring and logging

---

## About

This repository represents hands-on work at the intersection of **Data Engineering and Applied AI**.

The goal is to combine strong enterprise data engineering foundations with modern AI patterns such as RAG, AI Agents, Tool Calling, Natural Language to SQL, and RAG evaluation.

---

## Author

**Pramod Kumar Chintalapati**  
Senior Data Engineer + AI Engineer

- LinkedIn: https://www.linkedin.com/in/pramod-kumar-chintalapati-b6440319a/
- GitHub: https://github.com/pc65571
