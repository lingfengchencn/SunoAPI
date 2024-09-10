
import asyncio
import json
import random
from typing import List, Optional
from urllib.parse import urljoin
from enum import Enum
import requests
import time
import aiohttp
from .entities import BillingInfo, Clip, GenMusicRequest, GenMusicResponse, \
    SunoAuthTypeEnum, SunoLyric, SunoToken, SunoUploadAudioKey, SunoUploadAudioStatus, SunoUploadAudioStatusEnum
from .exceptions import ServiceUnavailableException, TooManyRequestsException, UnauthorizedException
from .suno_http import SunoCookie
import logging
logger = logging.getLogger(__name__)

class CONTENT_TYPE(Enum):
    JSON = "application/json;charset=UTF-8"
    MULTIPART = "multipart/form-data"
    FORM = "multipart/form-data"
    TEXT = "text/plain;charset=UTF-8"

COMMON_HEADERS = {
    "Content-Type": "text/plain;charset=UTF-8",
    # "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://suno.com",
    "Origin": "https://suno.com",
}



class SunoService:
    BASE_URL = "https://studio-api.suno.ai"  # 示例基础 URL，需要替换为实际值
    STUDIO_URL = "https://studio-api.suno.ai/api/"
    CLERK_URL = "https://clerk.suno.com"



    CLERK_JS_VERSION = "5.20.0"

    def __init__(self,suno_cookie:SunoCookie):
        
        self.suno_cookie = suno_cookie


    def fetch(self, url,  data=None, auth_type:Optional[ SunoAuthTypeEnum] =SunoAuthTypeEnum.JWT,method="POST",unauthorized = False, 
                    content_type:CONTENT_TYPE=CONTENT_TYPE.TEXT.value):
        if auth_type == SunoAuthTypeEnum.COOKIE: # 好像只有获取token需要用到
            headers = {"cookie": self.suno_cookie.get_cookie()}
        elif auth_type == SunoAuthTypeEnum.JWT:
            headers = {"Authorization": f"Bearer {self.suno_cookie.get_token()}"}
        
        headers.update(COMMON_HEADERS)
        headers.update({"Content-Type": content_type})

        if data is not None and type(data) is dict:
            data = json.dumps(data)

        
        logger.debug(f"fetch url: {url} data:{data} method:{method} headers:{headers} ")
        while True:
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers)
                else:
                    response = requests.post(url=url, data=data, headers=headers)
                logger.debug(f"fetch response: {response.text}")
                if "Too many requests." in response.text:
                    raise TooManyRequestsException(response.text)
                    
                if "Unauthorized" in response.text:
                    raise UnauthorizedException("Unauthorized")
                response.raise_for_status()
                response = response.json()
                
                return response
            except UnauthorizedException as ex:
                logger.error(f"fetch error: {response.text}")
                res = response.json()
                if res.get("detail") == "Unauthorized":
                    logger.debug(f"fetch error Unauthorized")
                    if unauthorized == True:
                        raise Exception("Unauthorized")
                    self.update_token()
                    return self.fetch(url, data=data, auth_type=auth_type, method=method,unauthorized=True,content_type=content_type)
            except TooManyRequestsException as ex:
                logger.error(f"fetch error: {response.text}")
                # time.sleep(random.uniform(1, 3))
                raise ex
            except ServiceUnavailableException as ex:
                logger.error(f"fetch error: {response.text}")
                # time.sleep(random.uniform(1, 3))
                raise ex
            except ConnectionError as ex:
                logger.error(f"fetch error: {ex}")
                raise ex

        # async with aiohttp.ClientSession() as session:
            
        #     try:
        #         if method == "GET":
        #             resp = await session.get(url, headers=headers)
        #         else:
        #             resp = await session.post(url, data=data, headers=headers)

        #         response = await resp.json()
        #         # {'detail': 'Unauthorized'}
        #         if 'detail' in response and response["detail"] == "Unauthorized":
        #             logger.debug(f"fetch error Unauthorized")
        #             if unauthorized ==  True:
        #                 raise Exception("Unauthorized")
        #             self.update_token()
        #             return self.fetch(url, data=data, auth_type=auth_type, method=method,unauthorized=True,content_type=content_type)
        #         return response
        #     except Exception as e:
        #         logger.error(f"fetch error: {e}")
        #         raise e

    def update_token(self) -> SunoToken:
        session_id = self.suno_cookie.get_session_id()
        api = f"/v1/client/sessions/{session_id}/tokens?_clerk_js_version={self.CLERK_JS_VERSION}"
        url= urljoin(self.CLERK_URL, api)
        
        headers = {"cookie": self.suno_cookie.get_cookie(),
                   "Content-Type":"application/x-www-form-urlencoded"}
        headers.update(COMMON_HEADERS)
        response = requests.post(url, headers=headers)
        logger.debug(f"update_token url: {url} headers:{headers} response: {response.text}")
        response.raise_for_status()
        resp_headers = dict(response.headers)
        set_cookie = resp_headers.get("Set-Cookie")
        self.suno_cookie.load_cookie(set_cookie)
        data = response.json()
        token = data.get("jwt")
        self.suno_cookie.set_token(token)

        logger.debug(f"update_token: {token}")

        return SunoToken.from_json(data)




    def get_feed(self, ids=[]) -> List[Clip]:
        url = urljoin(self.STUDIO_URL, f"feed/v2?ids={','.join(ids)}")
        response = self.fetch(url, method="GET")
        logger.debug(f"get_feed: {response}")
        return [Clip.from_json(clip) for clip in response.get("clips")]



    def gen_music(self, request) -> GenMusicResponse:
        url = urljoin(self.STUDIO_URL, "generate/v2/")
        response = self.fetch(url,  data=request,content_type=CONTENT_TYPE.JSON.value)
        logger.debug(f"gen_music: {response}")
        # {'detail': [{'type': 'missing', 'loc': ['body', 'params', 'prompt'], 'msg': 'Field required'}]}
        if "detail" in response:
            if "Service Unavailable" in response["detail"]:
                raise ServiceUnavailableException("Service Unavailable")
            raise Exception(response["detail"])
        return GenMusicResponse.from_json(response)
    def sync_gen_music(self, request:GenMusicRequest) -> GenMusicResponse:
        url = urljoin(self.STUDIO_URL, "generate/v2/")

        headers = {"Authorization": f"Bearer {self.suno_cookie.get_token()}"}
        headers.update(COMMON_HEADERS)
        headers.update({"Content-Type": CONTENT_TYPE.JSON.value})

        response = requests.post(url=url, json=request.to_json(),headers=headers)
        logger.debug(f"gen_music: {response.text}")
        # {'detail': [{'type': 'missing', 'loc': ['body', 'params', 'prompt'], 'msg': 'Field required'}]}
        if "detail" in response:
            if "Service Unavailable" in response["detail"]:
                raise ServiceUnavailableException("Service Unavailable")
        response = response.json()
        return GenMusicResponse.from_json(response)
    
    def gen_concat(self,data):
        api = "generate/concat/v2/"
        url = urljoin(self.STUDIO_URL, api)
        response = self.fetch(url, data)
        return response

    def gen_lyrics(self, prompt="") -> str:
        # https://studio-api.suno.ai/api/generate/lyrics/
        url = urljoin(self.STUDIO_URL, "generate/lyrics/")
        data = {"prompt": prompt}
        response = self.fetch(url,  data=data,content_type=CONTENT_TYPE.JSON.value)
        return response.get("id")

    def get_lyrics(self, lyrics_id) -> SunoLyric:
        # https://studio-api.suno.ai/api/generate/lyrics/9f479d79-cf46-4da0-ad51-bb482953b870
        url = urljoin(self.STUDIO_URL, f"generate/lyrics/{lyrics_id}")
        response = self.fetch(url,  method="GET")
        logger.debug(f"get_lyrics: {response}")
        lyrics = SunoLyric.from_json(response)
        return lyrics

    def get_credits(self) -> BillingInfo:
        url = urljoin(self.STUDIO_URL, "billing/info/")
        response = self.fetch(url, method="GET")
        logger.debug(f"get_credits: {response}")
        billing_info = BillingInfo.from_json(response)
        return billing_info
    
    def get_storage_key(self,file_ext) -> SunoUploadAudioKey:
        #  https://studio-api.suno.ai/api/uploads/audio/
        api = "uploads/audio/"
        url = urljoin(self.STUDIO_URL, api)
        data = {"extension":file_ext}
        response = self.fetch(url,  data=data)
        logger.debug(f"get_storage_key: {response}")
        key = SunoUploadAudioKey.from_json(response)
        return key

    def upload_file(self,file_name,file_data, file_ext):
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

        key = self.get_storage_key(file_ext)
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
        try:
            response = requests.post(key.url, data=form_data)
            # 判断 code == 204
            if response.status == 204:
                self.upload_finish(file_name,key.id)

                while True: # 获取上传状态
                    upload_status = self.get_upload_status(key.id)
                    if upload_status.status == SunoUploadAudioStatusEnum.complete:
                        break
                    if upload_status.status == SunoUploadAudioStatusEnum.error:
                        raise Exception(f"upload error: {upload_status.error_message}")
                    time.sleep(3)
                self.initialize_clip(key.id)
            else:
                raise Exception(f"upload error: {response.status} text: {response.text()}")
        except Exception as e:
            logger.error(f"upload file error: {e}")
            return e



    def upload_finish(self, file_name, file_id):
        # https://studio-api.suno.ai/api/uploads/audio/5d03b3ba-cd9e-42cf-ae5b-cf15b3b24841/upload-finish/
        # {"upload_type":"file_upload","upload_filename":"y2282.wav"}
        api = f"uploads/audio/{file_id}/upload-finish/"
        url = urljoin(self.STUDIO_URL, api)
        data = {"upload_type": "file_upload", "upload_filename": file_name}
        return self.fetch(url, data=data)

    def get_upload_status(self, file_id):
        # https://studio-api.suno.ai/api/uploads/audio/5d03b3ba-cd9e-42cf-ae5b-cf15b3b24841/
        api = f"uploads/audio/{file_id}/"
        url = urljoin(self.STUDIO_URL, api)
        response = self.fetch(url, method="GET")
        upload_status = SunoUploadAudioStatus.from_json(response)
        return upload_status
    # https://studio-api.suno.ai/api/uploads/audio/5d03b3ba-cd9e-42cf-ae5b-cf15b3b24841/initialize-clip/
    def initialize_clip(self, file_id):
        api = f"uploads/audio/{file_id}/initialize-clip/"
        url = urljoin(self.STUDIO_URL, api)
        response = self.fetch(url, method="POST")
        return response.get("clip_id")


