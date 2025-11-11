Railwayda telegram botimni ishlatmoqchiman. Starter varianti bormi? Kichkina botim bor shuni ishlatib qo'ymoqchiman. import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

users = {}

@dp.message(CommandStart())
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    admin = await bot.get_chat(ADMIN_ID)
    builder.button(
        text="👨‍💼 Admin bilan bog‘lanish",
        url=f"https://t.me/{admin.username}"
    )

    text = (
        "👋 <b>Salom!</b>\n"
        "🎓 <b>Mnemonika guruhining boshqaruvchi botiga xush kelibsiz!</b> 🎉\n\n"
        "🧠 Xotirangizni kuchaytirish sari tashlagan ilk qadamingiz muborak bo‘lsin! 🎊\n\n"
        "⏳ <b>Obuna muddati:</b> 30 kun\n"
        "💰 <b>Obuna narxi:</b> <code>💸 1️⃣2️⃣0️⃣,0️⃣0️⃣0️⃣ so'm</code> / oy\n\n"
        "💳 <b>To‘lov kartasi:</b>\n"
        "💳 9860 1301 7028 6244\n"
        "👤 Madad Eshimov\n\n"
        "📎 To‘lovni amalga oshirib, <b>chekni shu yerga yuboring.</b>\n"
        "✅ Admin tasdiqlagandan so‘ng kanalga ulanishingiz mumkin."
    )

    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@dp.message(F.photo | F.document)
async def receive_check(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📤 Yuborilsinmi?", callback_data="send_check")
    users[message.from_user.id] = {"check": message}
    await message.answer("Chekni yuborishni tasdiqlaysizmi?", reply_markup=builder.as_markup())


@dp.callback_query(F.data == "send_check")
async def send_check(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in users or "check" not in users[user_id]:
        await callback.message.answer("Avval chek yuboring.")
        return

    msg = users[user_id]["check"]
    caption = f"💰 Yangi to‘lov:\n👤 @{callback.from_user.username or callback.from_user.full_name}\nID: {user_id}"

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"approve_{user_id}")

    await msg.copy_to(ADMIN_ID, caption=caption, reply_markup=builder.as_markup())
    await callback.message.edit_text(
        "✅ Chekingiz yuborildi!\n"
        "👀 Hozir admin tekshiradi.\n"
        "⏳ Iltimos, ozgina kuting.\n\n"
        "🎯 Tasdiqlangandan so‘ng guruhga kirish havolasi beriladi."
    )


@dp.callback_query(F.data.startswith("approve_"))
async def approve_payment(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz.")
        return

    user_id = int(callback.data.split("_")[1])

    invite_link = await bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        name="Obuna kirish",
        creates_join_request=True,
        expire_date=datetime.now() + timedelta(minutes=10)
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔗 Kanalga kirish", url=invite_link.invite_link)]]
    )

    await bot.send_message(user_id, "🎉 To‘lov tasdiqlandi!", reply_markup=keyboard)
    await callback.message.answer("✅ Foydalanuvchi tasdiqlandi!")


@dp.chat_join_request()
async def approve_join_request(update: types.ChatJoinRequest):
    user_id = update.from_user.id
    if users.get(user_id):
        await bot.approve_chat_join_request(update.chat.id, user_id)
        await bot.send_message(user_id, "✅ Kanalga qo‘shildingiz!")
    else:
        await bot.decline_chat_join_request(update.chat.id, user_id)


async def main():
    print("✅ Bot pollingda ishlayapti...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
