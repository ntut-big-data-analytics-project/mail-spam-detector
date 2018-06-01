# coding: utf-8

import os
from glob import glob
from multiprocessing import Pool, freeze_support
from os.path import basename, dirname

from email_helper import *

data_set_path = 'Y:\\trec06c\\*\\*\\*'  # 'trec06c/data/*/*'
write_path = 'Y:\\chs_cut\\'


def process_and_write_data(file_path):
    try:
        seg_list = process_email(file_path)
        email_type = basename(dirname(dirname(file_path)))
        dst_file_name = write_path + os.path.join(email_type, basename(dirname(file_path)), basename(file_path))
        os.makedirs(dirname(dst_file_name), exist_ok=True)
        with open(dst_file_name, "w+", encoding='utf8') as f:
            f.write(EMAIL_CONTENT_DELIMITER.join(seg_list))
    except Exception as e:
        print(file_path, e)


if __name__ == '__main__':
    # process_email("Y:\\2c23eff186c76668c7bec9db096a65eb.eml")
    freeze_support()
    with Pool(processes=os.cpu_count()) as pool:
        (pool.map(process_and_write_data, glob(data_set_path)))
