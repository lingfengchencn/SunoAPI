import threading
from extentions.ext_app import app
from requests.exceptions import HTTPError

from request_model import GenLyricsRequest
from suno.entities import ClipStatusEnum, SunoLyricGenerageStatusEnum
from suno.exceptions import NotFoundException, ServiceUnavailableException , TooManyRequestsException

from models import SunoJobs, SunoJobTypeEnum
from sqlalchemy.sql.expression import not_
from services.lyrics_service import LyricsService
import logging
logger = logging.getLogger(__name__)


from flask import Blueprint, request, jsonify, Response, stream_with_context
from flask_restful import Resource, marshal_with, reqparse
from extentions.ext_restful_api import RestfulExternalApi
from extentions.ext_database import db

bp = Blueprint('lyrics', __name__, url_prefix='')
api = RestfulExternalApi(bp)


class GenLyricsApi(Resource):
    # @router.post("/gen_lyrics")
    def post(self):
        try:
            data = request.json
            job = LyricsService.create(data)
            return job.to_json()
        except ServiceUnavailableException as ex:
            return {"error": ex.message}
        

class GetLyricsApi(Resource):
    # @router.get("/get_lyrics/{job_id}")
    def get(job_id:str):
        try:
            job = LyricsService.get(job_id)

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


api.add_resource(GenLyricsApi, '/gen_lyrics')
api.add_resource(GetLyricsApi, '/get_lyrics/<job_id>')




def _thread_get_lyrics():
    if app.state.lyrics_task_running :
        return
    app.state.lyrics_task_running = True
    client = app.state.suno
    service = LyricsService()

    try:
        result = db.session.query(SunoJobs).filter(
            SunoJobs.job_type == SunoJobTypeEnum.LYRICS.value,
            not_(SunoJobs.status.in_([ClipStatusEnum.COMPLETE.value, ClipStatusEnum.ERROR.value]))
        ).all()
        # if not result:
        #     return
        logger.debug(f"thread get lyrics number:{len(result)} data:{result}")
        for job in result:
            logger.info(f"job_id:{job.job_id} status:{job.status}")
            new_job = service.get(job.id)
    finally:
        # 解锁
         app.state.lyrics_task_running = False