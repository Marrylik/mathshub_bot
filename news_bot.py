import asyncio
import logging
import time
from collections import deque

import feedparser
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Text
from aiogram.filters.command import Command

from config_reader import config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

#creat start command to greet user by name
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    logging.info(f'{user_id=}{user_name=} {time.asctime()}')
    await message.answer(f'Привет, {user_name}!')
    await asyncio.sleep(1)
    await message.answer('Почитаешь свежие новости?')
    await asyncio.sleep(1)
    await message.answer('Жми /news')

#creat news command with specified url and following interaction option to read economics news, latest 10 business and economics news are to be shown to the user
@dp.message(Command("news"))
async def cmd_news(message: types.Message, url = 'https://www.kommersant.ru/RSS/section-business.xml', follow = True):
    user_name = message.from_user.first_name
    rss_link = url
    httpx_client = httpx.AsyncClient()
    response = await httpx_client.get(rss_link)
    feed = feedparser.parse(response.text)
    x = 0
    for entry in feed.entries[0::]:
        summary = entry['summary']
        title = entry['title']
        url = entry['link']
        news_text = f'{title}\n{summary}'
        x += 1
        if title in posted_q:
            continue
        elif x < 11:
            await message.answer(f'{url}\n{news_text}')
            await asyncio.sleep(1)
        posted_q.appendleft(title)

    if follow == True:
        await asyncio.sleep(5)
        kb = [[types.KeyboardButton(text="Ещё новостей"), types.KeyboardButton(text="Спасибо не хочу")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                         input_field_placeholder="Выберете вариант ответа")
        await message.answer(f"{user_name}, хочешь еще экономических новостей?", reply_markup=keyboard)

    if follow == False:
        await asyncio.sleep(3)
        await message.answer("Отличного дня!")
        await asyncio.sleep(1)
        await message.answer(f"Заходи еще!")


@dp.message(Text("Ещё новостей"))
async def more_news(message: types.Message):
    await message.reply("Приятного чтения!", reply_markup=types.ReplyKeyboardRemove())
    await cmd_news(message, url = 'https://www.kommersant.ru/RSS/section-economics.xml', follow = False)


@dp.message(Text("Спасибо не хочу"))
async def no_more_news(message: types.Message):
    await message.reply("Отличного дня!", reply_markup=types.ReplyKeyboardRemove())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    posted_q = deque(maxlen=20)
    asyncio.run(main())
