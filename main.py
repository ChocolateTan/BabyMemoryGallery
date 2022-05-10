# -*- coding: UTF-8 -*-
from tkinter.messagebox import NO
from turtle import down
import requests
import sys
import json
import os
import zipfile

def http_get(kw, url): 

    #请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
        "Referer": "pan.baidu.com"
    }

    # params 接收一个字典或者字符串的查询参数，
    # 字典类型自动转换为url编码，不需要urlencode()
    response = requests.get(
        url,
        params = kw, 
        headers = headers,
    )

    # 查看响应内容，response.text 返回的是Unicode格式的数据
    # print (response.text)

    # 查看响应内容，response.content返回的字节流数据
    # print (response.content)

    # 查看完整url地址
    print (response.url)

    # 查看响应头部字符编码
    # print (response.encoding)

    # 查看响应码
    # print (response.status_code)
    return response

def http_get_json(kw, url):
    return http_get(kw, url).json()

# get code
def genAutorizeCode(client_id, device_id):
    return http_get(kw= {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://openapi.baidu.com/oauth/2.0/login_success',
        'scope': 'basic,netdisk',
        'device_id': device_id,
    }, url= "https://openapi.baidu.com/oauth/2.0/authorize?")

def getAccessToken(client_id, client_secret, code):
    return http_get_json(kw= {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'http://openapi.baidu.com/oauth/2.0/login_success',
    }, url= "http://openapi.baidu.com/oauth/2.0/token?")    

def imagelist(access_token, parent_path):
    return http_get_json(kw={
        'method': 'imagelist',
        'access_token': access_token,
        'page': '1',
        'num': '20',
        'parent_path': parent_path,
        'web': '1',
        'order': 'time',
    }, url="http://pan.baidu.com/rest/2.0/xpan/file?")

def multimediaListAll(access_token, path):
    return http_get_json(kw={
        'method': 'listall',
        'access_token': access_token,
        'path': path,
        'recursion': 1,
        'order': 'time',
        'desc': '1',
        'start': 0,
        'limit': 100,
        'web': '1',
    }, url="https://pan.baidu.com/rest/2.0/xpan/multimedia?")

def multimediaFilemetas(access_token, fsids):
    return http_get_json(kw={
        'method': 'filemetas',
        'access_token': access_token,
        'fsids': str(fsids),
        'dlink': 1,
        'thumb': 1,
        'extra': 1,
        'needmedia': 1,
    }, url="https://pan.baidu.com/rest/2.0/xpan/multimedia?")

def download(filename, access_token, url):
    url = url + '&access_token=' + access_token
    payload = {}
    files = {}
    headers = {
        'User-Agent': 'pan.baidu.com',
        # "Referer": "pan.baidu.com"
    }
    if 'livp' in filename:
        file_name = './downloadsource/' + str(filename).replace('livp', 'zip')
    else:
        file_name = './source/' + str(filename)
    print(url)
    response = requests.request("GET", url, headers=headers, data = payload, files = files)
    # print(response.text.encode('utf8'))

    with open(file_name,'wb') as file:
        file.write(response.content)
        
    return file_name
    # print(response.text.encode('utf8'))
    # return response.json()

# def multimediaFilemetas(access_token, path):
#     http_get(kw={
#         'method': 'streaming',
#         'access_token': access_token,
#         'path': path,
#         'type': 'M3U8_AUTO_480', # 480P: M3U8_AUTO_480 720P: M3U8_AUTO_720 1080P: M3U8_AUTO_1080
#         'thumb': 1,
#         'extra': 1,
#         'needmedia': 1,
#     }, url="https://pan.baidu.com/rest/2.0/xpan/file?")

def zip_file(filename):
    file_list = []
    zFile = zipfile.ZipFile(filename, "r")
    #ZipFile.namelist(): 获取ZIP文档内所有文件的名称列表
    for fileM in zFile.namelist(): 
        if '.mov' in fileM:
            zFile.extract(fileM, './source/')
            file_list.append('./source/' + fileM)
    zFile.close()
    return file_list

if __name__ == "__main__":
    access_token = sys.argv[1]

    file_list = multimediaListAll(access_token, '/Photo/BaiduApiTest')
    fs_id_list = []
    for item in file_list['list']:
        fs_id_list.append(item['fs_id'])

    file_info_list = multimediaFilemetas(access_token, fs_id_list)
    new_file_info_list = []
    for item in file_info_list['list']:
        if 'width' in item and 'height' in item and 'thumbs' in item:
            item['img_url'] = item['thumbs']['url3'] + '&size=' + 'c' + str(item['width']) + '_u' + str(item['height'])
        else:
            item['img_url'] = ''
        
        print(item['img_url'])
        new_file_info_list.append(item)
        file_name = download(item['filename'], access_token, item['dlink'])
        if '.zip' in file_name:
            file_list = zip_file(file_name)
        else:
            file_list = [file_name]
        
        item['github_url'] = file_list

    # print(json.dumps(new_file_info_list))
    file = open('test.txt', 'w')
    file.write(json.dumps(new_file_info_list))
    file.close()
