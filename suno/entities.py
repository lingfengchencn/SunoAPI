
from datetime import datetime
from enum import Enum
import json
from typing import List


class SunoAuthTypeEnum(Enum):
    COOKIE = "COOKIE"
    JWT = "JWT"

class ClipMetaData:
    tags: str
    prompt: str
    gpt_description_prompt: str
    audio_prompt_id: str
    history: str
    concat_history: str
    stem_from_id: str
    type: str
    duration: str
    refund_credits: str
    stream: bool
    infill: str
    has_vocal: str
    is_audio_upload_tos_accepted: str
    error_type: str
    error_message: str

    @classmethod
    def from_json(cls, json_data):
        metadata = ClipMetaData()
        metadata.tags = json_data.get("tags")
        metadata.prompt = json_data.get("prompt")
        metadata.gpt_description_prompt = json_data.get("gpt_description_prompt")
        metadata.audio_prompt_id = json_data.get("audio_prompt_id")
        metadata.history = json_data.get("history")
        metadata.concat_history = json_data.get("concat_history")
        metadata.stem_from_id = json_data.get("stem_from_id")
        metadata.type = json_data.get("type")
        metadata.duration = json_data.get("duration")
        metadata.refund_credits = json_data.get("refund_credits")
        metadata.stream = json_data.get("stream")
        metadata.infill = json_data.get("infill")
        metadata.has_vocal = json_data.get("has_vocal")
        metadata.is_audio_upload_tos_accepted = json_data.get("is_audio_upload_tos_accepted")
        metadata.error_type = json_data.get("error_type")
        metadata.error_message = json_data.get("error_message")
        return metadata
    
    def to_json(self):
        return {
            "tags": self.tags,
            "prompt": self.prompt,
            "gpt_description_prompt": self.gpt_description_prompt,
            "audio_prompt_id": self.audio_prompt_id,
            "history": self.history,
            "concat_history": self.concat_history,
            "stem_from_id":self.stem_from_id,
            "type": self.type,
            "duration": self.duration,
            "refund_credits": self.refund_credits,
            "stream": self.stream,
            "infill": self.infill,
            "has_vocal": self.has_vocal,
            "is_audio_upload_tos_accepted": self.is_audio_upload_tos_accepted,
            "error_type":self.error_type,
            "error_message": self.error_message
        }
class SunoToken:
    object:str 
    jwt: str

    @classmethod
    def from_json(cls, json_data):
        token = SunoToken()
        token.object = json_data.get("object")
        token.jwt = json_data.get("jwt")
        return token

    def to_json(self):
        return {
            "object": self.object,
            "jwt": self.jwt
        }



