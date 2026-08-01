import pandas
from matplotlib import pyplot

table = pandas.read_csv("доп 3.csv", sep=';')
_, axes = pyplot.subplots(1, 4, figsize=(20, 8))
t = table.groupby(['<DATE>']).boxplot(column=["<OPEN>","<CLOSE>","<HIGH>","<LOW>"], ax=axes)
pyplot.savefig('3.png')
pyplot.show()