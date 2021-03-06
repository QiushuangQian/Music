from django.http import StreamingHttpResponse
from django.shortcuts import render
from index.models import *


# Create your views here.
# 歌曲播放页面
def playView(request, song_id):
    # 热搜歌曲
    search_song = Dynamic.objects.select_related('song').order_by('-dynamic_search').all()[:6]
    # 歌曲信息
    song_info = Song.objects.get(song_id=int(song_id))
    # 播放列表
    play_list = request.session.get('play_list', [])
    song_exist = False
    if play_list:
        for i in play_list:
            if int(song_id) == i['song_id']:
                song_exist = True

    if song_exist == False:
        # 添加歌曲至播放列表
        play_list.append(
            {'song_id': int(song_id), 'song_singer': song_info.song_singer, 'song_name': song_info.song_name,
             'song_time': song_info.song_time})
    # 更新session中的播放列表
    request.session['play_list'] = play_list
    # 歌词
    if song_info.song_lyrics != '暂无歌词':
        f = open('static/songLyric/' + song_info.song_lyrics, 'r', encoding='utf-8')
        song_lyrics = f.read()
        f.close()
    # 相关歌曲
    song_type = Song.objects.values('song_type').get(song_id=song_id)['song_type']
    song_relevant = Dynamic.objects.select_related('song').filter(song__song_type=song_type).order_by(
        '-dynamic_plays').all()[:6]

    # 添加播放次数 可使用session实现每天添加一次播放次数
    dynamic_info = Dynamic.objects.filter(song_id=int(song_id)).first()
    # 判断歌曲动态信息是否存在，存在则加1
    if dynamic_info:
        dynamic_info.dynamic_plays += 1
        dynamic_info.save()
    # 若不存在则创建新的动态信息
    else:
        dynamic_info = Dynamic(dynamic_plays=1, dynamic_search=0, dynamic_download=0, song_id=song_id)
        dynamic_info.save()
    return render(request, 'play.html', locals())


# 歌曲下载
def downloadView(request, song_id):
    # 查找歌曲信息
    song_info = Song.objects.get(song_id=int(song_id))
    # 添加下载次数
    dynamic_info = Dynamic.objects.filter(song_id=int(song_id)).first()
    if dynamic_info:
        dynamic_info.dynamic_download += 1
        dynamic_info.save()
    # 若不存在则创建新的动态信息
    else:
        dynamic_info = Dynamic(dynamic_plays=1, dynamic_search=0, dynamic_download=0, song_id=song_id)
        dynamic_info.save()
    # 读取文件
    file = 'static/songFile' + song_info.song_file

    def file_iterator(file, chunk_size=512):
        with open(file, 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    # 将文件内容写入StreamingHttpResponse对象，以字节流的方式返回
    filename = str(song_id) + '.mp3'
    response = StreamingHttpResponse(file_iterator(file))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % (filename)
    return response
