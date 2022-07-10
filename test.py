from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os, re



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
        'base3': os.path.join(os.path.dirname(__file__), r'ui\img\base03.png'),
        'base4': os.path.join(os.path.dirname(__file__), r'ui\img\base04.png'),
        'plot': os.path.join(os.path.dirname(__file__), r'ui\img\chart.png'),
        'table': os.path.join(os.path.dirname(__file__), r'ui\img\tabla.png'),
        'hc': os.path.join(os.path.dirname(__file__), r'ui\img\hc.png'),
        'tf1': os.path.join(os.path.dirname(__file__), r'ui\img\tf1.png'),
        'tf2': os.path.join(os.path.dirname(__file__), r'ui\img\tf2.png'),
        'tf3': os.path.join(os.path.dirname(__file__), r'ui\img\tf3.png'),
        'tf4': os.path.join(os.path.dirname(__file__), r'ui\img\tf4.png'),
        }
    _cultivos_path = {'TRIGO B': os.path.join(
        os.path.dirname(__file__), r'ui\img\assets\cereal_esquema.png'),
        'MAIZ G': os.path.join(os.path.dirname(__file__), r'ui\img\assets\maiz_esquema.png')}

    def __init__(self, lote, parcela, cultivo, produccion, area, npk: list,formulas: list = []):
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
        self.formulas = formulas
        self.img = None

        self.font = ImageFont.truetype("arialbi.ttf", 15)
        self.font2 = ImageFont.truetype("arialbi.ttf", 10)
        self.font3 = ImageFont.truetype("arialbi.ttf", 12)
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

        datos = {
            'percent': -47,
            'biomasa': -10715,
            'chc': -10300,
            'cosecha': -4217,
            'residuo': -6498,
            'fertilizacion': -415
        }

        
        
        w = 117
        h = 307
        p1 = (67,155)
        p2 = (232,155)
        p3 = (400,155)
        p4 = (566,155)

        img = Image.open(self.path['base2'])
        draw = ImageDraw.Draw(img)
        if i >= 1: 
            tf1 = Image.open(self.path['tf1'])
            tf1 = tf1.resize((w, h))
            img.paste(tf1, p1, mask=tf1)
            f1 = self.formulas[0]
            draw.text((120,140), f1, font=ImageFont.truetype("arialbi.ttf", 16),fill=color,anchor='mm') #! FORMULA 1
            draw.text((75, 450), "125951 Kg/Ha\n4580 \u20ac/Ha", font=font, fill=color, align='center', spacing=8)
        if i >= 2:
            tf2 = Image.open(self.path['tf2'])
            tf2 = tf2.resize((w, h))
            img.paste(tf2, p2, mask=tf2)
            f2 = self.formulas[1]
            draw.text((285,140), f2, font=ImageFont.truetype("arialbi.ttf", 16),fill=color,anchor='mm') #! FORMULA 1
            draw.text((245, 450), "125952 Kg/Ha\n4580 $", font=font,fill=color, align='center', spacing=8)
        if i >= 3:
            tf3 = Image.open(self.path['tf3'])
            tf3 = tf3.resize((w, h))
            img.paste(tf3, p3, mask=tf3)
            f3 = self.formulas[2]
            draw.text((455,140), f3, font=ImageFont.truetype("arialbi.ttf", 16),fill=color,anchor='mm') #! FORMULA 1
            draw.text((410, 450), "125952 Kg/Ha\n4580 $", font=font,fill=color, align='center', spacing=8)
   
        if i >= 4:
            tf4 = Image.open(self.path['tf4'])
            tf4 = tf4.resize((w, h))
            img.paste(tf4, p4, mask=tf4)
            f4 = self.formulas[3]
            draw.text((620,140), f4, font=ImageFont.truetype("arialbi.ttf", 16),fill=color,anchor='mm') #! FORMULA 1
            draw.text((580, 450), "125952 Kg/Ha\n4580 $", font=font,fill=color, align='center', spacing=8)
        
        txt = 'Si hacemos las coseas BIEN, además\nde ahorrar Fertilizante, conseguimos un\n{}% de HUELLA DE CARBONO\nrepecto a seguir haciendolas como\nsiempre'.format(
            datos['percent'])
        draw = ImageDraw.Draw(img)
        draw.text((210, 735), txt, 
                    font=ImageFont.truetype("arialbi.ttf", 16),
        fill=self.color,
        anchor='mm', 
        align='center', 
        spacing=10)  # ! TEXTO PANEL
        draw.text((520, 652), '{:,} KgCO2eq/ha'.format(datos['chc']), font=ImageFont.truetype("arialbi.ttf", 22), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA HUELLA DE CARBONO
        draw.text((590, 687), '{:,} KgCO2eq/ha'.format(datos['biomasa']), font=ImageFont.truetype("arialbi.ttf", 15), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA BIOMASA
        draw.text((605, 722), '{:,} KgCO2eq/ha'.format(datos['cosecha']), font=ImageFont.truetype("arialbi.ttf", 15), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA COSECHA
        draw.text((605, 760), '{:,} KgCO2eq/ha'.format(datos['residuo']), font=ImageFont.truetype("arialbi.ttf", 15), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA RESIDUO
        draw.text((580, 797), '{:,} KgCO2eq/ha'.format(datos['fertilizacion']*(-1)), font=ImageFont.truetype("arialbi.ttf", 15), fill=(226, 59, 59),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA FERTILZIACION VARIABLE

        

        img.show()

    def panelTres(self, pesos:list,precios:list):
        def modify(formula):
           
            pa = re.compile('^[0]')
            f = ''
            formula = list(formula.split('-'))
            for e in formula:
                
                if re.match(pa, e):
                    e = e[1:]

                f = f + ' {}% -'.format(e)
                
            return f[:-1]
        
        x = 150
        y = 105
        font = self.font3
        font2 = ImageFont.truetype("arialbi.ttf", 14)
        color = self.color
        img = Image.open(self.path['base3'])
        draw = ImageDraw.Draw(img)
        total_unitario = 0



        if len(pesos) >= 1:
            f1 = self.formulas[0]
            f1 = modify(f1)
            t1 = round(precios[0]/self.area)
            draw.text((140, y), '{}\n\n{} Kg/ha\n{} $/ha\n\n{} Kg'.format(f1, pesos[0],t1, round(pesos[0]*self.area)), font=font2, fill=color, align='center', spacing=8)
            total_unitario = total_unitario + t1

        if len(pesos) >= 2:        
            f2 = self.formulas[1]
            f2 = modify(f2)
            t2= round(precios[1]/self.area)
            draw.text(((148*2)+10, y), '{}\n\n{} Kg/ha\n{} $/ha\n\n{} Kg'.format(f2, pesos[1], t2, round(pesos[1]*self.area)), font=font2, fill=color, align='center', spacing=8)
            total_unitario = total_unitario + t2
        
        if len(pesos) >= 3: 
            f3 = self.formulas[2]
            f3 = modify(f3)
            t3 = round(precios[2]/self.area)
            draw.text(((148*3)+20, y), '{}\n\n{} Kg/ha\n{} $/ha\n\n{} Kg'.format(f3, pesos[2], t3, round(
                pesos[2]*self.area)), font=font2, fill=color, align='center', spacing=8)
            total_unitario = total_unitario + t3
        
        if len(pesos) > 3 :
            f4 = self.formulas[3]
            f4 = modify(f4)
            t4 = round(precios[3]/self.area)
            draw.text(((148*4)+30, y), '{}\n\n{} Kg/ha\n{} $/ha\n\n{} Kg'.format(f3, pesos[3], t4, round(
                pesos[3]*self.area)), font=font2, fill=color, align='center', spacing=8)
            total_unitario = total_unitario + t4

        draw.text((340,295), 
            '{} $/ha'.format(total_unitario),
            font=ImageFont.truetype("arialbi.ttf", 16),
            fill=color,
            align='center')
        draw.text((340, 345),
            '{} Ha'.format(self.area),
            font=ImageFont.truetype("arialbi.ttf", 16),
            fill=color,
            align='center')

        draw.text((600,345),
        '{} $'.format(round(total_unitario*self.area)),
                  font=ImageFont.truetype("arialbi.ttf", 24),
        fill=color)
        formulas = ''
        for f in self.formulas: 
            formulas = formulas + f + ' --- '

        nota = 'Se han calculado {} combinaciones de Fertilizantes para ajustar las necesidades del Cultivo.\nDe ellas se ha seleccionado la combinacion mas economica. Los fertilizantes con los que\nse ha analizado han sido: {}\n***Precios Fertilizantes a dia {}. Pueden sufrir Variacion***'.format(
            len(precios), formulas[:-4], datetime.today().strftime("%d/%m/%Y"))

        draw.text((130, 430),
                  nota, font=ImageFont.truetype("arial.ttf", 12), fill=color)
        


            

        img.show()



        pass 
    
    def panelHuellaCarbono(self, 
    datos:dict={
        'percent':0,
        'chc':0,
        'biomasa':0,
        'cosecha':0,
        'residuo':0,
        'fertilizacion':0
        }):
        font = ImageFont.truetype("arialbi.ttf", 18)
        font2 = ImageFont.truetype("arialbi.ttf", 12)
        img = Image.open(self.path['base4'])
        draw = ImageDraw.Draw(img)
        txt = 'Si hacemos las coseas BIEN, además de\nahorrar Fertilizante, conseguimos un\n{}% de HUELLA DE CARBONO\nrepecto a seguir haciendolas como siempre'.format(datos['percent'])
        draw.text((240, 140), txt, font=font, fill=self.color,
                  anchor='mm', align='center', spacing=12)  # ! TEXTO PANEL
        draw.text((620, 100), '{:,} KgCO2eq/ha'.format(datos['chc']), font=font, fill=(110,178,83),
                  anchor='mm', align='center', spacing=12) #! CAPTURA HUELLA DE CARBONO
        draw.text((680, 135), '{:,} KgCO2eq/ha'.format(datos['biomasa']), font=font2, fill=(0, 0, 0),
                  anchor='mm', align='center', spacing=12) #! CAPTURA BIOMASA
        draw.text((680, 160), '{:,} KgCO2eq/ha'.format(datos['cosecha']), font=font2, fill=(0, 0, 0),
                  anchor='mm', align='center', spacing=12) #! CAPTURA COSECHA
        draw.text((680, 185), '{:,} KgCO2eq/ha'.format(datos['residuo']), font=font2, fill=(0, 0, 0),
                  anchor='mm', align='center', spacing=12) #! CAPTURA RESIDUO
        draw.text((680, 205), '{:,} KgCO2eq/ha'.format(datos['fertilizacion']*(-1)), font=font2, fill=(0, 0, 0),
                  anchor='mm', align='center', spacing=12) #! CAPTURA FERTILZIACION VARIABLE
        img.save(self.path['hc'])
        img.show()
        pass
    

    def showPanel(self):
        # self.panelTres()
        self.img.show()

    def savePanel(self):
        self.panelUno()
        self.img.save(f'{filename}\\{self.lote}-{self.parcela}-{self.cultivo}_{self.date}.png')
    

render = PanelRender('Prueba', 'Prueba', 'TRIGO B', 7895, 2.41 ,[200,200,200],['06-16-24','30-00-00','25-16-00','15-05-05'])
# panel = render.panelUno()
render.panelDos(4)
# graf = render.panelTres([250, 500,200,100],[1500,1000,2500,250])

# render.panelHuellaCarbono(datos)

