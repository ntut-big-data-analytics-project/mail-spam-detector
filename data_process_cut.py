# coding: utf-8

import os
from glob import glob
from multiprocessing import Pool, freeze_support
from os.path import basename, dirname

from email_helper import *

data_set_path = 'trec06c/data/yahoo/*'  # 'trec06c/data/*/*'
write_path = 'chs_cut/'


def process_and_write_data(file_path):
    try:
        seg_list = process_email(file_path)
        dst_file_name = write_path + os.path.join(basename(dirname(file_path)), basename(file_path))
        os.makedirs(dirname(dst_file_name), exist_ok=True)
        with open(dst_file_name, "w+", encoding='utf8') as f:
            f.write(EMAIL_CONTENT_DELIMITER.join(seg_list))
    except Exception as e:
        print(file_path, e)


if __name__ == '__main__':
    freeze_support()
    with Pool(processes=os.cpu_count() << 1) as pool:
        (pool.map(process_and_write_data, glob(data_set_path)))