class Clip:
    # {
    #         "id": "afe19a84-2a50-4b19-a502-818af07172af",
    #         "video_url": "",
    #         "audio_url": "https://audiopipe.suno.ai/?item_id=afe19a84-2a50-4b19-a502-818af07172af",
    #         "image_url": "https://cdn2.suno.ai/image_afe19a84-2a50-4b19-a502-818af07172af.jpeg",
    #         "image_large_url": "https://cdn2.suno.ai/image_large_afe19a84-2a50-4b19-a502-818af07172af.jpeg",
    #         "is_video_pending": false,
    #         "major_model_version": "v3.5",
    #         "model_name": "chirp-v3",
    #         "metadata": {
    #             "tags": "\u7535\u5b50 \u65cb\u5f8b\u611f \u6162\u6447 dj",
    #             "prompt": "[Verse]\n\u591c\u7a7a\u95ea\u70c1\u7684\u706f\u5149\n\u97f3\u4e50\u628a\u7a7a\u6c14\u70b9\u4eae\n\u6211\u4eec\u8df3\u5165\u8fd9\u7247\u6d77\u6d0b\n\u8ddf\u968f\u5fc3\u8df3\u53bb\u6d41\u6d6a\n\n[Verse 2]\n\u591c\u8272\u7b3c\u7f69\u7684\u8857\u9053\n\u811a\u6b65\u58f0\u56de\u8361\u5bc2\u5be5\n\u8eab\u8fb9\u4eba\u5f71\u6e10\u6e10\u5c11\n\u72ec\u81ea\u5f9c\u5f89\u4e0d\u89c9\u5f97\u51b7\n\n[Chorus]\n\u8ba9\u97f3\u4e50\u5ef6\u7eed\n\u6211\u4eec\u5fc3\u5728\u8df3\u52a8\n\u968f\u8282\u594f\u6447\u6446\n\u5c3d\u60c5\u91ca\u653e\n\n[Verse 3]\n\u5fae\u98ce\u8f7b\u62c2\u6211\u7684\u8138\n\u65f6\u95f4\u6084\u6084\u6e9c\u8d70\u7684\u77ac\u95f4\n\u6bcf\u4e00\u4e2a\u97f3\u7b26\u7684\u751c\n\u90fd\u5728\u591c\u91cc\u523b\u753b\u6210\u68a6\n\n[Bridge]\n\u95ed\u4e0a\u773c\u542c\u5fc3\u58f0\n\u591c\u7684\u8282\u594f\u5728\u547c\u5e94\n\u5b64\u5355\u9010\u6e10\u88ab\u541e\u566c\n\u97f3\u4e50\u5e2e\u6211\u653e\u677e\u5fc3\u60c5\n\n[Chorus]\n\u8ba9\u97f3\u4e50\u5ef6\u7eed\n\u6211\u4eec\u5fc3\u5728\u8df3\u52a8\n\u968f\u8282\u594f\u6447\u6446\n\u5c3d\u60c5\u91ca\u653e",
    #             "gpt_description_prompt": "\u521b\u5efa\u4e00\u9996\u6162\u6447\u7684DJ",
    #             "audio_prompt_id": null,
    #             "history": null,
    #             "concat_history": null,
    #             "stem_from_id": null,
    #             "type": "gen",
    #             "duration": null,
    #             "refund_credits": null,
    #             "stream": true,
    #             "infill": null,
    #             "has_vocal": null,
    #             "is_audio_upload_tos_accepted": null,
    #             "error_type": null,
    #             "error_message": null
    #         },
    #         "is_liked": false,
    #         "user_id": "38b7cb66-f5fc-454e-9848-4eed02bd62d2",
    #         "display_name": "RadicalClickTracks019",
    #         "handle": "radicalclicktracks019",
    #         "is_handle_updated": false,
    #         "avatar_image_url": "https://cdn1.suno.ai/defaultBlue.webp",
    #         "is_trashed": false,
    #         "reaction": null,
    #         "created_at": "2024-07-29T04:24:43.070Z",
    #         "status": "streaming",
    #         "title": "\u591c\u7684\u8282\u594f",
    #         "play_count": 0,
    #         "upvote_count": 0,
    #         "is_public": false
    #     }

    id:str = ""
    video_url:str  = ""
    audio_url:str  = ""
    image_url:str  = ""
    image_large_url:str  = ""
    is_video_pending:bool = False
    major_model_version:str  = ""
    model_name:str  = ""
    metadata:ClipMetaData 
    is_liked:bool = False
    user_id:str  = ""
    display_name:str  = ""
    handle:str  = ""
    is_handle_updated:bool = False
    avatar_image_url:str  = ""
    is_trashed:bool = False
    reaction:str  = None
    created_at:datetime = ""
    status:str  = ""
    title:str  = ""
    play_count:int = 0
    upvote_count:int = 0
    is_public:bool = False

    @classmethod
    def from_json(cls, json_data):
        clip = Clip()
        clip.id = json_data.get("id")
        clip.video_url = json_data.get("video_url")
        clip.audio_url = json_data.get("audio_url")
        clip.image_url = json_data.get("image_url")
        clip.image_large_url = json_data.get("image_large_url")
        clip.is_video_pending = json_data.get("is_video_pending")
        clip.major_model_version = json_data.get("major_model_version")
        clip.model_name = json_data.get("model_name")
        clip.metadata = ClipMetaData.from_json(json_data.get("metadata"))
        clip.is_liked = json_data.get("is_liked")
        clip.user_id = json_data.get("user_id")
        clip.display_name = json_data.get("display_name")
        clip.handle = json_data.get("handle")
        clip.is_handle_updated = json_data.get("is_handle_updated")
        clip.avatar_image_url = json_data.get("avatar_image_url")
        clip.is_trashed = json_data.get("is_trashed")
        clip.reaction = json_data.get("reaction")
        clip.created_at = datetime.fromisoformat(json_data.get("created_at").replace("Z", "+00:00"))
        clip.status = json_data.get("status")
        clip.title = json_data.get("title")
        clip.play_count = json_data.get("play_count")
        clip.upvote_count = json_data.get("upvote_count")
        clip.is_public = json_data.get("is_public")
        return clip
    def to_json(self):
        return {
            "id": self.id,
            "video_url": self.video_url,
            "audio_url": self.audio_url,
            "image_url": self.image_url,
            "image_large_url": self.image_large_url,
            "is_video_pending": self.is_video_pending,
            "major_model_version": self.major_model_version,
            "model_name": self.model_name,
            "metadata": self.metadata.to_json(),
            "is_liked": self.is_liked,
            "user_id": self.user_id,
            "display_name": self.display_name,
            "handle": self.handle,
            "is_handle_updated": self.is_handle_updated,
            "avatar_image_url": self.avatar_image_url,
            "is_trashed": self.is_trashed,
            "reaction": self.reaction,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") , # "2024-07-29 04:24:43.070"
            "status": self.status,
            "title": self.title,
            "play_count": self.play_count,
            "upvote_count": self.upvote_count,
            "is_public": self.is_public

        }

