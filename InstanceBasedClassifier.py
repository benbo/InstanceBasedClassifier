import os 
import pandas as pd
import numpy as np
import math
import json
import global_align as ga
#ucr dtw
from  _ucrdtw import ucrdtw
#R dtw
#import rpy2.robjects.numpy2ri
#from rpy2.robjects.packages import importr
#rpy2.robjects.numpy2ri.activate()

class InstanceBasedClassifier:

    def __init__(self):
        self.verbose=True
        self.X=None
        self.w=None
        self.normalize=False
        self.header=None
        self.symbols=None
        self.scores=None
        self.ranking=None
        self.example_data=None
        self.test_data=None
        self.labels=None
        
    #load fingerprints and test data
    #set labels for examples
    def load_data(self)
        examples=['COLV','RNBI']
        #data_info=('dtw','txt')
        data_info=('dtw')
        self.labels={key:1.0 for key in examples}#-1.0 for negatives
        
        #tickdata=self.load_all_ticks(directory='data/small/',remove_cols=[0,2])
        #tickdata=self.load_all_ticks(directory='data/securities/',remove_cols=[0,2])
        tickdata=self.load_all_ticks(directory='data/just3/',remove_cols=[0,2])
        tickdata=self.clean_ticks_naive(tickdata)
        
        
        return example_data,test_data
        
    def generate_scores(self):
        
        self.load_data()

        
        #do more preprocessing? Some linear amplitude scaling?        
        #if self.normalize: UCRDTW already does z-axis normalization
        #    tickdata={key:self.normalize_df(tickdata[key]) for key in tickdata }
        

        self.example_data={f:tickdata[f] for f in examples}
        #column_names=self.example_data[examples[0]].columns
        self.test_data={f:tickdata[f] for f in tickdata if f not in self.example_data}
        self.symbols=self.test_data.keys()

        #initialize hyper parameters
        self.n=len(self.symbols)
        num_columns=len(self.example_data[examples[0]].keys())
        self.w=np.array([1.0/num_columns]*num_columns)
        self.f=np.zeros(self.n)
        for j,ex_key in enumerate(self.example_data):
            #if self.verbose:
                #print ex_key
            fj=self.calc_distances(ex_key)
            self.f=self.f+self.labels[ex_key]*np.exp(-fj)
        self.ranking=self.f.argsort()[::-1]
        
    def calc_distances(self,ex_key):
        example=self.example_data[ex_key]
        
        #UCRDTW
        z=np.zeros(self.n)
        for c,col in enumerate(example):
            x=example[col].values[::-1]
            z_c=np.array([ucrdtw(df[col].values[::-1], x, 0.20, False)[1] for key, df in self.test_data.iteritems()])
            #print col
            #print z_c
            z=z+self.w[c]*z_c
        return z        
        
        #R DTW distance
        # Set up our R namespaces
        #R = rpy2.robjects.r
        #DTW = importr('dtw')
        #z=np.zeros(self.n)
        #for c,col in enumerate(example):
        #    x=example[col].values
        #    z_c=np.array([R.dtw(x, df[col].values, keep=True).rx('normalizedDistance')[0][0] for key, df in self.test_data.iteritems()])
        #    print col
        #    print z_c
        #    z=z+self.w[c]*z_c
        #return z        

    def load_promotions(self,path='data/promotions/3.jl'):
        data=json.loads(path)
        return data

    def normalize_df(self,df):
        return (df - df.mean()) / (df.max() - df.min())
            
    def clean_ticks_naive(self,data):
        for key in data:
            data[key].dropna(how='all',inplace=True)#remove rows that only contain nas
            data[key].fillna(method='ffill',inplace=True,limit=3)#forward fill next 3 days if nas are present
            data[key].fillna(0,inplace=True)#fill the rest with zeros
        return data

    def load_ticker(self,path,date_head='Date',remove_cols=[]):
        data = pd.read_csv(path)  
        data.index = pd.to_datetime(data.pop(date_head))
        for x in remove_cols:
            data.drop([data.columns[x]], axis=1,inplace=True)
        return data.astype(float)

    def load_all_ticks(self,directory='data/securities/',remove_cols=[]):
        fnames = [ fname for fname in os.listdir(directory) if os.path.isfile(os.path.join(directory,fname))]
        return {fname.replace('.csv',''):self.load_ticker(os.path.join(directory,fname),remove_cols=remove_cols) for fname in fnames}
