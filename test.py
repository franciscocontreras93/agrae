import sys
import qgis
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QApplication

class MainWindow(QMainWindow): 
    def __init__(self) -> None:
        super(MainWindow,self).__init__()
        
        self.UIComponents() 
        
        
        pass
    
    def UIComponents(self): 
        
        layout = QGridLayout() 
        self.setLayout(layout)
        
        label = QLabel()
        
        label.setText('Hello World') 
        
        layout.addWidget(label)
        
        
        
        
if __name__ == '__main__': 
    app = QApplication(sys.argv) 
    
    main = MainWindow() 
    
    main.show() 
    
    app.exec() 
    