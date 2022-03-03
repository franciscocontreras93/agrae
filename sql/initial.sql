
create table analisis ( 
idanalisis smallserial not null primary key,
idlote integer references lote(idlote),
cod_analisis varchar(10) not null
);

CREATE TABLE persona (
	idpersona serial NOT NULL PRIMARY KEY,
	dni text,
	nombre text,
	apellidos text,
	direccion text,
	telefono text,
	email text,
	borradologico boolean

)

ALTER TABLE persona
	ALTER COLUMN borradologico SET DEFAULT false


CREATE TABLE distribuidor (
	iddistribuidor serial NOT NULL PRIMARY KEY,
	cif text,
	personaContacto text,
	icono text,
	telefono text,
	email text,
	fechaInicio date,
	direccionFiscal text,
	direccionEnvio text,
	borradologico boolean
)

ALTER TABLE distribuidor
	ALTER COLUMN borradologico SET DEFAULT false

CREATE TABLE cultivo ( 
	idcultivo serial NOT NULL PRIMARY KEY,
	nombre text,
	extraccionCosechaN double precision,
	extraccionCosechaP double precision,
	extraccionCosechaK double precision,
	extraccionCosechaS double precision,
	extraccionCosechaCa double precision,
	extraccionCosechaMg double precision,
	extraccionCosechaB double precision,
	contenidoCosechaC double precision,
	extraccionResiduoN double precision,
	extraccionResiduoP double precision,
	extraccionResiduoK double precision,
	extraccionResiduoS double precision,
	extraccionResiduoCa double precision,
	extraccionResiduoMg double precision,
	extraccionResiduoB double precision,
	contenidoResiduo double precision,
	borradologico boolean
)
ALTER TABLE cultivo
	ALTER COLUMN borradologico SET DEFAULT false

CREATE TABLE fenologia(
	idfenologia serial NOT NULL PRIMARY KEY,
	idcultivo integer references cultivo (idcultivo),
	nombreEstado text,
	integralTermica double precision,
	borradologico boolean

)

ALTER TABLE fenologia
	ALTER COLUMN borradologico SET DEFAULT false

CREATE TABLE explotacion (
	idexplotacion serial NOT NULL PRIMARY KEY,
	nombre text,
	direccion text,
	borradologico boolean
)

ALTER TABLE explotacion
	ALTER COLUMN borradologico SET DEFAULT false

CREATE TABLE agricultor (
	idagricultor serial NOT NULL PRIMARY KEY,
	idpersona integer references persona (idpersona),
	idexplotacion integer references explotacion (idexplotacion),
	iddistribuidor integer references distribuidor (iddistribuidor),
	nombre text,
	borradologico boolean
)

ALTER TABLE agricultor
	ALTER COLUMN borradologico SET DEFAULT false

CREATE TABLE cultivoagricultor (
	idcultivoagricultor serial NOT NULL PRIMARY KEY,
	idagricultor integer references agricultor (idagricultor),
	idcultivo integer references cultivo (idcultivo),
	unidadesNPKtradicionales text,
	costeFertilizante double precision,
	costeFertilizanteUnidades text,
	fechaCultivo date,
	borradologico boolean
)

ALTER TABLE cultivoagricultor
	ALTER COLUMN borradologico SET DEFAULT false


create table ambiente (
	pk_uid uuid DEFAULT uuid_generate_v4 NOT NULL,
	idambiente bigserial not null  primary key,
	idparcela integer not null references parcela (idparcela)
	obj_amb integer,
	ambiente integer,
	ndvimax numeric,
	atlas varchar,
	geometria geometry(MultiPolygon,4326)

)

create table segmento (
	pk_uid bigserial not null,
	idsegmento bigserial not null primary key,
	idparcela integer references parcela (idparcela),
	segmento integer,
	atlas varchar,
	cod_control varchar(10),
	cod varchar (10),
	idanalisis integer references analisis(idanalisis),
	geometria geometry(MultiPolygon,4326)
)

create table unidades ( 
	pk_uid bigserial not null,
	idunidad bigserial not null primary key,
	idparcela integer references parcela (idparcela),
	segmento integer,
	ambiente integer,
	uf integer,
	geometria geometry(MultiPolygon,4326)

)

CREATE TABLE parcela (
	pk_uid uuid DEFAULT uuid_generate_v4 NOT NULL ,
	idparcela bigserial NOT NULL PRIMARY KEY,
	nombre text,
	provincia integer references public.pronvia (idprovincia),
	municipio integer references public.municipio (idmunicipio),
	agregado integer,
	zona integer,
	poligono integer,
	parcela integer,
	recinto integer,
	geometria geometry(MultiPolygon,4326),
	borradologico boolean ) 

ALTER TABLE parcela 
	ALTER COLUMN geometria TYPE geometry(MultiPolygon,4326)
		USING st_setsrid(geometria,4326)

ALTER TABLE parcela 
	ALTER COLUMN borradologico SET DEFAULT false

