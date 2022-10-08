from requests import get
from httpx import AsyncClient

from re import findall
from io import BytesIO
from PIL import Image


def convert_image(image, extention):  # "JPEG"
    byteImgIO = BytesIO()
    byteImg = Image.open(BytesIO(image)).convert("RGB")
    byteImg.save(byteImgIO, extention)
    byteImgIO.seek(0)
    return byteImgIO


async def tt_videos_or_images(url):
    headers1 = {
        "Host": "vm.tiktok.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
        "Accept": "text/html, application/xhtml+xml, application/xml; q=0.9, image/avif, image/webp, */*; q=0.8"
    }

    async with AsyncClient() as client:
        r1 = await client.get(url, headers=headers1)
    print("r1", r1.status_code)
    if r1.status_code ==301:
        video_id = findall('a href="https://www.tiktok.com/@.*?/video/(\d+)', r1.text)[0]
    #403
    else:
        video_id = findall("video&#47;(\d+)", r1.text)[0]

    url2 = f"http://api16-normal-useast5.us.tiktokv.com/aweme/v1/aweme/detail/?aweme_id={video_id}"
    headers2 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"}
    async with AsyncClient() as client:
        r2 = await client.get(url2, headers=headers2)
    print("r2", r1.status_code)
    resp = r2.json()

    is_video = len(resp["aweme_detail"]["video"]["bit_rate"]) > 0
    print("is_video", is_video)

    nickname = resp["aweme_detail"]["author"]["nickname"]
    desc = resp["aweme_detail"]["desc"]
    statistic = resp["aweme_detail"]["statistics"]
    music = resp["aweme_detail"]["music"]["play_url"]["uri"]
    if is_video:
        cover_url = resp["aweme_detail"]["video"]["origin_cover"]["url_list"][0]
        videos_url = resp["aweme_detail"]["video"]["bit_rate"][0]["play_addr"]["url_list"]
        return {"is_video": True, "cover": cover_url, "items": videos_url, "nickname": nickname, "desc": desc, "statistic": statistic, "music": music}
    else:
        images_url = []
        images = resp["aweme_detail"]["image_post_info"]["images"]
        for i in images:
            if len(i["display_image"]["url_list"]) > 0:
                images_url.append(i["display_image"]["url_list"][0])
            else:
                print("err. images_url 0 len")
        return {"is_video": False, "cover": None, "items": images_url, "nickname": nickname, "desc": desc, "statistic": statistic, "music": music}