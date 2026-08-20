from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from app.ingestion.document_service import ingest_document
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from app.security.auth import authenticate_user, security
from app.security.auth import create_access_token, get_current_username
import shutil
import os

from app.ingestion.loader import extract_pages_from_pdf
from app.rag.secure_pipeline import ask_secure_rag


app = FastAPI(
    title="SecureRAG",
    description="Permission-aware enterprise RAG system",
    version="1.0.0"
)


# ==================================================
# ROOT
# ==================================================

@app.get("/")
def home():

    return {
        "message": "SecureRAG API is running"
    }


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/api/health")
def health_check():

    return {
        "status": "healthy",
        "service": "SecureRAG"
    }


# ==================================================
# QUERY MODEL
# ==================================================

class QueryRequest(BaseModel):

    question: str

# ==================================================
# RAG QUERY
# ==================================================

@app.post("/api/query")
def query_rag(
    request: QueryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    username = get_current_username(
        credentials
    )

    try:

        result = ask_secure_rag(
            username=username,
            question=request.question
        )

        return {
            "username": username,
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
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


# ==================================================
# DOCUMENT UPLOAD
# ==================================================
@app.post("/documents/upload")
async def upload_document(
    classification: str,
    allowed_roles: str,
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    username = get_current_username(
        credentials
    )

    try:

        # ------------------------------------------
        # CREATE STORAGE DIRECTORY
        # ------------------------------------------

        os.makedirs(
            "data/documents",
            exist_ok=True
        )

        # ------------------------------------------
        # SAVE PDF
        # ------------------------------------------

        file_path = os.path.join(
            "data/documents",
            file.filename
        )

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # ------------------------------------------
        # PARSE ROLES
        # ------------------------------------------

        roles = [
            role.strip()
            for role in allowed_roles.split(",")
            if role.strip()
        ]

        if not roles:

            raise HTTPException(
                status_code=400,
                detail="At least one allowed role is required."
            )

        # ------------------------------------------
        # INGEST DOCUMENT
        # ------------------------------------------

        result = ingest_document(
            username=username,
            document_name=file.filename,
            file_path=file_path,
            classification=classification,
            allowed_roles=roles
        )

        return {
            "message": "Document uploaded and indexed successfully.",
            "document_id": result["document_id"],
            "filename": file.filename,
            "chunks": result["chunks_created"],
            "uploaded_by": username,
            "classification": classification,
            "allowed_roles": roles
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
@app.post("/api/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    username = authenticate_user(
        form_data.username,
        form_data.password
    )

    if username is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        username
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }