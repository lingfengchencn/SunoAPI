
import threading


def init_lock(app):

    # Check if state exists, else initialize it
    if not hasattr(app, 'state'):
        app.state = type('State', (object,), {})()  # Create a simple object for state
        
    # 定义全局锁
    app.state.lyrics_lock = threading.Lock()
    app.state.lyrics_task_running = False


    app.state.music_lock = threading.Lock()
    app.state.music_task_running = False