from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# ✅ CORS: Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Bearer token auth for Promptfoo or security
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token or token.strip() == "":
        raise HTTPException(status_code=403, detail="Invalid token")
    return token

# ✅ Load CSV files
try:
    discourse_df = pd.read_csv("discourse_data.csv")
except FileNotFoundError:
    discourse_df = pd.DataFrame()

try:
    tds_df = pd.read_csv("tds_timetable_2025.csv")
except FileNotFoundError:
    tds_df = pd.DataFrame()

# ✅ Input model
class QueryRequest(BaseModel):
    prompt: str
    attachments: list = []

# ✅ Main API endpoint
@app.post("/api/", dependencies=[Depends(verify_token)])
def answer_query(request: QueryRequest):
    q = request.prompt.lower()

    # Search in forum/discourse
    discourse_matches = discourse_df[
        discourse_df.apply(
            lambda row: any(q in str(row[col]).lower() for col in ['title', 'excerpt'] if pd.notna(row[col])),
            axis=1
        )
    ]

    if not discourse_matches.empty:
        best = discourse_matches.iloc[0]
        return {
            "answer": str(best.get('excerpt', best.get('title', 'No content available'))),
            "source": "Forum Discussion",
            "title": str(best.get('title', 'Untitled')),
            "links": [{"url": str(best.get('slug', '#')), "text": "See discussion"}]
        }

    # Search in timetable
    timetable_matches = tds_df[
        tds_df.apply(
            lambda row: any(q in str(row[col]).lower() for col in tds_df.columns if pd.notna(row[col])),
            axis=1
        )
    ]

    if not timetable_matches.empty:
        best = timetable_matches.iloc[0]
        return {
            "answer": f"Course: {best.get('title', 'N/A')} | Instructor: {best.get('instructor', 'N/A')} | Time: {best.get('slot', 'N/A')} | Venue: {best.get('venue', 'N/A')}",
            "source": "Timetable",
            "title": str(best.get('title', 'Course Information')),
            "links": []
        }

    return {
        "answer": "Sorry, I couldn't find anything relevant in the forum discussions or timetable.",
        "source": "No matches",
        "title": "No Results",
        "links": []
    }

# ✅ API metadata root
@app.get("/")
def root():
    return {
        "message": "University Forum Search API",
        "data_loaded": True,
        "forum_posts": len(discourse_df),
        "timetable_entries": len(tds_df),
        "docs": "/docs"
    }

# ✅ Browser homepage
@app.get("/", response_class=HTMLResponse)
def homepage():
    return """
    <html>
      <head><title>TDS FastAPI TA</title></head>
      <body>
        <h1>TDS Assistant API is Live ✅</h1>
        <p>Use <code>POST /api/</code> with Bearer token.</p>
        <p>Visit <a href='/docs'>/docs</a> and click "Authorize" to test.</p>
      </body>
    </html>
    """