class GenMusicRequest:
    # {"gpt_description_prompt":"创建一首慢摇的DJ","mv":"chirp-v3-5","prompt":"","make_instrumental":false,"user_uploaded_images_b64":[]}
    gpt_description_prompt:str = ""
    mv:str = "chirp-v3-5"
    prompt:str = ""
    make_instrumental:bool = False
    user_uploaded_images_b64:List[str] = []
    def to_json(self):
        return {
            "gpt_description_prompt": self.gpt_description_prompt,
            "mv": self.mv,
            "prompt": self.prompt,
            "make_instrumental": self.make_instrumental,
            "user_uploaded_images_b64": self.user_uploaded_images_b64
        }

class GenMusicResponse:

#     {
#     "id": "3e1ce505-95fa-401b-a6be-5f74cdcd6b48",
#     "clips": [
#    
#     ],
#     "metadata": {
#         "tags": null,
#         "prompt": "",
#         "gpt_description_prompt": "\u521b\u5efa\u4e00\u9996\u6162\u6447\u7684DJ",
#         "audio_prompt_id": null,
#         "history": null,
#         "concat_history": null,
#         "stem_from_id": null,
#         "type": "gen",
#         "duration": null,
#         "refund_credits": null,
#         "stream": true,
#         "infill": null,
#         "has_vocal": null,
#         "is_audio_upload_tos_accepted": null,
#         "error_type": null,
#         "error_message": null
#     },
#     "major_model_version": "v3",
#     "status": "complete",
#     "created_at": "2024-07-29T04:24:43.060Z",
#     "batch_size": 1
# }

    id:str = ""
    clips:List[Clip] = []
    metadata:ClipMetaData
    major_model_version:str = ""
    status:str = ""
    created_at:datetime = ""
    batch_size:int = 0

    @classmethod
    def from_json(cls, json_data):
        gen_music_response = GenMusicResponse()
        gen_music_response.id = json_data.get("id")
        gen_music_response.clips = [Clip.from_json(clip) for clip in json_data.get("clips")]
        gen_music_response.metadata = ClipMetaData.from_json(json_data.get("metadata"))
        gen_music_response.major_model_version = json_data.get("major_model_version")
        gen_music_response.status = json_data.get("status")
        gen_music_response.created_at = datetime.fromisoformat(json_data.get("created_at").replace("Z", "+00:00"))
        gen_music_response.batch_size = json_data.get("batch_size")
        return gen_music_response
    
    def to_json(self):
        return {
            "id": self.id,
            "clips": [clip.to_json() for clip in self.clips],
            "metadata": self.metadata.to_json(),
            "major_model_version": self.major_model_version,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "batch_size": self.batch_size
        }
    
