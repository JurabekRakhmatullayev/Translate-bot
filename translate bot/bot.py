from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command
from aiogram import F
from aiogram.types import Message
from data import config
import asyncio
import logging
import sys
from menucommands.set_bot_commands  import set_default_commands
from baza.sqlite import Database
from filtersS.admin import IsBotAdminFilter
from filtersS.check_sub_channel import IsCheckSubChannels
from keyboard_buttons import admin_keyboard
from aiogram.fsm.context import FSMContext
from middlewares.throttling import ThrottlingMiddleware #new
from states.reklama import Adverts
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from translate import Translator
import time 
ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS

dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message:Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name,telegram_id=telegram_id)
        await message.answer(text="Assalomu alaykum, translate botimizga hush kelibsiz.\nBu bot Ingliz Rus tillarini Uzbek tiliiga tarjima qiladi")
    except:
        await message.answer(text="Assalomu alaykum, translate botimizga hush kelibsiz.\nBu bot Ingliz Rus tillarini Uzbek tiliiga tarjima qiladi")


@dp.message(IsCheckSubChannels())
async def kanalga_obuna(message:Message):
    text = ""
    inline_channel = InlineKeyboardBuilder()
    for index,channel in enumerate(CHANNELS):
        ChatInviteLink = await bot.create_chat_invite_link(channel)
        inline_channel.add(InlineKeyboardButton(text=f"{index+1}-kanal",url=ChatInviteLink.invite_link))
    inline_channel.adjust(1,repeat=True)
    button = inline_channel.as_markup()
    await message.answer(f"{text} kanallarga azo bo'ling",reply_markup=button)


@dp.message(Command("help"))
async def is_admin(message:Message):
    await message.answer(text="bu botga ingliz va rus tillaridan text yuboring men uzbekchaga ugirib beraman")

@dp.message(Command("abaut"))
async def is_admin(message:Message):
    await message.answer(text="Dasturchi: Rustamqulov Boborahim Bu botni 2024 yil 23- mart kuni yaratdim ")



#Admin panel uchun
@dp.message(Command("admin"))
async def is_admin(message:Message):
    await message.answer(text="Admin menu",reply_markup=admin_keyboard.admin_button)

@dp.message(F.text == "Foydalanuvchilar soni")
async def users_count(message: Message):
    counts = db.count_users()
    text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
    await message.answer(text=text)

@dp.message(F.text == "Reklama yuborish")
async def advert_dp(message: Message, state: FSMContext):
    await state.set_state(Adverts.adverts)
    await bot.send_message(chat_id=message.chat.id, text="Reklama yuborishingiz mumkin !")

import asyncio

@dp.message(Adverts.adverts)
async def send_advert(message:Message, state:FSMContext):
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = db.all_users_id()  # Sinxron ravishda ma'lumotlar olish
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0], from_chat_id=from_chat_id, message_id=message_id)
            count += 1
        except:
            pass
        await asyncio.sleep(0.5)  # Asinxron ravishda boshqa tasklar yopiq qolish
    await message.answer(f"Reklama {count}ta foydalanuvchiga yuborildi")
    await state.clear()


@dp.message(F.text == "Bekor qilish")
async def cancel_advert(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Reklama yuborish bekor qilindi!")



@dp.message(F.text)
async def english(message:Message):
    translator = Translator(from_lang="ru",to_lang="uz")
    text_Eng = message.text
    text_Rus = translator.translate(text_Eng)
    await message.answer(text_Rus)


@dp.message(F.text)
async def russia(message:Message):
    translator = Translator(from_lang="eng",to_lang="uz")
    text_Rus = message.text
    text_Eng = translator.translate(text_Rus)
    await message.answer(text_Eng)


# @dp.message(F.text)
# async def russia(message:Message):
#     translator = Translator(from_lang="tatar",to_lang="uzb")
#     text_tojik = message.text
#     text_Ruf = translator.translate(text_tojik)
#     await message.answer(text_Ruf)



# @dp.message(F.text)
# async def russia(message:Message):
#     translator = Translator(from_lang="qozoq",to_lang="uzb")
#     text_qzoq = message.text
#     uz = translator.translate(text_qzoq)
#     await message.answer(uz)

@dp.message(F.text)
async def russia(message:Message):
    translator = Translator(from_lang="arab",to_lang="uz")
    text_arab = message.text
    uz = translator.translate(text_arab)
    await message.answer(uz)





@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishga tushdi")
        except Exception as err:
            logging.exception(err)

#bot ishga tushganini xabarini yuborish
@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishdan to'xtadi!")
        except Exception as err:
            logging.exception(err)




async def main() -> None:
    global bot,db
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    db = Database(path_to_db="main.db")
    db.create_table_users()
    await set_default_commands(bot)
    dp.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))
    await dp.start_polling(bot)
    





if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())




from googletrans import Translator

def tarjima_uz_ru(text_uz):
    translator = Translator()
    tarjima = translator.translate(text_uz, src='uz', dest='ru')
    return tarjima.text

def tarjima_ru_en(text_ru):
    translator = Translator()
    tarjima = translator.translate(text_ru, src='ru', dest='en')
    return tarjima.text

# Test qilish
if __name__ == "__main__":
    text_uzbekcha = "Salom, dunyo!"
    tarjima_ru = tarjima_uz_ru(text_uzbekcha)
    print("O'zbek tilidan rus tiliga tarjima:", tarjima_ru)

    text_ruscha = "Привет, мир!"
    tarjima_en = tarjima_ru_en(text_ruscha)
    print("Rus tilidan ingliz tiliga tarjima:", tarjima_en)




# from aiogram import Bot
# from aiogram.types import BotCommand
# from aiogram.utils import executor
# import asyncio

# async def change_token(old_token, new_token):
#     old_bot = Bot(token=old_token)
#     new_bot = Bot(token=new_token)

#     # Old tokenni bekor qilish
#     commands = await old_bot.get_my_commands()
#     for command in commands:
#         await old_bot.delete_my_commands(command.command)

#     # Yangi tokenni qo'llash
#     commands = [
#         BotCommand(command="/start", description="Botni boshlash"),
#         BotCommand(command="/help", description="Yordam"),
#         # Boshqa komandalarni ham qo'shing
#     ]
#     await new_bot.set_my_commands(commands)

#     print("Yangi token bilan bot komandalari qo'llandi")

# async def main():
#     old_token = "eskining_token"
#     new_token = "yangining_token"
#     await change_token(old_token, new_token)

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     loop.close()
