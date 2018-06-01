# coding: utf-8

import os
from glob import glob

from email_helper import *

data_set_path = 'trec06c/data/yahoo/*'  # 'trec06c/data/*/*'
write_path = 'chs_cut/'

for file_path in glob(data_set_path):
    try:
        seg_list = process_email(file_path)
        dst_file_name = write_path + file_path
        os.makedirs(os.path.dirname(dst_file_name), exist_ok=True)
        with open(dst_file_name, "w+", encoding='utf8') as f:
            f.write(EMAIL_CONTENT_DELIMITER.join(seg_list))
    except Exception as e:
        print(file_path, e)

os.getcwd()
