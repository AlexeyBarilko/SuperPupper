import os
import shutil
import re
import subprocess
from datetime import datetime

HUGO_PROJECT_DIR = "/app/maizel_site"


def deploy_to_github():
    try:
        subprocess.run(["git", "config", "user.email", "alexeybarilko@example.com"], cwd="/app")
        subprocess.run(["git", "config", "user.name", "AlexeyBarilko"], cwd="/app")

        subprocess.run(["git", "add", "."], cwd="/app", check=True)
        subprocess.run(["git", "commit", "-m", "auto publish"], cwd="/app", check=False)
        subprocess.run(["git", "push"], cwd="/app", check=True)
        print("[GitHub] Пуш выполнен успешно!")
    except Exception as Error:
        print(f"[GitHub Error] {Error}")


def create_new_post(temp_file_paths, caption_markdown):
    try:
        if not temp_file_paths:
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        post_name = f"post_{timestamp}"

        hugo_static_img_dir = os.path.join(HUGO_PROJECT_DIR, "static", "images")
        hugo_assets_img_dir = os.path.join(HUGO_PROJECT_DIR, "assets", "images")
        hugo_content_dir = os.path.join(HUGO_PROJECT_DIR, "content", "posts")

        os.makedirs(hugo_static_img_dir, exist_ok=True)
        os.makedirs(hugo_assets_img_dir, exist_ok=True)
        os.makedirs(hugo_content_dir, exist_ok=True)

        if isinstance(temp_file_paths, str):
            temp_file_paths = [temp_file_paths]

        main_photo_path = temp_file_paths[0]

        if os.path.exists(main_photo_path):
            main_img_name = f"{post_name}_main.png"

            shutil.copy(main_photo_path, os.path.join(hugo_assets_img_dir, main_img_name))
            shutil.move(main_photo_path, os.path.join(hugo_static_img_dir, main_img_name))

            web_main_url = f"/images/{main_img_name}"
        else:
            print(f"[Hugo] Главный файл не найден по пути: {main_photo_path}")
            return False

        clean_title = re.sub(r'[^\w\s\d\-\_\.\,\!\?\(\)]', '', caption_markdown[:40]).strip()
        clean_title = clean_title.replace('"', '\\"') if clean_title else "Новый post"
        current_time = datetime.now().isoformat()

        md_content = f"""---
title: "{clean_title}"
date: {current_time}
draft: false
featured_image: "https://alexeybarilko.github.io/SuperPupper{web_main_url}"
---

![Главное фото]({web_main_url})

{caption_markdown}
"""

        if len(temp_file_paths) > 1:
            md_content += "\n\n### Галерея альбома:\n"
            for index, extra_photo_path in enumerate(temp_file_paths[1:]):
                if os.path.exists(extra_photo_path):
                    extra_img_name = f"{post_name}_gallery_{index}.png"
                    shutil.move(extra_photo_path, os.path.join(hugo_static_img_dir, extra_img_name))
                    md_content += f"\n![Фото {index + 1}](/images/{extra_img_name})\n"

        hugo_md_path = os.path.join(hugo_content_dir, f"{post_name}.md")
        with open(hugo_md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"[Hugo] Успешно создан пост-альбом {post_name}")
        deploy_to_github()
        return True

    except Exception as e:
        print(f"[Hugo] Чото сломалось: {e}")
        return False

#idk123
