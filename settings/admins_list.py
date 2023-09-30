from functools import wraps

from aiogram import types, Dispatcher
from sqlalchemy.exc import IntegrityError

from data_base.sqlite_db import db, Admin


# decorator, which frees us from the need to give each employee an admin role in each chat
def admin_only(func):
    @wraps(func)
    async def wrapped(message: types.Message, *args, **kwargs):
        user_id = message.from_user.id
        admin = db.session.query(Admin).filter_by(user_id=user_id).first()
        if admin:
            return await func(message, *args, **kwargs)

    return wrapped


def super_admin_only(func):
    @wraps(func)
    async def wrapped(message: types.Message, *args, **kwargs):
        user_id = message.from_user.id
        admin = db.session.query(Admin).filter_by(user_id=user_id, super_admin=True).first()
        if admin:
            return await func(message, *args, **kwargs)
        else:
            await message.answer("У вас нет доступа к этой функции super.")

    return wrapped


# func to make employee as admin
@super_admin_only
async def make_admin_command(message: types.Message):
    try:
        data = message.text.split()
        db.make_admin_define(data)
        await message.answer('New Admin Successful')
    except IndexError:
        await message.answer('Перевірте будь ласка правильність вводу:\n/make_admin <username> <user_id>.'
                             '\n Якщо це не допомагає, зверніться у відділ підтримки')
    except IntegrityError:
        await message.answer('Цей користувач вже є адміністратором. Якщо бажаєте зробити його супер-адміністрато')

        return

    await message.answer(
        'Пробачте, сталась якась помилка. Перевірте будь ласка правильність вводу команди. '
        'Якщо це не допомагає, зверніться у відділ підтримки')


# func to make employee as super admin

async def make_super_admin_command(message: types.Message):
    admin = message.text.split()

    db.up_to_super_admin_define(admin[2])
    await message.answer('Great. That user is super admin now')

    await message.answer(
        'Пробачте, сталась якась помилка. Перевірте будь ласка правильність вводу команди. '
        'Якщо це не допомагає, зверніться у відділ підтримки')


def register_more_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(make_admin_command, commands='make_admin')
    dp.register_message_handler(make_super_admin_command, commands='make_super')
