# -*- coding: utf-8 -*-
import os
import time

from open_lib import youtube_dl
from utils.utils import get_current_time, safeFilename
import eyed3

class DownloadUtil:
    @staticmethod
    def download_audio( url, i,other_dir=''):
        sub_dir = time.strftime('%Y-%m-%d', time.localtime())
        if len(other_dir) != 0:
            sub_dir = other_dir
        new_dir = 'E:/python-workspace/selenium_crawl/files/%s' % sub_dir
        if not os.path.exists(new_dir):
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), new_dir, '创建目录,')
            os.makedirs(new_dir)

        proxy = "http://localhost:10809"

        # Set options for youtube_dl
        ydl_opts = {
            'noplaylist': True,
            'proxy': proxy,
            'format': 'bestaudio/best',
            'outtmpl': '%(id)s.%(ext)s',
            'writethumbnail': True,  # 图像
            'allsubtitles': False,  # 只下载默认字幕
            'writesubtitles': True,
            'subtitlesformat': 'vtt',  # 字幕格式
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],  # specify the language codes of the subtitles you want to download
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        # Create a youtube_dl instance and download the video
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title')
            video_title = safeFilename(video_title)

            video_id = info_dict.get('id')
            # Set the paths of the downloaded files
            audio_path = f'{video_id}.mp3'
            subtitle_path = f'{video_id}.en.vtt'
            img_path = f'{video_id}.jpg'
            webp_path = f'{video_id}.webp'
            # Rename the files to the user-specified names
            mp3_filename = 'E:/python-workspace/selenium_crawl/files/%s/%d-%s.mp3' % (sub_dir, i, video_title)
            # Subtitle file name
            subtitle_filename = 'E:/python-workspace/selenium_crawl/files/%s/%d-%s.vtt' % (sub_dir, i, video_title)
            img_filename = 'E:/python-workspace/selenium_crawl/files/%s/%d-%s.jpg' % (sub_dir, i, video_title)

            DownloadUtil.remove_files([mp3_filename, subtitle_filename, img_filename])

            os.rename(audio_path, mp3_filename)
            if os.path.exists(subtitle_path):
                os.rename(subtitle_path, subtitle_filename)
            if os.path.exists(img_path):
                os.rename(img_path, img_filename)
            if os.path.exists(webp_path):
                os.rename(webp_path, img_filename)
            #  删除文件
            DownloadUtil.remove_files([audio_path, subtitle_path, img_path, webp_path])

        mp3 = eyed3.load(mp3_filename)
        mp3.tag.title = info_dict.get('title')
        # Setting Lyrics to the ID3 "lyrics" tag
        if os.path.exists(subtitle_filename):
            with open(subtitle_filename, 'r', encoding='utf-8')as f:
                data = f.read()
                mp3.tag.lyrics.set(data)

        if os.path.exists(img_filename):
            with open(img_filename, "rb") as img:
                data = img.read()
                mp3.tag.images.set(3, data, "image/jpeg", info_dict.get('description'))
        mp3.tag.save()
    @staticmethod
    def remove_files( file_paths):
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)