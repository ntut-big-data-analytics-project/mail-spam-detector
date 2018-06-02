# coding: utf-8

import findspark

findspark.init()
from pyspark import SparkContext
from pyspark.mllib.feature import HashingTF
from pyspark.mllib.classification import NaiveBayesModel

sc = SparkContext()


class PredictSpam:
    def __init__(self):
        self.model = NaiveBayesModel.load(sc, '../Bayes/target/tmp/myNaiveBayesModel')

    def predict(self, dataList):
        tf = HashingTF(numFeatures=300)
        ft = tf.transform(dataList)
        return self.model.predict(ft)
