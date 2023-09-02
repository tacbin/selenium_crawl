# -*- coding: utf-8 -*-
import os
import threading
import time

import eyed3
from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.constants import Week, FuDuJiGroup
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl
from open_lib import youtube_dl
from utils.utils import get_current_time, safeFilename


class YoutubeMusicRightListCrawler(CommonCrawl):
    def __init__(self, url, title, jump=False):
        super().__init__()
        self.sub_dir = time.strftime('%Y-%m-%d', time.localtime())
        self.result_map = {}
        if not jump:
            last_time = CommonInstance.Redis_client.get('YoutubeMusicRightListCrawler')
            if last_time is None:
                last_time = get_current_time()
            else:
                last_time = int(last_time)
            if get_current_time() - Week < last_time:
                self.is_run = False
        self.show_head = True
        self.url = url
        self.title = title

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            self.url]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'YoutubeMusicRightListCrawler  '
        self.is_save_img = False
        self.mode = 1
        self.sub_dir = '%s(%s)' % (self.title, self.sub_dir)
        new_dir = './files/%s' % self.sub_dir
        if not os.path.exists(new_dir):
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), new_dir, '创建目录,')
            os.makedirs(new_dir)
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'YoutubeMusicRightListCrawler   start crawl..',
              browser.current_url)
        curr_url = browser.current_url
        time.sleep(60)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//ytd-playlist-panel-video-renderer[@class='style-scope ytd-playlist-panel-renderer']")
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))

            url = sel.xpath("//ytd-playlist-panel-video-renderer//a/@href")
            url = url[0] if len(url) > 0 else ''
            url = url.strip()
            url = 'https://www.youtube.com' + url.replace('\n', '')

            self.result_map[curr_url].append(TaskResult(url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'YoutubeMusicRightListCrawler   end crawl..',
              curr_url)

    def custom_send(self):
        i = 0
        threads = []
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                  'YoutubeMusicRightListCrawler   start custom_send..',
                  url)
            for data in self.result_map[url]:
                i += 1
                try:
                    thread = threadControl(data.url, i, self.sub_dir)
                    thread.start()
                    threads.append(thread)
                    # self.download_audio(data.url, i)
                except Exception as e:
                    print("YoutubeMusicRightListCrawler err:", e)
            for t in threads:
                t.join()
        CommonInstance.Redis_client.set('YoutubeMusicRightListCrawler', get_current_time())
        QQRobot.send_group_msg(FuDuJiGroup, ["youtube music 更新完毕"])
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'YoutubeMusicRightListCrawler  ending..')


class TaskResult:
    def __init__(self, url):
        self.type = 'youtube_music_top_50'
        self.url = url


class threadControl(threading.Thread):
    def __init__(self, url, i, sub_dir):
        super().__init__()
        self.url = url
        self.i = i
        self.sub_dir = sub_dir

    def run(self):
        self.download_audio(self.url, self.i)

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
            mp3_filename = './files/%s/%d-%s.mp3' % (self.sub_dir, self.i, video_title)
            # Subtitle file name
            subtitle_filename = './files/%s/%d-%s.vtt' % (self.sub_dir, self.i, video_title)
            img_filename = './files/%s/%d-%s.jpg' % (self.sub_dir, self.i, video_title)

            self.remove_files([mp3_filename, subtitle_filename, img_filename])

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
        if os.path.exists(subtitle_filename):
            with open(subtitle_filename, 'r', encoding='utf-8')as f:
                data = f.read()
                mp3.tag.lyrics.set(data)

        if os.path.exists(img_filename):
            with open(img_filename, "rb") as img:
                data = img.read()
                mp3.tag.images.set(3, data, "image/jpeg", info_dict.get('description'))
        mp3.tag.save()

    def remove_files(self, file_paths):
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
