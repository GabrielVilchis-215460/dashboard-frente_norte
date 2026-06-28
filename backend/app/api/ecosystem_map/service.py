"""
Servicio del Mapa Interactivo del Ecosistema STEM.

Provee los datos georreferenciados de actores para construir
el mapa interactivo solicitado en la ficha técnica.
"""
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.organizacion import Organizacion
from app.models.programa import Programa
from app.api.ecosystem_map.schemas import FichaActor, MapaEcosistema, PinMapa


def obtener_mapa(
    db: Session,
    tipo: Optional[str],
    area_stem: Optional[str],
    zona: Optional[str],
    madurez: Optional[str],
    nivel_educativo: Optional[str],
    poblacion: Optional[str],
    pct_mujeres_rango: Optional[str],
    solo_con_coordenadas: bool,
) -> MapaEcosistema:
    """
    Retorna todos los pins del mapa aplicando los filtros dados.

    Filtros a nivel organización: tipo, area_stem, zona, coordenadas.
    Filtros a nivel programa: madurez, nivel_educativo, poblacion, pct_mujeres_rango.
    Una organización se incluye si tiene al menos un programa que cumpla
    todos los filtros de programa especificados.
    """
    q = db.query(Organizacion).filter(Organizacion.activo == True)

    if tipo:
        q = q.filter(Organizacion.tipo == tipo)
    if area_stem:
        q = q.filter(Organizacion.areas_stem.any(area_stem))
    if zona:
        q = q.filter(Organizacion.zona == zona)
    if solo_con_coordenadas:
        q = q.filter(Organizacion.latitud.isnot(None), Organizacion.longitud.isnot(None))

    if madurez or nivel_educativo or poblacion or pct_mujeres_rango:
        pq = db.query(Programa.organizacion_id).filter(Programa.activo == True)
        if madurez:
            pq = pq.filter(Programa.madurez == madurez)
        if nivel_educativo:
            pq = pq.filter(Programa.nivel_educativo == nivel_educativo)
        if poblacion:
            pq = pq.filter(Programa.poblacion_objetivo == poblacion)
        if pct_mujeres_rango:
            pq = pq.filter(Programa.pct_mujeres_rango == pct_mujeres_rango)
        ids_validos = [r[0] for r in pq.distinct().all()]
        q = q.filter(Organizacion.id.in_(ids_validos))

    organizaciones = q.order_by(Organizacion.nombre).all()

    conteos = {
        org_id: count
        for org_id, count in db.query(Programa.organizacion_id, func.count(Programa.id))
        .filter(Programa.activo == True)
        .group_by(Programa.organizacion_id)
        .all()
    }

    pins = [
        PinMapa(
            id=org.id,
            nombre=org.nombre,
            tipo=org.tipo or "",
            areas_stem=org.areas_stem or [],
            latitud=org.latitud,
            longitud=org.longitud,
            zona=org.zona,
            total_programas=conteos.get(org.id, 0),
        )
        for org in organizaciones
    ]

    return MapaEcosistema(
        total_actores=len(organizaciones),
        actores_con_coordenadas=sum(1 for p in pins if p.latitud and p.longitud),
        pins=pins,
    )


def obtener_ficha_actor(db: Session, org_id: int) -> Optional[FichaActor]:
    """
    Retorna la ficha descriptiva completa de un actor para mostrarla
    al hacer clic en su pin en el mapa.
    """
    org = db.query(Organizacion).filter(
        Organizacion.id == org_id, Organizacion.activo == True
    ).first()

    if not org:
        return None

    programas_activos = (
        db.query(Programa)
        .filter(Programa.organizacion_id == org_id, Programa.activo == True)
        .all()
    )

    return FichaActor(
        id=org.id,
        nombre=org.nombre,
        tipo=org.tipo or "",
        descripcion=org.descripcion,
        areas_stem=org.areas_stem or [],
        enfoque_principal=org.enfoque_principal,
        sitio_web=org.sitio_web,
        contacto_nombre=org.contacto_nombre,
        contacto_email=org.contacto_email,
        contacto_telefono=org.contacto_telefono,
        direccion=org.direccion,
        zona=org.zona,
        colonias=org.colonias or [],
        latitud=org.latitud,
        longitud=org.longitud,
        total_programas=len(programas_activos),
        programas=[p.nombre for p in programas_activos if p.nombre],
    )
