import requests
import json
import time
import re
import urllib.parse

# config

# 操作的百度云目录
# 需要修改的路径可取自URL，无需解码
# dir_path = '/图片/学代会照片'
# dir_path = '%2F图片%2F学代会照片'
dir_path = ''

# BDTOKEN可在请求的params中找到
BDTOKEN = ''

# COOKIE可在请求的headers中找到
COOKIE = ''

############################################

# custom param

# custom_name = kCustomPrefix + index + kCustomSuffix
# suffix应为 . + 后缀名 的形式，如 .png, .jpg
kCustomPrefix = 'image_'
kCustomSuffix = '.jpg'

############################################

headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
}

def create_custom_new_name(index):
    # 文件序号
    return kCustomPrefix + str(index) + kCustomSuffix

def list_name_desc(dir):
    """
        查询指定dir的文件,以列表方式返回文件信息
        输入：dir
        输出：file_info_list
    """
    dir = urllib.parse.unquote(dir)
    apilist_url = 'https://pan.baidu.com/api/list'
    params = {
        'dir': dir,
    }
    response = requests.get(apilist_url, params=params, headers=headers)
    response.raise_for_status()
    if response.json()['errno'] == 0:
        file_list = response.json()['list']
        file_info_list = []
        for file in file_list:
            server_filename = file['server_filename']
            isdir = file['isdir']
            path = file['path']
            if 'dir_empty' in file.keys():
                dir_empty = file['dir_empty']
            else:
                dir_empty = 0
            each_file_info = {
                'server_filename': server_filename,
                'isdir': isdir,
                'path': path,
                'dir_empty': dir_empty
            }
            file_info_list.append(each_file_info)
        return file_info_list

def baiduyun_rename(rename_list):
    '''
        将 rename_list 向接口https://pan.baidu.com/api/filemanager发送重命名请求
        输入：rename_list
        输出：result
        rename_list 格式 [{"path":PATH,"newname":NEWNAME},{"path":PATH,"newname":NEWNAME},]
        用 rename_list 构造 post 请求的 data 时， rename_list 需要 json.dumps 转成字符串
    '''
    try_max = 5
    try_count = 0
    params = {
        'opera': 'rename',
        'async': '2',
        'onnest': 'fail',
        'channel': 'chunlei',
        'web': '1',
        'app_id': '250528',
        'bdstoken': BDTOKEN,
        # 'logid':get_logid() ,
        'clienttype': '0',
    }
    if not rename_list == []:
        # ensure_ascii=False 加不加都可以，但key "filelist" 对应的 value 必须用json.dumps()转成字符串类型
        data = {"filelist": json.dumps(rename_list, ensure_ascii=False)}
        url = 'https://pan.baidu.com/api/filemanager'
        response = requests.post(url, params=params, data=data, headers=headers)
        response.raise_for_status()
        errno = response.json()['errno']
        if errno == 0:
            print('[info] : rename successfully!')
        elif errno == 12:
            print('[warning]: 批量处理错误，5s后重试')
            try_count += 1
            if try_count <= try_max:
                time.sleep(5)
                baiduyun_rename(rename_list)
            else:
                print('[error] : 批量处理错误且达到最大重试上限')
        else:
            print(response.json())
    else:
        pass
        # print('[error] : rename_list is empty')

def create_new_name(old_name, custom_name=None, prefix=None, suffix=None, extension_name=None, pattern=None, replace=None):
    '''
        old_name必要参数
        prefix 用于添加前缀
        suffix 用于添加后缀
        extension_name 用于改扩展名
        pattern 和 replace 用于正则替换
        custom_name 用于指定文件名，需包含文件后缀
    '''

    new_name = ''
    if old_name:
        if custom_name:
            new_name = custom_name
        elif prefix:
            # 添加前缀 prefix
            new_name = prefix + old_name
        elif suffix:
            # 仅适用于后缀名字母数为3的文件
            # 添加后缀 suffix
            new_name = old_name[:-4] + suffix + old_name[-4:]
        elif extension_name:
            # 仅适用于后缀名字母数为3的文件
            # 改扩展名为 extension_name
            new_name = old_name[:-3] + extension_name
        elif pattern:
            # 正则替换 pattern 改为 replace
            new_name = re.sub(pattern, replace, old_name, re.S)

        if not new_name == '':
            return new_name
        else:
            raise Exception('create_new_name error')
    else:
        raise Exception('old_name 缺失')

def rename_file_in_dir(dir, rename_dir_children=True):
    """
        调用函数list_name_desc(dir)查询
        调用函数baiduyun_rename(rename_list)重命名
        renameDirChildren 如果为真文件夹将会迭代，即按相同的规则重命名文件夹中的文件
    """
    file_info_list = list_name_desc(dir)
    rename_list = []
    index = 0
    for each in file_info_list:
        print(each)
        if each['isdir'] == 0:
            CUSTOM_NAME = create_custom_new_name(index)
            index += 1
            rename_dict = {
                'path': each['path'],
                'newname': create_new_name(old_name=each['server_filename'], custom_name=CUSTOM_NAME),
            }
            rename_list.append(rename_dict)
        if rename_dir_children and each['isdir'] == 1 and each['dir_empty'] == 0:
            time.sleep(2)
            rename_file_in_dir(each['path'], rename_dir_children=True)
    baiduyun_rename(rename_list)

if __name__ == "__main__":
    #for file in list_name_desc(dir_path):
         #print(file)
    #print("===================================")
    # rename_dir_children 是否迭代更新子文件夹
    rename_file_in_dir(dir_path, rename_dir_children=False)
