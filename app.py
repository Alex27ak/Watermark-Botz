from flask import Flask, request
import telebot

API_TOKEN = '7812256131:AAGuXvvNexwRXizlYszq4_O2VfKx04miT8s'  # Replace with your actual API token
bot = telebot.TeleBot(API_TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Video Watermark Bot API!"

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://watermark-botz.onrender.com')  # Set your Render URL here
    app.run(host='0.0.0.0', port=8000)  # Change the port to 8000
