# -*- coding: utf-8 -*-
import time

import eyed3
from lxml import html
from moviepy.editor import *
from qiniu import Auth, put_file
from selenium.webdriver.firefox.webdriver import WebDriver

from common_crawl import CommonCrawl
from open_lib import youtube_dl


class YoutubeMusicCrawler(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://www.youtube.com/playlist?list=PLiqmg20oFCodQ68Gi2TrLlTJKFFP2w9PE"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'YoutubeMusicCrawler  '
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'YoutubeMusicCrawler   start crawl..',
              browser.current_url)
        curr_url = browser.current_url
        time.sleep(60)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//ytd-playlist-video-renderer')
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//ytd-playlist-video-renderer//a[@id='video-title']/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')
            title = title.strip()

            url = sel.xpath("//ytd-playlist-video-renderer//a[@id='video-title']/@href")
            url = url[0] if len(url) > 0 else ''
            url = url.strip()
            url = 'https://www.youtube.com' + url.replace('\n', '')

            self.result_map[curr_url].append(TaskResult(title, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'YoutubeMusicCrawler   end crawl..',
              curr_url)

    def custom_send(self):
        i = 0
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'YoutubeMusicCrawler   start custom_send..',
                  url)
            for data in self.result_map[url]:
                i += 1
                try:
                    self.download_audio(data.url, i)
                except Exception as e:
                    print("mq err:", e)
        # QQRobot.send_group_msg(FuDuJiGroup, ["youtube music 更新完毕"])
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'YoutubeMusicCrawler  ending..')

    def upload_file(self, i, mp3_path):
        # 需要填写你的 Access Key 和 Secret Key
        access_key = 'X4GniBjYNd5nWYl8v88N9PgPuTFrp3HFe49FqMjk'
        secret_key = 'ZMFofjsAu8GQkmKevEteT5abAMC2_hH1IMfrYDeh'
        # 构建鉴权对象
        q = Auth(access_key, secret_key)
        # 要上传的空间
        bucket_name = 'tacbin-files'
        # 上传后保存的文件名
        key = '%d.mp3' % i
        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name, key, 3600)
        # 要上传文件的本地路径
        # localfile = './sync/bbb.jpg'
        ret, info = put_file(token, key, mp3_path, version='v2')
        print(info)

    def download_audio(self, url, i):
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
        mp3_filename = './files/%d.mp3' % i
        # Subtitle file name
        subtitle_filename = './files/%d.vtt' % i
        img_filename = './files/%d.jpg' % i
        self.remove_files([mp3_filename, subtitle_filename, img_filename])
        # Create a youtube_dl instance and download the video
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            import os
            info_dict = ydl.extract_info(url, download=True)
            # video_title = info_dict.get('title')
            video_id = info_dict.get('id')
            # Set the paths of the downloaded files
            audio_path = f'{video_id}.mp3'
            subtitle_path = f'{video_id}.en.vtt'
            img_path = f'{video_id}.jpg'
            webp_path = f'{video_id}.webp'
            # Rename the files to the user-specified names
            os.rename(audio_path, mp3_filename)
            if os.path.exists(subtitle_path):
                os.rename(subtitle_path, subtitle_filename)
            if os.path.exists(img_path):
                os.rename(img_path, img_filename)
            if os.path.exists(webp_path):
                os.rename(webp_path, img_filename)
            #  删除文件
            self.remove_files([audio_path, subtitle_path, img_path, webp_path])

        mp3 = eyed3.load(mp3_filename)
        mp3.tag.title = info_dict.get('title')
        # Setting Lyrics to the ID3 "lyrics" tag
        with open(subtitle_filename, 'r', encoding='utf-8')as f, open(img_filename, "rb") as img:
            data = f.read()
            mp3.tag.lyrics.set(data)

        with open(img_filename, "rb") as img:
            data = img.read()
            mp3.tag.images.set(3, data, "image/jpeg", info_dict.get('description'))
        mp3.tag.save()

    def remove_files(self, file_paths):
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)


class TaskResult:
    def __init__(self, title, url):
        self.type = 'youtube_music_top_50'
        self.title = title
        self.url = url
