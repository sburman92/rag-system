# Code RAG System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- **Ollama** installed and running (https://ollama.ai)
- **Python 3.10+**
- **Node.js 18+**

### Step 1: Start Ollama
```bash
ollama serve
```
Then in another terminal:
```bash
ollama pull mistral
```

### Step 2: Setup Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Start Backend Server
```bash
python -m uvicorn app.main:app --reload
# API runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Step 4: Setup Frontend
```bash
cd frontend
npm install
npm start
# Frontend runs at http://localhost:4200
```

### Step 5: Use the System

1. **Index a Repository**
   - Go to "Index Repository" tab
   - Paste GitHub URL: `https://github.com/angular/angular`
   - Click "Start Indexing"
   - Wait for completion (2-10 minutes depending on repo size)

2. **Ask Questions**
   - Go to "Chat" tab
   - Ask: "How does routing work?"
   - Get AI-powered answer with code references

## 📚 Example Repositories to Try

- Small: https://github.com/lodash/lodash
- Medium: https://github.com/angular/angular
- Large: https://github.com/torvalds/linux (very large)

## 🔧 Common Issues

**"Cannot connect to Ollama"**
- Ensure Ollama is running: `ollama serve`
- Check localhost:11434

**"No chunks indexed"**
- Check if repository was successfully indexed
- View stats in "Index Repository" tab

**"Slow responses"**
- Wait for Ollama to complete processing
- Larger models take longer
- Check system resources

## 📖 Full Documentation

See [README.md](./README.md) for complete documentation.
