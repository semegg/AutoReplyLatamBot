from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


button_english = InlineKeyboardButton('🇬🇧 English (UTC+0)', callback_data='english')
button_spanish = InlineKeyboardButton('🇪🇸 Spanish (UTC-5)', callback_data='spanish')

kb_admin = InlineKeyboardMarkup().row(button_english, button_spanish)


button_yes = InlineKeyboardButton("✅ Yes", callback_data='yes')
button_no = InlineKeyboardButton('⛔️ No', callback_data='no')

kb_accept = InlineKeyboardMarkup().row(button_yes, button_no)
