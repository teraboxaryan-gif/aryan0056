import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= CONFIG =================
TOKEN = "8984871023:AAFY-ROrzW5qA0L8q4aITrzPQUN6k92oVx0"

# Multiple Force Subscribe Channels (username ke saath @ lagakar likho)
FORCE_CHANNELS = [
    "@aryanobleet",           # yeh wala jo aapne diya
    # "@aryanobleet",
    # "@aryanobleet",
    # Agar group hai to uska username ya invite link daal sakte ho
]

API_URL = "http://number-free1year.vercel.app/?apikey=toxicadminn&number="
# =========================================

logging.basicConfig(level=logging.INFO)

async def is_user_joined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    
    for channel in FORCE_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            # Agar channel private hai ya error aaye to bhi force karo
            return False
    return True

async def send_force_message(update: Update):
    keyboard = []
    for channel in FORCE_CHANNELS:
        keyboard.append([InlineKeyboardButton(" Join Channel", url=f"https://t.me/{channel.strip('@')}")])
    
    keyboard.append([InlineKeyboardButton(" Check Again", callback_data="check_join")])
    
    await update.message.reply_text(
        "❗ **Force Subscribe Required**\n\n"
        "Bot use karne ke liye pehle neeche diye channels join kar lo:\n\n"
        + "\n".join([f"• {ch}" for ch in FORCE_CHANNELS]),
        reply_markup=InlineKeyboardMarkup(keyboard),
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_joined(update, context):
        await send_force_message(update)
        return
    
    await update.message.reply_text(
        "👋 Welcome to **Aryan Num Info Bot**\n\n"
        "Koi 10 digit Indian number bhejo aur details mil jayengi."
    )

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if await is_user_joined(update, context):
        await query.edit_message_text("✅ Thank you! Ab aap bot use kar sakte ho.\n\nAb number bhejo.")
    else:
        await query.edit_message_text("❌ Aapne abhi bhi channels join nahi kiye. Pehle join karein.")

async def lookup_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_joined(update, context):
        await send_force_message(update)
        return

    number = update.message.text.strip()
    
    if not number.isdigit() or len(number) != 10:
        await update.message.reply_text("❌ Please send a valid 10-digit Indian number (without +91).")
        return

    try:
        response = requests.get(API_URL + number, timeout=15)
        data = response.json()

        if data.get("success"):
            results = data.get("result", [])
            if results:
                msg = f"✅ **Information Found**\n\n"
                for i, res in enumerate(results[:3], 1):
                    msg += f"**#{i}**\n"
                    msg += f"📛 Name: {res.get('name', 'N/A')}\n"
                    msg += f"👤 Father: {res.get('fname', 'N/A')}\n"
                    msg += f"📱 Number: +91{res.get('num', number)}\n"
                    msg += f"🏠 Address: {res.get('address', 'N/A')}\n"
                    msg += f"🔢 Aadhaar: {res.get('aadhar', 'N/A')}\n"
                    msg += f"📡 Circle: {res.get('circle', 'N/A')}\n\n"
                
                await update.message.reply_text(msg, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ No information found for this number.")
        else:
            await update.message.reply_text("❌ API Error")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup_number))
    
    # Callback handler for "Check Again" button
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
    
    print("🤖 Toxic Num Bot with Force Subscribe is running...")
    app.run_polling()

if __name__ == "__main__":
    main()