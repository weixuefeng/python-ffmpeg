'''
Author: pony@diynova.com
Date: 2022-05-27 11:57:22
LastEditors: pony@diynova.com
LastEditTime: 2022-05-27 11:57:47
FilePath: /ffmpegTest/app/service.py
Description: 
'''
import os
import re
import logging
from django.conf import settings
from django.core.cache import cache
from ffmpy import FFmpeg
logger = logging.getLogger(__name__)


def cut_change(video_path, password, base_path):
    """
    操作ffmpeg执行： ffmpeg -i a.MP4 -codec: copy -bsf:v h264_mp4toannexb -start_number 0 -hls_time 10 -hls_list_size 0 -f hls -hls_enc_key 123456 big/outpub.m3u8
    :param video_path: 处理输入流视频
    :param out_path: 合成缩略图 10×10
    :param out_path2: 封面图路径
    :param out_path3: 合成Ts流和 *.m3u8文件
    :param fps_r: 对视频帧截取速度
    """
    ff = FFmpeg(inputs={video_path: None},
                outputs={None: '-c copy -bsf:v h264_mp4toannexb -start_number 0 -hls_time 10 -hls_list_size 0 -f hls -hls_enc_key {0} {1}/output.m3u8'.format(
                              password, base_path),
                         })
    print(ff.cmd)
    ff.run()


def execCmd(cmd):
    """
    执行计算命令时间
    """
    r = os.popen(cmd)
    text = r.read().strip()
    r.close()
    return text


# 获取完整的上传文件路径
def has_video(video_path):
    MEDIA_DIR = settings.MEDIA_ROOT
    FULL_PATH = os.path.join(MEDIA_DIR, video_path)
    flag = False
    if os.path.exists(FULL_PATH):
        flag = True
    return flag, FULL_PATH, MEDIA_DIR


def handle_video_cut(instance):
    video_path = instance.video.name
    video_name = os.path.splitext(video_path.split('/')[-1])[0][:5]
    flag, full_path, media_path = has_video(video_path)

    base_preview_path = os.path.join(media_path, 'video_trans/preview')
    base_poster_path = os.path.join(media_path, 'video_trans/poster')
    base_path = os.path.join(media_path, 'video_trans/video_change', str(instance.id))
    # 必须先创建路径， ffmpeg不会自己创建
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    if not os.path.exists(base_poster_path):
        os.makedirs(base_poster_path)
    if not os.path.exists(base_preview_path):
        os.makedirs(base_preview_path)
    preview_path = os.path.join(base_preview_path, video_name + '{}_out.png'.format(str(instance.id)))
    poster_path = os.path.join(base_poster_path, video_name + '{}_poster.jpeg'.format(str(instance.id)))
    video_change = os.path.join(base_path, 'playlist.m3u8')

    if not flag:
        logger.info('this video_path({}) is not exists'.format(full_path))
        return None
    cmd = "ffmpeg -i {} 2>&1 | grep 'Duration' | cut -d ' ' -f 4 | sed s/,//".format(full_path)
    text = execCmd(cmd)
    search_group = re.search('(\d+):(\d+):(\d+)', text)
    if search_group:
        time_hours = int(search_group.group(1))
        time_minutes = int(search_group.group(2))
        time_seconds = int(search_group.group(3))
        all_count_seconds = time_hours * 60 * 60 + time_minutes * 60 + time_seconds
        # print(all_count_seconds)
    else:
        logger.info('this video({}) is no time'.format(full_path))
        return None

    # 因无法精确分配100分压缩图片，存在误差， 以下函数会有错误但是并不会影响结果, 会有exception
    try:
        cut_change(full_path, preview_path, poster_path, video_change, base_path, r)
    except:
        pass
    # print('change video code success')
    logger.info('change video code success and clean cache')
    return None