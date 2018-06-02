# coding: utf-8

import findspark

findspark.init()
from pyspark.sql import SparkSession
from pyspark.mllib.feature import HashingTF, IDFModel, IDF
from pyspark.mllib.classification import NaiveBayesModel
from pyspark.mllib.linalg import Vectors

from os import path

sc = SparkSession \
    .builder \
    .appName("PythonBayesPredict") \
    .getOrCreate() \
    .sparkContext

sc.setLogLevel("INFO")


class PredictSpam:
    def __init__(self):
        self.base_path = 'T:/NaiveBayesModel'
        self.model = None
        self.tf = None
        # self.idf = None

    def predict(self, dataList):
        if self.model is None:
            self.init_spark_components()

        v = self.tf.transform(dataList)
        return self.model.predict(v)

    def load_idf(self):
        print("Loading idf")
        idf_vec_path = path.join(self.base_path, 'idfVector.txt')
        vec = []
        with open(idf_vec_path, 'r') as f:
            vec = [float(val) for val in f.read().split('\n')]
            vec = Vectors.dense(vec)
        idf_model = IDFModel(vec)
        return idf_model

    def init_spark_components(self):
        print("Loading Model")
        self.model = NaiveBayesModel.load(sc, path.join(self.base_path, 'model'))
        self.tf = HashingTF()
        # self.idf = self.load_idf()
