
import asyncio
from time import time
from suno.suno import Suno


cookie = ""
session_id =""
async def main():
    suno = Suno(session_id, cookie)

    result = await suno.get_credits()
    print(result.to_json())  # print result

    ids = ["97d0c456-542a-4ef8-aa54-403606aae09a","8ec91087-7dfe-4407-895f-8b101e5ee486"]
    result = await suno.get_music(ids)
    for clip in result:
        print(clip.to_json())

    # result = await suno_client.gen_lyrics("")
    # print(result)

    # result = await suno_client.get_lyrics("535f879a-cb9a-45af-af6b-efb3742f319c")
    # print(result.to_json())
    

    
 

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())