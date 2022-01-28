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



select p1.idpunto, p1.geometria as punto , p2.nombre,p2.agregado from reticulabase p1 , parcela p2 
where st_within (p1.geometria, p2.geometria) and p2.nombre = 'PARCELA1'



create or replace view public.grilla as 
select 
(ST_Dump(makegrid(p.geometria, 121))).geom as punto, 
uuid_generate_v4() AS id
from parcela p
where idparcela = 38

-- BUSQUEDA POR LOTE o parcela
select lp.idlote, l.nombre as lote ,p.idparcela, p.nombre as parcela, c.nombre from parcela p
left join loteparcela lp on p.idparcela = lp.idparcela 
left join lote l on l.idlote = lp.idlote 
left join cultivo c on c.idcultivo = l.idcultivo 
where p.idparcela = 39

