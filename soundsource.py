# -*- coding: utf-8 -*-
import os.path
import threading
import urllib.request

import webview

import requests
from tkinter import messagebox

shtml = """
    <html>
    <head>
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid black;
                padding: 10px;
                text-align: left;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
        </style>
        <script>
            function selectMusic(row) {
                var music = [row.cells[0].innerHTML,row.cells[1].innerHTML,row.cells[2].innerHTML];
                window.pywebview.api.select_music(music);
                window.close();
            }

            function search() {
                var keyword = document.getElementById("keyword").value;
                if (keyword == "") {
                    alert("请输入要搜索的关键词");
                    return;
                }
                window.pywebview.api.search_song(keyword).then(function(music_list) {
                    var table = document.getElementById("table");
                    table.innerHTML = "";
                    var header = "<tr><th>音乐ID</th><th>音乐名称</th><th>歌手</th></tr>";
                    table.innerHTML += header;
                    for (var i = 0; i < music_list.length; i++) {
                        var music = music_list[i];
                        var row = "<tr onclick='selectMusic(this)'><td>" + music[0] + "</td><td>" + music[1] + "</td><td>" + music[2] + "</td></tr>";
                        table.innerHTML += row;
                    }
                });
            }
        </script>
    </head>
    <body>
        <h1>请选择一首音乐</h1>
        <input id="keyword" placeholder="请输入要搜索的关键词">
        <button onclick="search()">搜索</button>
        <table id="table">
        </table>
    </body>
    </html>
    """


def run_unblock():
    os.system('UnblockNeteaseMusic.exe -a 127.0.0.1 -p 43107:43108 -o kugou kuwo bilibili pyncmd')


if not os.path.exists('UnblockNeteaseMusic.exe'):
    messagebox.showinfo('tip', '请等待下载完成窗口弹出即可使用音乐搜索！')
    filename = "UnblockNeteaseMusic.exe"
    urllib.request.urlretrieve('https://ghproxy.com/https://github.com/UnblockNeteaseMusic/server/releases/download'
                               '/v0.27.1/unblockneteasemusic-win-x64.exe', "UnblockNeteaseMusic.exe")
    messagebox.showinfo('tip', '下载完成！')
thread = threading.Thread(target=run_unblock)
thread.start()

# 定义常量
API_URL = "http://music.163.com/api/"
MUSIC_PATH = "./templates/resources/"
LYRIC_PATH = "./templates/resources/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                         'like Gecko) Chrome/114.0.0.0 Safari/537.36'}
session = requests.Session()
session.get('https://music.163.com/', headers=headers)


def request_api(url, params=None):
    global headers
    proxies = {"http": "http://127.0.0.1:43107/", "https": "http://127.0.0.1:43108/"}
    response = session.get(url, params=params, headers=headers, proxies=proxies)
    if response.status_code == 200:
        return response.json()
    else:
        return None


class SAPI(object):

    def search_song(self, mkeyword):
        params = {"s": mkeyword, "type": 1, "limit": 50}
        data = request_api(API_URL + "search/pc", params=params)
        print(data)
        song_list = []
        if data and data["result"]["songCount"] > 0:
            for song in data["result"]["songs"]:
                msong_id = song["id"]
                martist = []
                for i in song["artists"]:
                    martist.append(i['name'])
                msong_name = song["name"]
                song_list.append([msong_id, msong_name, '/'.join(martist)])
            return song_list
        else:
            return None

    def select_music(self, music):
        print(f"你选择了：{music}")
        download(music)
        swindow.destroy()


def download(music):
    if download_lyric(music[0]):
        print('lyric')
    if download_song(music[0]):
        print('music')


def download_song(song_id, song_name='music'):
    params = {"ids": "[{}]".format(song_id), 'br': '999000'}
    data = request_api(API_URL + "song/enhance/player/url", params=params)
    print(data)
    if data and data["data"]:
        url = data["data"][0]["url"]
        print(url)
        if url[-4:] == 'flac':
            filename = MUSIC_PATH + song_name + ".flac"
            filename2 = MUSIC_PATH + song_name + ".mp3"
            urllib.request.urlretrieve(url, filename)
            os.system(
                f'./lib/ffmpeg-master-latest-win64-lgpl-shared/bin/ffmpeg.exe -i "{filename}" -ab 320k "{filename2}" -y')
            return True
        filename = MUSIC_PATH + song_name + ".mp3"
        urllib.request.urlretrieve(url, filename)
        return True
    else:
        return False


def download_lyric(song_id, song_name='lyric'):
    params = {"id": song_id, "lv": -1, "kv": -1, "tv": -1}
    data = request_api(API_URL + "song/lyric", params=params)
    print(data)
    if data and data["lrc"]:
        lyric = data["lrc"]["lyric"]
        filename = LYRIC_PATH + song_name + ".lyc"
        file = open(filename, "w", encoding="utf-8")
        file.write(lyric)
        file.close()
        return True
    else:
        return False


sapi = SAPI()
swindow = webview.create_window("选择列表", html=shtml, js_api=sapi)
webview.start()
