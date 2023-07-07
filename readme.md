# 环境配置

## 1. 获取BDTOKEN 

- 登录百度云空间
- 按下图`打开控制台-网络-XHR-Param（可在预览中看到）`
- 刷新页面检查请求中的报文（暂不知道具体在哪个报文，耐心找一下吧）

![pic1](D:\Project\pyProject\pyForBaiduCloud\image\pic1.png)

## 2. COOKIE

同上，可在Request Headers中找到，可能会更新，失败了的话检查下这个值




## 3. dir_path 

操作的百度云目录，可以直接复制url中的path部分

![pic2](D:\Project\pyProject\pyForBaiduCloud\image\pic2.png)


# 方法

## 1. create_custom_new_name

构建自定义的新文件名

```
custom_name = create_custom_new_name()
# create_custom_new_name()方法可自定义规则
# 当前的规则是传入文件序号拼接前后缀
```

## 2.create_new_name()

创建新文件名有五种命名模式，建议不适用的模式涉及的参数置空即可

old_name = "oldName.png" ,

### 2.1使用自定义命名

**与 old_name 无关**

```
e.g.
custom_name = "newName.png"
new_name = "newName.png"
```

### 2.2 添加前缀 

prefix 用于添加前缀

```
e.g. 
prefix = "image_"
new_name = "image_oldName.png"
```

### 2.3 添加后缀 

仅适用于后缀名字母数为3的文件

```
e.g. 
prefix = "_image"
new_name = "oldName_image.png"
```

### 2.4 替换扩展名

仅适用于后缀名字母数为3的文件

```
e.g.
extension_name = "txt"
new_name = "oldName.txt"
```

### 2.5 正则替换

pattern 和 replace 用于正则替换
匹配文件中的pattern替换为replace

```
e.g.
pattern = "Name"
replace = "image"
new_name = "oldimage.png"
```

## 3. rename_file_in_dir()

调用函数  list_name_desc(dir)  查询
调用函数  baiduyun_rename(rename_list)  重命名

renameDirChildren 如果为真文件夹将会迭代，即按相同的规则重命名文件夹中的文件



## 4.baiduyun_rename()

将  rename_list 向接口 **https://pan.baidu.com/api/filemanager** 发送重命名请求
输入：rename_list
输出：result

`rename_list` 格式
```
[{"path":PATH,"newname":NEWNAME},{"path":PATH,"newname":NEWNAME}]
```
用`rename_list` 构造`post`请求的`data`时，rename_list 需要 `json.dumps` 转成字符串


## 5.list_name_desc(dir)

查询指定dir的文件,以列表方式返回文件信息
输入：dir
输出：file_info_list
