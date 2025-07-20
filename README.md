# Legal RAG Chatbot

A Flask-based AI chatbot for answering questions about India’s Information Technology Act, 2000, with streaming responses powered by Google Gemini and Chroma vector search.

## Features

- **Retrieval-Augmented Generation (RAG)** on the IT Act PDF
- **Streaming chatbot UI** with a modern dark theme (DeepAI-inspired)
- **Google Gemini integration** for both embeddings and LLM
- **PDF document ingestion** and custom chunking for precise answers
- **Citations and professional legal tone**
- Live system status indicator and robust error handling


## Quickstart

### 1. Prerequisites

- Python 3.9+
- Google API key with Gemini access
- The file `data/it_act_2000_updated.pdf`


### 2. Setup

Clone/download the repository and ensure the directory structure:

```
your-project/
│
├── app.py
├── rag_engine.py
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   └── loading.html
├── static/
│   ├── style.css
│   └── script.js
└── data/
    └── it_act_2000_updated.pdf
```


### 3. Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```


### 4. Environment Variables

Create a `.env` file (not committed for security) with your API key:

```
GOOGLE_API_KEY=your-google-api-key-here
FLASK_SECRET_KEY=your-secret-key
```


### 5. Start the Application

```bash
python app.py
```

- By default, the server runs on: http://127.0.0.1:5000


## Usage

- Visit the homepage for a status/loading screen if the backend is processing the PDF.
- Once loaded, get a chat interface. Ask any legal question regarding the IT Act, 2000.
- Answers are streamed live. If a direct answer cannot be found, you will be informed accordingly.


## File Structure

| File | Purpose |
| :-- | :-- |
| `app.py` | Main Flask server, routes, streaming endpoints, system health/status checks |
| `rag_engine.py` | RAG initialization, PDF ingestion and chunking, vector store (Chroma) and LLM integration |
| `requirements.txt` | Python dependencies |
| `templates/` | Jinja2 HTML templates for UI and loading |
| `static/style.css` | Dark theme CSS |
| `static/script.js` | Front-end chat logic with streaming SSE support |
| `data/it_act_2000_updated.pdf` | The core legal document ingested for retrieval |

## Configuration \& Customization

- **PDF File**: Place the IT Act PDF as `data/it_act_2000_updated.pdf`.
- **Chunking**: Adjust parameters in `rag_engine.py` (`chunk_size`, `chunk_overlap`) for smarter splitting.
- **Model Version**: Change Gemini model (`gemini-1.5-flash-latest`) as desired.
- **Prompting**: Custom prompt logic for legal language is set in `rag_engine.py`.


## Common Errors

- **"PDF file not found"**: Ensure the PDF is present at `data/it_act_2000_updated.pdf`.
- **"GOOGLE_API_KEY not found"**: Ensure your key is in your environment or `.env`.
- **Vector DB stuck or slow**: First-run builds the Chroma DB; restart to reload existing vectors.



## Acknowledgments

- Built with [LangChain](https://python.langchain.com), [ChromaDB](https://docs.trychroma.com/), [Google Gemini](https://ai.google.dev/), and [Flask](https://flask.palletsprojects.com).



