from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import ffmpeg
import os

# Replace with your Telegram Bot Token
TOKEN = '7684872557:AAGR03j6foIyrUt_8fCo6xCceT4-jGR1U-o'
bot = Bot(token=TOKEN)
app = Flask(__name__)

# Set up dispatcher
dispatcher = Dispatcher(bot, None, workers=0)

# Start Command
def start(update: Update, context):
    update.message.reply_text('Welcome! Send me a file, and I will help you convert it.')

# Handle File Upload
def handle_file(update: Update, context):
    file = update.message.document
    file_path = file.get_file().download()
    context.user_data['file_path'] = file_path
    context.user_data['file_name'] = file.file_name

    keyboard = [
        [InlineKeyboardButton("Convert to MP4", callback_data='mp4')],
        [InlineKeyboardButton("Convert to MKV", callback_data='mkv')],
        [InlineKeyboardButton("Convert to AVI", callback_data='avi')],
        [InlineKeyboardButton("Convert to MOV", callback_data='mov')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Choose the format you want to convert to:', reply_markup=reply_markup)

# Handle Conversion
def convert_file(update: Update, context):
    query = update.callback_query
    query.answer()
    target_format = query.data
    file_path = context.user_data['file_path']
    file_name, _ = os.path.splitext(context.user_data['file_name'])
    output_path = f'{file_name}.{target_format}'

    try:
        ffmpeg.input(file_path).output(output_path).run(overwrite_output=True)
        query.edit_message_text(f'Conversion to {target_format.upper()} successful!')
        query.message.reply_document(open(output_path, 'rb'))
        os.remove(output_path)
        os.remove(file_path)
    except Exception as e:
        query.edit_message_text(f'Error converting file: {e}')

# Set up handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.document, handle_file))
dispatcher.add_handler(CallbackQueryHandler(convert_file))

# Webhook Route
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Home route for Render health checks
@app.route('/')
def index():
    return 'Bot is running!'

if __name__ == '__main__':
    app.run(port=5000)