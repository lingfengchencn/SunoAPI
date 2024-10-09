
from datetime import datetime, timedelta

from requests import request
from sqlalchemy import not_, select
from flask import current_app as app
from extentions.ext_database import db
from models import SunoJobTypeEnum, SunoJobs
from suno.entities import ClipStatusEnum
import logging
from configs import config
logger = logging.getLogger(__name__)


class MusicService:

    @classmethod
    def create(cls, request: dict) -> list[SunoJobs]:
        client = app.state.suno
        result = client.gen_music(request)
        jobs = []
        for clip in result.clips:
            job = SunoJobs(
                job_type=SunoJobTypeEnum.MUSIC.value,
                status=ClipStatusEnum.QUEUED.value,
                account=config.SUNO_ACCOUNT,
                request=request,
                created_at=datetime.now()
            )
            job.job_id = clip.id
            job.response = clip.to_json()
            db.session.add(job)
            jobs.append(job)

        db.session.commit()

        return jobs

    @classmethod
    def get(cls, job_id: str) -> SunoJobs:
        job = db.session.query(SunoJobs).filter(
            SunoJobs.job_type == SunoJobTypeEnum.MUSIC.value,
            SunoJobs.id == job_id).one_or_none()

        return job
    @classmethod
    def get_list(cls, job_ids: list) -> list[SunoJobs]:
        # stmt = select(SunoJobs).where(
        #     SunoJobs.job_type == SunoJobTypeEnum.MUSIC.value,
        #     SunoJobs.id.in_(job_ids)
        # )
        # jobs = db.execute(stmt).scalars().all()

        jobs =  db.session.query(SunoJobs).filter(
            SunoJobs.job_type == SunoJobTypeEnum.MUSIC.value,
            SunoJobs.id.in_(job_ids)
            ).all()


        return jobs

    @classmethod
    def get_running_jobs(cls, job_type: SunoJobTypeEnum, created_duration: int = 60*5):
        """
        获取运行中任务
        job_type: 任务类型
        created_duration  int : 创建时间间隔,单位：秒

        """
        # stmt = select(SunoJobs).where(
        #     not_(SunoJobs.status.in_(
        #         [ClipStatusEnum.COMPLETE.value, ClipStatusEnum.ERROR.value])),
        #     SunoJobs.account == config.SUNO_ACCOUNT
        # )
        # if job_type:
        #     stmt = stmt.where(SunoJobs.job_type == job_type.value)

        # if created_duration:
        #     time_delta = timedelta(seconds=created_duration)
        #     stmt = stmt.where(SunoJobs.created_at >=
        #                       datetime.now() - time_delta)

        # jobs = db.execute(stmt).scalars().all()

        query = db.session.query(SunoJobs).filter(
            not_(SunoJobs.status.in_(
                [ClipStatusEnum.COMPLETE.value, ClipStatusEnum.ERROR.value])),
            SunoJobs.account == config.SUNO_ACCOUNT
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

    @classmethod
    def mq_fetch_suno(cls):
        # stmt = select(SunoJobs).where(
        #     SunoJobs.job_type == SunoJobTypeEnum.MUSIC.value,
        #     not_(SunoJobs.status.in_(
        #         [ClipStatusEnum.COMPLETE.value, ClipStatusEnum.ERROR.value])),
        #     SunoJobs.account == config.SUNO_ACCOUNT
        # ).limit(20)
        # jobs = db.execute(stmt).scalars().all()


        jobs = db.session.query(SunoJobs).filter(
            SunoJobs.job_type == SunoJobTypeEnum.MUSIC.value,
            not_(SunoJobs.status.in_(
                [ClipStatusEnum.COMPLETE.value, ClipStatusEnum.ERROR.value])),
            SunoJobs.account == config.SUNO_ACCOUNT
        ).limit(20).all()

        if not jobs:
            return []

        client = app.state.suno
        ids = [str(clip.job_id) for clip in jobs]
        logger.info(f"get suno music ids : {ids}")
        music_list = client.get_music(ids)

        logger.info(
            f"get suno music data : {[music.to_json() for music in music_list]}")

        clip_exception = None
        for clip in music_list:
            db_clips = [db_c for db_c in jobs if str(db_c.job_id) == clip.id]
            db_clip = db_clips[0] if db_clips else None
            if db_clip:
                db_clip.response = clip.to_json()
                # if clip.status in [ClipStatusEnum.COMPLETE,ClipStatusEnum.ERROR]:
                db_clip.status = clip.status.value
                db.session.add(db_clip)
            db.session.commit()
        return jobs
