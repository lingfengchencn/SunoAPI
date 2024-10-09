

# from configs import config

# # from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# # from sqlalchemy.orm import sessionmaker, declarative_base
# # engine = create_async_engine(config.DB_URL)
# # # 创建会话工厂，用于生成新的数据库会话
# # AsyncSessionLocal = sessionmaker(
# #     autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
# # )

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# engine = create_engine(config.DB_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # # 创建基础模型类，所有模型将继承自这个类
# # Base = declarative_base()
# from fastapi import Depends, HTTPException, status
# from sqlalchemy.orm import Session

# # 获取数据库会话
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
import flask_migrate

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    import models

def init_migrate(app):
    flask_migrate.Migrate(app, db)