CREATE TABLE lote (
	idlote serial NOT NULL PRIMARY KEY,
	idexplotacion integer references explotacion (idexplotacion),
	idcultivo integer references cultivo (idcultivo),
	nombre text,
	fechaSiembra date,
	fechaCosecha date,
	fechaFertilizacionFondo date,
	fertilizanteFondoFormula text,
	fertilizanteFondoPrecio double precision,
	fertilizanteFondoCalculado double precision,
	fertilizanteFondoAjustado double precision,
	fertilizanteFondoAplicado double precision,
	fechaFertilizacionCBO1 date,
	fertilizanteCOB1Formula text,
	fertilizanteCOB1Precio double precision,
	fertilizanteCOB1Calculado double precision,
	fertilizanteCOB1Ajustado double precision,
	fertilizanteCOB1Aplicado double precision,
	fechaFertilizacionCBO2 date,
	fertilizanteCOB2Formula text,
	fertilizanteCOB2Precio double precision,
	fertilizanteCOB2Calculado double precision,
	fertilizanteCOB2Ajustado double precision,
	fertilizanteCOB2Aplicado double precision,
	fechaFertilizacionCBO3 date,
	fertilizanteCOB3Formula text,
	fertilizanteCOB3Precio double precision,
	fertilizanteCOB3Calculado double precision,
	fertilizanteCOB3Ajustado double precision,
	fertilizanteCOB3Aplicado double precision,
	unidadesprecio text,
	borradologico boolean
)

ALTER TABLE lote
	ALTER COLUMN borradologico SET DEFAULT false

CREATE TABLE loteparcela (
	idloteparcela serial NOT NULL PRIMARY KEY,
	idparcela integer references parcela (idparcela),
	idlote integer references lote (idlote),
	borradologico boolean
)

ALTER TABLE loteparcela
	ALTER COLUMN borradologico SET DEFAULT false


CREATE TABLE unidad ( 
	pk_uid bigserial ,
	idunidad bigserial NOT NULL PRIMARY KEY,
	idlote integer references lote (idlote),
	nombre text,
	tipoLote text,
	geometria geometry(MultiPolygon,4326),
	borradologico boolean
)

ALTER TABLE unidad 
	ALTER COLUMN geometria TYPE geometry(MultiPolygon,4326)
		USING st_setsrid(geometria,4326)

ALTER TABLE unidad 
	ALTER COLUMN borradologico SET DEFAULT false


CREATE TABLE reticulabase ( 
	pk_uid bigserial,
	idpunto bigserial NOT NULL PRIMARY KEY,
	geometria geometry(MultiPoint,4326),
	borradologico boolean
)

ALTER TABLE reticulabase 
	ALTER COLUMN geometria TYPE geometry(MultiPoint,4326)
		USING st_setsrid(geometria,4326)

ALTER TABLE reticulabase 
	ALTER COLUMN borradologico SET DEFAULT false

CREATE TABLE reticula ( 
	idreticula serial NOT NULL PRIMARY KEY,
	idunidad integer references unidad (idunidad), 
	idpunto integer references reticulabase (idpunto),
	borradologico boolean
)

ALTER TABLE reticula
	ALTER COLUMN borradologico SET DEFAULT false

CREATE TABLE variable ( 
	idvariable serial NOT NULL PRIMARY KEY,
	nombreVariable text,
	unidadesVariable text,
	descripcionVariable text,
	borradologico boolean
)

ALTER TABLE variable
	ALTER COLUMN borradologico SET DEFAULT false

CREATE TABLE medidaunidad ( 
	idmedidaunidad serial NOT NULL PRIMARY KEY,
	idunidad integer references unidad (idunidad) ,
	idvariable integer references variable (idvariable),
	fecha date,
	medida double precision,
	borradologico boolean
)

ALTER TABLE medidaunidad
	ALTER COLUMN borradologico SET DEFAULT false

CREATE TABLE puntomuestreo ( 
	idpuntomuestreo serial NOT NULL PRIMARY KEY,
	idmedidaunidad integer references medidaunidad (idmedidaunidad),
	idreticula integer references reticula (idreticula),
	reticulaVirtual boolean,
	borradologico boolean
)

ALTER TABLE puntomuestreo
	ALTER COLUMN reticulaVirtual SET DEFAULT false

ALTER TABLE puntomuestreo
	ALTER COLUMN borradologico SET DEFAULT false



CREATE TABLE medidapunto ( 
	idmedidapunto serial NOT NULL PRIMARY KEY,
	idreticula integer references reticula (idreticula),
	idvariable integer references variable (idvariable),
	fecha date,
	medida double precision,
	borradologico boolean
)

ALTER TABLE medidapunto
	ALTER COLUMN borradologico SET DEFAULT false


CREATE INDEX parcela_geom_idx
  ON parcela
  USING GIST (geometria);
CREATE INDEX unidad_geom_idx
  ON unidad
  USING GIST (geometria);
CREATE INDEX reticula_geom_idx
  ON reticulabase
  USING GIST (geometria);


create function sp_idparcela_ambiente() 
returns trigger as $$ 
begin 
	update ambiente
	set idparcela = subquery.id
	from (select p.idparcela id from parcela p where st_intersects(p.geometria , new.geometria)) as subquery
	where idambiente = new.idambiente;
	return new;
end
$$ 
language plpgsql 

create trigger tr_update_ambiente after insert on ambiente 
for each row 
execute procedure sp_idparcela_ambiente();

create function sp_idparcela_segmento() 
returns trigger as $$ 
begin 
	update segmento
	set idparcela = subquery.id
	set cod_control = new.atlas||new.segmento
	from (select p.idparcela id from parcela p where st_intersects(p.geometria , new.geometria)) as subquery
	where idsegmento = new.idsegmento;
	return new;
end
$$ 
language plpgsql 

create trigger tr_update_ambiente after insert on segmento 
for each row 
execute procedure sp_idparcela_segmento();