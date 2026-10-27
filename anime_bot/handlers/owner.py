import asyncio
import secrets
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import config
from database import db
from filters.admin_filter import IsOwnerFilter
from states.fsm import CreateVipCodeFSM, BroadcastFSM
from keyboards.reply import (
    get_owner_reply_keyboard,
    get_cancel_reply_keyboard,
    get_main_reply_keyboard
)

owner_router = Router(name="owner_router")
owner_router.message.filter(IsOwnerFilter())
owner_router.callback_query.filter(IsOwnerFilter())


@owner_router.message(F.text == "👑 Owner (Egasi) Paneli")
async def owner_panel_home(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "👑 <b>Bot Egasining Boshqaruv Markazi</b>",
        reply_markup=get_owner_reply_keyboard()
    )


@owner_router.message(F.text == "👥 Admin qo'shish / o'chirish")
async def manage_admins_menu(message: Message) -> None:
    admins = await db.get_admins()
    text = "👥 <b>Hozirgi Bot Adminlari:</b>\n\n"
    for a in admins:
        name = a.get("full_name") or "Noma'lum"
        username = f"(@{a['username']})" if a.get("username") else ""
        text += f"• <code>{a['user_id']}</code> — <b>{name}</b> {username}\n"
    text += (
        "\n<b>Admin qo'shish:</b> <code>/add_admin ID</code>\n"
        "<b>Adminni o'chirish:</b> <code>/del_admin ID</code>"
    )
    await message.answer(text)


@owner_router.message(F.text.startswith("/add_admin"))
async def add_admin_command(message: Message) -> None:
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: <code>/add_admin 123456789</code>")
        return
    admin_id = int(parts[1])
    success = await db.add_admin(admin_id, added_by=config.OWNER_ID)
    if success:
        await message.answer(f"✅ <code>{admin_id}</code> Admin qilindi.")
    else:
        await message.answer("❌ Xatolik yoki allaqachon admin.")


@owner_router.message(F.text.startswith("/del_admin"))
async def del_admin_command(message: Message) -> None:
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: <code>/del_admin 123456789</code>")
        return
    admin_id = int(parts[1])
    if admin_id == config.OWNER_ID:
        await message.answer("❌ O'zingizni o'chira olmaysiz!")
        return
    success = await db.delete_admin(admin_id)
    if success:
        await message.answer(f"✅ <code>{admin_id}</code> o'chirildi.")
    else:
        await message.answer("❌ Admin topilmadi.")


@owner_router.message(F.text == "📢 Kanallarni sozlash")
async def manage_channels_menu(message: Message) -> None:
    channels = await db.get_channels()
    text = "📢 <b>Majburiy Kanallar:</b>\n\n"
    if not channels:
        text += "<i>Hozircha yo'q.</i>\n"
    else:
        for idx, ch in enumerate(channels, start=1):
            text += f"{idx}. <b>{ch['name']}</b>\nID: <code>{ch['channel_id']}</code>\n{ch['url']}\n\n"
    text += (
        "<b>Qo'shish:</b> <code>/add_channel KANAL_ID NOMI HAVOLA</code>\n"
        "<b>O'chirish:</b> <code>/del_channel KANAL_ID</code>"
    )
    await message.answer(text)


@owner_router.message(F.text.startswith("/add_channel"))
async def add_channel_command(message: Message) -> None:
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer(
            "❌ To'liq kiriting:\n"
            "<code>/add_channel -1001234567890 KanalNomi https://t.me/kanal</code>"
        )
        return
    ch_id = parts[1].strip()
    ch_name = parts[2].strip()
    ch_url = parts[3].strip()
    success = await db.add_channel(ch_id, ch_name, ch_url)
    if success:
        await message.answer(f"✅ <b>{ch_name}</b> qo'shildi!")
    else:
        await message.answer("❌ Xatolik.")


@owner_router.message(F.text.startswith("/del_channel"))
async def del_channel_command(message: Message) -> None:
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Foydalanish: <code>/del_channel -1001234567890</code>")
        return
    ch_id = parts[1].strip()
    success = await db.delete_channel(ch_id)
    if success:
        await message.answer(f"✅ <code>{ch_id}</code> o'chirildi.")
    else:
        await message.answer("❌ Kanal topilmadi.")


@owner_router.message(F.text == "🎁 VIP Promo yaratish")
async def start_create_vip_code(message: Message, state: FSMContext) -> None:
    await state.set_state(CreateVipCodeFSM.waiting_duration_days)
    await message.answer(
        "🎁 Necha kunlik VIP? (Masalan: <code>30</code>):",
        reply_markup=get_cancel_reply_keyboard()
    )


@owner_router.message(CreateVipCodeFSM.waiting_duration_days)
async def process_vip_duration(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("Faqat raqam kiriting:")
        return
    days = int(message.text.strip())
    random_str = secrets.token_hex(3).upper()
    promo_code = f"VIP-{days}D-{random_str}"
    success = await db.create_vip_code(promo_code, days)
    await state.clear()

    if success:
        await message.answer(
            f"🎉 <b>Yangi Promo-kod:</b>\n\n"
            f"🔑 <code>{promo_code}</code>\n"
            f"⏳ {days} kun",
            reply_markup=get_owner_reply_keyboard()
        )
    else:
        await message.answer("Xatolik yuz berdi.", reply_markup=get_owner_reply_keyboard())


@owner_router.message(F.text == "📊 To'liq statistika")
async def show_full_statistics(message: Message) -> None:
    total_users = await db.get_all_users_count()
    vip_users = await db.get_vip_count()
    total_anime = await db.get_total_anime_count()
    total_episodes = await db.get_total_episodes_count()
    channels = await db.get_channels()
    admins = await db.get_admins()

    stats_text = (
        "📊 <b>Bot Statistikasi:</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{total_users}</b>\n"
        f"👑 VIP: <b>{vip_users}</b>\n"
        f"🎬 Animelar: <b>{total_anime}</b>\n"
        f"🎞 Qismlar: <b>{total_episodes}</b>\n"
        f"📢 Kanallar: <b>{len(channels)}</b>\n"
        f"🛡 Adminlar: <b>{len(admins)}</b>"
    )
    await message.answer(stats_text)


@owner_router.message(F.text == "✉️ Xabar tarqatish (Broadcast)")
async def start_broadcast(message: Message, state: FSMContext) -> None:
    await state.set_state(BroadcastFSM.waiting_message)
    await message.answer(
        "✉️ Yubormoqchi bo'lgan xabarni yuboring:",
        reply_markup=get_cancel_reply_keyboard()
    )


@owner_router.message(BroadcastFSM.waiting_message)
async def process_broadcast_message(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🚀 Tarqatish boshlandi...", reply_markup=get_owner_reply_keyboard())

    user_ids = await db.get_all_users_ids()
    sent_count = 0
    blocked_count = 0

    for uid in user_ids:
        try:
            await message.copy_to(chat_id=uid)
            sent_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            blocked_count += 1

    await message.answer(
        f"🏁 <b>Yakunlandi!</b>\n\n"
        f"✅ Yuborildi: <b>{sent_count}</b>\n"
        f"🚫 Bloklangan: <b>{blocked_count}</b>"
    )
