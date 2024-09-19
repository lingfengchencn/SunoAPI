from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, FieldValidationInfo

class GenLyricsRequest(BaseModel):
    prompt: str

    def to_dict(self):
        return {
            "prompt": self.prompt
        }

class GenLyricsMusicRequest(BaseModel):
    title: Optional[str] = Field(default="", max_length=80)
    prompt: Optional[str] = Field(default="", max_length=3000)
    # {"prompt":"风吹","generation_type":"TEXT","tags":"deep techno","negative_tags":"","mv":"chirp-v3-5","title":"对伐",
    # "continue_clip_id":null,"continue_at":null,"infill_start_s":null,"infill_end_s":null,"task":""}
    generation_type:str = "TEXT"
    tags: Optional[List[str]] = Field(default=[])
    negative_tags:list = []
    mv:str = "chirp-v3-5"
    continue_clip_id:Optional[str] = None
    continue_at:Optional[int] = None
    infill_start_s:Optional[int] = None
    infill_end_s:Optional[int] = None
    task:Optional[str] = ""

    # @field_validator("title", "prompt")
    # def validate_length(cls, value, info: FieldValidationInfo):
    #     max_length = info.field_info.extra.get('max_length')
    #     if max_length and len(value) > max_length:
    #         raise ValueError(f'{info.field_name} must be less than {max_length} characters')
        # return value

    @field_validator('tags')
    def validate_style_of_music_length(cls, value):
        # 将列表转换为逗号分隔的字符串
        joined_string = ','.join(value)
        if len(joined_string) > 120:
            raise ValueError('The length of the comma-separated tags string must be less than 120 characters')
        return value
    
    @model_validator(mode='before')
    def check_at_least_one_field(cls, values):
        prompt = values.get('prompt')
        tags = values.get('tags')
        
        if not (prompt or (tags and len(tags) > 0)):
            raise ValueError('At least one of `prompt` or `tags` must be provided.')
        
        return values
    
    def to_dict(self):
        return {
            "prompt": self.prompt,
            "generation_type": self.generation_type,
            "tags": self.tags,
            "negative_tags": self.negative_tags,
            "mv": self.mv,
            "title": self.title,
            "continue_clip_id": self.continue_clip_id,
            "continue_at": self.continue_at,
            "infill_start_s": self.infill_start_s,
            "infill_end_s": self.infill_end_s,
            "task": self.task
        }

    
class GenGPTMusicRequest(BaseModel):
    # {"gpt_description_prompt":"aha","mv":"chirp-v3-5","prompt":"","make_instrumental":false,"user_uploaded_images_b64":[],"generation_type":"TEXT"}
    mv:str = "chirp-v3-5"
    prompt:str = ""
    gpt_description_prompt:str = Field( max_length=200)
    make_instrumental:bool = False # 是否乐器
    user_uploaded_images_b64:List[str] = []

    def to_dict(self ):
        return {
            "gpt_description_prompt": self.gpt_description_prompt,
            "mv": self.mv,
            "prompt": self.prompt,
            "make_instrumental": self.make_instrumental,
            "user_uploaded_images_b64": self.user_uploaded_images_b64
        }

class GetMusicRequest(BaseModel):
    music_ids: List[str] 
    