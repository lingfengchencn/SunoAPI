from fastapi import APIRouter
from extentions.ext_app import app
router = APIRouter()

from controller.lyrics_controller import router as lyrics_router
from controller.music_controller import router as music_router  

router.include_router(lyrics_router, prefix="/api/v1")
router.include_router(music_router, prefix="/api/v1")