from pydantic import BaseModel

class URLRequest(BaseModel):
    originalUrl: str
    customSlug: str | None = None

class URLResponse(BaseModel):
    shortUrl: str
