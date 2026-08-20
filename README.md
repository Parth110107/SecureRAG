RAG Pipeline

User Question
      ↓
JWT Authentication
      ↓
Organization & Role Authorization
      ↓
Authorized Document Filtering
      ↓
Vector Similarity Search
      ↓
Similarity Threshold
      ↓
Relevant Context
      ↓
Llama 3.2 3B
      ↓
Grounded Answer
      ↓
Verified Source Metadata


| Metric               | Current Implementation |
| -------------------- | ---------------------: |
| User roles           |                      3 |
| Demo users           |                      3 |
| Organizations        |    1 test organization |
| Embedding dimensions |                    384 |
| Similarity threshold |                   0.25 |
| LLM                  |           Llama 3.2 3B |
| Vector database      |  PostgreSQL + pgvector |
| API framework        |                FastAPI |
| Authentication       |                    JWT |
| Document access      |             Role-based |
| Audit logging        |            Implemented |


Tech Used :

Backend :
Python,
FastAPI,
Uvicorn,

AI / RAG:
Llama 3.2 3B,
Ollama,
Sentence Transformers,
all-MiniLM-L6-v2,

Database:
PostgreSQL,
pgvector,

Security:
JWT,
RBAC,
Document authorization,
Audit logging,
Password hashing,

Document Processing:
PDF extraction,
Recursive text splitting,
Vector embeddings,

Development:
Docker,
Docker Compose,
Git,
GitHub


PROJECT STRUCTURE:

SecureRAG/
│
├── app/
│   │
│   ├── api/
│   │
│   ├── generation/
│   │   └── llm.py
│   │
│   ├── ingestion/
│   │   ├── chunker.py
│   │   ├── document_service.py
│   │   ├── embedder.py
│   │   ├── enterprise_ingest.py
│   │   └── loader.py
│   │
│   ├── rag/
│   │   ├── pipeline.py
│   │   └── secure_pipeline.py
│   │
│   ├── retrieval/
│   │   ├── secure_search.py
│   │   └── citations.py
│   │
│   ├── security/
│   │   ├── auth.py
│   │   ├── authorization.py
│   │   ├── audit.py
│   │   └── setup_demo_users.py
│   │
│   ├── database.py
│   ├── main.py
│   └── setup_database.py
│
├── data/
├── docker-compose.yml
├── .gitignore
└── README.md
