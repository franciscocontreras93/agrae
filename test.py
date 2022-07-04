from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os



class PanelRender():
    """
    Class PanelRender:  Renderiza el panel agropecuario con los siguientes parametros. 
    lote(string) = Nombre del Lote.
    parcela(string) = Nombre Parcelario.
    cultivo = Nombre Cultivo
    produccion(int) = Produccion Ponderada
    n,p,k (int) = Valores Resultantes de NPK 

    """

    path = {
        'base': os.path.join(os.path.dirname(__file__), r'ui\img\base00.png'),
        'base2': os.path.join(os.path.dirname(__file__), r'ui\img\base02.png'),
        'plot': os.path.join(os.path.dirname(__file__), r'ui\img\chart.png'),
        'table': os.path.join(os.path.dirname(__file__), r'ui\img\tabla.png'),
        'tf1': os.path.join(os.path.dirname(__file__), r'ui\img\tf1.png'),
        'tf2': os.path.join(os.path.dirname(__file__), r'ui\img\tf2.png'),
        'tf3': os.path.join(os.path.dirname(__file__), r'ui\img\tf3.png'),
        'tf4': os.path.join(os.path.dirname(__file__), r'ui\img\tf4.png'),
            }
    _cultivos_path = {'TRIGO B': os.path.join(
        os.path.dirname(__file__), r'ui\img\assets\cereal_esquema.png'),
        'MAIZ G': os.path.join(os.path.dirname(__file__), r'ui\img\assets\maiz_esquema.png')}

    def __init__(self, lote, parcela, cultivo, produccion,area, npk:list):
        self.now = datetime.now()
        self.date = self.now.strftime("%H%M%S%d%m%y")
        self.lote = lote
        self.parcela = parcela
        self.cultivo = cultivo
        self.prod_ponderado = produccion
        self.area = area
        self.n_ponderado = npk[0]
        self.p_ponderado = npk[1]
        self.k_ponderado = npk[2]

        self.img = None

        self.font = ImageFont.truetype("arialbi.ttf", 15)
        self.font2 = ImageFont.truetype("arialbi.ttf", 10)
        self.color = (0, 0, 0)


        pass
    
    def panelUno(self):
        filename = r'C:\Users\FRANCISCO\Documents\agrae\Paneles'
        img = Image.open(self.path['base'])
        font = self.font
        font2 = self.font2
        color = self.color
        d1 = ImageDraw.Draw(img)
        d1.text((328, 434), "{} Kg cosecha/Ha".format(self.prod_ponderado),
                font=self.font, fill=color)
        d2 = ImageDraw.Draw(img)
        d2.text((630, 434), "{} Ha".format(self.area), font=self.font, fill=color)
        d3 = ImageDraw.Draw(img)
        d3.text((576, 456), "{} / {} / {}".format(self.n_ponderado, self.p_ponderado, self.k_ponderado),
                font=self.font, fill=color)
        img2 = Image.open(self.path['plot'])
        img2 = img2.resize((281, 211))
        img.paste(img2, (25, 184), mask=img2)  # ! PASTE PLOT
        img3 = Image.open(self.path['table'])
        img3 = img3.resize((386, 225))
        img.paste(img3, (314, 187), mask=img3)  # ! PASTE TABLE
        # img4 = Image.open(self.path['trigo_esquema'])
        # img4 = img4.resize((290,141))
        # img.paste(img4, (25, 50), mask=img4)   # ! PASTE ESQUEMA
        self.setEsquema(self.cultivo, img)
        d4 = ImageDraw.Draw(img)
        d4.text((44, 225), "N", font=font2, fill=color)
        d4.text((44, 262), "P", font=font2, fill=color)
        d4.text((44, 303), "K", font=font2, fill=color)
        d4.text((28, 340), "Carb.", font=font2, fill=color)

        # d5 = ImageDraw.Draw(img)
        # d5.text((157, 95), "TITULO CULTIVO",
        #         font=ImageFont.truetype("arialbi.ttf", 18), fill=color)

        self.img = img    
    
    def setEsquema(self,cultivo,img):
        try: 
            if cultivo in self._cultivos_path: 
                path = self._cultivos_path[cultivo]
                esquema = Image.open(path)
                esquema = esquema.resize((290, 141))
                img.paste(esquema, (25, 50), mask=esquema)
        except UnboundLocalError:
            print('No existe Grafico') 
            pass

        
    def panelDos(self,i):
        font = self.font
        font2 = self.font2
        color = self.color
        
        w = 117
        h = 307
        p1 = (67,135)
        p2 = (232,135)
        p3 = (400,135)
        p4 = (566,135)

        img = Image.open(self.path['base2'])
        if i >= 1: 
            tf1 = Image.open(self.path['tf1'])
            tf1 = tf1.resize((w, h))
            img.paste(tf1, p1, mask=tf1)
            peso_1 = ImageDraw.Draw(img)
            peso_1.text((100, 430), "125951 Kg/Ha", font=font, fill=color)
            precio_1 = ImageDraw.Draw(img)
            precio_1.text((100, 450), "4580 \u20ac/Ha", font=font2, fill=color)
        if i >= 2:
            tf2 = Image.open(self.path['tf2'])
            tf2 = tf2.resize((w, h))
            img.paste(tf2, p2, mask=tf2)
            peso_2 = ImageDraw.Draw(img)
            peso_2.text((266, 430), "125952 Kg/Ha", font=font, fill=color)
            precio_2 = ImageDraw.Draw(img)
            precio_2.text((266, 450), "4580 $", font=font2, fill=color)
        if i >= 3:
            tf3 = Image.open(self.path['tf3'])
            tf3 = tf3.resize((w, h))
            img.paste(tf3, p3, mask=tf3)
            peso_3 = ImageDraw.Draw(img)
            peso_3.text((432, 430), "125953 Kg/Ha", font=font, fill=color)
            precio_3 = ImageDraw.Draw(img)
            precio_3.text((432, 450), "4580 $", font=font2, fill=color)
        if i >= 4:
            tf4 = Image.open(self.path['tf4'])
            tf4 = tf4.resize((w, h))
            img.paste(tf4, p4, mask=tf4)
            peso_4 = ImageDraw.Draw(img)
            peso_4.text((598, 430), "125954 Kg/Ha", font=font, fill=color)
            precio_3 = ImageDraw.Draw(img)
            precio_3.text((598, 450), "4580 $", font=font2, fill=color)

        img.show()

    def showPanel(self):
        self.panelUno()
        self.img.show()

    def savePanel(self):
        self.panelUno()
        self.img.save(f'{filename}\\{self.lote}-{self.parcela}-{self.cultivo}_{self.date}.png')
    
    

render = PanelRender('Prueba', 'Prueba', 'TRIGO B', 7895, 0.85,[200,200,200])
# panel = render.panelUno()
graf = render.panelDos(4)
