from pydantic import BaseModel
from typing import List, Optional


class PaperResponse(BaseModel):
    id: str
    title: str
    authors: List[str]
    year: Optional[int] = None
    journal: Optional[str] = None
    abstract: Optional[str] = None
    
    class Config:
        from_attributes = True