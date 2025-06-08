# 🧠 AI Research Assistant Agent

An intelligent research assistant that processes PDFs, YouTube videos, and web articles, enabling natural language Q&A using LangChain, Groq LLM, and FAISS. Designed to help students, researchers, and professionals streamline the way they extract and interact with knowledge from diverse sources.

---

## 🚀 Features

- 📄 **PDF Processing** – Upload academic papers or books and make them searchable.
- 📺 **YouTube Transcript Analysis** – Extract and understand content from lecture or documentary videos.
- 🌐 **Web Page Scraping** – Summarize or question content from blogs, articles, or research websites.
- 🔍 **Semantic Q&A** – Ask questions across all processed sources using vector similarity and MMR-based retrieval.
- 🧩 **LangChain Agent** – Tools-based agent that decides *when* and *how* to use each tool for optimal answers.
- 💬 **Conversational Memory** – Keeps track of context for coherent multi-turn interactions.

---

## 📦 Tech Stack

| Technology               | Purpose                                      |
|--------------------------|----------------------------------------------|
| `LangChain`              | Agentic framework and tool orchestration     |
| `Groq LLM`               | Fast, powerful inference (LLaMA3)            |
| `FAISS`                  | Vector store for semantic retrieval          |
| `YouTubeTranscriptAPI`   | Fetches transcripts from videos              |
| `PyPDFLoader`            | Extracts and chunks PDF content              |
| `WebBaseLoader`          | Scrapes web content for processing           |
| `HuggingFaceEmbeddings`  | Embeds documents for similarity search       |
| `FastAPI`                | Backend API layer                            |
| `React.js`               | Frontend interface                           |

---

## 📁 Folder Structure

```
📦 ai-research-agent/
├── backend/
│   ├── main.py              # FastAPI backend
│   ├── agent.py             # Core agent logic (LangChain + tools)
│   ├── requirements.txt
├── frontend/
│   ├── src/
│   ├── App.jsx
│   └── ...
├── .env                     # API keys and configs
└── README.md
```

---

## 🛠️ How It Works

The assistant is powered by **LangChain’s Conversational Agent**, which uses tool-based reasoning to decide the best way to help the user. It can:

1. Detect YouTube links and process transcripts.
2. Accept PDF file paths and extract academic text.
3. Scrape web articles.
4. Answer questions using a semantic vector search from previously processed content.

---

## 🧪 Usage

1. Clone the repo:

```bash
git clone https://github.com/rohit0796/Reasearch-Asisstant-AI.git
cd Reasearch-Asisstant-AI
```

2. Set up environment variables in `.env`:

```env
GROQ_API_KEY=your_groq_api_key
```

3. Install backend dependencies:

```bash
pip install -r requirements.txt
```

4. Run backend:

```bash
uvicorn main:app --reload
```

5. Start the React frontend:

```bash
cd ../Frontend
npm install
npm run dev
```

6. Visit `http://localhost:5173` to start chatting with your AI research buddy!

---

## 🔐 Environment Variables

Create a `.env` file and add:

```env
GROQ_API_KEY=your_groq_key
```
---

## 👨‍💻 Author

**Rohit Kumar Sahu**  
🎓 M.Tech CSE @ NIT Durgapur  
🌐 [GitHub](https://github.com/rohit0796) • [LinkedIn](https://www.linkedin.com/in/rohit--sahu-/)

---

## 📜 License

MIT License – feel free to use, modify, and share.
