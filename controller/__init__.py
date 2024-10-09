# from fastapi import APIRouter
# from extentions.ext_app import app
# router = APIRouter()

# from controller.lyrics_controller import router as lyrics_router
# from controller.music_controller import router as music_router  

# router.include_router(lyrics_router, prefix="/api/v1")
# router.include_router(music_router, prefix="/api/v1")

from flask import Blueprint
from controller.lyrics_controller import bp as lyrics_bp
from controller.music_controller import bp as music_bp

bp = Blueprint('api', __name__, url_prefix='/api/v1')
# 导入并注册子蓝图
bp.register_blueprint(lyrics_bp)
bp.register_blueprint(music_bp)