import logging
import requests
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '1403126696:AAFqCtiiX-gzNLsFYsTmTmpQJRHSCHZY1cw'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)    

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(types.InlineKeyboardButton(text='Generate email'))
keyboard.add(types.InlineKeyboardButton(text='Refresh inbox'))
keyboard.add(types.InlineKeyboardButton(text='About'))


async def temp_keyboard(email):
    """
    Создает обьект временного меню

    :param email:
    :return:
    """
    temp_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    temp_keyboard.add(types.InlineKeyboardButton(text='Generate email'))
    temp_keyboard.add(types.InlineKeyboardButton(text=f'Refresh inbox\n[{email}]'))
    temp_keyboard.add(types.InlineKeyboardButton(text='About'))
    return temp_keyboard


async def refresh_inbox(email, message):
    bkeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bkeyboard.add(types.InlineKeyboardButton(text=f'Refresh inbox\n[{email}]'))
    bkeyboard.add(types.InlineKeyboardButton(text='Generate email'))
    try:
        data = requests.get(
            url="https://www.1secmail.com/api/v1/",
            params={'action': 'getMessages', 'login': email[:email.find("@")], 'domain': email[email.find("@") + 1:]}
        ).json()
        if data:
            count = 0
            for msg in data:
                id = msg['id']
                msg_subject = msg['subject']
                msg_from = msg['from']
                date = msg['date']
                if len(msg_subject) > 15:
                    msg_subject = str(msg_subject[0:15]) + "..."
                bkeyboard.add(
                    types.InlineKeyboardButton(
                        f'{msg_subject}\n from: {msg_from} in [id{id}][{email}]'
                    )
                )
                await message.answer(f"Message Subject: {msg_subject}\nFrom: {msg_from}\nDate: {date}",
                                     reply_markup=bkeyboard)
                count += 1
            await message.answer(f"A total of {count} messages found\nClick on the button to read the message")
        else:
            await message.answer('Nothing found', reply_markup=bkeyboard)
    except BaseException:
        await message.answer('...', reply_markup=bkeyboard)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply('Welcome! Click the "Generate email" button to generate your temporary email. Click the '
                        '"Refresh inbox" button to check your e-mail.', reply_markup=keyboard)


@dp.message_handler(content_types=['text'])
async def echo(message: types.Message):
    if message.text.lower() == 'generate email':
        email = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1").json()[0]
        await message.answer("Your temporary e-mail:")
        await message.answer(email, reply_markup=await temp_keyboard(email))
    elif message.text.lower() == 'refresh inbox':
        await message.answer('First, generate an email', reply_markup=keyboard)
    elif message.text.lower() == 'about':
        await message.answer('About:_\n\ndev by @JKearnsl')
    elif message.text.lower()[14] == "[":
        email = message.text.lower()[15:message.text.lower().find("]")]
        await refresh_inbox(email, message)
    elif message.text.lower().find("[id"):
        data = message.text.lower()[message.text.lower().find("[id"):]
        _id = data[data.find("[") + 3:data.find(']')]
        email = data[data.find("][") + 2:-1]
        msg = requests.get(
            url="https://www.1secmail.com/api/v1/",
            params={'action': 'readMessage',
                    'login': email[:email.find("@")],
                    'domain': email[email.find("@") + 1:],
                    'id': _id
                    }
        ).json()
        await message.answer(
            text='Message\n'
                 f' From: {msg["from"]}\n'
                 f' Subject: {msg["subject"]}\n'
                 f' Date: {msg["date"]}\n'
                 f'Content:\n{msg["textBody"]}',
        )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
