# coding: utf-8

import findspark

findspark.init()
from pyspark import SparkContext
from pyspark.mllib.feature import HashingTF, IDFModel
from pyspark.mllib.classification import NaiveBayesModel

from os import path

sc = SparkContext()
sc.setLogLevel("INFO")


class PredictSpam:
    def __init__(self):
        self.base_path = 'T:/NaiveBayesModel'
        self.model = None
        self.tf = None
        self.idf = None

    def predict(self, dataList):
        if self.model is None:
            self.init_spark_components()

        v1 = self.tf.transform(dataList)
        ft = self.idf.transform(v1)
        return self.model.predict(ft)

    def load_idf(self):
        idf_vec_path = path.join(self.base_path, 'idfVector.txt')
        vec = []
        with open(idf_vec_path, 'r') as f:
            arr = f.read().split('\n')
            vec = list(map(lambda v: float(v), arr))
        idf_model = IDFModel(vec)

        return idf_model

    def init_spark_components(self):
        self.model = NaiveBayesModel.load(sc, path.join(self.base_path, 'model'))
        self.tf = HashingTF()
        self.idf = self.load_idf()
