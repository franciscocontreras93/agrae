import uuid
import csv

class uuidGenerator(): 
    """uuidGenerator _summary_

    _extended_summary_
    """    
    def __init__(self,n) -> None:
        self.n = n
        pass
        
    
    def run(self):
        l = list()
        try:
            for e in range(self.n): 
                e = str(uuid.uuid4())
                l.append([e])
            
            with open('agrae_uuid.csv','w',newline='') as file: 
                writer = csv.writer(file)
                writer.writerows(l)
            print('Work Done!')
            return l
        except: 
            print('An Error has Ocurred while creating UUID')
            return None
