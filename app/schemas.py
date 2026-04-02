from pydantic import BaseModel
from datetime import datetime

class URLCreate(BaseModel):
    original: str


class URLResponse(BaseModel):
    original: str
    slug: str
    clicks: int
    created_at: datetime

    class Config: 
        from_attributes = True


class URLStats(BaseModel):
    original: str
    slug: str
    clicks: int
    created_at: datetime
    last_clicked: datetime | None = None
        