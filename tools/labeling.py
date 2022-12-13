import math
import os 
GTK_FOLDER = r'C:\Program Files\GTK3-Runtime Win64\lib'
os.environ['PATH'] = GTK_FOLDER + os.pathsep + os.environ.get('PATH', '')

# import psycopg2, psycopg2.extras
from blabel import LabelWriter
import csv
from UUID import uuidGenerator



class AgraeLabelingTools(): 
    label_writer = LabelWriter("resources/item_template.html",default_stylesheets=("resources/style.css",)) # Label template and style (html,css)
    def __init__(self):
        """ AgraeToolset to generate UUID QRCodes

        Utilitie to generate qrcodes to field work.

        Arguments:
            n -- Number of labels to generate with UUID and QRCode
        """        
        
        pass
    
    def progress(self,progress,total):
        
        percent = 100 * (progress/float(total))
        
        bar = '█' + str(percent) + '-' + str((100-percent))
        
        print(f'\r|{bar}| {percent:.2f}%',end='\r')
        
        

    def labels(self,n:int):
        self.uuid = uuidGenerator(n) # uuid generator instance
        self.data = self.uuid.run() # uuid list data 
        numbers = [x for x in range(len(self.data))]
        results = []
        
        self.progress(0,len(numbers))
        for i,x in enumerate(numbers): 
            results.append(math.factorial(x))
            self.progress(i+1,len(numbers))
            
        
        
        print(len(numbers))
        # labels = self.data
        # records = list()
        # i = 0
        # for e in labels:
        #     records.append(dict(uid=e[0]))
        #     i += 1
        #     # print(i)
        # self.label_writer.write_labels(records, target='agrae_labels.pdf')
        


if __name__ == '__main__':
    # n = input('Numero de UUID a generar')
    n = 1000
    labeling = AgraeLabelingTools()
    labeling.labels(n)
