from aiogram import Router, F, Bot
from aiogram.types import Message, BufferedInputFile
from aiogram.utils.chat_action import ChatActionSender
from aiogram_media_group import media_group_handler
from database_crud import users_database
from ai_client import ai_client


router = Router()


@router.message(F.media_group_id, F.photo)
@media_group_handler  # ← декоратор собирает альбом в list[Message]
async def photos_album_handler(messages: list[Message]):
    """Хендлер для события пользователь отправляет группу изображение в режиме фото"""
    # messages — уже собранный альбом (2–10 сообщений)
    # проверяем наличие текста
    # caption это дополнительный текст к изображению(ям)
    captions = [m.caption for m in messages if m.caption]
    if not captions:
        return await messages[0].answer(text='Вы не добавили текст с промтом к изображениям')
    bot = messages[0].bot  # берём bot из любого сообщения

    # показывает статус 'печатает' пока код выполняется внутри блока
    async with ChatActionSender.typing(
            bot=bot,
            chat_id=messages[0].chat.id):
        text = " ".join(c.strip() for c in captions if c)
        photo_file_ids = [m.photo[-1].file_id for m in messages]  # вытягиваем file_id для каждого изображения
        photos_bytes: list = []  # результирующий массив для хранения байтов каждого изображения
        for photo_file_id in photo_file_ids:
            photo_bytes = await bot.download(photo_file_id)  # получаем байты изображения по его telegram file_id
            photos_bytes.append(photo_bytes)  # пихаем в результирующий массив

        # передаём данные в метод объекта по взаимодействию с ai, ждём результат
        image_files: list = await ai_client.request_to_api_gpt_image_1(
            images_bytes=photos_bytes,
            prompt=text.strip()
        )
        # тут reply_document выёбывается на bytes, поэтому перед отправкой оборачиваем каждый в BufferedInputFile
        for document in [BufferedInputFile(file=item, filename="ai_generated.png") for item in image_files]:
            # итерируемся и отдаём ответом на сообщение пользователю в режиме Документ
            await messages[0].reply_document(document=document)
        return


@router.message(F.photo)
async def photo_handler(message: Message):
    """
    Хендлер для события пользователь отправляет одно изображение в режиме фото
    """
    # message.photo[-1] — самая большая доступная фотография
    # тут и далее код крайне похож на photos_album_handler, подробные комменты излишни
    photo = message.photo[-1]
    photo_bytes = await message.bot.download(photo.file_id)
    caption = message.caption  # это дополнительный текст к изображению
    if not caption:
        return await message.answer(text='Вы не добавили текст с промтом к изображению')
    async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id):

        image_files: list = await ai_client.request_to_api_gpt_image_1(
            images_bytes=[photo_bytes],
            prompt=caption.strip()
        )
        for document in [BufferedInputFile(file=item, filename="ai_generated.png") for item in image_files]:
            await message.reply_document(document=document)
        return


@router.message(lambda m: m.reply_to_message is not None)
async def reply_document(message: Message, bot: Bot):

    reply_msg = message.reply_to_message
    prompt = message.text.strip()  # телеграм обязательно требует текст на реплай сообщения, доп. проверка не нужна
    # проверяем, что отвечают на сообщение с документом
    if not reply_msg.document:
        return
    async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id):

        file_id = reply_msg.document.file_id  # получаем file_id
        file = await bot.get_file(file_id)  # получаем информацию о файле
        file_bytes = await bot.download_file(file.file_path)  # скачиваем файл в ram память
        image_bytes = file_bytes.read()  # file_bytes — это BytesIO, нужно прочитать

        # отправляем в API для редактирования
        edited_images: list = await ai_client.request_to_api_gpt_image_1(
            images_bytes=[image_bytes],
            prompt=prompt
        )
        for document in [BufferedInputFile(file=item, filename="ai_generated.png") for item in edited_images]:
            await message.reply_document(document=document)
        return


@router.message(F.text)
async def only_text(message: Message, bot: Bot):
    user_id = message.from_user.id
    if not users_database.cash.get(user_id):
        return

    user_text = message.text.strip()
    # показываем "печатает" пока выполняется код внутри блока
    async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id):
        # получаем байты изображения из DALL-E 3
        image_bytes = await ai_client.request_to_api_dall_e_3(user_text)
        # создаём объект BufferedInputFile
        image_file = BufferedInputFile(file=image_bytes, filename="image.png")

        await message.reply_document(
            document=image_file,
        )
