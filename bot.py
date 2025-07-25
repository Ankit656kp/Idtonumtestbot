import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN

proxy = Client("proxy_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

TARGET_BOT = "Kapq0_bot"
TARGET_KEYWORD = "Telegram"

@proxy.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply_text("🔎 Send /search <query> to fetch result from @Kapq0_bot anonymously.")

@proxy.on_message(filters.command("search") & filters.private)
async def search_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: /search <query>")

    user_query = message.text.split(" ", 1)[1]
    sent = await client.send_message(TARGET_BOT, user_query)

    try:
        # Wait for inline buttons
        response = await client.listen(TARGET_BOT, timeout=20)

        # Auto-click "Telegram" button
        if response.reply_markup:
            for row in response.reply_markup.inline_keyboard:
                for button in row:
                    if TARGET_KEYWORD.lower() in button.text.lower():
                        await client.request_callback_answer(
                            chat_id=TARGET_BOT,
                            message_id=response.id,
                            callback_data=button.callback_data
                        )
                        break

        # Wait for final result
        final = await client.listen(TARGET_BOT, timeout=20)
        await message.reply_text(final.text or "✔️ Got a response.", disable_web_page_preview=True)

    except asyncio.TimeoutError:
        await message.reply_text("⚠️ No response or timeout. Try again.")
    finally:
        await sent.delete()
        try:
            await response.delete()
        except:
            pass
        try:
            await final.delete()
        except:
            pass

proxy.run()
