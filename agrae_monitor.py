
import os
import sys
from psycopg2 import extras,errors

from qgis.PyQt import uic
from qgis.core import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QSettings, QDateTime, QThreadPool, QSize
from PyQt5.QtGui import QColor,QFont,QIcon
from .utils import AgraeToolset, AgraeUtils, AgraeZipper
from .agrae_worker import Worker

agraeRindesMonitorDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/monitor.ui'))
agraeRindesMonitorVerify, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/monitorVerify.ui'))
class agraeRindesMonitor(QDialog,agraeRindesMonitorDialog):
    closingPlugin = pyqtSignal()
    def __init__(self, parent=None) -> None:
        super(agraeRindesMonitor,self).__init__(parent)
        self.setupUi(self)
        self.utils = AgraeUtils()
        self.tools = AgraeToolset()
        self.conn = AgraeUtils().Conn()
        self.icons_path = self.utils.iconsPath()
        self.sinceDateStatus = False
        self.setWindowTitle('Monitor de Rendimientos')

        self.UIComponents()
        self.getCampanias()

    def UIComponents(self):
         #* COMPLETERS
        # dataLotes = 
        completerLote = QCompleter([str(e[0]).upper() for e in self.dataAutoLote()])
        completerLote.setCaseSensitivity(False)

        #* UI COMPONENTS
        self.setWindowIcon(QIcon(self.icons_path['monitor']))

        #* TABLE WIDGETS COLUMNS HIDE
        self.tableWidget.setColumnHidden(0, True)   # columna id lote parcela
        self.tableWidget.setColumnHidden(1, True)   # columna id explotacion
        self.tableWidget.setColumnHidden(2, True)   # columna id CAMPANIA
        self.tableWidget .horizontalHeader().setStretchLastSection(True)

        self.tableWidget_2.setColumnHidden(0, True)   # columna id lote parcela
        self.tableWidget_2.setColumnHidden(1, True)   # columna id explotacion
        self.tableWidget_2.setColumnHidden(2, True)   # columna id CAMPANIA
        self.tableWidget_2 .horizontalHeader().setStretchLastSection(True)
        
        
        #* LINES
        self.line_buscar.setClearButtonEnabled(True)
        self.line_buscar.returnPressed.connect(self.buscarLotes)
        self.line_buscar.setCompleter(completerLote)
        line_buscar_action = self.line_buscar.addAction(
                    QIcon(self.icons_path['search_icon_path']), self.line_buscar.TrailingPosition)
        line_buscar_action.triggered.connect(self.buscarLotes)

        #* BUTTONS
        self.btn_add.setIcon(QIcon(self.icons_path['add_plus']))
        self.btn_add.setIconSize(QSize(20, 20))
        self.btn_add.setToolTip('Agregar Lote')
        self.btn_add.clicked.connect(self._addRow)

        
        self.btn_remove.setIcon(QIcon(self.icons_path['drop_rel']))
        self.btn_remove.setIconSize(QSize(20, 20))
        self.btn_remove.clicked.connect(self._removeRow)
        self.btn_remove.setToolTip('Remover Lote seleccionado')

        self.btn_save.setIcon(QIcon(self.icons_path['save']))
        self.btn_save.setIconSize(QSize(20, 20))
        # self.btn_save.clicked.connect(self.test)
        self.btn_save.clicked.connect(self.saveProductionData)
        self.btn_save.setToolTip('Guardar Datos de Produccion')
        
       
        self.btn_adjust.setIcon(QIcon(self.icons_path['regression']))
        self.btn_adjust.setIconSize(QSize(20, 20))
        self.btn_adjust.setToolTip('Ajustar valores de Rendimiento')
        self.btn_adjust.clicked.connect(self.ajusteRinde)
        
        self.btn_validate.setIcon(QIcon(self.icons_path['check']))
        self.btn_validate.setIconSize(QSize(20, 20))
        self.btn_validate.setToolTip('Validar datos de rindes')
        self.btn_validate.clicked.connect(self.validateRinde)
        

        #* COMBOS
        self.combo_exp.currentIndexChanged.connect(self.buscarLotes)
        self.combo_camp.currentIndexChanged.connect(self.getExpCampanias)

       


     

        pass

    def dataAutoLote(self): 
        cursor = self.conn.cursor()
        sql = '''select distinct unnest(array[lote,exp_nombre]) from lotes'''
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    
    def getCampanias(self):
        with self.conn.cursor(cursor_factory = extras.RealDictCursor) as cursor: 
            sql = '''select id,nombre FROM datos.campanias ORDER BY nombre'''
            cursor.execute(sql)
            data = cursor.fetchall()
            for e in data:
                self.combo_camp.addItem(e['nombre'],e['id'])

    def getExpCampanias(self):
        idCampania = self.combo_camp.currentData()
        self.combo_exp.clear()
        
        with self.conn.cursor(cursor_factory = extras.RealDictCursor) as cursor: 
            sql = '''SELECT distinct e.idexplotacion id, e.nombre FROM public.explotacion e 
            JOIN public.campania cmp ON cmp.idexplotacion = e.idexplotacion 
            JOIN public.lotecampania lc1 ON lc1.idcampania = cmp.idcampania 
            JOIN datos.lotescampania lc2 ON lc2.idlotecampania  = lc1.idlotecampania  
            JOIN datos.campanias camp ON camp.id = lc2.idcampania
            WHERE camp.id = {}; '''.format(idCampania)
            cursor.execute(sql)
            data = cursor.fetchall()
            # print(data)

            for e in data:
                self.combo_exp.addItem(e['nombre'],e['id'])

    def  buscarLotes(self):
        status = self.sinceDateStatus
        nombre = self.line_buscar.text()
        idCampania = self.combo_camp.currentData()
        idExp = self.combo_exp.currentData()
        sinceDate = self.sinceDate.date().toString('yyyy-MM-dd')
        untilDate = self.untilDate.date().toString('yyyy-MM-dd')
        sqlQuery = ''
        
        
         
        with self.conn as conn:
            try:
                if nombre == '' and status == False:
                    sqlQuery = f'''select lc.idlotecampania , ex.idexplotacion, ls.id_campania, l.nombre lote, ex.nombre explotacion, coalesce(ls.nombre_campania,'Sin Datos') campania, coalesce(ca.fechasiembra::varchar,'Sin Datos') fechasiembra, cu.nombre cultivo, ca.prod_esperada, ls.prod_final, ls.rinde_status
                    from lotecampania lc
                    join lotes ls on lc.idlotecampania = ls.idlotecampania
                    left join lote l on l.idlote = lc.idlote
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    left join explotacion ex on ex.idexplotacion = ca.idexplotacion
                    where ls.id_campania = {idCampania} and ls.idexp = {idExp}
                    group by lc.idlotecampania , ex.idexplotacion, l.nombre , ex.nombre, ca.fechasiembra , ca.fechacosecha , cu.nombre, ca.prod_esperada , ls.id_campania, ls.nombre_campania, ls.prod_final,ls.rinde_status
                    order by ex.nombre, cu.nombre, ca.fechasiembra desc'''
                   
                    

                elif nombre != '' and status == False:
                    sqlQuery = f"""select lc.idlotecampania , ex.idexplotacion, ls.id_campania, l.nombre lote, ex.nombre explotacion,coalesce(ls.nombre_campania,'Sin Datos') campania,coalesce(ca.fechasiembra::varchar,'Sin Datos') fechasiembra, cu.nombre cultivo, ca.prod_esperada, ls.prod_final,ls.rinde_status
                    from lotecampania lc
                    join lotes ls on lc.idlotecampania = ls.idlotecampania
                    left join lote l on l.idlote = lc.idlote
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    left join explotacion ex on ex.idexplotacion = ca.idexplotacion 
                    where l.nombre ilike '%{nombre}%' or ex.nombre ilike '%{nombre}%'
                    group by lc.idlotecampania , ex.idexplotacion, l.nombre , ex.nombre , ca.fechasiembra , ca.fechacosecha , cu.nombre, ca.prod_esperada , ls.id_campania, ls.nombre_campania, ls.prod_final,ls.rinde_status
                    order by ex.nombre, cu.nombre, ca.fechasiembra desc;                        
                    """
                    

                elif nombre == '' and status == True:
                    sqlQuery = f"""select lc.idlotecampania , ex.idexplotacion, ls.id_campania, l.nombre lote, ex.nombre explotacion,coalesce(ls.nombre_campania,'Sin Datos') campania,coalesce(ca.fechasiembra::varchar,'Sin Datos') fechasiembra, cu.nombre cultivo, ca.prod_esperada, ls.prod_final,ls.rinde_status
                    from lotecampania lc
                    join lotes ls on lc.idlotecampania = ls.idlotecampania
                    left join lote l on l.idlote = lc.idlote
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    left join explotacion ex on ex.idexplotacion = ca.idexplotacion
                    where ca.fechasiembra >= '{sinceDate}' and ca.fechasiembra <= '{untilDate}' 
                    group by lc.idlotecampania , ex.idexplotacion, l.nombre , ex.nombre , ca.fechasiembra , ca.fechacosecha , cu.nombre, ca.prod_esperada , ls.id_campania, ls.nombre_campania, ls.prod_final,ls.rinde_status
                    order ex.nombre, by cu.nombre, ca.fechasiembra desc
                    """
                    

                elif nombre != '' and status == True:
                    sqlQuery = f"""select lc.idlotecampania , ex.idexplotacion, ls.id_campania, l.nombre lote, ex.nombre explotacion,coalesce(ls.nombre_campania,'Sin Datos') campania,coalesce(ca.fechasiembra::varchar,'Sin Datos') fechasiembra, cu.nombre cultivo, ca.prod_esperada, ls.prod_final,ls.rinde_status
                    from lotecampania lc
                    join lotes ls on lc.idlotecampania = ls.idlotecampania
                    left join lote l on l.idlote = lc.idlote
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    left join explotacion ex on ex.idexplotacion = ca.idexplotacion
                    where ca.fechasiembra >= '{sinceDate}' and ca.fechasiembra <= '{untilDate}'
                    or l.nombre ilike '%{nombre}%' or ex.nombre ilike '%{nombre}%' 
                    group by lc.idlotecampania , ex.idexplotacion, l.nombre , ex.nombre, ca.fechasiembra , ca.fechacosecha , cu.nombre, ca.prod_esperada , ls.id_campania, ls.nombre_campania, ls.prod_final,ls.rinde_status
                    order by ex.nombre,cu.nombre, ca.fechasiembra desc 
                    """
                    
                


                cursor = conn.cursor()
                # print(sqlQuery)
                cursor.execute(sqlQuery)
                data = cursor.fetchall()
                # print(data)
                if len(data) == 0:
                    QMessageBox.about(
                        self, "aGrae GIS:", "No existen registros con los parametros de busqueda")
                    self.tableWidget.setRowCount(0)
                else:
                    
                    # self.btn_add_layer_2.setEnabled(True)
                    self.sinceDateStatus = False
                    self.untilDate.setEnabled(False)
                    self.queryCapaLotes = sqlQuery
                    try:
                        self.combo_cultivos.clear()
                        cultivos = list(set([i[7] for i in data]))
                        # print(cultivos)
                        self.combo_cultivos.addItems(cultivos)
                        self.check_cultivos.setEnabled(True)
                        self.combo_cultivos.setEnabled(True)
                    except Exception as ex: 
                        QgsMessageLog.logMessage(f'{ex}', 'aGrae GIS', level=1)
                        pass
                    a = len(data)
                    b = len(data[0])
                    i = 1
                    j = 1
                
                
                    self.tableWidget.setRowCount(a)
                    self.tableWidget.setColumnCount(b)
                    for j in range(a):
                        for i in range(b):
                            item = QTableWidgetItem(str(data[j][i]))
                            self.tableWidget.setItem(j,i,item)
            except Exception as ex:

                QgsMessageLog.logMessage(f'{ex}', 'aGrae GIS', level=1)
                QMessageBox.about(self, "Error:", f"Verifica el Parametro de Consulta (ID o Nombre)")

    def _addRow(self):
        idx = self.tableWidget.selectionModel().selectedRows()
        rowCount = self.tableWidget_2.rowCount()
        for i in sorted(idx):
            r = i.row()
            self.tableWidget_2.insertRow(rowCount)
            self.tableWidget_2.setItem(rowCount,0,QTableWidgetItem(self.tableWidget.item(r,0).text()))
            self.tableWidget_2.setItem(rowCount,1,QTableWidgetItem(self.tableWidget.item(r,1).text()))
            self.tableWidget_2.setItem(rowCount,2,QTableWidgetItem(self.tableWidget.item(r,2).text()))
            self.tableWidget_2.setItem(rowCount,3,QTableWidgetItem(self.tableWidget.item(r,3).text()))
            self.tableWidget_2.setItem(rowCount,4,QTableWidgetItem(self.tableWidget.item(r,4).text()))
            self.tableWidget_2.setItem(rowCount,5,QTableWidgetItem(self.tableWidget.item(r,7).text()))
            self.tableWidget_2.setItem(rowCount,6,QTableWidgetItem(self.tableWidget.item(r,5).text()))
            self.tableWidget_2.setItem(rowCount,7,QTableWidgetItem(self.tableWidget.item(r,10).text()))

    def _removeRow(self):
        if self.tableWidget_2.rowCount() > 0: 
            self.tableWidget_2.removeRow(self.tableWidget_2.currentRow())
        pass
    
    def getIds(self) -> str:
        rowCount = self.tableWidget_2.rowCount()
        ids = [(self.tableWidget_2.item(i,0).text()) for i in range(rowCount)]
        exp = ' ,'.join(ids)
        return exp

    def saveProductionData(self):

        exp = self.getIds()

        with self.conn.cursor() as cursor:
            try:
                sql = '''
                    select distinct  dr.fecha_muestreo::varchar  from public.lotes ls
                join (select fecha_muestreo,geom from field.data_rindes ) as dr  on st_intersects(ls.geometria,dr.geom)
                where ls.idlotecampania in ({}) order by dr.fecha_muestreo::varchar desc
                '''.format(exp)
                cursor.execute(sql)
                data = [f[0] for f in cursor.fetchall()]
                # print(data)
                if len(data) == 0: 
                    print('Debe cargar datos de rindes para este lote')
                elif len(data) > 1:
                    dialog = monitorVerifyDialog(data)
                    dialog.dateSignal.connect(lambda date : self.ajusteHumedad(exp,date))
                    dialog.exec()
                else:
                    self.ajusteHumedad(exp,data[0])
                    


                
            except Exception as ex:
              print('{}'.format(ex))


        # confirm = QMessageBox.question(self, 'aGrae GIS', "Se asignaran los valores de produccion final, deseas continuar?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # if confirm:
        #     if self.spin_prod.value() > 0:

        #         prod = self.spin_prod.value()
        #         sql =  '''with precalculo as (
        #         select l.idcampania as id, r.idlotecampania , sum(ajuste) from monitor.rindes r 
        #         join lotecampania l on l.idlotecampania = r.idlotecampania 
        #         where r.idlotecampania in ({})
        #         group by r.idlotecampania,  l.idcampania ),
        #         total as (select sum(sum) total from precalculo)
        #         update public.campania 
        #         set prod_final = round(q.produccion)
        #         from (
        #         select  id, sum / (select total from total) * {} produccion from precalculo ) as q
        #         where public.campania.idcampania = q.id'''.format(exp,prod)
        #         with self.conn.cursor() as cursor:
        #             try:
        #                 cursor.execute(sql)
        #                 self.conn.commit()
        #                 # print(sql)
        #                 self.utils.logger('Informacion almacenada correctamente'.format(),3)
        #                 self.tools.UserMessages('Informacion almacenada correctamente',level=Qgis.Success)
        #                 self.buscarLotes()
        #                 self.tableWidget_2.setRowCount(0)
        #                 self.spin_prod.setValue(0)
                    
        #             except Exception as ex:
        #                 self.conn.rollback()
        #                 self.utils.logger('{}'.format(ex),2)
        #                 self.tools.UserMessages('Ocurrio un Error, revisa el panel de registros de mensajes',level=Qgis.Critical)


                




        pass
    
    def test(self):
        dialog = monitorVerifyDialog(['2022-08','2023-08'])
        dialog.dateSignal.connect(self.ajusteHumedad)
        dialog.exec()

    def ajusteHumedad(self,exp,fecha):
        buffer = 5
        sql = '''with ls as (
        select st_buffer(st_transform(geometria,25830),{}) geometria , ls.idlotecampania, ls.area_ha , c.humedad, ls.prod_final  from public.lotes ls 
        join public.cultivo c on ls.idcultivo = c.idcultivo 
        where ls.idlotecampania in ({}) 
        ),
        rb as (select r.id, r.geometria , r.idlotecampania, ls.prod_final  from public.reticulabase r join ls on  r.idlotecampania = ls.idlotecampania),
        dr as (
        select  dr.* , (dr.volumen * (1-dr.humedad/100) / (1-ls.humedad/100) ) ajuste, ls.idlotecampania
        from field.data_rindes dr
        join ls on st_intersects(st_transform(ls.geometria,4326),dr.geom)
        where dr.fecha_muestreo = '{}')
        INSERT INTO monitor.rindes
        (idpoi, idlotecampania, fecha_archivo, humedad, volumen, ajuste, fecha_muestreo, geom)
        select id, idlotecampania, fecha_archivo,humedad,volumen,ajuste, fecha_muestreo,geom   from dr'''.format(buffer,exp,fecha)
        with self.conn.cursor() as cursor:
            try: 
                cursor.execute(sql)
                self.conn.commit()
                self.utils.logger('Humedad Ajustada Correctamente'.format(),3)
            
            except errors.lookup('23505'):
                        self.utils.logger('El lote ya existe en ajustes de humedad'.format(),1)
                        # self.tools.UserMessages('Duplicados',level=Qgis.Success)
                        self.conn.rollback()

            except Exception as ex:
                self.utils.logger('{}'.format(ex),2)
                self.tools.UserMessages('Ocurrio un Error, revisa el panel de registros de mensajes',level=Qgis.Critical)
        
        confirm = QMessageBox.question(self, 'aGrae GIS', "Se asignaran los valores de produccion final, deseas continuar?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm:
            if self.spin_prod.value() > 0:
                prod = self.spin_prod.value()
                self.dataProduccion(exp,prod)
        
    def dataProduccion(self,exp,prod):
        with self.conn.cursor() as cursor:
            sql =  '''with precalculo as (
            select l.idcampania as id, r.idlotecampania , sum(ajuste) from monitor.rindes r 
            join lotecampania l on l.idlotecampania = r.idlotecampania 
            where r.idlotecampania in ({})
            group by r.idlotecampania,  l.idcampania ),
            total as (select sum(sum) total from precalculo)
            update public.campania 
            set prod_final = round(q.produccion)
            from (
            select  id, sum / (select total from total) * {} produccion from precalculo ) as q
            where public.campania.idcampania = q.id'''.format(exp,prod)
            try:
                cursor.execute(sql)
                self.conn.commit()
                # print(sql)
                self.utils.logger('Informacion almacenada correctamente'.format(),3)
                self.tools.UserMessages('Informacion almacenada correctamente',level=Qgis.Success,alert=True,parent=self)
                self.buscarLotes()
                # self.tableWidget_2.setRowCount(0)
                # self.spin_prod.setValue(0)
            
            except Exception as ex:
                self.conn.rollback()
                self.utils.logger('{}'.format(ex),2)
                self.tools.UserMessages('Ocurrio un Error, revisa el panel de registros de mensajes',level=Qgis.Critical)

    
    def ajusteRinde(self):
        exp = self.getIds()
        confirm = QMessageBox.question(self, 'aGrae GIS', "Se ajustaran los valores de Rinde Reales, deseas continuar?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm:
            sql = '''with ls as (select idlotecampania, area_ha, prod_final  from public.lotes where idlotecampania in ({})),
            dr as (select r.* from monitor.rindes r join ls on r.idlotecampania = ls.idlotecampania),
            rl as (
            select 0 as min, (ls.prod_final /ls.area_ha) as median, (ls.prod_final/ls.area_ha) * 1.85 as max  from ls
            ),
            rm as (
            select min(dr.ajuste), percentile_cont(0.5) within group(order by dr.ajuste) as median, max(dr.ajuste)
            from dr
            ),
            unidos as (
            select * from rl
            union all
            select * from rm
            ),
            rmdv as (select  stddev(q.v) from (select unnest(array[min,median,max]) as v from rm) as q  ),
            rldv as (select stddev(q.v) from (select unnest(array[min,median,max]) as v from rl) as q  ),
            rm2 as ( select row_number() over () as id, x from (select unnest(array[min,median,max]) as x from rm) as q ),
            rl2 as ( select row_number() over () as id, y from (select unnest(array[min,median,max]) as y from rl) as q ),
            correlation as (select corr(x,y) v from rm2 join rl2 on rm2.id = rl2.id),
            slope as (select (select * from rldv) / (select * from rmdv) * v  as v from correlation),
            rindes as (select dr.idpoi as id , dr.idlotecampania as idl ,(dr.ajuste * (select v from slope)) rinde from dr)
            update monitor.rindes r
            set rinde = q.rinde
            from (select * from rindes) as q
            where idpoi = q.id and idlotecampania = q.idl'''.format(exp)
            with self.conn.cursor() as cursor:
                try:
                  cursor.execute(sql)
                  self.conn.commit()
                  self.setStatus('Ajustado',exp)
                  self.utils.logger('Se Ajustaron los valores reales de Rendimiento',3)
                  self.tools.UserMessages('Se Ajustaron los valores reales de Rendimiento',level=Qgis.Success,alert=True,parent=self)
                except Exception as ex:
                  self.conn.rollback()
                  self.utils.logger('{}'.format(ex),2)
                  self.tools.UserMessages('{}'.format(ex),level=Qgis.Critical)
                #   print('An exception occurred')
    
    def validateRinde(self):
        confirm = QMessageBox.question(self, 'aGrae GIS', "Desea Validar los valores de Rendimiento?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm:
            exp = self.getIds()
            sql = '''update monitor.rindes 
            set rinde = q.rinde
            from ( select r.id i , r.idpoi ip ,r. idlotecampania il, r.ajuste rinde from monitor.rindes r where idlotecampania in({}) ) as q
            where id = q.i and idpoi = q.ip and idlotecampania = q.il'''.format(exp)
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql)
                    self.conn.commit()
                    self.setStatus('Validado',exp)
                    self.utils.logger('Se Validaron los valores de Rendimiento',3)
                    self.tools.UserMessages('Se Validaron los valores de Rendimiento',level=Qgis.Success,alert=True,parent=self)
                except Exception as ex:
                    self.conn.rollback()
                    self.utils.logger('{}'.format(ex),2)
                    self.tools.UserMessages('{}'.format(ex),level=Qgis.Critical)

    def setStatus(self,value,exp):
        with self.conn.cursor() as cursor:
                try:
                    sql = '''update public.campania 
                    set rinde_status = '{}'
                    from (select ls.idcampania id from public.lotes ls
                    where ls.idlotecampania in ({}) ) as q
                    where idcampania = q.id'''.format(value,exp)
                    cursor.execute(sql)
                    self.conn.commit()
                    self.utils.logger('status_rindes actualizado correctamente',3)
                    # self.tools.UserMessages('Se Ajustaron los valores reales de Rendimiento',level=Qgis.Success)
                except Exception as ex:
                    self.conn.rollback()
                    self.utils.logger('setStatus: {}'.format(ex),2)
                    # self.tools.UserMessages('setStatus: {}'.format(ex),level=Qgis.Critical)


class monitorVerifyDialog(QDialog,agraeRindesMonitorVerify):
    dateSignal = pyqtSignal(str)
    def __init__(self,dates:list,parent=None) -> None:
        super(monitorVerifyDialog,self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('aGrae GIS')
        self.dates = dates
        
        self.UIComponents()

    def UIComponents(self):
        self.comboBox.addItems(self.dates)
        self.buttonBox.accepted.connect(self._getDate)
    

    def _getDate(self):
        fecha = self.comboBox.currentText()
        self.dateSignal.emit(fecha)
    





        pass





    



      
