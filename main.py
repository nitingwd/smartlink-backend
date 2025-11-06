from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from database import SessionLocal, init_db
from models import URL
from schemas import URLRequest, URLResponse
from utils import get_unique_short_url

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/shorten", response_model=URLResponse)
def shorten_url(request: URLRequest):
    db = SessionLocal()
    try:
        short = request.customSlug or get_unique_short_url(db, URL)
        exists = db.query(URL).filter(URL.short_url == short).first()
        if exists:
            raise HTTPException(status_code=400, detail="Slug already taken")
        new_url = URL(original_url=request.originalUrl, short_url=short)
        db.add(new_url)
        db.commit()
        db.refresh(new_url)
        return {"shortUrl": f"http://localhost:8000/{new_url.short_url}"}
    finally:
        db.close()

@app.get("/{short}")
def redirect_to_original(short: str):
    db = SessionLocal()
    try:
        url_entry = db.query(URL).filter(URL.short_url == short).first()
        if url_entry:
            url_entry.clicks += 1
            db.commit()
            return RedirectResponse(url=url_entry.original_url)
        raise HTTPException(status_code=404, detail="Short URL not found")
    finally:
        db.close()
