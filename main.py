import asyncio

from aiogram import types
from aiogram.utils import executor

from create_bot import dp
from data_base.sqlite_db import db
from settings.admin_settings import register_handler_admin
from settings.admins_list import register_more_admin_handlers, admin_only

register_handler_admin(dp)
register_more_admin_handlers(dp)


# The function that is called when a message is sent from the admin. If status = true (i.e. it's not a working day),
# then it changes the status so that message_from_user does not work

@dp.message_handler()
@admin_only
async def admin_status_falser(message: types.Message):
    chat_id = message.chat.id
    try:
        if await db.get_chat_status(chat_id):
            await db.status_falser(chat_id)
    except TypeError:
        pass


# The function that is called when a message is received from the user. If the status is true, it waits half an hour
# and checks the status again. If the status has not changed, retrieves the settings from the database and sends a
# message based on them
@dp.message_handler()
async def message_from_user(message: types.Message):
    chat_id = message.chat.id
    try:
        if await db.get_chat_status(chat_id):
            await asyncio.sleep(18000)
            reply = await db.bot_reply_config(chat_id)
            if reply.status:
                await message.answer(db.messages[reply.language])
                await db.status_falser(chat_id)

    except TypeError:
        pass


async def on_startup(_):
    print("Online")
    db.sql_startup()
    asyncio.create_task(db.run_scheduler())


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
