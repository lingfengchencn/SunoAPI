
import threading
from .suno_client import SunoClient


class KeepAliveManager:
    def __init__(self,suno_client:SunoClient ,  interval:int =30):
        self.suno_client = suno_client
        self.interval = interval
        self.lock = threading.Lock()
        self.keep_alive_threads = {}
        self.keep_alive_events = {}
        self.instance_counts = {}


    def start_keep_alive(self, key):
        with self.lock:
            if key not in self.keep_alive_threads:
                event = threading.Event()
                thread = threading.Thread(target=self.keep_alive, args=(key, event))
                self.keep_alive_threads[key] = thread
                self.keep_alive_events[key] = event
                self.instance_counts[key] = 0
                thread.start()
            self.instance_counts[key] += 1

    def stop_keep_alive(self, key):
        with self.lock:
            if key in self.instance_counts:
                self.instance_counts[key] -= 1
                if self.instance_counts[key] <= 0:
                    event = self.keep_alive_events.pop(key, None)
                    thread = self.keep_alive_threads.pop(key, None)
                    if event and thread:
                        event.set()
                        thread.join()
    def stop_all(self):
        with self.lock:
            for key in list(self.keep_alive_threads.keys()):
                self.stop_keep_alive(key)

    def keep_alive(self, key, event):
        while not event.is_set():
            print(f"Keep-alive thread for {key} is running.")
            self.suno_client.update_token()
            event.wait(self.interval)  # 每10秒检查一次
    
