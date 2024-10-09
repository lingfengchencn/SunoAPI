import threading
import time
from sqlalchemy import not_, select
from extentions.ext_app import app
from models import SunoJobTypeEnum, SunoJobs
from request_model import GenGPTMusicRequest, GenLyricsMusicRequest, GetMusicRequest
from suno.entities import ClipStatusEnum
from services.music_service import MusicService

import logging
logger = logging.getLogger(__name__)


from flask import Blueprint, request, jsonify, Response, stream_with_context
from flask_restful import Resource, marshal_with, reqparse
from extentions.ext_restful_api import RestfulExternalApi
from extentions.ext_database import db

bp = Blueprint('music', __name__, url_prefix='')
api = RestfulExternalApi(bp)

class GenMusicByLyricsApi(Resource):
    # @router.post("/gen_music_by_lyrics")
    def post(self):
        data = GenLyricsMusicRequest(**request.json)
        job_list = MusicService.create(data.to_dict())
        result = [job.to_json() for job in job_list]
        return result

class GenMusicByGptApi(Resource):
    # @router.post("/gen_music_gpt")
    def post(self):
        data = GenGPTMusicRequest(**request.json)
        job_list = MusicService.create(data.to_dict())
        result = [job.to_json() for job in job_list]
        

        with app.state.music_lock:
            # 启用线程，查询剩下所有任务的情况。并枷锁，单线程
            thread = threading.Thread(target=_thread_get_musics)
            thread.start()
        return result
    
class GetMusicApi(Resource):
    # @router.post("/get_music")
    def post(self):
        jobs = MusicService.get_list(request.json.get("music_ids"))

        result = [job.to_json() for job in jobs]
        
        logger.info(f"get music data : { result }")
        
        with app.state.music_lock:
            # 启用线程，查询剩下所有任务的情况。并枷锁，单线程
            thread = threading.Thread(target=_thread_get_musics )
            thread.start()
        return result


api.add_resource(GenMusicByLyricsApi, '/gen_music_by_lyrics')
api.add_resource(GenMusicByGptApi, '/gen_music_gpt')
api.add_resource(GetMusicApi, '/get_music')


# @router.post("/gen_music_by_lyrics")
# async def gen_music_by_lyrics(request: GenLyricsMusicRequest,db:Session = Depends(get_db)):
    
#     service = MusicService()
#     job_list = service.create(request.to_dict())
#     result = [job.to_json() for job in job_list]
    
#     with app.state.music_lock:
#         # 启用线程，查询剩下所有任务的情况。并枷锁，单线程
#         thread = threading.Thread(target=_thread_get_musics,args=(db,))
#         thread.start()    
#     return result




# @router.post("/gen_music_gpt")
# async def gen_music_gpt(request: GenGPTMusicRequest,db:Session = Depends(get_db)):
#     service = MusicService()
#     job_list = service.create(request.to_dict())
#     result = [job.to_json() for job in job_list]
    

#     with app.state.music_lock:
#         # 启用线程，查询剩下所有任务的情况。并枷锁，单线程
#         thread = threading.Thread(target=_thread_get_musics,args=(db,))
#         thread.start()
#     return result

# @router.post("/get_music")
# async def get_music(request: GetMusicRequest,db:Session = Depends(get_db)):
#     service = MusicService()
#     jobs = service.get(request.job_ids)

#     result = [job.to_json() for job in jobs]
    
#     logger.info(f"get music data : { result }")
    
#     with app.state.music_lock:
#         # 启用线程，查询剩下所有任务的情况。并枷锁，单线程
#         thread = threading.Thread(target=_thread_get_musics,args=(db,))
#         thread.start()
#     return result


def _update_music_data():

    client = app.state.suno

    result = db.session.query(SunoJobs).filter(
            SunoJobs.job_type == SunoJobTypeEnum.MUSIC.value,
            not_(SunoJobs.status.in_([ClipStatusEnum.COMPLETE.value, ClipStatusEnum.ERROR.value]))
        ).all()

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
                db.session.add(db_clip)
        db.session.commit()
        return len(ids),len(music_list)
    except Exception as ex:
        logger.error(f"update music data exception:{ex}")
        return len(ids),0


def _thread_get_musics():
    if app.state.music_task_running :
        return
    app.state.music_task_running = True

    try:
        with app.app_context():
            while True:
                db_num,updated_num = _update_music_data()
                logger.info(f"thread get musics , db number={db_num} , updated_num={updated_num}")
                if db_num == 0 :
                    break
                else:
                    time.sleep(30)
                    continue
    finally:
        # 解锁
        app.state.music_task_running = False