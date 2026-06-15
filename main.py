import os
import time
import threading
import telebot
from hugo_manager import create_new_post
from CONFIG import TOKEN

bot = telebot.TeleBot(TOKEN)

DOWNLOAD_DIR = '/app/maizel_site/temp/'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

media_groups = {}
lock = threading.Lock()

def process_album(media_group_id):
    time.sleep(3)

    with lock:
        if media_group_id not in media_groups:
            return
        data = media_groups.pop(media_group_id)

    print(f"Пришел новый пост, содержит {len(data['photos'])} фото")

    main_photo = data['photos'][0]
    final_caption = data['caption']

    if len(data['photos']) > 1:
        final_caption += "\n\n### Галерея альбома:\n"
        for index, photo_path in enumerate(data['photos'][1:]):
            file_name = os.path.basename(photo_path)
            final_caption += f"\n![Фото {index + 1}](/images/{file_name})\n"

            hugo_static_dir = './maizel_site/static/images'
            os.makedirs(hugo_static_dir, exist_ok=True)
            try:
                import shutil
                shutil.move(photo_path, os.path.join(hugo_static_dir, file_name))
            except Exception as e:
                print(f"[Ошибка бота, с фотками чота] {e}")

    success = create_new_post(data["photos"], final_caption)

    if success:
        bot.send_message(
            chat_id=data["chat_id"],
            text=f"Успешно!"
        )

@bot.message_handler(content_types=['text', 'photo'])
def handle_channel_post(message):
    try:
        if not message.is_automatic_forward:
            return

        caption = message.caption if message.caption else ""

        if message.content_type == "text":
            return

        elif message.content_type == 'photo':
            photo_file = message.photo[-1]
            file_info = bot.get_file(photo_file.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            file_name = f"{photo_file.file_id}.png"
            file_path = os.path.join(DOWNLOAD_DIR, file_name)

            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            if message.media_group_id:
                mg_id = message.media_group_id
                with lock:
                    if mg_id not in media_groups:
                        media_groups[mg_id] = {
                            "photos": [file_path],
                            "caption": caption,
                            "chat_id": message.chat.id,
                            "message_id": message.message_id
                        }
                        threading.Thread(target=process_album, args=(mg_id,)).start()
                    else:
                        media_groups[mg_id]["photos"].append(file_path)
                        if caption and not media_groups[mg_id]["caption"]:
                            media_groups[mg_id]["caption"] = caption
            else:
                success = create_new_post([file_path], caption)

                if success:
                    bot.send_message(
                        chat_id=message.chat.id,
                        text="Успешно!"
                    )

    except Exception as error:
        print(error)


if __name__ == '__main__':
    bot.infinity_polling()
