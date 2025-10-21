Web RAG Engine — Asynchronous URL Ingestion, Vector Search, and Chat RAG

## Overview
This project implements a scalable, web‑aware RAG (Retrieval‑Augmented Generation) system with:
- Asynchronous URL ingestion via a Redis queue and a separate worker process
- Chunking and embedding of scraped content (MiniLM embeddings)
- Vector search in Pinecone with metadata in MongoDB
- Query API that retrieves top chunks and generates grounded answers via an LLM (Groq)
- Optional persistent chat session memory (MongoDB) to support multi‑turn context


## Architecture

High‑level data flow:

```
User → POST /ingest-url → FastAPI API → Redis Queue → Worker →
  Firecrawl (scrape) → Chunk (Markdown + Recursive) →
  Embeddings (MiniLM) → Pinecone (vectors) + MongoDB (chunks) → mark completed

User → POST /query → Query embedding → Pinecone search →
  MongoDB fetch chunks → Build prompt (+ chat history) → Groq LLM → Answer
```

```mermaid
flowchart TD
    %% User Interface
    U[👤 User]
    FE[🖥️ Streamlit Frontend]
    
    %% API Layer
    API[🚀 FastAPI API<br/>/routes]
    
    %% Queue System
    RQ[📋 Redis Queue<br/>url_processing_queue]
    
    %% Worker Process
    W[⚙️ Worker Process<br/>worker.py]
    
    %% Processing Pipeline
    SC[🕷️ Firecrawl Scraper<br/>Web Content Extraction]
    CH[✂️ Chunking Service<br/>Markdown + Recursive Splitter]
    EMB[🧠 Embeddings Service<br/>MiniLM (384d)]
    
    %% Storage Systems
    PC[🌲 Pinecone Vector DB<br/>web-rag-index]
    MG[(🗄️ MongoDB<br/>urls, chunks, chat_sessions)]
    
    %% LLM Service
    LLM[🤖 Groq LLM<br/>Llama 3.3 70B]
    
    %% URL Ingestion Flow
    U -->|1. POST /ingest-url| API
    FE <-->|HTTP Requests| API
    API -->|2. lpush job| RQ
    W -->|3. brpop job| RQ
    W -->|4. scrape| SC
    SC -->|5. markdown content| CH
    CH -->|6. text chunks| EMB
    CH -->|7. store chunks| MG
    EMB -->|8. upsert vectors| PC
    W -->|9. update job status| MG
    
    %% Query Flow
    U -->|10. POST /query| API
    API -->|11. embed query| EMB
    API -->|12. search similar| PC
    PC -->|13. return chunk IDs| API
    API -->|14. fetch full chunks| MG
    MG -->|15. return chunk content| API
    API -->|16. build prompt + chat history| LLM
    LLM -->|17. generate answer| API
    API -->|18. return response| U
    
    %% Styling
    classDef userClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef apiClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef queueClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef workerClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef storageClass fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef llmClass fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    
    class U,FE userClass
    class API apiClass
    class RQ queueClass
    class W,SC,CH,EMB workerClass
    class PC,MG storageClass
    class LLM llmClass
```

Clean architecture layering in the codebase:
- routes → controllers → usecases → services/repositories → config

## Design Choices & Justifications

### **1. Backend Framework – FastAPI**

- **Why:** Chosen for its modern async capabilities, built-in validation via Pydantic, and automatic documentation (Swagger UI).
- **Impact:** Enables clean, type-safe request/response models and non-blocking APIs

### **2. Task Queue – Redis Queue**

- **Why:** Used to decouple ingestion (API layer) from heavy processing (scraping, chunking, embedding).
- **Impact:** Enables asynchronous job execution and scalability. Worker can process URLs in parallel without blocking user requests.

### **3. Worker Architecture**

- **Why:** Implemented as a standalone process that continuously polls Redis for new jobs.
- **Impact:** Allows ingestion and processing to happen asynchronously while the API remains responsive.

### **4. Data Storage – MongoDB (Motor)**

- **Why:** Selected for its flexible schema, ideal for storing documents like chunks, embeddings metadata, and job statuses.
- **Impact:** Fully asynchronous with the `Motor` driver, ensuring consistency with the overall async design.

### **5. Web Scraping – Firecrawl**

- **Why:** Firecrawl provides reliable, clean Markdown output and handles website parsing complexity.
- **Impact:** Reduces implementation overhead and improves text quality for downstream chunking and embeddings.

### **6. Chunking Strategy**

- **Why:** Markdown-based chunking along with recursive text splitter captures semantic context using headers and sections, avoiding sentence-level fragmentation.
- **Impact:** Improves retrieval accuracy while keeping chunks small enough (~1000 chars) for efficient embedding and recall.

