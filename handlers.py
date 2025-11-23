from aiogram import F, Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv
from states import SaveText, AnswerProblem
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import os
load_dotenv()
main_router = Router()
admin_id = os.getenv("ADMIN_ID")

@main_router.callback_query(F.data == "back")
@main_router.message(CommandStart())
async def start_handler(event: Message | CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_data({})
    text = """
<b>Здравствуйте! Если у вас возникли проблемы с получением звезд на аккаунт, отправьте заявку по шаблону ниже</b>

1) Номер заказа (если CryptoBot, то ищите внизу в CryptoBot Mini App) или чек об оплате (PDF/скриншот из банка/TXID)
2) Username получателя
3) Товар и его количество
4) Дата и время оплаты (примерное)
5) Краткое описание проблемы

Ответим вам оперативно, если ваш запрос по делу ⚡️"""
    if isinstance(event, Message):
        await event.answer(text=text, parse_mode="HTML")
    else:
        await bot.delete_message(event.message.chat.id, event.message.message_id)
        await event.message.answer(text=text, parse_mode="HTML")
    await state.set_state(SaveText.write_text)


@main_router.message(SaveText.write_text)
async def write_message(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)
    user_id = message.from_user.id
    await message.answer(text=f"Ваш текст:\n\n{text}",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="💬 Отправить", callback_data=f"send_message_{user_id}")],
                             [InlineKeyboardButton(text="❌ Отменить", callback_data="back")]
                         ]))

@main_router.callback_query(F.data.startswith("send_message"))
async def send_message(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(None)
    await callback.answer()
    data = await state.get_data()
    user_id = callback.data.split('_')[-1]
    await state.update_data(recipient_id=user_id)
    text = data["text"]
    await bot.send_message(chat_id=admin_id, text=f"💬 Получено новое сообщение от @{callback.from_user.username} :\n\n{text}",
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                               [InlineKeyboardButton(text="🔊 Ответить", callback_data=f"respond_to_{user_id}")],
                               [InlineKeyboardButton(text="❌ Удалить", callback_data="delete_message")]
                           ]))
    await callback.message.answer(text="Сообщение отправлено 👌\nОжидайте ответа ⌛", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать заново", callback_data="back")]
    ]))

@main_router.callback_query(F.data.startswith("respond_to"))
async def state_to_respond_message(callback: CallbackQuery,state: FSMContext):
    await callback.answer()
    user_id = callback.data.split('_')[-1]
    await state.update_data(recipient_id=user_id)
    await callback.message.answer(text="👥 Напишите ваш ответ на проблему:")
    await state.set_state(AnswerProblem.give_answer)

@main_router.message(AnswerProblem.give_answer)
async def answer_problem(message: Message, state: FSMContext, bot: Bot):
    text = message.text
    data = await state.get_data()
    recipient_id = data["recipient_id"]
    await bot.send_message(chat_id=recipient_id, text=f"⚠️ Ответ от администрации:\n\n{text}")
    await state.set_state(None)

@main_router.callback_query(F.data == "delete_message")
async def delete_this_message(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)