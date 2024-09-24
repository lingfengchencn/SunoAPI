
from datetime import datetime
import threading
import time
import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from requests import Session
from sqlalchemy import not_, select
from extentions.ext_app import app
from requests.exceptions import HTTPError

from extentions.ext_database import get_db
from models import SunoJobTypeEnum, SunoJobs
from request_model import GenGPTMusicRequest, GenLyricsMusicRequest, GetMusicRequest
from suno.entities import ClipStatusEnum
router = APIRouter()
from services.music_service import MusicService
import logging
logger = logging.getLogger(__name__)

@router.post("/gen_music_by_lyrics")
async def gen_music_by_lyrics(request: GenLyricsMusicRequest,db:Session = Depends(get_db)):
    
    service = MusicService()
    job_list = service.create(request.to_dict())
    result = [job.to_json() for job in job_list]
    
    with app.state.music_lock:
        # 启用线程，查询剩下所有任务的情况。并枷锁，单线程
        thread = threading.Thread(target=_thread_get_musics,args=(db,))
        thread.start()    
    return result




@router.post("/gen_music_gpt")
async def gen_music_gpt(request: GenGPTMusicRequest,db:Session = Depends(get_db)):
    service = MusicService()
    job_list = service.create(request.to_dict())
    result = [job.to_json() for job in job_list]
    

    with app.state.music_lock:
        # 启用线程，查询剩下所有任务的情况。并枷锁，单线程
        thread = threading.Thread(target=_thread_get_musics,args=(db,))
        thread.start()
    return result

@router.post("/get_music")
async def get_music(request: GetMusicRequest,db:Session = Depends(get_db)):
    service = MusicService()
    jobs = service.get(request.job_ids)

    result = [job.to_json() for job in jobs]
    
    logger.info(f"get music data : { result }")
    
    with app.state.music_lock:
        # 启用线程，查询剩下所有任务的情况。并枷锁，单线程
        thread = threading.Thread(target=_thread_get_musics,args=(db,))
        thread.start()
    return result


def _update_music_data(db:Session):

    client = app.state.suno
    stmt = select(SunoJobs).where(
                SunoJobs.job_type == SunoJobTypeEnum.MUSIC.value,
                not_(SunoJobs.status.in_([ClipStatusEnum.COMPLETE.value, ClipStatusEnum.ERROR.value]))
            ).limit(20)
    result = db.execute(stmt).scalars().all()
    logger.debug(f"thread get lyrics number:{len(result)} data:{result}")
    if not result:
        return 0,0

    ids =  [str(clip.job_id) for clip in result ]

    try:
        music_list = client.get_music(ids)

        logger.info(f"get suno music data : {[music.to_json() for music in music_list]}")

        for clip in music_list:
            db_clips = [db_c for db_c in result if str(db_c.job_id) == clip.id]
            db_clip = db_clips[0] if db_clips else None
            if db_clip:
                db_clip.response = clip.to_json()
                # if clip.status in [ClipStatusEnum.COMPLETE,ClipStatusEnum.ERROR]:
                db_clip.status = clip.status.value
                db.add(db_clip)
        db.commit()
        return len(ids),len(music_list)
    except Exception as ex:
        logger.error(f"update music data exception:{ex}")
        return len(ids),0


def _thread_get_musics(db: Session):
    if app.state.music_task_running :
        return
    app.state.music_task_running = True

    try:
        while True:
            db_num,updated_num = _update_music_data(db)
            logger.info(f"thread get musics , db number={db_num} , updated_num={updated_num}")
            if db_num == 0 :
                break
            else:
                time.sleep(30)
                continue
    finally:
        # 解锁
        app.state.music_task_running = False