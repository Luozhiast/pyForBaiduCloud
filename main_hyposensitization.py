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
dir_path = '/图片/学代会照片'

# BDTOKEN可在请求的params中找到
BDTOKEN = ''

# COOKIE可在请求的headers中找到
COOKIE = ''

headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
}

############################################

# custom param
global_mode = 1

# custom_name = global_custom_prefix + index + global_custom_suffix
# suffix应为 . + 后缀名 的形式，如 .png, .jpg
global_custom_prefix = 'temp_'
global_custom_suffix = '.txt'

global_prefix = ""
global_suffix = ""
global_extension_name = ""
global_pattern = ""
global_replace = ""


############################################

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


def create_custom_new_name(index):
    # 文件序号
    return global_custom_prefix + str(index) + global_custom_suffix


def choose_rename_mode():
    '''
        选择重命名模式
    '''
    global global_mode
    global_mode = int(input("1:序号依次递加\n"
                            "2:添加文件名前缀\n"
                            "3:添加文件名后缀\n"
                            "4:修改文件扩展名\n"
                            "5:正则替换\n"
                            "请选择重命名模式: "))
    if global_mode == 1:
        global global_custom_prefix
        global_custom_prefix = input("请输入文件前缀: ")
        global global_custom_suffix
        global_custom_suffix = input("请输入文件扩展名，形如 .png, .jpg: ")
    elif global_mode == 2:
        global global_prefix
        global_prefix = input("请输入文件前缀: ")
    elif global_mode == 3:
        global global_suffix
        global_suffix = input("请输入文件后缀: ")
    elif global_mode == 4:
        global global_extension_name
        global_extension_name = input("请输入文件扩展名: ")
    elif global_mode == 5:
        global global_pattern
        global_pattern = input("请输入被替换的词: ")
        global global_replace
        global_replace = input("请输入替换成的词: ")


def create_new_name(old_name, custom_name=None, prefix=None, suffix=None, extension_name=None, pattern=None,
                    replace=None):
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
        if prefix:
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
        elif custom_name:
            new_name = custom_name
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
        # print(each)
        if each['isdir'] == 0:
            CUSTOM_NAME = create_custom_new_name(index)
            index += 1
            rename_dict = {
                'path': each['path'],
                'newname': create_new_name(old_name=each['server_filename'], custom_name=CUSTOM_NAME,
                                           prefix=global_prefix, suffix=global_suffix,
                                           extension_name=global_extension_name, pattern=global_pattern,
                                           replace=global_replace),
            }
            rename_list.append(rename_dict)
            print(each['server_filename'] + " -> " + rename_dict['newname'])
        if rename_dir_children and each['isdir'] == 1 and each['dir_empty'] == 0:
            time.sleep(2)
            rename_file_in_dir(each['path'], rename_dir_children=True)
    baiduyun_rename(rename_list)


if __name__ == "__main__":
    dir_path = input("请输入工作目录， 形如  /图片/学代会照片 : ")
    choose_rename_mode()
    # for file in list_name_desc(dir_path):
    # print(file)
    # print("===================================")
    # rename_dir_children 是否迭代更新子文件夹
    rename_file_in_dir(dir_path, rename_dir_children=(input("请输入是否修改子文件夹 y/n:") == 'y'))
