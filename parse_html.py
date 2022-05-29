# 此脚本从Wiki的网页中提取文字信息，放入到指定文件夹中
# author: YangSh
# date: 20220112

from bs4 import BeautifulSoup
import os
import shutil
import opencc
from urllib import parse as urlparse

# 繁体转简体
chinese_t2s = opencc.OpenCC('t2s')

HTML_ROOT_DIR = r'D:\gitworkspace\robert6757\kiwix\out\A'
ENTITY_OUTPUT_DIR = r'D:\gitworkspace\robert6757\embedding\Datas\wiki\top\ori'

IGNORE_IMAGES = {
    'Wikibooks-logo-en-noslogan.svg.png.webp',
    'Commons-logo.svg.png.webp',
    'Disambig_gray.svg.png.webp'
}

SYMBOL_REPLACE_DICT = {
    '/':'&slash;',
    '\\':'&nslash;',
    ':':'&colon;',
    '*':'&asterisk;',
    '"':'&quote;',
    '<':'&lab;',
    '>':'&rab;',
    '|':'&vl;'
}

class HtmlEntityObj:
    # 实体名称
    entityName = ""
    # 实体内容
    entityContent = ""
    # 实体附件
    entityAttachments = []

    def __init__(self):
        self.entityName = ""
        self.entityContent = ""
        self.entityAttachments = []

    def export(self, html_path, folder_path):
        print('Begin %s' % html_path)
        try:
            # 1.准备路径、文件夹
            entity_folder_name = self.entityName
            for key in SYMBOL_REPLACE_DICT.keys():
                # 特殊符号替换
                entity_folder_name = entity_folder_name.replace(key, SYMBOL_REPLACE_DICT[key])

            entity_output_dir = os.path.join(folder_path, entity_folder_name)
            if os.path.exists(entity_output_dir) is False:
                os.makedirs(entity_output_dir)
            content_file_path = os.path.join(entity_output_dir, 'content.txt')

            # 2.导出文档
            with open(content_file_path, 'w', encoding='utf-8') as content_file:
                content_file.write(self.entityContent)
                content_file.close()

            # 3.导出附件
            for attachment_file in self.entityAttachments:
                html_folder = html_path[:html_path.rfind('\\')]
                attachment_file_path = os.path.join(html_folder, os.path.normpath(attachment_file))
                attachment_file_path = os.path.normpath(attachment_file_path)
                copy_to_filename = attachment_file[attachment_file.rfind('/')+1:]
                copy_to_filename = copy_to_filename[:-5]
                copy_to_fullpath = os.path.join(entity_output_dir, copy_to_filename)

                if os.path.exists(attachment_file_path) is False:
                    print('Cannot find attachment file %s' % attachment_file_path)
                    continue
                shutil.copyfile(attachment_file_path, copy_to_fullpath)

            # 4.导出原始文件
            shutil.copyfile(html_path, os.path.join(entity_output_dir, 'raw.html'))
            print('Finish exporting to %s' % entity_output_dir)
        except:
            print('Failed to exporting %s' % html_path)


def gen_entity(html_path, output_dir):
    # 1. read html
    if os.path.exists(html_path) is False:
        return

    with open(html_path, encoding='utf-8') as html_file_obj:
        html_full_content = html_file_obj.read()
        html_file_obj.close()

    # 2. parse html
    soup = BeautifulSoup(html_full_content, 'html.parser')
    if (soup.title is None):
        return
    # print(soup.prettify())

    entity = HtmlEntityObj()
    entity.entityName = soup.title.string
    entity.entityName = chinese_t2s.convert(entity.entityName)

    # TODO
    # 空格部分待移除
    # print(soup.get_text())
    entity.entityContent = soup.get_text()
    # 繁体转简体
    entity.entityContent = chinese_t2s.convert(entity.entityContent)

    # 3.找寻所有相关的图片
    for img_tag in soup.find_all('img'):
        img_src = img_tag.get('src')
        if img_src is None:
            continue
        img_src = urlparse.unquote(img_src)
        img_name = os.path.basename(img_src)

        if img_name in IGNORE_IMAGES:
            # 忽略图片
            continue
        entity.entityAttachments.append(img_src)

    # 4.导出到磁盘
    entity.export(html_path, output_dir)

def find_all_files(path, all_files):
    file_list = os.listdir(path)
    for file in file_list:
        cur_path = os.path.join(path, file)
        if os.path.isdir(cur_path):
            # 递归调用
            find_all_files(cur_path, all_files)
        else:
            all_files.append(cur_path)
    return all_files

def main_i():
    all_file_path = []
    find_all_files(HTML_ROOT_DIR, all_file_path)
    # all_file_path.append(r'F:\kiwix\mount\dump\A\8B\10B')

    count_all = len(all_file_path)
    count_i = 1
    output_dir = ENTITY_OUTPUT_DIR + "\\parse_out_0"
    for html_path in all_file_path:
        if count_i % 1000 == 0:
            # 输出到文件夹中
            output_dir = ENTITY_OUTPUT_DIR + "\\parse_out_%d" % count_i
        gen_entity(html_path, output_dir)
        print("Process [%d, %d]" % (count_i, count_all))
        count_i += 1

if __name__ == "__main__":
    main_i()


