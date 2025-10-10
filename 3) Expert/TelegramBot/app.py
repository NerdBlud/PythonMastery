import logging
import os
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
load_dotenv()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ADMIN_IDS = []
user_data_store: Dict[int, dict] = {}

CHOOSING_CURRENCY, TYPING_AMOUNT = range(2)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_data_store:
        user_data_store[user_id] = {
            "join_date": datetime.now().isoformat(),
            "message_count": 0,
            "commands_used": []
        }
    
    welcome_message = (
        f"👋 Welcome, {user.mention_html()}!\n\n"
        "🤖 I'm an advanced Telegram bot with expert-level features.\n\n"
        "📚 Use /help to see all available commands."
    )
    
    await update.message.reply_html(welcome_message)
    logger.info(f"User {user.username} ({user_id}) started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
🔰 <b>Available Commands:</b>

<b>Basic Commands:</b>
/start - Start the bot
/help - Show this help message
/about - About this bot
/stats - Your usage statistics

<b>Utility Commands:</b>
/weather [city] - Get weather information
/crypto [symbol] - Get cryptocurrency price
/convert - Currency converter (interactive)
/translate [lang] [text] - Translate text
/calc [expression] - Calculate math expressions

<b>Advanced Features:</b>
/remind [minutes] [message] - Set a reminder
/poll [question] | [option1] | [option2]... - Create a poll
/schedule - View your scheduled tasks
/export - Export your data as JSON

<b>Admin Commands:</b> (Admin only)
/broadcast [message] - Send message to all users
/userstats - Get bot usage statistics
/ban [user_id] - Ban a user
/unban [user_id] - Unban a user

💡 <b>Tips:</b>
- Send any text and I'll analyze it
- Forward messages for analysis
- Send photos for metadata extraction
"""
    await update.message.reply_html(help_text)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    about_text = """
🤖 <b>Advanced Telegram Bot v2.0</b>

Built with:
• Python 3.11+
• python-telegram-bot 20.x
• Async/await architecture
• RESTful API integrations

Features:
✅ Real-time data fetching
✅ User analytics & tracking
✅ Scheduled tasks & reminders
✅ Multi-language support
✅ Admin management system
✅ Data export functionality

Developer: Senior Python Developer
License: MIT
"""
    await update.message.reply_html(about_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in user_data_store:
        await update.message.reply_text("No statistics available. Use the bot first!")
        return
    
    user_data = user_data_store[user_id]
    join_date = datetime.fromisoformat(user_data["join_date"])
    days_active = (datetime.now() - join_date).days
    
    stats_text = f"""
📊 <b>Your Statistics:</b>

👤 User ID: <code>{user_id}</code>
📅 Joined: {join_date.strftime('%Y-%m-%d %H:%M')}
⏱ Days Active: {days_active}
💬 Messages Sent: {user_data['message_count']}
🎯 Commands Used: {len(user_data['commands_used'])}
"""
    await update.message.reply_html(stats_text)

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /weather [city]\nExample: /weather London")
        return
    
    city = " ".join(context.args)
    
    await update.message.reply_text(f"🌤 Fetching weather data for {city}...")
    
    api_key = os.getenv("WEATHER_API_KEY", "demo")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    weather_text = f"""
🌍 <b>Weather in {data['name']}, {data['sys']['country']}</b>

🌡 Temperature: {data['main']['temp']}°C
💧 Humidity: {data['main']['humidity']}%
🌬 Wind Speed: {data['wind']['speed']} m/s
☁️ Condition: {data['weather'][0]['description'].title()}
"""
                    await update.message.reply_html(weather_text)
                else:
                    await update.message.reply_text("❌ City not found. Please check the spelling.")
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        await update.message.reply_text("⚠️ Weather service temporarily unavailable.")

async def crypto_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /crypto [symbol]\nExample: /crypto BTC")
        return
    
    symbol = context.args[0].upper()
    
    await update.message.reply_text(f"📈 Fetching {symbol} price...")
    
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd&include_24hr_change=true"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if symbol.lower() in data:
                        price_data = data[symbol.lower()]
                        change = price_data.get('usd_24h_change', 0)
                        emoji = "📈" if change > 0 else "📉"
                        
                        crypto_text = f"""
💰 <b>{symbol} Price</b>

💵 Price: ${price_data['usd']:,.2f}
{emoji} 24h Change: {change:.2f}%
"""
                        await update.message.reply_html(crypto_text)
                    else:
                        await update.message.reply_text(f"❌ Cryptocurrency {symbol} not found.")
                else:
                    await update.message.reply_text("❌ Failed to fetch crypto data.")
    except Exception as e:
        logger.error(f"Crypto API error: {e}")
        await update.message.reply_text("⚠️ Crypto service temporarily unavailable.")

async def convert_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("USD 🇺🇸", callback_data="USD"),
         InlineKeyboardButton("EUR 🇪🇺", callback_data="EUR")],
        [InlineKeyboardButton("GBP 🇬🇧", callback_data="GBP"),
         InlineKeyboardButton("JPY 🇯🇵", callback_data="JPY")],
        [InlineKeyboardButton("Cancel ❌", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💱 <b>Currency Converter</b>\n\nSelect source currency:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return CHOOSING_CURRENCY

async def currency_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Conversion cancelled.")
        return ConversationHandler.END
    
    context.user_data['from_currency'] = query.data
    
    keyboard = [
        [InlineKeyboardButton("USD 🇺🇸", callback_data="USD"),
         InlineKeyboardButton("EUR 🇪🇺", callback_data="EUR")],
        [InlineKeyboardButton("GBP 🇬🇧", callback_data="GBP"),
         InlineKeyboardButton("JPY 🇯🇵", callback_data="JPY")],
        [InlineKeyboardButton("Cancel ❌", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"Selected: {query.data}\n\nNow select target currency:",
        reply_markup=reply_markup
    )
    return TYPING_AMOUNT

async def amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Conversion cancelled.")
        return ConversationHandler.END
    
    context.user_data['to_currency'] = query.data
    
    await query.edit_message_text(
        f"Converting {context.user_data['from_currency']} → {query.data}\n\n"
        "Please enter the amount:"
    )
    return ConversationHandler.END

async def calc_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /calc [expression]\nExample: /calc 2 + 2 * 3")
        return
    
    expression = " ".join(context.args)
    
    try:
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            await update.message.reply_text("❌ Invalid characters in expression. Use only: 0-9 + - * / ( )")
            return
        
        result = eval(expression)
        await update.message.reply_html(f"🔢 <b>Result:</b>\n\n<code>{expression} = {result}</code>")
    except Exception as e:
        await update.message.reply_text(f"❌ Error calculating: {str(e)}")

async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /remind [minutes] [message]\n"
            "Example: /remind 5 Check the oven"
        )
        return
    
    try:
        minutes = int(context.args[0])
        message = " ".join(context.args[1:])
        
        await update.message.reply_text(f"⏰ Reminder set for {minutes} minute(s)!")
        
        await asyncio.sleep(minutes * 60)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🔔 <b>Reminder:</b>\n\n{message}",
            parse_mode="HTML"
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid time format. Use a number for minutes.")
    except Exception as e:
        logger.error(f"Reminder error: {e}")

async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /poll [question] | [option1] | [option2] | ...\n"
            "Example: /poll Best language? | Python | Java | C++"
        )
        return
    
    poll_data = " ".join(context.args).split("|")
    
    if len(poll_data) < 3:
        await update.message.reply_text("❌ You need at least a question and 2 options.")
        return
    
    question = poll_data[0].strip()
    options = [opt.strip() for opt in poll_data[1:]]
    
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question,
        options=options,
        is_anonymous=False
    )
    await update.message.reply_text("✅ Poll created!")

async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in user_data_store:
        await update.message.reply_text("No data to export.")
        return
    
    user_data = user_data_store[user_id]
    json_data = json.dumps(user_data, indent=2)
    
    filename = f"user_data_{user_id}.json"
    with open(filename, 'w') as f:
        f.write(json_data)
    
    await update.message.reply_document(
        document=open(filename, 'rb'),
        filename=filename,
        caption="📦 Your data export"
    )
    
    os.remove(filename)

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ This command is admin-only.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast [message]")
        return
    
    message = " ".join(context.args)
    success_count = 0
    
    for uid in user_data_store.keys():
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>Broadcast:</b>\n\n{message}", parse_mode="HTML")
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send to {uid}: {e}")
    
    await update.message.reply_text(f"✅ Broadcast sent to {success_count} users.")

async def userstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ This command is admin-only.")
        return
    
    total_users = len(user_data_store)
    total_messages = sum(data['message_count'] for data in user_data_store.values())
    
    stats = f"""
📊 <b>Bot Statistics:</b>

👥 Total Users: {total_users}
💬 Total Messages: {total_messages}
📈 Avg Messages/User: {total_messages/total_users if total_users > 0 else 0:.1f}
"""
    await update.message.reply_html(stats)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    message_text = update.message.text
    
    if user_id in user_data_store:
        user_data_store[user_id]['message_count'] += 1
    
    word_count = len(message_text.split())
    char_count = len(message_text)
    
    analysis = f"""
📝 <b>Message Analysis:</b>

📊 Words: {word_count}
🔤 Characters: {char_count}
📏 Length: {"Short" if word_count < 10 else "Medium" if word_count < 50 else "Long"}

💡 Your message: "<i>{message_text[:100]}...</i>" if len(message_text) > 100 else "<i>{message_text}</i>"
"""
    await update.message.reply_html(analysis)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred while processing your request. Please try again."
        )

async def post_init(application: Application) -> None:
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help message"),
        BotCommand("about", "About this bot"),
        BotCommand("stats", "Your statistics"),
        BotCommand("weather", "Get weather info"),
        BotCommand("crypto", "Get crypto prices"),
        BotCommand("convert", "Currency converter"),
        BotCommand("calc", "Calculate expressions"),
        BotCommand("remind", "Set a reminder"),
        BotCommand("poll", "Create a poll"),
        BotCommand("export", "Export your data"),
    ]
    await application.bot.set_my_commands(commands)

async def post_shutdown(application: Application) -> None:
    logger.info("Bot is shutting down gracefully...")

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        return
    
    application = Application.builder().token(token).post_init(post_init).post_shutdown(post_shutdown).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("crypto", crypto_command))
    application.add_handler(CommandHandler("calc", calc_command))
    application.add_handler(CommandHandler("remind", remind_command))
    application.add_handler(CommandHandler("poll", poll_command))
    application.add_handler(CommandHandler("export", export_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("userstats", userstats_command))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("convert", convert_start)],
        states={
            CHOOSING_CURRENCY: [CallbackQueryHandler(currency_selected)],
            TYPING_AMOUNT: [CallbackQueryHandler(amount_input)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Bot started successfully!")
    logger.info("Press Ctrl+C to stop the bot")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()