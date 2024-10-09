
from datetime import datetime, timedelta

from requests import HTTPError
from extentions.ext_app import app
from models import SunoJobTypeEnum, SunoJobs
from suno.entities import ClipStatusEnum, SunoLyricGenerageStatusEnum
from models import SunoJobs, SunoJobTypeEnum
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql.expression import not_
from extentions.ext_database import db

import logging
from configs import config

from suno.exceptions import NotFoundException, ServiceUnavailableException
logger = logging.getLogger(__name__)

class LyricsService:

    @classmethod
    def create(cls,request:dict) -> SunoJobs:
        client = app.state.suno
        try:
            job = SunoJobs(
                job_type=SunoJobTypeEnum.LYRICS.value,
                status=ClipStatusEnum.QUEUED.value,
                account=config.SUNO_ACCOUNT,
                request= request,
                created_at=datetime.now()
            )
            try:
                lyrics_id = client.gen_lyrics(request.get("prompt"))
                # 更新工作状态
                job.job_id = lyrics_id
                job.status = ClipStatusEnum.SUBMITTED.value
                db.session.add(job)
                db.session.commit()
            except Exception as ex:
                logger.error(f"gen lyrics exception:{str(ex)}")
                raise ex
            return job
        except ServiceUnavailableException as ex:
            logger.error(f"suno service unavailable:{str(ex)}")
            raise ex
    @classmethod
    def get(cls,job_id:str, fetech_suno:bool = True) -> SunoJobs:
        client = app.state.suno
        try:
            job = db.session.query(SunoJobs).filter(SunoJobs.id == job_id).first()

            if job  and job.status in [ClipStatusEnum.COMPLETE.value ,ClipStatusEnum.ERROR.value]:
                pass
            elif fetech_suno:
                suno_lyrics = client.get_lyrics(job.job_id)
                if suno_lyrics.status == SunoLyricGenerageStatusEnum.COMPLETE:
                    job.status = ClipStatusEnum.COMPLETE.value
                    job.response = suno_lyrics.to_json()
                    db.session.add(job)
                    db.session.commit()
        except HTTPError as e:
            # 如果为404 说明 id不存在
            job.status = ClipStatusEnum.ERROR.value
            job.response = suno_lyrics.to_json()
            db.session.add(job)
            db.session.commit()
            if e.response.status_code == 404:
                raise NotFoundException("lyrics id is invalid or expired")

        return job
    
    @classmethod
    def get_running_jobs(cls, job_type: SunoJobTypeEnum = SunoJobTypeEnum.LYRICS, created_duration: int = 60*5):
        """
        获取运行中任务
        job_type: 任务类型
        created_duration  int : 创建时间间隔,单位：秒

        """

        query = db.session.query(SunoJobs).filter(
            SunoJobs.account == config.SUNO_ACCOUNT,
            not_(SunoJobs.status.in_(
                [ClipStatusEnum.COMPLETE.value, ClipStatusEnum.ERROR.value]))
        )
        if job_type:
            query = query.filter(SunoJobs.job_type == job_type.value)
        if created_duration:
            time_delta = timedelta(seconds=created_duration)
            query = query.filter(SunoJobs.created_at >=
                                 datetime.now() - time_delta)
        jobs = query.all()

        logger.info(
            f"get suno jobs number: {len(jobs)}, job info : {','.join( [str(job.id)  for job in jobs])}")
        return jobs
