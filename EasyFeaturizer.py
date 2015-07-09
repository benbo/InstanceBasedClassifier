from os import listdir
import os # isfile, join

class EasyFeaturizer:
    def __init__ (self, verbose=True):
        self.verbose=True
        self.strfalse=['false', '0', 'f', 'n', 'no', 'nope', 'certainly not']
    #Read in Annual and Quarterly Financial Statements data
    def featurize_AQFS(self,config_files):
        for config_file in config_files:
            #parse args
            args=self.parse_config(config_file)

            data=self.read_from_flatfiles(args)

    def read_from_flatfiles(self,args):
        #initialize variables from args
        header=False
        if 'header' in args:
            header=True
            if args['header'].lower() in self.strfalse:
                header=False

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
        
        #all files to be parsed should now be in files

        

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


