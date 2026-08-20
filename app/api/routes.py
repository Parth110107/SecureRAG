from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.rag.secure_pipeline import ask_secure_rag


router = APIRouter(
    prefix="/api",
    tags=["SecureRAG"]
)


class QueryRequest(BaseModel):

    username: str

    question: str


@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "SecureRAG"
    }


@router.post("/query")
def query_rag(request: QueryRequest):

    try:

        result = ask_secure_rag(
            username=request.username,
            question=request.question
        )

        return {
            "username": request.username,
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )