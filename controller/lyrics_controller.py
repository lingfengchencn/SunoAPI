import asyncio
from datetime import datetime
import json
import threading
import uuid
from fastapi import APIRouter,Depends
from pydantic import BaseModel
from extentions.ext_app import app
from requests.exceptions import HTTPError

from request_model import GenLyricsRequest
from suno.entities import ClipStatusEnum, SunoLyricGenerageStatusEnum
from suno.exceptions import NotFoundException, ServiceUnavailableException , TooManyRequestsException
router = APIRouter()


from models import SunoJobs, SunoJobTypeEnum
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql.expression import not_
from extentions.ext_database import get_db
from services.lyrics_service import LyricsService
import logging
logger = logging.getLogger(__name__)

@router.post("/gen_lyrics")
async def gen_lyrics(request: GenLyricsRequest,db:Session = Depends(get_db)):
    try:
        service = LyricsService()
        job = service.create(request.to_dict(),db)
        return job.to_json()
    except ServiceUnavailableException as ex:
        return {"error": ex.message}


@router.get("/get_lyrics/{job_id}")
async def get_lyrics(job_id:str,db:Session = Depends(get_db)):
    try:
        service = LyricsService()
        job = service.get(job_id,db)

    except HTTPError as e:
        # 如果为404 说明 id不存在
        if e.response.status_code == 404:
            raise NotFoundException("lyrics id is invalid or expired")
    finally:
       with app.state.lyrics_lock:
            # 启用线程，查询剩下所有任务的情况。并枷锁，单线程
            thread = threading.Thread(target=_thread_get_lyrics,args=(db,))
            thread.start()

    return job.to_json()

def _thread_get_lyrics(db: Session):
    if app.state.lyrics_task_running :
        return
    app.state.lyrics_task_running = True
    client = app.state.suno
    service = LyricsService()

    try:
        stmt = select(SunoJobs).where(
                SunoJobs.job_type == SunoJobTypeEnum.LYRICS.value,
                not_(SunoJobs.status.in_([ClipStatusEnum.COMPLETE.value, ClipStatusEnum.ERROR.value]))
            )
        result = db.execute(stmt).scalars().all()
        # if not result:
        #     return
        logger.debug(f"thread get lyrics number:{len(result)} data:{result}")
        for job in result:
            logger.info(f"job_id:{job.job_id} status:{job.status}")
            new_job = service.get(job.id)
    finally:
        # 解锁
         app.state.lyrics_task_running = False