class CreditPack:
    id:str = ""
    amount:int = 0
    price_usd:float = 0

    @classmethod
    def from_json(cls, json_data):
        creadit_pack = CreditPack()
        creadit_pack.id = json_data.get("id")
        creadit_pack.amount = json_data.get("amount")
        creadit_pack.price_usd = json_data.get("price_usd")
        return creadit_pack
    def to_json(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "price_usd": self.price_usd
        }

class Plan:
    id:str = ""
    level:int = 0
    name:str = ""
    features:str = ""
    monthly_price_usd:float = 0

    @classmethod
    def from_json(cls, json_data):
        plan = Plan()
        plan.id = json_data.get("id")
        plan.level = json_data.get("level")
        plan.name = json_data.get("name")
        plan.features = json_data.get("features")
        plan.monthly_price_usd = json_data.get("monthly_price_usd")
        return plan
    
    def to_json(self):
        return {
            "id": self.id,
            "level": self.level,
            "name": self.name,
            "features": self.features,
            "monthly_price_usd": self.monthly_price_usd
        }

class BillingInfo:
#     {
#     "subscription_platform": null,
#     "is_active": false,
#     "is_past_due": false,
#     "credits": 610,
#     "subscription_type": false,
#     "renews_on": null,
#     "cancel_on": null,
#     "period": null,
#     "changing_to": null,
#     "monthly_usage": 0,
#     "monthly_limit": 50,
#     "credit_packs": [
#         {
#             "id": "a79f3640-d366-4c21-8d85-b35dad751f70",
#             "amount": 500,
#             "price_usd": 4
#         },
#         {
#             "id": "98a80157-c3af-489f-84ab-a1db33913d1c",
#             "amount": 1000,
#             "price_usd": 8
#         },
#         {
#             "id": "00f996ac-7674-42db-8135-851f25cac2c0",
#             "amount": 2000,
#             "price_usd": 16
#         },
#         {
#             "id": "4cb5c6d9-bdb2-4bc1-9f62-c2cc55d48586",
#             "amount": 4000,
#             "price_usd": 30
#         }
#     ],
#     "plan": null,
#     "plans": [
#         {
#             "id": "4497580c-f4eb-4f86-9f0e-960eb7c48d7d",
#             "level": 0,
#             "name": "Basic Plan",
#             "features": "50 credits renew daily (10 songs)\r\nNon-commercial terms\r\nNo credit top ups\r\nShared generation queue\r\n2 running jobs at once",
#             "monthly_price_usd": 0.0
#         },
#         {
#             "id": "3eaebef3-ef46-446a-931c-3d50cd1514f1",
#             "level": 10,
#             "name": "Pro Plan",
#             "features": "2,500 credits renew monthly (500 songs)\r\nGeneral commercial terms\r\nOptional credit top ups\r\nPriority generation queue\r\n10 running jobs at once",
#             "monthly_price_usd": 10.0
#         },
#         {
#             "id": "e1235dd7-9f4d-4738-aeb2-1470466cba27",
#             "level": 30,
#             "name": "Premier Plan",
#             "features": "10,000 credits renew monthly (2,000 songs)\r\nGeneral commercial terms\r\nOptional credit top ups\r\nPriority generation queue\r\n10 running jobs at once",
#             "monthly_price_usd": 30.0
#         }
#     ],
#     "total_credits_left": 660
# }
    subscription_platform:str = ""
    is_active:bool = False
    is_past_due:bool = False
    credits:int = 0
    subscription_type:bool = False
    renews_on:str = ""
    cancel_on:str = ""
    period:str = ""
    changing_to:str = ""
    monthly_usage:int = 0
    monthly_limit:int = 0
    credit_packs:List[CreditPack] = []
    plan:str = ""
    plans:List[Plan] = []
    total_credits_left:int = 0

    @classmethod
    def from_json(cls, json_data):
        billing_info = BillingInfo()
        billing_info.subscription_platform = json_data.get("subscription_platform")
        billing_info.is_active = json_data.get("is_active")
        billing_info.is_past_due = json_data.get("is_past_due")
        billing_info.credits = json_data.get("credits")
        billing_info.subscription_type = json_data.get("subscription_type")
        billing_info.renews_on = json_data.get("renews_on")
        billing_info.cancel_on = json_data.get("cancel_on")
        billing_info.period = json_data.get("period")
        billing_info.changing_to = json_data.get("changing_to")
        billing_info.monthly_usage = json_data.get("monthly_usage")
        billing_info.monthly_limit = json_data.get("monthly_limit")
        billing_info.credit_packs = [CreditPack.from_json(credit_pack) for credit_pack in json_data.get("credit_packs")]
        billing_info.plan = json_data.get("plan")
        billing_info.plans = [Plan.from_json(plan) for plan in json_data.get("plans")]
        billing_info.total_credits_left = json_data.get("total_credits_left")
        return billing_info

    def to_json(self):
        return {
            "subscription_platform": self.subscription_platform,
            "is_active": self.is_active,
            "is_past_due": self.is_past_due,
            "credits": self.credits,
            "subscription_type": self.subscription_type,
            "renews_on": self.renews_on,
            "cancel_on": self.cancel_on,
            "period": self.period,
            "changing_to": self.changing_to,
            "monthly_usage": self.monthly_usage,
            "monthly_limit": self.monthly_limit,
            "credit_packs": [credit_pack.to_json() for credit_pack in self.credit_packs],
            "plan": self.plan,
            "plans": [plan.to_json() for plan in self.plans],
            "total_credits_left": self.total_credits_left
        }

