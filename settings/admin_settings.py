import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from create_bot import bot
from data_base.sqlite_db import db
from settings.admins_list import admin_only
from settings.buttons import kb_admin, kb_accept


# Func to format time based on provided parameters
def time_formatter(bot_start_hours, bot_end_hours, utc):
    start_time = datetime.datetime.strptime(str(bot_start_hours), "%H") + datetime.timedelta(hours=int(utc))
    end_time = datetime.datetime.strptime(str(bot_end_hours), "%H") + datetime.timedelta(hours=int(utc))
    return int(start_time.hour), int(end_time.hour)


# State machine for admin settings using FSM (Finite State Machine)
class FSMAdmin(StatesGroup):
    language = State()
    buffer = State()
    start_time = State()
    end_time = State()
    complete = State()


# Func to start the registration process
@admin_only
async def start_registration(message: types.Message):
    await message.answer(
        'Hi! I am your auto-reply bot. Please choose the language and time zone for auto-reply messages:',
        reply_markup=kb_admin)
    await message.delete()
    await FSMAdmin.language.set()


# Func to handle language selection during registration

async def registration_language(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback.data not in db.messages:
            await callback.message.answer('Please press the button to choose a language.')
            return

        data['chat_id'] = callback.message.chat.id
        data['language'] = callback.data

    await FSMAdmin.next()
    await callback.message.answer('Would you like to set the default settings? (Your working day time from 9am to 6pm)',
                                  reply_markup=kb_accept)
    await callback.message.delete()


# Func to handle user choice of default settings or custom settings
async def buffer(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback.data == 'no':
            await callback.message.answer(
                'Please, enter the hour when your working day finishes (for example, "9" means 9:00).')
            await FSMAdmin.next()
        elif callback.data == 'yes':
            await FSMAdmin.complete.set()
            data['bot_startup_time'] = 18
            data['bot_endup_time'] = 9
            if data['language'] == "spanish":
                data['bot_startup_time'], data['bot_endup_time'] = time_formatter(data['bot_startup_time'],
                                                                                  data['bot_endup_time'], 5)

            await end_registration(callback.message.chat.id, data)
            await callback.message.delete()
            await state.finish()
        await callback.message.delete()


# Func to handle user input for bot start and end times
async def choice_bot_hour(message: types.Message, state: FSMContext, start_time=True):
    await message.delete()
    async with state.proxy() as data:
        try:
            time = int(message.text)
            if 0 <= time <= 23:
                if start_time:
                    data['bot_startup_time'] = time
                else:
                    data['bot_endup_time'] = time
            else:
                raise ValueError
        except ValueError:
            await message.answer('Please, indicate the hour from 0 to 23.')
            return

        if start_time:
            await FSMAdmin.next()
            await message.answer('Please, enter the hour when your labor day begins (for example, "9" means 9:00).')
        else:
            await end_registration(message.chat.id, data)
            await state.finish()


# Handler to complete the registration process and save settings
async def end_registration(chat_id, data):
    data['status'] = False
    db.add_chat_to_config(data)
    await bot.send_message(chat_id=chat_id,
                           text='✅ Saved!\nIf you want to change something, text the command /update\nIf you want to '
                                'turn me off, text /off\nTo turn me on again, text /start')


# Handler to handle updating settings
@admin_only
async def update_define(message: types.Message):
    db.delete_chat_from_config(message.chat.id)
    await start_registration(message)


# Function to register admin-specific message handlers with the dispatcher
def register_handler_admin(dp: Dispatcher):
    dp.register_message_handler(start_registration, commands='start', is_chat_admin=True, state=None)
    dp.register_callback_query_handler(registration_language, is_chat_admin=True, state=FSMAdmin.language)
    dp.register_callback_query_handler(buffer, is_chat_admin=True, state=FSMAdmin.buffer)
    dp.register_message_handler(lambda message, state: choice_bot_hour(message, state, start_time=True),
                                is_chat_admin=True, state=FSMAdmin.start_time)
    dp.register_message_handler(lambda message, state: choice_bot_hour(message, state, start_time=False),
                                is_chat_admin=True, state=FSMAdmin.end_time)
    dp.register_message_handler(update_define, commands='update', is_chat_admin=True, state=None)
