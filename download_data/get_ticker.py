import os
import urllib

if __name__ == "__main__":
    #load ticker symbols
    penny_stock_symbols=[line.split('\t')[0].strip() for line in open('../data/Stock_screener.csv','r')]
    from_year='2010'
    u="http://ichart.yahoo.com/table.csv?s=%s&a=0&b=1&c="+from_year
    directory='../data/securities/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    d=directory+'%s.csv'
    for s in penny_stock_symbols:
        #urllib.urlretrieve(u % s, d % s)
        print s
