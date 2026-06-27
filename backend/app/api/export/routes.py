"""
Módulo de exportación de datos.

Permite descargar los datos del ecosistema en formato CSV o Excel
para análisis externo, reportes o respaldo de información.
Todos los endpoints requieren autenticación de administrador.
"""
import csv
import io
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.auth.service import get_current_admin
from app.db.session import get_db
from app.models.organizacion import Organizacion
from app.models.programa import Programa

router = APIRouter(
    prefix="/exportar",
    tags=["Exportación de Datos"],
    dependencies=[Depends(get_current_admin)],
)


def _csv_response(filename: str, headers: list, rows: list) -> StreamingResponse:
    """Genera una respuesta CSV en memoria lista para descarga."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/organizaciones",
    summary="Exportar organizaciones a CSV",
    description="Descarga todas las organizaciones activas (o todas si activo=false) en formato CSV.",
)
def exportar_organizaciones(
    activo: Optional[bool] = Query(None, description="True=activas, False=inactivas, None=todas"),
    db: Session = Depends(get_db),
):
    q = db.query(Organizacion)
    if activo is not None:
        q = q.filter(Organizacion.activo == activo)
    orgs = q.order_by(Organizacion.nombre).all()

    headers = [
        "id", "nombre", "tipo", "enfoque_principal", "areas_stem",
        "descripcion", "sitio_web", "contacto_nombre", "contacto_email",
        "contacto_telefono", "direccion", "zona", "colonias",
        "latitud", "longitud", "activo", "fuente",
    ]
    rows = [
        [
            o.id, o.nombre, o.tipo, o.enfoque_principal,
            "|".join(o.areas_stem or []), o.descripcion, o.sitio_web,
            o.contacto_nombre, o.contacto_email, o.contacto_telefono,
            o.direccion, o.zona, "|".join(o.colonias or []),
            o.latitud, o.longitud, o.activo, o.fuente,
        ]
        for o in orgs
    ]

    return _csv_response("organizaciones.csv", headers, rows)


@router.get(
    "/programas",
    summary="Exportar programas a CSV",
    description="Descarga todos los programas activos (o todos si activo=false) en formato CSV.",
)
def exportar_programas(
    activo: Optional[bool] = Query(None, description="True=activos, False=inactivos, None=todos"),
    db: Session = Depends(get_db),
):
    q = db.query(Programa)
    if activo is not None:
        q = q.filter(Programa.activo == activo)
    programas = q.order_by(Programa.nombre).all()

    headers = [
        "id", "organizacion_id", "nombre", "descripcion", "areas_stem",
        "tipos_actividad", "modalidad", "poblacion_objetivo", "nivel_educativo",
        "pct_mujeres_rango", "pct_mujeres_mid", "zona", "colonias_impacto",
        "volumen_semestral", "volumen_mid", "temporalidad", "madurez",
        "casos_exito", "siguiente_paso", "activo", "fuente",
    ]
    rows = [
        [
            p.id, p.organizacion_id, p.nombre, p.descripcion,
            "|".join(p.areas_stem or []), "|".join(p.tipos_actividad or []),
            p.modalidad, p.poblacion_objetivo, p.nivel_educativo,
            p.pct_mujeres_rango, p.pct_mujeres_mid, p.zona,
            "|".join(p.colonias_impacto or []), p.volumen_semestral,
            p.volumen_mid, p.temporalidad, p.madurez,
            p.casos_exito, p.siguiente_paso, p.activo, p.fuente,
        ]
        for p in programas
    ]

    return _csv_response("programas.csv", headers, rows)


