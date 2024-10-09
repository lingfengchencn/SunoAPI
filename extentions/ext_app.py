from flask import Flask
from flask_cors import CORS
from configs import config

# app = FastAPI(lifespan=lifespan)

from gevent import monkey
monkey.patch_all()  # 补丁所有标准库，确保兼容

import extentions.ext_database as ext_database
import extentions.ext_lock as ext_lock
import extentions.ext_logger as ext_logger
import extentions.ext_suno as ext_suno
import extentions.ext_rabbitmq as ext_rabbitmq
import extentions.ext_response_hooks as ext_response_hooks

def initialize_extensions(app):
    ext_database.init_db(app)
    ext_database.init_migrate(app)
    ext_lock.init_lock(app)
    ext_logger.setup_logger(app)
    ext_suno.init_suno(app)
    ext_rabbitmq.init_mq(app)
    ext_response_hooks.register_response_hook(app)


    



def create_app():
    app = Flask(__name__)
    # Enable CORS for all routes and origins  # 允许跨域请求
    CORS(app, resources={r"/*": {"origins": "*"}})
    # 加载配置
    app.config.from_mapping(config.model_dump())


    initialize_extensions(app)

    return app

app = create_app()