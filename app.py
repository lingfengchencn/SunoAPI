
from extentions.ext_app import app
import argparse

# 注册蓝图
from controller import bp
app.register_blueprint(bp)


if __name__ == '__main__':
    # 如果启动参数包含port，则使用port启动
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--port', type=int,default=5000, help='Port number to run the server on', required=False)
    args = parser.parse_args()
    
    port = args.port
    app.run(host="0.0.0.0",port=port)


