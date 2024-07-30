
import asyncio
import json
from typing import List, Optional
from urllib.parse import urljoin

import requests

import aiohttp
from .entities import BillingInfo, Clip, GenMusicRequest, GenMusicResponse, SunoAuthTypeEnum, SunoLyric, SunoToken, SunoUploadAudioKey, SunoUploadAudioStatus, SunoUploadAudioStatusEnum
from .suno_http import SunoCookie
import logging
logger = logging.getLogger(__name__)

COMMON_HEADERS = {
    "Content-Type": "text/plain;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://suno.com",
    "Origin": "https://suno.com",
}



class SunoClient:
    BASE_URL = "https://studio-api.suno.ai"  # 示例基础 URL，需要替换为实际值
    STUDIO_URL = "https://studio-api.suno.ai/api/"
    CLERK_URL = "https://clerk.suno.com"



    CLERK_JS_VERSION = "4.73.4"

    def __init__(self,suno_cookie:SunoCookie):
        
        self.suno_cookie = suno_cookie


    async def fetch(self, url,  data=None, auth_type:Optional[ SunoAuthTypeEnum] =SunoAuthTypeEnum.JWT,method="POST",unauthorized = False):
        if auth_type == SunoAuthTypeEnum.COOKIE: # 好像只有获取token需要用到
            headers = {"cookie": self.suno_cookie.get_cookie()}
        elif auth_type == SunoAuthTypeEnum.JWT:
            headers = {"Authorization": f"Bearer {self.suno_cookie.get_token()}"}
        
        headers.update(COMMON_HEADERS)

        if data is not None :
            data = json.dumps(data)

        
        logger.debug(f"fetch url: {url} data:{data} headers:{headers}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method, url=url, data=data, headers=headers
                ) as resp:
                    response = await resp.json()
                    # {'detail': 'Unauthorized'}
                    if 'detail' in response and response["detail"] == "Unauthorized":
                        logger.debug(f"fetch error Unauthorized")
                        if unauthorized ==  True:
                            raise Exception("Unauthorized")
                        self.update_token()
                        return await self.fetch(url, data=data, auth_type=auth_type, method=method,unauthorized=True)
                    return await resp.json()
            except Exception as e:
                logger.error(f"fetch error: {e}")
                raise e

    def update_token(self) -> SunoToken:
        session_id = self.suno_cookie.get_session_id()
        api = f"/v1/client/sessions/{session_id}/tokens?_clerk_js_version={self.CLERK_JS_VERSION}"
        url= urljoin(self.CLERK_URL, api)
        
        headers = {"cookie": self.suno_cookie.get_cookie(),
                   "Content-Type":"application/x-www-form-urlencoded"}
        headers.update(COMMON_HEADERS)
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        resp_headers = dict(response.headers)
        set_cookie = resp_headers.get("Set-Cookie")
        self.suno_cookie.load_cookie(set_cookie)
        data = response.json()
        token = data.get("jwt")
        self.suno_cookie.set_token(token)

        logger.debug(f"update_token: {token}")

        return SunoToken.from_json(data)




    async def get_feed(self, ids=[]) -> List[Clip]:
        url = urljoin(self.STUDIO_URL, f"feed/v2?ids={','.join(ids)}")
        response = await self.fetch(url, auth_type=SunoAuthTypeEnum.JWT, method="GET")
        logger.debug(f"get_feed: {response}")
        return [Clip.from_json(clip) for clip in response.get("clips")]



    async def gen_music(self, request:GenMusicRequest) -> GenMusicResponse:
        url = urljoin(self.STUDIO_URL, "generate/v2/")
        response = await self.fetch(url, auth_type=SunoAuthTypeEnum.JWT, data=request.to_json())
        return GenMusicResponse.from_json(response)
    async def gen_concat(self,data):
        api = "generate/concat/v2/"
        url = urljoin(self.STUDIO_URL, api)
        response = await self.fetch(url, data)
        return response

    async def gen_lyrics(self, prompt="") -> str:
        # https://studio-api.suno.ai/api/generate/lyrics/
        url = urljoin(self.STUDIO_URL, "generate/lyrics/")
        data = {"prompt": prompt}
        response = await self.fetch(url, auth_type=SunoAuthTypeEnum.JWT, data=data)
        return response.get("id")

    async def get_lyrics(self, lyrics_id) -> SunoLyric:
        # https://studio-api.suno.ai/api/generate/lyrics/9f479d79-cf46-4da0-ad51-bb482953b870
        url = urljoin(self.STUDIO_URL, f"generate/lyrics/{lyrics_id}")
        response = await self.fetch(url, auth_type=SunoAuthTypeEnum.JWT, method="GET")
        logger.debug(f"get_lyrics: {response}")
        lyrics = SunoLyric.from_json(response)
        return lyrics

    async def get_credits(self) -> BillingInfo:
        url = urljoin(self.STUDIO_URL, "billing/info/")
        response = await self.fetch(url, auth_type=SunoAuthTypeEnum.JWT, method="GET")
        logger.debug(f"get_credits: {response}")
        billing_info = BillingInfo.from_json(response)
        return billing_info
    
    async def get_storage_key(self,file_ext) -> SunoUploadAudioKey:
        #  https://studio-api.suno.ai/api/uploads/audio/
        api = "uploads/audio/"
        url = urljoin(self.STUDIO_URL, api)
        data = {"extension":file_ext}
        response = await self.fetch(url,  data=data)
        logger.debug(f"get_storage_key: {response}")
        key = SunoUploadAudioKey.from_json(response)
        return key

    async def upload_file(self,file_name,file_data, file_ext):
        # https://suno-uploads.s3.amazonaws.com/
        # Content-Type:multipart/form-data; boundary=----WebKitFormBoundarydl5HFaWNoeUnwoFn
        # ------WebKitFormBoundarydl5HFaWNoeUnwoFn
        # Content-Disposition: form-data; name="Content-Type"

        # audio/wav
        # ------WebKitFormBoundarydl5HFaWNoeUnwoFn
        # Content-Disposition: form-data; name="key"

        # raw_uploads/5d03b3ba-cd9e-42cf-ae5b-cf15b3b24841.wav
        # ------WebKitFormBoundarydl5HFaWNoeUnwoFn
        # Content-Disposition: form-data; name="AWSAccessKeyId"

        # AKIA2V4GXGDKJMTPWLXO
        # ------WebKitFormBoundarydl5HFaWNoeUnwoFn
        # Content-Disposition: form-data; name="policy"

        # eyJleHBpcmF0aW9uIjogIjIwMjQtMDctMjlUMTA6MTc6NTNaIiwgImNvbmRpdGlvbnMiOiBbWyJjb250ZW50LWxlbmd0aC1yYW5nZSIsIDAsIDEwNDg1NzYwMF0sIFsic3RhcnRzLXdpdGgiLCAiJENvbnRlbnQtVHlwZSIsICJhdWRpby93YXYiXSwgeyJidWNrZXQiOiAic3Vuby11cGxvYWRzIn0sIHsia2V5IjogInJhd191cGxvYWRzLzVkMDNiM2JhLWNkOWUtNDJjZi1hZTViLWNmMTViM2IyNDg0MS53YXYifV19
        # ------WebKitFormBoundarydl5HFaWNoeUnwoFn
        # Content-Disposition: form-data; name="signature"

        # wB1bZvq7YkZWENfDKNZb7dBIqsg=
        # ------WebKitFormBoundarydl5HFaWNoeUnwoFn
        # Content-Disposition: form-data; name="file"; filename="y2282.wav"
        # Content-Type: audio/wav

        # RIFFFcWAVEfmt À]wLISTINFOISFTLavf58.76.100datacShow more

        key = await self.get_storage_key(file_ext)
        fields = key.fields
        data = {
            "Content-Type": fields.content_type,
            "key": fields.key,
            "AWSAccessKeyId": fields.AWSAccessKeyId,
            "policy": fields.policy,
            "signature": fields.signature,
        }
        form_data = aiohttp.FormData(data)
        form_data.add_field("file", file_data, filename=file_name, content_type=f"audio/{file_ext}")
        # 使用form post
        async with aiohttp.ClientSession() as session:
            async with session.post(key.url, data=form_data) as response:
                # 判断 code == 204
                if response.status == 204:
                    await self.upload_finish(file_name,key.id)

                    while True: # 获取上传状态
                        upload_status = await self.get_upload_status(key.id)
                        if upload_status.status == SunoUploadAudioStatusEnum.complete:
                            break
                        if upload_status.status == SunoUploadAudioStatusEnum.error:
                            raise Exception(f"upload error: {upload_status.error_message}")
                        await asyncio.sleep(3)
                    await self.initialize_clip(key.id)
                else:
                    raise Exception(f"upload error: {response.status} text: {await response.text()}")



    async def upload_finish(self, file_name, file_id):
        # https://studio-api.suno.ai/api/uploads/audio/5d03b3ba-cd9e-42cf-ae5b-cf15b3b24841/upload-finish/
        # {"upload_type":"file_upload","upload_filename":"y2282.wav"}
        api = f"uploads/audio/{file_id}/upload-finish/"
        url = urljoin(self.STUDIO_URL, api)
        data = {"upload_type": "file_upload", "upload_filename": file_name}
        return await self.fetch(url, data=data)

    async def get_upload_status(self, file_id):
        # https://studio-api.suno.ai/api/uploads/audio/5d03b3ba-cd9e-42cf-ae5b-cf15b3b24841/
        api = f"uploads/audio/{file_id}/"
        url = urljoin(self.STUDIO_URL, api)
        response = await self.fetch(url, method="GET")
        upload_status = SunoUploadAudioStatus.from_json(response)
        return upload_status
    # https://studio-api.suno.ai/api/uploads/audio/5d03b3ba-cd9e-42cf-ae5b-cf15b3b24841/initialize-clip/
    async def initialize_clip(self, file_id):
        api = f"uploads/audio/{file_id}/initialize-clip/"
        url = urljoin(self.STUDIO_URL, api)
        response = await self.fetch(url, method="POST")
        return response.get("clip_id")


