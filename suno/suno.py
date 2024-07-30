
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

    
    async def gen_lyrics(self, prompt="") -> str:
        result = await self.suno_client.gen_lyrics(prompt)
        return result
    async def get_lyrics(self, lyrics_id) -> SunoLyric:
        result = await self.suno_client.get_lyrics(lyrics_id)
        return result
    
    async def gen_music(self, request:GenMusicRequest) -> GenMusicResponse:
        result = await self.suno_client.gen_music(request)
        return result
    async def get_music(self, music_ids = []):
        result = await self.suno_client.get_feed(music_ids)
        return result
    
    # need to test
    async def gen_concat(self,data):
        result = await self.suno_client.gen_concat(data)
        return result

    async def get_credits(self) -> BillingInfo:
        result = await self.suno_client.get_credits()
        return result
    
    async def upload_file(self,file_name,file_data, file_ext):
        result = await self.suno_client.upload_file(file_name,file_data, file_ext)
        return result


