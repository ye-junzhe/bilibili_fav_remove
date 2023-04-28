import requests
import time
import json
import argparse
import requests
import re

parser = argparse.ArgumentParser()
parser.add_argument('--write_to_json', action="store_true", help='Write video info to JSON files')
parser.add_argument('--remove', action="store_true", help='Remove all unviewable videos')
args = parser.parse_args()

# 请添加以下参数
uid = 
cookies = {'SESSDATA': ''}
csrf_token = ''

api_url_get_fav_folders = 'https://api.bilibili.com/x/v3/fav/folder/created/list-all'
api_url_get_fav_videos = 'https://api.bilibili.com/x/v3/fav/resource/list'
api_url_remove = 'https://api.bilibili.com/x/v3/fav/resource/clean'
folders = []
videos = []
unviewable_videos = []

######## get all the fav folders, not videos ########
def get_fav_folders():
    params = {
        'up_mid': str(uid)
    }
    response = requests.get(api_url_get_fav_folders, params=params, cookies=cookies)
    if response.status_code == 200:
        try:
            data = response.json()
            for item in data['data']['list']:
                folder_info = {'id': item['id'], 'title': item['title'], 'media_count': item['media_count']}
                folders.append(folder_info)
        except TypeError:
            print("请确认提供了正确的cookie和uid, 或数据对象下没有该字段")

    else:
        print('请求失败，状态码为：', response.status_code)
    return folders

######## get all fav videos by folders ########
def get_fav_videos():
    for folder in folders:
        folder_title = folder['title']
        folder_id = folder['id']
        print("收藏夹名：", folder_title)
        for pn in range(1, int(folder['media_count'])//20 + 1 + 1):
            params = {
                'media_id' : str(folder_id),
                'platform' : 'web',
                'pn' : str(pn),
                'ps' : '5',
            }
            response = requests.get(api_url_get_fav_videos, params=params, cookies=cookies)
            if response.status_code == 200:
                print("获取第", pn, "页的视频", "->", end=" ")
                try:
                    data = response.json()
                    videos.extend(data['data']['medias'])
                    for video in data['data']['medias']:
                        title = video['title']
                        if title == '已失效视频':
                            unviewable_videos.extend([video['id']])
                    time.sleep(0.1)
                    print("OK 200...")
                except TypeError:
                    print("请确认提供了正确的cookie和uid, 或数据对象下没有该字段")
            else:
                print('请求失败，状态码为：', response.status_code)
    print("All finished")
    return videos, unviewable_videos


def write_to_json():
    with open('data.json', 'w', encoding='utf-8') as f:
        print("Writing to data.json")
        json.dump(folders, f, ensure_ascii=False, indent=4)
    with open('videos.json', 'w', encoding='utf-8') as f:
        print("Writing to videos.json")
        json.dump(videos, f, ensure_ascii=False, indent=4)
    with open('unviewable_videos.json', 'w', encoding='utf-8') as f:
        print("Writing to unviewable_videos.json")
        json.dump(unviewable_videos, f, ensure_ascii=False, indent=4)

def remove():
    for folder in folders:
        folder_id = folder['id']
        params = {
            'media_id': str(folder_id),
            'csrf' : csrf_token
        }
        response = requests.post(api_url_remove, params=params, cookies=cookies)
        if response.status_code == 200:
            print("OK 200... -> Removing in folder: ", folder['title'], folder['id'])


if args.write_to_json:
    get_fav_folders()
    get_fav_videos()
    write_to_json()
elif args.remove:
    get_fav_folders()
    remove()
