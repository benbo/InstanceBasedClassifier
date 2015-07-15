import os 
import pandas as pd
import numpy as np
import math
import json
import global_align as ga

class InstanceBasedClassifier:

    def __init__(self):
        self.verbose=True
        self.X=None
        self.w=None
        self.normalize=False
        self.header=None
        self.tickdata=None
        self.symbols=None
        self.scores=None
        self.ranking=None
        
    def init_weights(self):
        num_columns=self.X.shape[1]
        self.w=np.array([1.0/num_columns]*num_columns)
        

    def generate_ranking_matrix(self):
        pos_examples=['COLV','RNBI']
        tickdata=self.load_all_ticks(directory='data/small/',remove_cols=[0,2])
        tickdata=self.clean_ticks_naive(tickdata)
        #do more preprocessing? Some linear amplitude scaling?        
        if self.normalize:
            tickdata={key:self.normalize_df(tickdata[key]) for key in tickdata }

        lengths=np.array([len(tickdata[m]) for m in tickdata ])

        pos_data={f:tickdata[f] for f in pos_examples}
        column_names=pos_data[pos_examples[0]].columns
        pos_examples=set(pos_examples)
        neg_data={f:tickdata[f] for f in tickdata if f not in pos_examples}
        #del tickdata
        #############
        #Use GA kernel (naive)
        #############

        #initialize hyper parameters
        median_length=np.median(lengths)
        sigma=10*math.sqrt(median_length)
        pos_lengths=np.array([len(pos_data[m]) for m in pos_data])
        lmin=pos_lengths.min()
        #Ts=[np.abs(lmin/4),np.abs(lmin/2),lmin]
        Ts=[np.abs(lmin/4),np.abs(lmin/2)]
        n=len(neg_data.keys())
        num_col=len(column_names)
        num_pos=len(pos_examples)
        num_Ts=len(Ts)
        m=num_col*num_pos*num_Ts
        X=np.zeros((n, m))
        header=['']*m
        for i,pos_key in enumerate(pos_data):
            if self.verbose:
                print pos_key
            for j,colname in enumerate(column_names):
                x=pos_data[pos_key][colname].values.reshape((-1,1))
                for k,triangular in enumerate(Ts):
                    idx=i*num_col*num_Ts+j*num_Ts+k
                    header[idx]=pos_key+'_'+colname+'_GA_T'+str(triangular)
                    for row,neg_key in enumerate(neg_data): 
                        y=neg_data[neg_key][colname].values.reshape((-1,1))
                        norm_sim=1.0/(np.exp(ga.tga_dissimilarity(x,y,sigma,triangular)-0.5*(ga.tga_dissimilarity(x,x,sigma,triangular)+ga.tga_dissimilarity(y,y,sigma,triangular))))
                        if norm_sim > 0:
                            X[row,idx]=norm_sim
        self.X=X
        self.header=header
        self.tickdata=tickdata
        self.symbols=tickdata.keys()

    def generate_ranking(self):
        if self.w is None:
            self.init_weights()
        self.scores=self.X.dot(self.w)
        self.ranking=self.scores.argsort()[::-1]#[:n]

    def load_promotions(self,path='data/promotions/3.jl'):
        data=json.loads(path)
        return data

    def normalize_df(self,df):
        return (df - df.mean()) / (df.max() - df.min())
    #def featurize_tick(self,df,function_list=[]):
        #featurelist=[]
        #TODO implement a more general way
        #generic
        #for func_name in function_list:
        #    temp_method = getattr(self, func_name)
            
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
        #return pd.concat([self.load_ticker(os.path.join(directory,fname)) for fname in fnames],axis=1,keys =[fname.replace('.csv','') for fname in fnames])
