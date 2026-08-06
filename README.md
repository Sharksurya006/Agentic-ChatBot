<div align="center">

# 🤖 Agentic ChatBot

**A multi-tool, memory-aware AI agent built with LangGraph — not just a chatbot, a reasoning engine that plans, calls tools, and remembers.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Orchestration-1C3C3C?style=flat)](https://www.langchain.com/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Live Demo](#) · [Report Bug](../../issues) · [Request Feature](../../issues)

</div>

---

## 📌 Overview

**Agentic ChatBot** is a tool-using AI agent, not a wrapper around a chat API. It is built on **LangGraph's** stateful graph model so the LLM can decide, on its own, when to search the web, do math, check the weather, pull a stock quote, generate an image, answer questions from an uploaded PDF, or send an email — then loop back and keep reasoning until it has a real answer.

The project demonstrates end-to-end applied AI engineering: agent orchestration, tool calling, Retrieval-Augmented Generation (RAG), persistent conversation memory, and a production-style Streamlit front end — all containerized with Docker.

---

## ✨ Key Features

| Capability | Description |
|---|---|
| 🧠 **Agentic Reasoning** | Built on `LangGraph`'s `StateGraph`: the LLM decides when to call a tool vs. respond directly, via a `chat_node ↔ tools` conditional loop |
| 🔧 **Multi-Tool Agent** | Web search (Tavily), live weather (Open-Meteo), stock quotes (Alpha Vantage), a sandboxed calculator, AI image generation, email sending, and document Q&A — all exposed as LangChain tools |
| 📄 **RAG over your own PDFs** | Upload any PDF from the UI — it's chunked, embedded with Google Gemini embeddings, indexed in **FAISS**, and retrieved on demand so the agent can answer questions grounded in *your* documents |
| 💾 **Persistent Multi-Thread Memory** | Every conversation is checkpointed to SQLite via `langgraph-checkpoint-sqlite`, so users can start new chats, revisit old ones, and resume exactly where they left off — even after a restart |
| 📧 **Real-World Actions** | The agent can compose and send actual emails (with attachments, CC/BCC, HTML body, priority) as a first-class tool call, not just describe what it *would* send |
| 🖼️ **Multi-Modal Output** | Handles interleaved text + generated images in a single response, streamed live to the UI |
| ⚡ **Live Status Streaming** | The Streamlit UI streams token-by-token responses and shows real-time status ("🌐 Searching the web...", "📈 Fetching stock price...") while the agent works |
| 🐳 **Containerized** | Ships with a `Dockerfile` for one-command, reproducible deployment |

---

## 🏗️ Architecture

The core of the project is a LangGraph state machine: the LLM node either answers directly or emits a tool call, control passes to a `ToolNode`, and the result is routed back to the LLM — repeating until the model is satisfied with its answer.

```
                         ┌─────────────────────────┐
                         │        START             │
                         └────────────┬─────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │       chat_node          │
                         │  (Gemini LLM + tools)     │
                         └────────────┬─────────────┘
                                      │
                     tools_condition (router)
                          │                    │
                no tool call needed      tool call requested
                          │                    │
                          ▼                    ▼
                       ┌─────┐          ┌──────────────┐
                       │ END │          │  tools node   │
                       └─────┘          │ (ToolNode)    │
                                        └──────┬────────┘
                                               │
                                               ▼
                                   loops back to chat_node
```

**Tool belt available to the agent:**

```
web_search_tool     → Tavily live web search
get_weather_update  → Open-Meteo geocoding + forecast API
stock_update         → Alpha Vantage live quotes
calculator_tool      → sandboxed math evaluator
RAG_tool             → FAISS similarity search over uploaded PDFs
generate_image       → Pollinations AI text-to-image
send_email           → Gmail-based email dispatch
```

Every conversation thread is checkpointed with `SqliteSaver`, so state, tool outputs, and full message history persist per `thread_id` across sessions.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Agent Orchestration** | LangGraph (`StateGraph`, `ToolNode`, conditional routing) |
| **LLMs** | Google Gemini (primary), Groq / Llama 3.3 70B (configurable) |
| **RAG / Vector Store** | FAISS + Google Generative AI Embeddings + `PyPDFLoader` |
| **Tools & Integrations** | Tavily Search, Open-Meteo, Alpha Vantage, Pollinations AI, Gmail API |
| **Persistence** | SQLite via `langgraph-checkpoint-sqlite` |
| **Frontend** | Streamlit (chat UI, sidebar thread history, file upload) |
| **Deployment** | Docker |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- API keys for: Google AI Studio (Gemini), Groq, Tavily, Alpha Vantage, and Gmail OAuth credentials (for the email tool)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Sharksurya006/Agentic-ChatBot.git
cd Agentic-ChatBot

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env          # then fill in your keys
```

Create a `.env` file with:

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key   # optional
```

### Run locally

```bash
streamlit run frontend.py
```

The app will be available at `http://localhost:8501`.

### Run with Docker

```bash
docker build -t agentic-chatbot .
docker run -p 8501:8501 --env-file .env agentic-chatbot
```

---

## 📂 Project Structure

```
Agentic-ChatBot/
├── frontend.py       # Streamlit UI — chat, sidebar, thread history, file upload, live streaming
├── backend.py         # LangGraph agent definition — nodes, tool bindings, checkpointing
├── tools.py            # Weather, calculator, RAG, and stock-price tool implementations
├── rag_tool.py         # PDF ingestion + FAISS vector store retrieval for RAG
├── email_tool.py       # Gmail-based email sending tool
├── prompt.py            # System prompt driving agent behavior
├── Dockerfile           # Container build definition
├── requirements.txt      # Python dependencies
└── pyproject.toml         # Project metadata / uv package management
```

---

## 🗺️ Roadmap

- [ ] Swap hard-coded API keys for fully environment-driven config across all tools
- [ ] Add automated tests for tool routing and RAG retrieval accuracy
- [ ] Support multi-document RAG collections instead of a single FAISS index
- [ ] Add authentication for multi-user deployments
- [ ] CI/CD pipeline for automated Docker builds

---

## 🙋 About the Developer

Built by **Surya S** — M.Tech in Computer Science (Information Security) from NIT Calicut, with prior software development experience at SAP Labs. Focused on full-stack, backend, and AI/LLM systems engineering.

- 🌐 Portfolio: [surya-portfolio-iota.vercel.app](https://surya-portfolio-iota.vercel.app)
- 💻 GitHub: [@Sharksurya006](https://github.com/Sharksurya006)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

<div align="center">

⭐ If you find this project interesting, consider giving it a star!

</div>