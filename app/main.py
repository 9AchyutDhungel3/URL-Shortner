from datetime import datetime
import random
import string
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app import models
from app.schemas import URLCreate, URLResponse, URLStats
from app.database import engine, get_db
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address 
from slowapi.errors import RateLimitExceeded

models.Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def get_slug(length: int = 6) -> str :
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=6))

def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("https://", "http://")):
        return f"https://{url}"
    return url

@app.get("/")
def root():
    return {"message": "URL Shortener is running"}

@app.post("/shorten", response_model=URLResponse)
@limiter.limit("10/minute")
def shorten_url(request: Request, payload: URLCreate, db: Session = Depends(get_db)):
    while True:
        slug = get_slug()
        exists = db.query(models.URL).filter(models.URL.slug == slug).first()
        if not exists:
            break
        
    entry = models.URL(original = normalize_url(payload.original), slug=slug)

    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    return entry

@app.get("/stats/{slug}", response_model=URLStats)
@limiter.limit("30/minute")
def get_stats(request: Request, slug: str, db: Session = Depends(get_db)):
    entry = db.query(models.URL).filter(models.URL.slug==slug).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Page not found (custom error)")

    return entry

@app.get("/{slug}")
@limiter.limit("60/minute")
def redirect(request: Request, slug: str, db: Session = Depends(get_db)):
    entry = db.query(models.URL).filter(models.URL.slug==slug).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Page not found")
    
    entry.clicks += 1
    entry.last_clicked = datetime.utcnow()
    db.commit()

    return RedirectResponse(url=entry.original)