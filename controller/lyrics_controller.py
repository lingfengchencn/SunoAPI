from fastapi import APIRouter
from pydantic import BaseModel
from extentions.ext_app import app
from requests.exceptions import HTTPError

from request_model import GenLyricsRequest
from suno.exceptions import ServiceUnavailableException , TooManyRequestsException
router = APIRouter()


@router.post("/gen_lyrics")
async def gen_lyrics(request: GenLyricsRequest):
    # raise TooManyRequestsException("too many requests")
    # raise ServiceUnavailableException("service unavailable")
    client = app.state.suno
    try:
        lyrics_id = client.gen_lyrics(request.prompt)
        return {"lyrics_id": lyrics_id}
    except ServiceUnavailableException as ex:
        return {"error": ex.message}


@router.get("/get_lyrics/{lyrics_id}")
async def gen_lyrics(lyrics_id:str):
    client = app.state.suno
    try:
        lyrics = client.get_lyrics(lyrics_id)
        
    except HTTPError as e:
        # 如果为404 说明 id不存在
        if e.response.status_code == 404:
            return {"error": "lyrics id is invalid or expired"}
    return {"lyrics": lyrics.to_json()}