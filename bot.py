import os
import logging
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import qrcode
from googletrans import Translator
from forex_python.converter import CurrencyRates
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from faker import Faker
import textwrap
import random
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get credentials from environment
TOKEN = os.getenv('TOKEN', '7754654122:AAFGB0bzhfQh6VH5AZ-trPdI5YHEZ6MTfFE')
REMOVE_BG_API_KEY = os.getenv('REMOVE_BG_API_KEY', 'qLfRtLd6MebVzGTuFcQ7Yv9j')

# Initialize tools
translator = Translator()
currency_converter = CurrencyRates()
fake = Faker()

# Processing messages
PROCESSING_MESSAGES = [
    "Processing your request...",
    "Working on it...",
    "Generating output...",
    "Almost done..."
]

def start(update: Update, context: CallbackContext) -> None:
    """Main menu with all tools"""
    keyboard = [
        [InlineKeyboardButton("🖼️ Remove Background", callback_data='remove_bg')],
        [InlineKeyboardButton("📄 Image to PDF", callback_data='img_to_pdf')],
        [InlineKeyboardButton("🎨 Text to Image", callback_data='text_to_img')],
        [InlineKeyboardButton("📉 Compress Image", callback_data='compress_img')],
        [InlineKeyboardButton("🔳 QR Code Generator", callback_data='qr_code')],
        [InlineKeyboardButton("🌍 Translator", callback_data='translator')],
        [InlineKeyboardButton("💱 Currency Converter", callback_data='currency')],
        [InlineKeyboardButton("🖼️ Image Upscaler", callback_data='upscale')],
        [InlineKeyboardButton("📝 Text Summarizer", callback_data='summarize')],
        [InlineKeyboardButton("😂 Random Joke", callback_data='joke')],
        [InlineKeyboardButton("😂 Bangla Joke", callback_data='joke_bn')],
        [InlineKeyboardButton("🌤️ Weather Info", callback_data='weather')],
        [InlineKeyboardButton("🎭 Cartoonify Image", callback_data='cartoonify')],
        [InlineKeyboardButton("📺 YouTube Thumbnail", callback_data='yt_thumb')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "🤖 **All-in-One Bot** 🤖\n\n"
        "Select a tool from below:",
        reply_markup=reply_markup
    )

# --------------- All Tool Functions ---------------

def remove_background(update: Update, context: CallbackContext):
    """Remove image background"""
    if not update.message.photo:
        update.message.reply_text("Please send an image to remove background")
        return
    
    photo = update.message.photo[-1].get_file()
    img_data = BytesIO()
    photo.download(out=img_data)
    img_data.seek(0)
    
    try:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': img_data},
            data={'size': 'auto'},
            headers={'X-Api-Key': REMOVE_BG_API_KEY}
        )
        
        if response.status_code == 200:
            output = BytesIO(response.content)
            update.message.reply_document(
                document=InputFile(output, filename='no_bg.png'),
                caption="✅ Background removed successfully!"
            )
        else:
            update.message.reply_text(f"❌ Error: {response.status_code}")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def images_to_pdf(update: Update, context: CallbackContext):
    """Convert images to PDF"""
    if not context.user_data.get('pdf_images'):
        context.user_data['pdf_images'] = []
        update.message.reply_text("📄 Send me images to convert to PDF. Send /done when finished.")
        return
    
    if update.message.photo:  # line 110
    photo = update.message.photo[-1].get_file()  # line 111
    img_data = BytesIO()
    photo.download(out=img_data)
    img_data.seek(0)
    # বাকি কোড...
    
    try:
        img = Image.open(img_data).convert('RGB')
        context.user_data['pdf_images'].append(img)
        update.message.reply_text(f"✅ Image added ({len(context.user_data['pdf_images'])}). Send more or /done")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")
    elif update.message.text and update.message.text.lower() == '/done':
        if not context.user_data['pdf_images']:
            update.message.reply_text("❌ No images received")
            return
        
        try:
            pdf_buffer = BytesIO()
            context.user_data['pdf_images'][0].save(
                pdf_buffer, "PDF", save_all=True, 
                append_images=context.user_data['pdf_images'][1:]
            )
            pdf_buffer.seek(0)
            update.message.reply_document(
                document=InputFile(pdf_buffer, filename='output.pdf'),
                caption="✅ PDF created successfully!"
            )
        except Exception as e:
            update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            context.user_data['pdf_images'] = []

# [Add all other tool functions here following the same pattern...]
# [Include text_to_image, compress_image, generate_qrcode, translate_text, etc.]

def button_handler(update: Update, context: CallbackContext):
    """Handle button clicks"""
    query = update.callback_query
    query.answer()
    
    tool_instructions = {
        'remove_bg': "Send an image to remove background",
        'img_to_pdf': "Send images to convert to PDF (/done when finished)",
        'text_to_img': "Send text to convert to image",
        'compress_img': "Send an image to compress",
        'qr_code': "Send text to generate QR code",
        'translator': "Send text in format: 'text to lang' (e.g. 'hello to es')",
        'currency': "Send in format: 'amount from to' (e.g. '100 usd bdt')",
        'upscale': "Send image to upscale",
        'summarize': "Send text to summarize",
        'joke': "Here's a joke for you:",
        'joke_bn': "একটা বাংলা জোক:",
        'weather': "Send city name for weather",
        'cartoonify': "Send image to cartoonify",
        'yt_thumb': "Send YouTube URL for thumbnail"
    }
    
    if query.data in tool_instructions:
        if query.data == 'joke':
            query.edit_message_text(f"😂 Joke:\n\nWhy did the {fake.word()} cross the road?\nTo {fake.word()} the {fake.word()}!")
        elif query.data == 'joke_bn':
            jokes = ["বাচ্চা: বাবা, আমি ডাক্তার হতে চাই! বাবা: কেন? বাচ্চা: কারণ ডাক্তাররা সবসময় বল্টু থাকে!"]
            query.edit_message_text(f"😂 বাংলা জোক:\n\n{random.choice(jokes)}")
        else:
            query.edit_message_text(f"🛠️ {tool_instructions[query.data]}\n\nSend /cancel to go back")
            context.user_data['current_tool'] = query.data

def main():
    """Start the bot"""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dp.add_handler(MessageHandler(Filters.photo, message_handler))
    dp.add_handler(CommandHandler("cancel", cancel))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
