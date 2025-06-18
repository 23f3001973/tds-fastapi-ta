from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme for Bearer token
security = HTTPBearer()

# Dummy token verifier (accept any token)
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=403, detail="Invalid token")
    return token

# Request schema expected by Promptfoo
class QueryRequest(BaseModel):
    prompt: str

# Main POST API endpoint
@app.post("/api/", dependencies=[Depends(verify_token)])
async def answer_query(request: QueryRequest):
    prompt = request.prompt

    # Example response logic (replace with your actual logic)
    if "capital" in prompt.lower():
        return {"output": "The capital of France is Paris."}
    elif "hello" in prompt.lower():
        return {"output": "Hi there!"}
    else:
        return {"output": f"I received your prompt: {prompt}"}