class SunoUploadAudioFileds:
    content_type:str = ""
    key:str = ""
    AWSAccessKeyId:str = ""
    policy:str = ""
    signature:str = ""

    @classmethod
    def from_json(cls, json_data):
        fields = SunoUploadAudioFileds()
        fields.content_type = json_data.get("Content-Type")
        fields.key = json_data.get("key")
        fields.AWSAccessKeyId = json_data.get("AWSAccessKeyId")
        fields.policy = json_data.get("policy")
        fields.signature = json_data.get("signature")
        return fields
    def to_json(self):
        return {
            "Content-Type": self.content_type,
            "key": self.key,
            "AWSAccessKeyId": self.AWSAccessKeyId,
            "policy": self.policy,
            "signature": self.signature
        }

class SunoUploadAudioKey:
    # {
    #     "id": "5d03b3ba-cd9e-42cf-ae5b-cf15b3b24841",
    #     "url": "https://suno-uploads.s3.amazonaws.com/",
    #     "fields": {
    #         "Content-Type": "audio/wav",
    #         "key": "raw_uploads/5d03b3ba-cd9e-42cf-ae5b-cf15b3b24841.wav",
    #         "AWSAccessKeyId": "AKIA2V4GXGDKJMTPWLXO",
    #         "policy": "eyJleHBpcmF0aW9uIjogIjIwMjQtMDctMjlUMTA6MTc6NTNaIiwgImNvbmRpdGlvbnMiOiBbWyJjb250ZW50LWxlbmd0aC1yYW5nZSIsIDAsIDEwNDg1NzYwMF0sIFsic3RhcnRzLXdpdGgiLCAiJENvbnRlbnQtVHlwZSIsICJhdWRpby93YXYiXSwgeyJidWNrZXQiOiAic3Vuby11cGxvYWRzIn0sIHsia2V5IjogInJhd191cGxvYWRzLzVkMDNiM2JhLWNkOWUtNDJjZi1hZTViLWNmMTViM2IyNDg0MS53YXYifV19",
    #         "signature": "wB1bZvq7YkZWENfDKNZb7dBIqsg="
    #     }
    # }
    id:str = ""
    url:str = ""
    fields:SunoUploadAudioFileds

    @classmethod
    def from_json(cls, json_data):
        upload_key = SunoUploadAudioKey()
        upload_key.id = json_data.get("id")
        upload_key.url = json_data.get("url")
        upload_key.fields = SunoUploadAudioFileds.from_json(json_data.get("fields"))
        return upload_key
    def to_json(self):
        return {
            "id": self.id,
            "url": self.url,
            "fields": self.fields.to_json()
        }

