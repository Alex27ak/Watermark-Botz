import telebot
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
import os

API_TOKEN = '7812256131:AAGuXvvNexwRXizlYszq4_O2VfKx04miT8s'
bot = telebot.TeleBot(API_TOKEN)

# Function to add a watermark to the video
def add_watermark(input_video_path, output_video_path, watermark_text):
    clip = VideoFileClip(input_video_path)
    watermark = TextClip(watermark_text, fontsize=24, color='white')
    watermark = watermark.set_pos(("right", "bottom")).set_duration(clip.duration)
    final = CompositeVideoClip([clip, watermark])
    final.write_videofile(output_video_path, codec="libx264")

# Handler for video or document uploads
@bot.message_handler(content_types=['video', 'document'])
def handle_video_or_document(message):
    # Check if the uploaded document is a video
    if message.content_type == 'document':
        file_info = bot.get_file(message.document.file_id)
        file_extension = os.path.splitext(file_info.file_path)[1].lower()
        
        # Only proceed if the document is a video file (e.g., .mp4)
        if file_extension in ['.mp4', '.mov', '.avi', '.mkv']:
            downloaded_video = f'{message.document.file_id}.mp4'
            output_video = f'{message.document.file_id}_watermarked.mp4'
            
            # Download the video from Telegram
            video_data = bot.download_file(file_info.file_path)
            with open(downloaded_video, 'wb') as new_file:
                new_file.write(video_data)

            # Add watermark
            watermark_text = "@AKLINKSZ"
            add_watermark(downloaded_video, output_video, watermark_text)
            
            # Send back the watermarked video as a document
            with open(output_video, 'rb') as video:
                bot.send_document(message.chat.id, video, caption=f"Here is your watermarked video: {message.document.file_id}_watermarked.mp4")
            
            # Clean up files
            os.remove(downloaded_video)
            os.remove(output_video)
            return

    # Handle video uploads directly
    elif message.content_type == 'video':
        video_info = bot.get_file(message.video.file_id)
        downloaded_video = f'{message.video.file_id}.mp4'
        output_video = f'{message.video.file_id}_watermarked.mp4'

        # Download the video from Telegram
        video_data = bot.download_file(video_info.file_path)
        with open(downloaded_video, 'wb') as new_file:
            new_file.write(video_data)

        # Add watermark
        watermark_text = "@AKLINKSZ"
        add_watermark(downloaded_video, output_video, watermark_text)

        # Send back the watermarked video as a document
        with open(output_video, 'rb') as video:
            bot.send_document(message.chat.id, video, caption=f"Here is your watermarked video: {message.video.file_id}_watermarked.mp4")
        
        # Clean up files
        os.remove(downloaded_video)
        os.remove(output_video)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Send me a video or document, and I'll add a watermark to it!")

bot.polling()
