
import asyncio
from hashlib import md5
from .entities import BillingInfo, GenMusicRequest, GenMusicResponse, SunoLyric
from .suno_client import SunoClient
from .kee_alive_manager import KeepAliveManager
import logging

from .suno_http import SunoCookie
logging.basicConfig(level=logging.DEBUG,format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Suno:

    _client_key = "suno_client_key"
    def __init__(self, session_id, cookie):
        self.suno_cookie = SunoCookie()
        self.suno_cookie.set_session_id(session_id)
        self.suno_cookie.load_cookie(cookie)
        
        self.suno_client = SunoClient(self.suno_cookie)

        self.keep_alive_manager = KeepAliveManager(self.suno_client)
        # md5 key
        self._client_key = md5(f"{session_id}:{cookie}".encode('utf-8')).hexdigest()
        logger.debug(f"suno client key : {self._client_key}")
        # self.suno_client.update_token()
        self.keep_alive_manager.start_keep_alive(self._client_key)


    def stop_keep_alive(self):
        self.keep_alive_manager.stop_keep_alive(self._client_key)

    def _do_sync_call(self,request):
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(request)
        return result
    
    def gen_lyrics(self, prompt="") -> str:
        request = self.suno_client.gen_lyrics(prompt)
        result = self._do_sync_call(request)
        return result
    def get_lyrics(self, lyrics_id) -> SunoLyric:
        request = self.suno_client.get_lyrics(lyrics_id)
        result = self._do_sync_call(request)
        return result
    
    def gen_music(self, request:GenMusicRequest) -> GenMusicResponse:
        request =  self.suno_client.gen_music(request)
        result = self._do_sync_call(request)
        return result
    def get_music(self, music_ids = []):
        # result = await self.suno_client.get_feed(music_ids)
        # return result
        request =  self.suno_client.get_feed(music_ids)
        result = self._do_sync_call(request)
        return result
    
    # need to test
    def gen_concat(self,data):
        request = self.suno_client.gen_concat(data)
        result = self._do_sync_call(request)
        return result
    def get_credits(self) -> BillingInfo:
        request = self.suno_client.get_credits()
        result = self._do_sync_call(request)
        return result
    
    def upload_file(self,file_name,file_data, file_ext):
        request = self.suno_client.upload_file(file_name,file_data, file_ext)
        result = self._do_sync_call(request)
        return result


