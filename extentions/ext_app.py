from fastapi import FastAPI
from extentions.ext_rabbitmq import lifespan

app = FastAPI(lifespan=lifespan)

# app = FastAPI()
