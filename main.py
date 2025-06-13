from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# Load your data files
discourse_df = pd.read_csv("discourse_data.csv")
tds_df = pd.read_csv("tds_timetable_2025.csv")

# Input model
class Question(BaseModel):
    question: str
    attachments: list = []

@app.post("/api/")
def answer_query(payload: Question):
    q = payload.question.lower()
    
    # Search in discourse data
    discourse_matches = discourse_df[
        discourse_df.apply(
            lambda row: any(q in str(row[col]).lower() for col in ['title', 'excerpt'] if pd.notna(row[col])), 
            axis=1
        )
    ]
    
    # Search in timetable data
    timetable_matches = tds_df[
        tds_df.apply(
            lambda row: any(q in str(row[col]).lower() for col in tds_df.columns if pd.notna(row[col])), 
            axis=1
        )
    ]
    
    # Return discourse results first
    if not discourse_matches.empty:
        best = discourse_matches.iloc[0]
        return {
            "answer": str(best.get('excerpt', best.get('title', 'No content available'))),
            "source": "Forum Discussion",
            "title": str(best.get('title', 'Untitled')),
            "links": [{"url": str(best.get('slug', '#')), "text": "See discussion"}]
        }
    
    # Return timetable results if no discourse matches
    elif not timetable_matches.empty:
        best = timetable_matches.iloc[0]
        return {
            "answer": f"Course: {best.get('title', 'N/A')} | Instructor: {best.get('instructor', 'N/A')} | Time: {best.get('slot', 'N/A')} | Venue: {best.get('venue', 'N/A')}",
            "source": "Timetable",
            "title": str(best.get('title', 'Course Information')),
            "links": []
        }
    
    else:
        return {
            "answer": "Sorry, I couldn't find anything relevant in the forum discussions or timetable.",
            "source": "No matches",
            "title": "No Results",
            "links": []
        }

@app.get("/")
def root():
    return {
        "message": "University Forum Search API",
        "data_loaded": True,
        "forum_posts": len(discourse_df),
        "timetable_entries": len(tds_df),
        "docs": "/docs"
    }
