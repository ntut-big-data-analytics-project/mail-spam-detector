
# coding: utf-8



import findspark
findspark.init()
from glob import glob
import pyspark # only run after findspark.init()
from pyspark.sql import SparkSession
from pyspark import SparkFiles
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.mllib.feature import HashingTF
from pyspark.mllib.classification import NaiveBayes, NaiveBayesModel
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.util import MLUtils
from email_helper import *
sc = SparkContext()


class PredictSpam():
    def __init__(self):
        self.model = NaiveBayesModel.load(sc,'../Bayes/target/tmp/myNaiveBayesModel')




    def predict(self,dataList):
        tf = HashingTF(numFeatures=300)
        ft=tf.transform(dataList)
        return self.model.predict(ft)
        





