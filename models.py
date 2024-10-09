from datetime import datetime, timezone
from enum import Enum
import uuid
from sqlalchemy import Column, String, JSON ,DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from suno.entities import SunoLyricGenerageStatusEnum

# 创建基础模型类，所有模型将继承自这个类
from extentions.ext_database import db

from sqlalchemy import CHAR, TypeDecorator


class StringUUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            return value.hex

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return str(value)

class SunoJobTypeEnum(Enum):
    MUSIC = "music"
    LYRICS = "lyrics"

    @classmethod
    def value_of(cls, value):
        for item in cls:
            if item.value == value:
                return item

class SunoJobs(db.Model):
    __tablename__ = "suno_jobs"

    id = db.Column(StringUUID,primary_key=True, server_default=db.text("uuid_generate_v4()"), index=True) # 任务id
    job_id = db.Column(db.String(40), index=True) #suno music id
    job_type = db.Column(db.String(10)) # 任务类型
    account=db.Column(db.String,default='') # suno 用户
    status = db.Column(db.String) # 任务状态
    request = db.Column(db.JSON) # 请求参数
    response = db.Column(db.JSON) # 响应参数
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc)) #   创建时间

    @property
    def job_type_enum(self):
        return SunoJobTypeEnum.value_of(self.job_type)
    @job_type_enum.setter
    def job_type_enum(self, value: SunoJobTypeEnum):
        self.job_type = value.value


    def to_json(self):
        return {
            "id": str(self.id),
            "job_id": str(self.job_id),
            "job_type": self.job_type,
            "account": self.account,
            "status": self.status,
            "request": self.request,
            "response": self.response,
            # 格式化时间 为字符串   
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