### **7. Embeddings Model – MiniLM (all-MiniLM-L6-v2, 384-dim)**

- **Why:** Lightweight, fast, open-source model with strong semantic performance for text-based content.
- **Impact:** Allows high-speed embedding generation without external paid dependencies (e.g., OpenAI, Cohere).

### **8. Vector Database – Pinecone**

- **Why:** Fully managed, serverless, and production-grade vector DB supporting cosine similarity.
- **Impact:** Simplifies infrastructure setup and scales automatically, removing the need for local FAISS or Chroma setup.

### **9. LLM for Querying**

- **Why:** Groq-hosted **Llama 3.3 70B** chosen for its open-source nature, fast inference, and free access.
- **Impact:** Allows cost-free, low-latency inference suitable for grounded RAG responses.

### **10. System Constraints & Docker Note**

- **Why:** While the architecture is designed for containerization, local Docker Desktop setup was avoided due to hardware limitations in my laptop as the system lags upon docker usage.
- **Impact:** The services can still be containerized easily with a simple `Dockerfile` and `docker-compose` if deployed to cloud or higher-spec local environments.

### **11. Scalability Considerations**

- API and worker layers are fully asynchronous
- Redis acts as a central message bus enabling distributed ingestion.
- Pinecone and MongoDB can scale independently based on load.

### **12. Memory Aware**

- **Memory-aware but stateless by design:** Implemented short-term chat memory (last 10 messages) to keep interactions contextually grounded without overengineering.


## Technology Stack
- Backend: Python 3.11, FastAPI, Uvicorn
- Queue: Redis (Redis Cloud)
- DBs: MongoDB (metadata, chat), Pinecone (vectors)
- Embeddings: sentence-transformers (MiniLM, 384‑dim)
- LLM: Groq
- Scraping: Firecrawl API
- Frontend: Streamlit


## Data Model & Schemas

### MongoDB Collections

#### 1) `urls` Collection
**Purpose:** Tracks URL ingestion jobs and their processing status
```jsonc
{
  "job_id": "uuid-string",                    // Unique job identifier
  "url": "https://example.com/article",      // Source URL being processed
  "status": "pending|processing|completed|failed",  // Current job status
  "submitted_at": "2024-01-15 14:30:25",    // Job submission timestamp (IST)
  "created_at": "2024-01-15 14:30:25"       // Job creation timestamp (IST)
}
```

#### 2) `chunks` Collection
**Purpose:** Stores text chunks with metadata for retrieval and context
```jsonc
{
  "chunk_id": "uuid-string",                 // Unique chunk identifier (matches Pinecone vector ID)
  "content": "Chunk text content...",        // Actual text content of the chunk
  "metadata": {
    "url": "https://example.com/article",    // Source URL
    "job_id": "uuid-string",                 // Associated job ID
    "chunk_index": 0,                        // Sequential chunk number
    "section_index": 0,                      // Section within document (from markdown headers)
    "sub_chunk_index": 0,                   // Sub-chunk index (if section was split further)
    "chunk_size": 856,                      // Character count of chunk
    "fallback": false,                      // Whether created by fallback chunking
    "header_1": "Main Title",               // H1 header context (if present)
    "header_2": "Section Title",            // H2 header context (if present)
    "header_3": "Subsection",               // H3 header context (if present)
    "header_4": "Sub-subsection"            // H4 header context (if present)
  }
}
```

#### 3) `chat_sessions` Collection
**Purpose:** Stores conversational context for multi-turn chat interactions
```jsonc
{
  "session_id": "uuid-string",              // Unique session identifier
  "messages": [                             // Array of conversation messages
    {
      "role": "user|assistant",             // Message sender role
      "content": "User question or AI response",  // Message text content
      "timestamp": "2024-01-15T14:30:25Z",  // Message creation time (UTC)
      "sources": [                          // Sources cited (assistant messages only)
        {
          "chunk_id": "uuid-string",
          "url": "https://example.com",
          "content": "Relevant text snippet...",
          "score": 0.91,
          "metadata": { /* chunk metadata */ }
        }
      ]
    }
  ],
  "created_at": "2024-01-15T14:30:25Z",     // Session creation time (UTC)
  "updated_at": "2024-01-15T14:35:42Z"     // Last message timestamp (UTC)
}
```

### Pinecone Vector Database

#### Index Configuration
- **Index Name:** `web-rag-index`
- **Dimension:** `384` (MiniLM embedding size)
- **Metric:** `cosine` (similarity measurement)
- **Environment:** `gcp-starter` (serverless)

