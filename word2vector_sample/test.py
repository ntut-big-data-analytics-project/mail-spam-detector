 #-*- coding: utf-8 -*-
__author__ = "ALEX-CHUN-YU (P76064538@mail.ncku.edu.tw)"
import warnings
import sys
warnings.filterwarnings(action = 'ignore', category = UserWarning, module = 'gensim')
from gensim.models.keyedvectors import KeyedVectors
'''# 一次處理完畢
from wiki_to_txt import Wiki_to_txt
from segmentation import Segmentation
from train import Train
'''

#載入 model 並去運用
def main():
        word_vectors = KeyedVectors.load_word2vec_format("wiki300.model.bin", binary = True)
        try:
                query = sys.argv[1:]
                res = word_vectors.most_similar(query[0], topn = 5)
                for item in res:
                        print(item[0] + "," + str(item[1]))
                return res
        except Exception as e:
                print("Error:" + repr(e))

if __name__ == "__main__":
    main()
