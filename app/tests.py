'''
Author: pony@diynova.com
Date: 2022-05-27 11:47:28
LastEditors: pony@diynova.com
LastEditTime: 2022-05-27 11:56:30
FilePath: /ffmpegTest/app/tests.py
Description: 
'''
from django.test import TestCase
from .service import cut_change

# Create your tests here.
class TestFFmpeg(TestCase):

    def setUp(self):
        print("setUp")

    def test_ffmpeg(self):
        base_path = "/Users/weixuefeng/source/github/ffmpegTest/app/asset"
        input_path = "{}/a.MP4".format(base_path)
        password = "123456"
        ts_path = "{}/res".format(base_path)
        cut_change(input_path, password, ts_path)
        print(input_path)

