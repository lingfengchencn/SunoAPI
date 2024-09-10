
import random
import time
from urllib.parse import urljoin

from jinja2 import Template
import requests
from .entities import ClipStatusEnum
import logging
logger = logging.getLogger(__name__)

class Lyrics:
    id:str
    title:str
    text:str
    status:str

    def to_dict(self):
        return {
            "id":self.id,
            "title":self.title,
            "text":self.text,
            "status":self.status
        }
class Music:
    id: str
    title: str
    video_url: str
    audio_url: str
    image_url: str
    image_large_url: str
    is_video_pending:bool = False
    major_model_version:str = "v3"
    model_name:str = "chirp-v3"
    metadata: dict = {}
    is_liked:bool = False
    display_name: str 
    status: ClipStatusEnum
    created_at:str

    @classmethod
    def from_clip(cls, clip) -> 'Music':
        music = Music()
        music.id = clip["id"]
        music.title = clip["title"]
        music.video_url = clip["video_url"]
        music.audio_url = clip["audio_url"]
        music.image_url = clip["image_url"]
        music.image_large_url = clip["image_large_url"]
        music.is_video_pending = clip["is_video_pending"]
        music.major_model_version = clip["major_model_version"]
        music.model_name = clip["model_name"]
        music.metadata = clip["metadata"]
        music.is_liked = clip["is_liked"]
        music.display_name = clip["display_name"]
        music.status = ClipStatusEnum.from_str(clip["status"])
        music.created_at = clip["created_at"]
        return music

    def to_dict(self):
        return {
            "id":self.id,
            "title":self.title,
            "video_url":self.video_url,
            "audio_url":self.audio_url,
            "image_url":self.image_url,
            "image_large_url":self.image_large_url,
            "is_video_pending":self.is_video_pending,
            "major_model_version":self.major_model_version,
            "model_name":self.model_name,
            "metadata":self.metadata,
            "is_liked":self.is_liked,
            "display_name":self.display_name,
            "status":self.status.value,
            "created_at":self.created_at
        }

class SunoClient:

    API_GEN_LYRICS = "gen_lyrics"
    API_GET_LYRICS = "get_lyrics/{{lyrics_id}}"


    API_GEN_MUSIC_BY_LYRICS = "gen_music_by_lyrics"
    API_GEN_MUSIC_BY_PROMPT = "gen_music_gpt"
    API_GET_MUSIC = "get_music"

    def fetch(self, url,  data=None,method="POST"):
        for _ in range(30):    
            try :
                if method == "POST":
                    response = requests.post(url,json=data)
                else:
                    response = requests.get(url)
                response.raise_for_status()
                
                return response
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    logger.warning("429 Too Many Requests")
                    time.sleep(random.randint(1, 5))
                    continue
                else:
                    raise e

    def __init__(self,base_url:str):
        self.base_url = base_url + "/"

    def gen_lyrics(self, prompt:str) -> Lyrics:
        url = urljoin(self.base_url,self.API_GEN_LYRICS)
        data  = {
            "prompt":prompt
        }
        response = self.fetch(url,data=data)
        lyrics_id = response.json()["lyrics_id"]
        lyrics = Lyrics()
        lyrics.id = lyrics_id
        return lyrics
    
    def get_lyrics(self, lyrics_id:str) -> Lyrics:
        url = urljoin(self.base_url,self.API_GET_LYRICS)
        template = Template(url)
        final_url = template.render(lyrics_id=lyrics_id)
        
        # http://127.0.0.1:8000/api/v1/get_lyrics/24c4d2f1-a290-4e44-861e-150bbee08c83

        response = self.fetch(final_url,method="GET")
        
        data = response.json()["lyrics"]
        lyrics = Lyrics()
        lyrics.id = lyrics_id
        lyrics.title = data.get("title","")
        lyrics.text = data.get("text","")
        lyrics.status = data.get("status","")
        return lyrics
    
    def gen_music_by_lyrics(self, title:str="",
                            lyrics:str="",
                            generation_type:str="TEXT",
                            tags:list=[],
                            negative_tags:list=[],
                            continue_clip_id:str="",
                            continue_at:int=None,
                            infill_start_s:int=None,
                            infill_end_s:int=None,
                            task:str=None,
                            mv:str="chirp-v3-5"
                            ) -> list[Music]:
        url = urljoin(self.base_url,self.API_GEN_MUSIC_BY_LYRICS)
        joined_string = ','.join(tags)
        if len(joined_string) > 120:
            raise ValueError('The length of the comma-separated tags string must be less than 120 characters')
        if len(title) > 80:
            raise ValueError('The length of the title string must be less than 80 characters')
        if len(lyrics) > 3000:
            raise ValueError('The length of the prompt string must be less than 3000 characters')
        
    
        
        if not (lyrics or (tags and len(tags) > 0)):
            raise ValueError('At least one of `lyrics` or `tags` must be provided.')

        data = {
            "title":title,
            "prompt":lyrics,
            "generation_type":generation_type,
            "tags":tags,
            "negative_tags":negative_tags,
            "mv":mv,
            "continue_clip_id":continue_clip_id,
            "continue_at":continue_at,
            "infill_start_s":infill_start_s,
            "infill_end_s":infill_end_s,
            "task":task
        }
        response = self.fetch(url,data=data)
        clips = response.json()["clips"]
        music_list = []
        for clip in clips:
            music = Music.from_clip(clip)
            music_list.append(music)
        return music_list

    def gen_music_by_prompt(self, gpt_description_prompt:str="",
                            prompt:str="",
                            mv:str = "chirp-v3-5",
                            make_instrumental:bool=False, # 是否是乐器
                            user_uploaded_images_b64:list=[]
    ) -> list[Music]:
        # {
        #   "gpt_description_prompt": "string",
        #   "prompt": "string",
        #   "mv": "string",
        #   "make_instrumental": true,
        #   "user_uploaded_images_b64": [
        #     "string"
        #   ]
        # }
        url = urljoin(self.base_url,self.API_GEN_MUSIC_BY_PROMPT)
        data = {
            "gpt_description_prompt":gpt_description_prompt,
            "prompt":prompt,
            "mv":mv,
            "make_instrumental":make_instrumental,
            "user_uploaded_images_b64":user_uploaded_images_b64
        }
        response = self.fetch(url,data=data)
        response.raise_for_status()
        clips = response.json()["clips"]
        music_list = []
        for clip in clips:
            music = Music.from_clip(clip)
            music_list.append(music)
        return music_list

    def get_music_list(self,music_ids:list) -> list[Music]:
        url = urljoin(self.base_url,self.API_GET_MUSIC)
        data = {
            "music_ids":music_ids
        }
        response = self.fetch(url,data=data)
        response.raise_for_status()
        clips = response.json()["clips"]
        return [Music.from_clip(clip) for clip in clips]