#### Vector Schema
**Purpose:** Stores embeddings with minimal metadata for fast similarity search
```jsonc
{
  "id": "chunk_id-uuid",                    // Matches MongoDB chunk_id
  "values": [0.123, -0.456, 0.789, ...],   // 384-dimensional embedding vector
  "metadata": {
    "chunk_id": "chunk_id-uuid",           // Reference to MongoDB chunk
    "url": "https://example.com/article",   // Source URL for filtering
    "job_id": "job-uuid"                   // Job ID for batch operations
  }
}
```

### API Request/Response Schemas

#### URL Ingestion Request
```jsonc
{
  "url": "https://example.com/article"      // Valid HTTP/HTTPS URL (Pydantic HttpUrl validation)
}
```

#### URL Ingestion Response (HTTP 202)
```jsonc
{
  "job_id": "uuid-string",                 // Unique job identifier
  "status": "pending",                     // Initial job status
  "message": "URL queued for processing",  // Status message
  "submitted_at": "2024-01-15 14:30:25"   // Submission timestamp (IST)
}
```

#### Query Request
```jsonc
{
  "query": "What is machine learning?",     // User's question
  "session_id": "uuid-string",             // Optional: for conversation context
  "top_k": 5                              // Optional: number of chunks to retrieve (default: 5)
}
```

#### Query Response
```jsonc
{
  "answer": "Machine learning is...",       // LLM-generated response
  "sources": [                             // Retrieved source chunks
    {
      "chunk_id": "uuid-string",           // Chunk identifier
      "url": "https://example.com",        // Source URL
      "content": "Relevant text snippet...", // Chunk content preview
      "score": 0.91,                       // Similarity score (0-1)
      "metadata": { /* full chunk metadata */ }
    }
  ],
  "query": "What is machine learning?"     // Echo of original query
}
```


## APIs

### 1) Ingestion API — POST /api/v1/ingest-url
Queues a URL for background processing.

- Request
```
POST http://localhost:8000/api/v1/ingest-url
Content-Type: application/json

{
  "url": "https://example.com/article"
}
```

- Response (202 Accepted)
```
{
  "job_id": "<uuid>",
  "status": "pending",
  "message": "URL queued for processing",
  "submitted_at": "YYYY-MM-DD HH:MM:SS"
}
```

- curl
```
curl -X POST http://localhost:8000/api/v1/ingest-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}' -i
```

### 2) Query API — POST /api/v1/query
Embeds the user query, searches Pinecone, fetches chunk content from MongoDB, builds a prompt (with chat history), and generates an answer with Groq.

- Request
```
POST http://localhost:8000/api/v1/query
Content-Type: application/json

{
  "query": "What is Pinecone?",
  "session_id": "<optional-uuid>",
  "top_k": 5
}
```

- Response (200 OK)
```
{
  "answer": "<grounded LLM answer>",
  "sources": [
    {
      "chunk_id": "...",
      "url": "...",
      "content": "...",
      "score": 0.91,
      "metadata": { /* chunk metadata */ }
    }
  ],
  "query": "What is Pinecone?"
}
```

- curl
```
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Pinecone?", "top_k": 5}'
```


## Setup & Installation

### Prerequisites
- Python 3.11+
- MongoDB (local or Atlas)
- Redis (Redis Cloud URL recommended)
- Pinecone API key + serverless environment
- Firecrawl API key
- Groq API key

### Environment Variables (.env)
Create a `.env` at repo root:
```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=web-rag-engine

# Redis
REDIS_URL=redis://<user>:<password>@<host>:<port>
REDIS_DB=0
REDIS_QUEUE_NAME=url_processing_queue

# Firecrawl
FIRECRAWL_API_URL=https://api.firecrawl.dev/v2/scrape
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=gcp-starter   # or appropriate serverless region
PINECONE_INDEX_NAME=web-rag-index

# Groq
GROQ_API_KEY=your_groq_api_key
```
### Install
```
python -m venv .venv
. .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run Services
1) Start API
```
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

2) Start Worker (separate terminal)
```
python worker.py
```

3) Start Frontend (separate terminal)
```
streamlit run frontend/app.py
```

Visit:
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:8501

## Demo Video 
Link for the video

## Folder Structure
```
backend/
  config/        # settings, db clients (Mongo, Redis)
  controllers/   # thin orchestrators for routes → usecases
  routes/        # FastAPI routers (URL ingest, Query)
  repositories/  # MongoDB access for urls/chunks/chat sessions
  services/      # infra services (HTTP client, queue)
  usecases/      # business logic (worker, chunking, embeddings, vectordb, query)
  prompts/       # LLM prompts
frontend/
  app.py         # Streamlit UI
worker.py        # Worker entrypoint
requirements.txt
README.md
```