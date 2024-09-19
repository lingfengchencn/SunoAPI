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

import logging
logger = logging.getLogger(__name__)

@router.post("/gen_lyrics")
async def gen_lyrics(request: GenLyricsRequest,db:Session = Depends(get_db)):
    # raise TooManyRequestsException("too many requests")
    # raise ServiceUnavailableException("service unavailable")
    client = app.state.suno
    try:
        job = SunoJobs(
            id=uuid.uuid4(),
            job_type=SunoJobTypeEnum.LYRICS.value,
            status=ClipStatusEnum.QUEUED.value,
            request= request.to_dict(),
            created_at=datetime.now()
        )
        try:
            lyrics_id = client.gen_lyrics(request.prompt)
            # 更新工作状态
            job.job_id = lyrics_id
            job.status = ClipStatusEnum.SUBMITTED.value
            db.add(job)
            db.commit()
        except Exception as ex:
            logger.error(f"gen lyrics exception:{str(ex)}")
            raise ex
        return {"lyrics_id": job.id}
    except ServiceUnavailableException as ex:
        return {"error": ex.message}


@router.get("/get_lyrics/{lyrics_id}")
async def get_lyrics(lyrics_id:str,db:Session = Depends(get_db)):
    client = app.state.suno
    try:
        stmt = select(SunoJobs).where(SunoJobs.id == lyrics_id)
        # 执行查询
        result = db.execute(stmt)
        lyrics = result.scalar_one_or_none()
        if lyrics  and lyrics.status in [ClipStatusEnum.COMPLETE.value ,ClipStatusEnum.ERROR.value]:
                return {"lyrics": lyrics.response}

        else:
            suno_lyrics = client.get_lyrics(lyrics_id)
            if suno_lyrics.status == SunoLyricGenerageStatusEnum.COMPLETE:
                lyrics.status = ClipStatusEnum.COMPLETE.value
                lyrics.response = suno_lyrics.to_json()
                db.add(lyrics)
                db.commit()
    except HTTPError as e:
        # 如果为404 说明 id不存在
        if e.response.status_code == 404:
            raise NotFoundException("lyrics id is invalid or expired")
    finally:
       with app.state.lyrics_lock:
            # 启用线程，查询剩下所有任务的情况。并枷锁，单线程
            thread = threading.Thread(target=_thread_get_lyrics,args=(db,))
            thread.start()

    return {"lyrics": lyrics.to_json()}

def _thread_get_lyrics(db: Session):
    if app.state.lyrics_task_running :
        return
    app.state.lyrics_task_running = True
    client = app.state.suno

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
            try:
                suno_lyrics = client.get_lyrics(job.job_id)
                logger.info(f"job_id:{job.job_id} status:{suno_lyrics.status} data:{suno_lyrics.to_json()}")
                if suno_lyrics.status == SunoLyricGenerageStatusEnum.COMPLETE:
                    job.status = ClipStatusEnum.COMPLETE.value
                    job.response = suno_lyrics.to_json()
            except HTTPError as e:
                job.status = ClipStatusEnum.ERROR.value
                job.response = {"error": str(e)}
                logger.error(e)
            db.add(job)
            db.commit()
    finally:
        # 解锁
         app.state.lyrics_task_running = False