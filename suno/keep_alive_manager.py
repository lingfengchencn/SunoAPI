
import signal
import sys
import threading
from .suno_service import SunoService
import logging
logger = logging.getLogger(__name__)

class KeepAliveManager:

    keep_alive_threads = {}


    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(KeepAliveManager, cls).__new__(cls)
        return cls.instance


    def __init__(self,suno_client:SunoService ,  interval:int =30):

        if not hasattr(self, '_instanced'):
            self.suno_client = suno_client
            self.interval = interval
            self.lock = threading.Lock()
            self.keep_alive_threads = {}
            self.keep_alive_events = {}
            self._instanced = True
            self._is_running = {}

    def __del__(self):
        self.stop_all()

    def start_keep_alive(self, key):
        with self.lock:
            if key not in self.keep_alive_threads:
                event = threading.Event()
                thread = threading.Thread(target=self.keep_alive, args=(key, event))
                self.keep_alive_threads[key] = thread
                self.keep_alive_events[key] = event
                thread.start()
            self._is_running[key] = True

    def stop_keep_alive(self, key):
        with self.lock:
            if key in self.keep_alive_threads:
                self._is_running[key] = False
                event = self.keep_alive_events.pop(key, None)
                 # 设置事件标志
                thread = self.keep_alive_threads.pop(key, None)
                if event:
                    event.set() 
                if thread:
                    thread.join()  # 确保线程执行完
    def stop_all(self):
        with self.lock:
            for key in list(self.keep_alive_threads.keys()):
                self.stop_keep_alive(key)

    def keep_alive(self, key, event):
        while not event.is_set():
            logger.debug(f"Keep-alive thread for {key} is running.")
            self.suno_client.update_token()
            event.wait(self.interval)  # 每10秒检查一次
        
        if not ( key in self._is_running) or  not self._is_running[key]:
            logger.debug(f"Keep-alive thread for {key} is stopped.")
            self._is_running.pop(key, None)
        
    
