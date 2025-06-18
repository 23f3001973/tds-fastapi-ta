from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load CSVs
discourse_df = pd.read_csv("discourse_data.csv")
tds_df = pd.read_csv("tds_timetable_2025.csv")

class Question(BaseModel):
    question: str
    attachments: list = []

@app.post("/api/")
def answer_query(payload: Question):
    q = payload.question.lower()

    # forum search
    forum = discourse_df[
        discourse_df.apply(
            lambda row: any(q in str(row[col]).lower() for col in ['title','excerpt'] if pd.notna(row[col])),
            axis=1
        )
    ]
    if not forum.empty:
        best = forum.iloc[0]
        return {
            "answer": best.get('excerpt', best.get('title','')),
            "source": "Forum Discussion",
            "title": best.get('title',''),
            "links": [{"url": best.get('slug','#'), "text":"See discussion"}]
        }

    # timetable search
    tt = tds_df[
        tds_df.apply(
            lambda row: any(q in str(row[col]).lower() for col in tds_df.columns if pd.notna(row[col])),
            axis=1
        )
    ]
    if not tt.empty:
        b = tt.iloc[0]
        return {
            "answer": f"{b['title']} by {b['instructor']} at {b['slot']} in {b['venue']}",
            "source": "Timetable",
            "title": b['title'],
            "links": []
        }

    return {
        "answer": "Sorry, nothing found.",
        "source": "No matches",
        "title": "No Results",
        "links": []
    }

@app.get("/", response_class=HTMLResponse)
def homepage():
    return """
    <h1>TDS Assistant API is Live</h1>
    <p>POST to /api/ with JSON {"question": "..."} to query.</p>
    """

@app.get("/docs")
def swagger_redirect():
    return HTMLResponse('<script>window.location="/docs"</script>')