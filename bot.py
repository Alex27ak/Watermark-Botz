import telebot
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
from moviepy.video.fx.all import resize
from PIL import Image
import os

API_TOKEN = 'YOUR_API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

# Dictionary to store user video data
user_data = {}

def add_watermark(input_video_path, output_video_path, watermark_text):
    clip = VideoFileClip(input_video_path)
    watermark = TextClip(watermark_text, fontsize=24, color='white')
    watermark = watermark.set_pos(("right", "bottom")).set_duration(clip.duration)
    final = CompositeVideoClip([clip, watermark])
    final.write_videofile(output_video_path, codec="libx264")

def generate_thumbnail(video_path, thumbnail_path, time=1):
    clip = VideoFileClip(video_path)
    frame = clip.get_frame(time)
    
    image = Image.fromarray(frame)
    image.thumbnail((320, 320))
    image.save(thumbnail_path, "JPEG")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    video_info = bot.get_file(message.video.file_id)
    video_download_link = f'https://api.telegram.org/file/bot{API_TOKEN}/{video_info.file_path}'
    
    downloaded_video = f'{message.video.file_id}.mp4'
    
    # Download the video from Telegram
    video_data = bot.download_file(video_info.file_path)
    with open(downloaded_video, 'wb') as new_file:
        new_file.write(video_data)
    
    # Save video info in user_data and ask for a file name
    user_data[message.chat.id] = {'video_path': downloaded_video}
    bot.send_message(message.chat.id, "Please provide a new name for the watermarked video file (without extension).")

@bot.message_handler(func=lambda message: message.chat.id in user_data and 'video_path' in user_data[message.chat.id])
def handle_file_name(message):
    new_file_name = message.text
    user_info = user_data[message.chat.id]
    
    # Watermarked video paths
    downloaded_video = user_info['video_path']
    output_video = f'{new_file_name}.mp4'
    thumbnail_image = f'{new_file_name}_thumb.jpg'
    
    # Add watermark
    watermark_text = "@AKLINKSZ"
    add_watermark(downloaded_video, output_video, watermark_text)
    
    # Generate thumbnail
    generate_thumbnail(output_video, thumbnail_image)
    
    # Send back the watermarked video as a file with thumbnail
    with open(output_video, 'rb') as video, open(thumbnail_image, 'rb') as thumb:
        bot.send_document(message.chat.id, video, thumb=thumb, caption=f"Here is your watermarked video: {new_file_name}.mp4")
    
    # Clean up files and reset user data
    os.remove(downloaded_video)
    os.remove(output_video)
    os.remove(thumbnail_image)
    del user_data[message.chat.id]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Send me a video, and I'll ask for a new file name and add a watermark to it!")

bot.polling()
