
from fastapi import APIRouter
from pydantic import BaseModel
from extentions.ext_app import app
from requests.exceptions import HTTPError

from request_model import GenGPTMusicRequest, GenLyricsMusicRequest, GetMusicRequest
router = APIRouter()


@router.post("/gen_music_by_lyrics")
async def gen_music_by_lyrics(request: GenLyricsMusicRequest):
    client = app.state.suno
    return client.gen_music(request.model_dump())

@router.post("/gen_music_gpt")
async def gen_music_gpt(request: GenGPTMusicRequest):
    client = app.state.suno
    return client.gen_music(request.model_dump())

@router.post("/get_music")
async def get_music(request: GetMusicRequest):
    client = app.state.suno
    return {"clips":client.get_music(request.music_ids)}