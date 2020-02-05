from django.shortcuts import render

# Create your views here.
from index.models import *


def indexView(request):
    # 热搜
    search_song = Dynamic.objects.select_related('song').order_by('-dynamic_search').all()[:8]
    # 分类
    label_list = Label.objects.all()
    # 热门
    play_hot_song = Dynamic.objects.select_related('song').order_by('-dynamic_plays').all()[:10]
    # 新歌推荐
    daily_recommendation = Song.objects.order_by('-song_release').all()[:3]
    # 热门搜索
    search_ranking = search_song[:6]
    # 热门下载
    download_ranking = Dynamic.objects.select_related('song').order_by('-dynamic_down').all()[:6]
    all_ranking = [search_ranking, download_ranking]
    return render(request, 'index.html', locals())
