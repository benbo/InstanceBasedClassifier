from os import listdir
import os # isfile, join
import numpy as np

class EasyFeaturizer:
    def __init__ (self, verbose=True):
        self.verbose=True
        self.strfalse=['false', '0', 'f', 'n', 'no', 'nope', 'certainly not']
        #TODO store data in a database
        self.datastore={}


    def add_to_datastore(self,name,data):
        self.datastore[name]=data

    #Read in Annual and Quarterly Financial Statements data
    def featurize_AQFS(self,config_files):
        datastore={}
        for config_file in config_files:
            #parse args
            args=self.parse_config(config_file)

            data=self.read_from_flatfiles(args)
            name=config_file.split('.')[0].split('/')[-1]
            if 'name' in args:
                name=args['name']
            self.add_to_datastore(name,data)
        print 'done extracting data'

    def read_from_flatfiles(self,args):
        #gather all files into files list
        paths=[]
        path=''
        files=[]
        if 'path' in args:
            path=args['path'][0]
        if 'paths' in args:
            paths=args['paths']
        if 'root' in args:
            paths=[x[0] for x in os.walk(root)]
        if 'files' in args:
            files=[os.path.join(path,f) for f in args['files']]
            files=[ f for f in files if os.path.isfile(f)]
            if len(files)==0:
                raise Exception ("No files found. Check filenames.")
        else:
            if self.verbose:
                print 'gathering files'
            if 'filename' in args:
                filename=args['filename'][0]
                for path in paths:
                    files.extend( [ os.path.join(path,f) for f in listdir(path) if f == filename ])
            elif 'fileprefix' in args:
                prefix=tuple(args['fileprefix'])
                for path in paths:
                    files.extend( [ os.path.join(path,f) for f in listdir(path) if f.startswith(prefix)])
            elif 'filesuffix' in args:
                suffix=tuple(args['filesuffix'])
                for path in paths:
                    files.extend( [ os.path.join(path,f) for f in listdir(path) if f.endswith(suffix)])
            else:
                for path in paths:
                    files.extend( [ os.path.join(path,f) for f in listdir(path)])

            files=[ f for f in files if os.path.isfile(f)]
            if len(files)==0:
                raise Exception ("No files could be found")
        if self.verbose:
            print 'the following files will be parsed:'
            for f in files:
                print f 
        if 'csv' in args:
            self.read_csv(files,args)
        else:#custom
            self.read_flat_custom(files,args)
            #all files to be parsed should now be in files

    def read_csv(self,files,args):
        skip_head=0
        if 'header' in args:
            skip_head=1
            if args['header'] != '':
                try:
                    skip_head=int(args['header'])
                except:
                    skip_head=1
        delim=','
        if 'delimeter' in args:
            delim=args['delimeter']
        if 'columns' in args:
            columns=(int(a) for a in args.['columns'])
        #read
        data = np.genfromtxt(csvfile,skip_header=skip_head, delimiter=delim, dtype=None,usecols=columns)
        #TODO apply filters
        return data 

    def read_flat_custom(self,files,args):
        skip_head=0
        if 'header' in args:
            skip_head=1
            if args['header'] != '':
                try:
                    skip_head=int(args['header'])
                except:
                    skip_head=1
        delimeter=','
        if 'delimeter' in args:
            delimeter=args['delimeter']
        for fname in files:
            with open(fname,'r') as f:
                if skip_head>0:
                    for line in xrange(skip_head):
                        next(f)
                for line in f:
                    #dosomething
                    line=line
                    #TODO custom read lines
                    #TODO apply filters
    def parse_config(self,filepath):
        args_dict={}
        with open(filepath,'r') as f:
            for line in f:
                text=line.rstrip().split('#')#everything after # is comment so config string is in [0]
                fields = text[0].split('=')
                if len(fields) > 1:
                    args_dict[fields[0]]=fields[1].split(',')
                else:
                    args_dict[fields[0]]=''
        return args_dict


