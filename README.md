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
