

from fastapi import FastAPI
from configs import config
from suno.suno import Suno


def init_suno(app: FastAPI):
    client = Suno(config.SESSION_ID, config.COOKIE)
    app.state.suno = client

