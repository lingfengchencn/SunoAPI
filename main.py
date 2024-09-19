
from extentions.ext_app import app
from configs import config
from extentions.ext_logger import setup_logger
from extentions.ext_suno import init_suno
from extentions.ext_lock import init_lock
from request_model import GenLyricsMusicRequest, GenLyricsRequest


from middlewares import RequestIdMiddleware,ResponseExceptionMiddleware
setup_logger(app)
init_suno(app)
init_lock(app)
from controller import router
app.include_router(router)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(ResponseExceptionMiddleware)


import logging

logger = logging.getLogger("sunoapi")


