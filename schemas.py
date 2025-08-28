# schemas.py

from pydantic import BaseModel

class TTSRequest(BaseModel):
    text: str
    voiceId: str = "en-US-natalie"