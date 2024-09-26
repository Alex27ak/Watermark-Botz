import telebot
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
from moviepy.video.fx.all import resize
from PIL import Image
import os

API_TOKEN = 'YOUR_API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

def add_watermark(input_video_path, output_video_path, watermark_text):
    clip = VideoFileClip(input_video_path)
    watermark = TextClip(watermark_text, fontsize=24, color='white')
    watermark = watermark.set_pos(("right", "bottom")).set_duration(clip.duration)
    final = CompositeVideoClip([clip, watermark])
    final.write_videofile(output_video_path, codec="libx264")

def generate_thumbnail(video_path, thumbnail_path, time=1):
    # Load video and extract a frame at a specified time (e.g., 1 second in)
    clip = VideoFileClip(video_path)
    frame = clip.get_frame(time)
    
    # Convert the frame to an image
    image = Image.fromarray(frame)
    
    # Resize image to meet Telegram's thumbnail size requirements (320x320 max)
    image.thumbnail((320, 320))
    
    # Save the image as a JPEG (required by Telegram for thumbnails)
    image.save(thumbnail_path, "JPEG")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    video_info = bot.get_file(message.video.file_id)
    video_download_link = f'https://api.telegram.org/file/bot{API_TOKEN}/{video_info.file_path}'
    
    # Download video
    downloaded_video = f'{message.video.file_id}.mp4'
    output_video = f'{message.video.file_id}_watermarked.mp4'
    thumbnail_image = f'{message.video.file_id}_thumb.jpg'
    
    # Download the video from Telegram
    video_data = bot.download_file(video_info.file_path)
    with open(downloaded_video, 'wb') as new_file:
        new_file.write(video_data)
    
    # Add watermark to video
    watermark_text = "Watermark Text Here"
    add_watermark(downloaded_video, output_video, watermark_text)
    
    # Generate a thumbnail from the watermarked video
    generate_thumbnail(output_video, thumbnail_image)
    
    # Send back the watermarked video as a file with thumbnail
    with open(output_video, 'rb') as video, open(thumbnail_image, 'rb') as thumb:
        bot.send_document(message.chat.id, video, thumb=thumb, caption="Here is your watermarked video.")

    # Clean up files
    os.remove(downloaded_video)
    os.remove(output_video)
    os.remove(thumbnail_image)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Send me a video, and I'll add a watermark with a thumbnail to it!")

bot.polling()