class SunoUploadAudioStatusEnum(Enum):
    # processing
    # passed_artist_moderation
    # complete
    processing = "processing"
    passed_artist_moderation = "passed_artist_moderation"
    complete = "complete"
    error = "error"

    def __str__(self):
        return self.value
    def from_str(cls, value):
        for member in cls:
            if member.value == value:
                return member
class SunoUploadAudioStatus:
    #{
    #     "id": "5d03b3ba-cd9e-42cf-ae5b-cf15b3b24841",
    #     "status": "processing",
    #     "error_message": null,
    #     "s3_id": null,
    #     "title": "",
    #     "image_url": null
    # }
    id:str = ""
    status:SunoUploadAudioStatusEnum = ""
    error_message:str = ""
    s3_id:str = ""
    title:str = ""
    image_url:str = ""

    @classmethod
    def from_json(cls, json_data):
        upload_status = SunoUploadAudioStatus()
        upload_status.id = json_data.get("id")
        upload_status.status = SunoUploadAudioStatusEnum.from_str(json_data.get("status"))
        upload_status.error_message = json_data.get("error_message")
        upload_status.s3_id = json_data.get("s3_id")
        upload_status.title = json_data.get("title")
        upload_status.image_url = json_data.get("image_url")
        return upload_status
    
    def to_json(self):
        return {
            "id": self.id,
            "status": str(self.status),
            "error_message": self.error_message,
            "s3_id": self.s3_id,
            "title": self.title,
            "image_url": self.image_url
        }
    
class SunoLyricGenerageStatusEnum(Enum):
    RUNNING = "running"
    COMPLETE = "complete"

    def __str__(self):
        return self.value
    @classmethod
    def from_str(cls, value):
        for member in cls:
            if member.value == value:
                return member
    
class SunoLyric:
    #{
    #     "text": "[Verse]\nWalking down the street\nSunny skies are bright\nStep to the beat\nEverything feels right\n\n[Verse 2]\nWhistling a tune\nClouds floating away\nAfternoon in June\nIt's a breezy kind of day\n\n[Chorus]\nBreezy daydream\nLiving in a scene\nEverything's serene\nBreezy daydream\n\n[Verse 3]\nLaughing as we go\nDancing in the sun\nFeeling in the flow\nHaving so much fun\n\n[Bridge]\nClose my eyes and see\nThe world just fades away\nIt's just you and me\nLiving for today\n\n[Chorus]\nBreezy daydream\nLiving in a scene\nEverything's serene\nBreezy daydream",
    #     "title": "Breezy Dream",
    #     "status": "complete"
    # }
    text:str = ""
    title:str = ""
    status:SunoLyricGenerageStatusEnum = ""

    @classmethod
    def from_json(cls, json_data):
        lyric = SunoLyric()
        lyric.text = json_data.get("text")
        lyric.title = json_data.get("title")
        lyric.status = SunoLyricGenerageStatusEnum.from_str(json_data.get("status"))
        return lyric
    def to_json(self):
        return {
            "text": self.text,
            "title": self.title,
            "status": str(self.status)
        }