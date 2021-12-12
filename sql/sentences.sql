-- CALCULO DE AREAS EN DETERMINADO SRID 25830 NE ESPAÑA

select 
idparcela , parcela , municipio, agregado, zona, poligono, parcela, recinto, 
st_area(st_transform(geometria,25830))/10000 as area
from parcela

-- INSERTAR POLIGONOS DENTRO DE UNA TABLA
insert into parcela(geometria)
values (st_multi(st_geomfromtext(st_astext(st_makepolygon(ST_MakeLine(ARRAY[ST_MakePoint(-5.12528,39.92508), 
ST_MakePoint(-4.98963,39.87777),ST_MakePoint(-5.09914,39.83625),ST_MakePoint(-5.12528,39.92508)]))),4326)));


-- CREATE GRID POINTS
insert into reticulabase(geometria) 
(SELECT (ST_Dump(makegrid(geometria, 121))).geom from parcela
where idparcela = 30)


-- 121 = 9.959 METROS