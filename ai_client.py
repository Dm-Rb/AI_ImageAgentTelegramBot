from config import config_
import aiohttp
import base64


class APIClientSupportBy:

    def __init__(self):
        self.API_BASE_URL = config_.API_BASE_URL
        self.EP_GENERATIONS = config_.EP_GENERATIONS
        self.EP_EDITS = config_.EP_EDITS
        self.headers = {
            "Authorization": f"Bearer {str(config_.API_TOKEN)}"
            }

    async def request_to_api_dall_e_3(self, prompt: str):
        session = aiohttp.ClientSession()
        try:
            body_ = {
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024"
                  }
            url = f"{self.API_BASE_URL}{self.EP_GENERATIONS}"
            async with session.post(url=url, json=body_, headers=self.headers) as resp:
                resp.raise_for_status()
                response_json = await resp.json()

                # response_json = {'created': int, 'data': [{'b64_json': '', 'url': str}], 'usage': None}
                data = response_json.get('data', [])
                if data:
                    image_url = data[0]['url']
                    # апи возвращает временную ссылку на изображение. качаем файл и оборачиваем бинарник в io.BytesIO
                    image_bytes = await self.download_image(image_url, session)
                    return image_bytes
        except Exception as e:
            raise e

        finally:
            await session.close()

    @staticmethod
    async def download_image(url: str, session) -> str:
        async with session.get(url) as response:
            response.raise_for_status()
            # читаем изображение в память
            image_bytes = await response.read()
            return image_bytes

    async def request_to_api_gpt_image_1(self, prompt: str, images_bytes: list):
        session = aiohttp.ClientSession()
        # ендоинт на редактирование не принимает тело с json, делаем через формы

        try:
            data = aiohttp.FormData()
            data.add_field("model", "gpt-image-1")
            data.add_field("prompt", prompt)
            data.add_field("size", "1024x1024")
            # добавляем все изображения в поле image[]
            for idx, item in enumerate(images_bytes, 1):
                file_bytes = item
                filename = f"input_{idx}.png"
                data.add_field(
                    name="image[]",  # ← именно так — несколько раз с одним именем
                    value=file_bytes,
                    filename=filename,
                    content_type="image/png"
                )

            url = f"{self.API_BASE_URL}{self.EP_EDITS}"
            async with session.post(url=url, data=data, headers=self.headers) as resp:
                resp.raise_for_status()
                response_json = await resp.json()
                if response_json:
                    response_images_bytes = []
                    for item in response_json.get('data', []):
                        response_images_bytes.append(base64.b64decode(item['b64_json']))
                    return response_images_bytes

        except Exception as ex_:
            raise ex_
        finally:
            await session.close()


ai_client = APIClientSupportBy()
