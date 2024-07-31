
import asyncio
from time import time
from suno.suno import Suno
from suno.entities import *
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

cookie =""
session_id = ""
async def main():
    suno = Suno(session_id, cookie)

    # result = await suno.get_credits()
    # print(result.to_json())  # print result



    # ids = ["97d0c456-542a-4ef8-aa54-403606aae09a","8ec91087-7dfe-4407-895f-8b101e5ee486"]
    # result = await suno.get_music(ids)
    # for clip in result:
    #     print(clip.to_json())

    # result = await suno_client.gen_lyrics("")
    # print(result)

    # result = await suno_client.get_lyrics("535f879a-cb9a-45af-af6b-efb3742f319c")
    # print(result.to_json())

    prompt = GenMusicRequest()
    prompt.gpt_description_prompt = "I want to make a song about a cat"
    prompt.prompt = ""
    result = await suno.gen_music(prompt)
    print(result.to_json())
    

    
def test():
    logger.debug("start")
    suno = Suno(session_id, cookie)

    # prompt = GenMusicRequest()

    # prompt.gpt_description_prompt = "I want to make a song about a cat"
    # prompt.prompt = ""

    # logger.debug(f"{prompt.to_json()}")
    # result = suno.gen_music(prompt)
    # print(result.to_json())

    ids = ["97d0c456-542a-4ef8-aa54-403606aae09a","8ec91087-7dfe-4407-895f-8b101e5ee486"]
    result = suno.get_music(ids)
    for clip in result:
        print(clip.to_json())
    suno.stop_keep_alive()


if __name__ == "__main__":
    # 运行异步主函数
    # asyncio.run(main())
   test()