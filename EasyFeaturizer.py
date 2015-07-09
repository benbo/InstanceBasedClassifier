from os import listdir
import os.path # isfile, join

class EasyFeaturizer:
    def __init__ (self, verbose=True):
        self.verbose=True

    #Read in Annual and Quarterly Financial Statements data
    def featurize_AQFS(self,config_file):
        #parse args
        args=self.parse_config(config_file)

        data=self.read_from_flatfiles(args)

    def read_from_flatfiles(self,args):
        #initialize variables from args
        header=False
        if 'header' in args:
            header=True
        path=''
        if 'path' in args:
            path=args['path'][0]
        files=[]
        if 'files' in args:
            files=[os.path.join(path,f) for f in args['files']]
            files=[ f for f in files if os.path.isfile(f)]
            if len(files)==0:
                raise Exception ("No files found. Check filenames.")
        else:
            files = [ f for f in listdir(path) if os.path.isfile(os.path.join(path,f)) ]
            if len(files)==0:
                raise Exception ("No files specified and path is empty")
    
        

    def parse_config(self,filepath):
        args_dict={}
        with open(filepath,'r') as f:
            for line in f:
                text=line.split('#')#everything after # is comment so config string is in [0]
                fields = text[0].split('=')
                if len(fields) > 0:
                    args_dict[fields[0]]=fields[1].split(',')
                else:
                    args_dict[fields[0]]=''
        return args_dict


