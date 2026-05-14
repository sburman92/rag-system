# Code RAG System

A local Retrieval-Augmented Generation app for indexing GitHub repositories and asking questions about the code. The backend is built with FastAPI, Chroma, LangChain, and Ollama. The frontend is built with Angular.

## Features

- Index a GitHub repository by URL
- Split source files into searchable chunks
- Generate local embeddings through Ollama
- Store embeddings in a local Chroma database
- Ask questions about the indexed codebase
- View source file references in answers

## Tech Stack

- Backend: Python, FastAPI, LangChain, Chroma, PyGithub
- Frontend: Angular
- Local AI runtime: Ollama
- Vector store: local Chroma DB

## Prerequisites

- Python 3.9+
- Node.js and npm
- Docker Desktop, if running Ollama in Docker
- A GitHub personal access token with repository `Contents: Read-only`

## Local Ports

| Service | URL |
| --- | --- |
| FastAPI backend | `http://localhost:8000` |
| Angular frontend | `http://localhost:4200` |
| Ollama | `http://localhost:11434` |

## Docker Desktop Setup

You can run the backend, frontend, and Ollama together with Docker Compose.

First make sure `backend/.env` exists and contains your real GitHub token:

```bash
cp backend/.env.example backend/.env
```

Start everything from the `rag-system` folder:

```bash
docker compose up --build
```

Open the app:

```txt
http://localhost:4200
```

The API is available at:

```txt
http://localhost:8000
```

The Compose setup stores Chroma data and Ollama models in Docker volumes, so they survive container restarts.

Pull the Ollama model once after the containers are running:

```bash
docker compose exec ollama ollama pull llama3.2
```

If your `backend/.env` uses a different model name, pull that model instead.

Stop the containers:

```bash
docker compose down
```

Remove containers and stored Chroma/Ollama data:

```bash
docker compose down -v
```

## Backend Setup

From the repo root:

```bash
cd backend
python3 -m venv ../../.venv
source ../../.venv/bin/activate
python3 -m pip install -r requirements.txt
```

Create a real environment file from the example:

```bash
cp .env.example .env
```

Update `backend/.env`:

```env
GITHUB_TOKEN=your_real_github_token_here
GITHUB_REPO_URL=https://github.com/username/repo
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
CHROMA_DB_PATH=./chroma_db
API_PORT=8000
ANONYMIZED_TELEMETRY=False
```

Do not commit `backend/.env`. It contains secrets.

Start the backend:

```bash
uvicorn app.main:app --reload
```

Open the API docs:

```txt
http://localhost:8000/docs
```

## Ollama With Docker

Pull and run the Ollama server image:

```bash
docker pull ollama/ollama
docker run -d --name ollama -p 11434:11434 -v ollama:/root/.ollama ollama/ollama
```

Pull a small local model:

```bash
docker exec -it ollama ollama pull llama3.2:1b
```

Check installed models:

```bash
docker exec -it ollama ollama list
```

Check that Ollama is reachable from the host:

```bash
curl http://localhost:11434/api/tags
```

## Frontend Setup

From the repo root:

```bash
cd frontend
npm install
npm start
```

Open:

```txt
http://localhost:4200
```

The Angular app calls the backend at `http://localhost:8000`.

## API Examples

Health check:

```bash
curl http://localhost:8000/health
```

Index a repository:

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/username/repo"}'
```

Ask a question:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What does this project do?","top_k":5}'
```

Clear the vector store:

```bash
curl -X POST http://localhost:8000/clear
```

## Re-Indexing Note

The current implementation adds documents to the same Chroma collection. If you index the same repository multiple times, duplicate chunks can be stored.

For now, clear the vector store before re-indexing:

```bash
curl -X POST http://localhost:8000/clear
```

Then call `POST /index` again.

## GitHub Token Permissions

For a fine-grained GitHub token, select the repository you want to index and grant:

- `Contents: Read-only`
- `Metadata: Read-only`

Metadata alone is not enough to read repository files.

## Project Structure

```txt
rag-system/
├── backend/
│   ├── app/
│   │   ├── modules/
│   │   │   ├── chunker.py
│   │   │   ├── embeddings.py
│   │   │   ├── github_reader.py
│   │   │   ├── llm.py
│   │   │   └── vector_store.py
│   │   ├── config.py
│   │   └── main.py
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── angular.json
│   └── package.json
├── .github/
│   └── CODEOWNERS
├── .gitignore
└── README.md
```

## Troubleshooting

If FastAPI cannot connect to Ollama, confirm Docker is running and check:

```bash
curl http://localhost:11434/api/tags
```

If GitHub returns unauthorized, verify that `backend/.env` contains a real token and restart FastAPI.

If Chroma logs telemetry errors, set:

```env
ANONYMIZED_TELEMETRY=False
```

If Angular fails to start, install dependencies again:

```bash
cd frontend
npm install
npm start
```
