
import asyncio
from hashlib import md5
import threading
from .entities import BillingInfo, GenMusicRequest, GenMusicResponse, SunoLyric
from .suno_service import SunoService
from .keep_alive_manager import KeepAliveManager
import logging

from .suno_http import SunoCookie
logger = logging.getLogger(__name__)


class Suno:

    _client_key = "suno_client_key"
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, session_id, cookie, *args, **kwargs):
        client_key = md5(f"{session_id}:{cookie}".encode('utf-8')).hexdigest()
        
        # Check if an instance with this key already exists
        if client_key not in cls._instances:
            with cls._lock:
                # Double-check within the lock to ensure thread safety
                if client_key not in cls._instances:
                    cls._instances[client_key] = super().__new__(cls)
        
        return cls._instances[client_key]

    def __init__(self, session_id, cookie):
        # if not hasattr(self, '_initialized'):
            self.suno_cookie = SunoCookie()
            self.suno_cookie.set_session_id(session_id)
            self.suno_cookie.load_cookie(cookie)
            
            self.suno_client = SunoService(self.suno_cookie)

            self.keep_alive_manager = KeepAliveManager(self.suno_client)
            # md5 key
            self._client_key = md5(f"{session_id}:{cookie}".encode('utf-8')).hexdigest()
            # self.suno_client.update_token()
            self.keep_alive_manager.start_keep_alive(self._client_key)
            
            self._initialized = True  # Mark the instance as initialized

    def __del__(self):
        # Ensure the keep-alive process is stopped when the Suno instance is destroyed
        self.stop_keep_alive()


    def stop_keep_alive(self):
        self.keep_alive_manager.stop_keep_alive(self._client_key)

    def _do_sync_call(self,request):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(request)
        return result
    
    def gen_lyrics(self, prompt="") -> str:
        result = self.suno_client.gen_lyrics(prompt)
        # result = async_to_sync(self.suno_client.gen_lyrics)(prompt)
        logger.debug(f"gen_lyrics result: {result}")
        return result
    def get_lyrics(self, lyrics_id) -> SunoLyric:
        result = self.suno_client.get_lyrics(lyrics_id)
        logger.debug(f"get_lyrics result: {result}")
        return result
    
    def gen_music(self, request:dict) -> GenMusicResponse:
        if "tags" in request:
            request["tags"] = ",".join(request["tags"])
        if "negative_tags" in request:
            request["negative_tags"] = ",".join(request["negative_tags"])
        result =  self.suno_client.gen_music(request)
        return result
    def get_music(self, music_ids = []):
        # result = await self.suno_client.get_feed(music_ids)
        # return result
        result =  self.suno_client.get_feed(music_ids)
        return result
    
    # need to test
    def gen_concat(self,data):
        result = self.suno_client.gen_concat(data)
        return result
    def get_credits(self) -> BillingInfo:
        result = self.suno_client.get_credits()
        return result
    
    def upload_file(self,file_name,file_data, file_ext):
        result = self.suno_client.upload_file(file_name,file_data, file_ext)
        return result


