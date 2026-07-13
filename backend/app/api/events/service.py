from sqlalchemy.orm import Session
from datetime import date
from app.models.eventos import Evento
from sqlalchemy import func

def obtener_eventos_proximos(db: Session, fecha_filtro: date):
    """
    Devuelve todos los eventos activos desde una fecha de inicio en adelante,
    ordenados del más cercano al más lejano.
    """
    return db.query(Evento).filter(
        Evento.fecha >= fecha_filtro,
        Evento.activo == True
    ).order_by(
        Evento.fecha.asc()
    ).all()

# Funciones auxiliares
def contar_eventos_activos(db: Session) -> int:
    """
    Cuenta cuántos eventos activos hay desde HOY en adelante.
    (No cuenta los eventos que ya pasaron).
    """
    fecha_hoy = date.today()
    return db.query(Evento).filter(
        Evento.fecha >= fecha_hoy,
        Evento.activo == True
    ).count()

def contar_organizaciones_con_eventos_activos(db: Session) -> int:
    """Cuenta cuántas organizaciones distintas tienen eventos de hoy en adelante."""
    fecha_hoy = date.today()
    return db.query(Evento.organizacion_id).filter(
        Evento.fecha >= fecha_hoy,
        Evento.activo == True
    ).distinct().count()

def obtener_distribucion(db: Session, columna_modelo):
    """
    Función genérica para agrupar por columna (enfoque o tipo),
    contar los resultados y calcular el porcentaje para gráficas de pastel.
    """
    # se obtiene primero el total de eventos que si tienen este campo lleno
    total = db.query(Evento).filter(columna_modelo.isnot(None), Evento.activo == True).count()
    
    if total == 0:
        return []

    resultados = db.query(
        columna_modelo, 
        func.count(Evento.id)
    ).filter(
        columna_modelo.isnot(None), 
        Evento.activo == True
    ).group_by(
        columna_modelo
    ).all()

    # formateo de datos para el frontend
    datos_grafica = []
    for nombre, cantidad in resultados:
        porcentaje = round((cantidad / total) * 100, 2)
        datos_grafica.append({
            "label": nombre,
            "count": cantidad,
            "porcentaje": porcentaje
        })
        
    return datos_grafica

def obtener_historico_trimestral(db: Session):
    """
    Genera los últimos 4 trimestres (ej. 'Q3 2025', 'Q4 2025') y cuenta los 
    eventos históricos que ocurrieron en esos periodos para una gráfica de línea.
    """
    hoy = date.today()
    trimestres_info = []
    
    # Construir las etiquetas y rangos de los últimos 4 trimestres
    for i in range(4):
        # Calcular el trimestre actual retrocediendo meses
        mes_calculo = hoy.month - (3 * i)
        año_calculo = hoy.year
        
        while mes_calculo <= 0:
            mes_calculo += 12
            año_calculo -= 1
            
        trimestre_num = (mes_calculo - 1) // 3 + 1
        label = f"Q{trimestre_num} {año_calculo}"
        
        # Determinar el primer y último mes del trimestre
        mes_inicio = (trimestre_num - 1) * 3 + 1
        mes_fin = trimestre_num * 3
        
        # Fechas límite para la consulta SQL
        fecha_inicio_q = date(año_calculo, mes_inicio, 1)
        
        # Para la fecha de fin, calculamos el primer día del SIGUIENTE mes y usamos '<' en SQL
        if mes_fin == 12:
            fecha_fin_q = date(año_calculo + 1, 1, 1)
        else:
            fecha_fin_q = date(año_calculo, mes_fin + 1, 1)
            
        trimestres_info.append({
            "label": label,
            "inicio": fecha_inicio_q,
            "fin": fecha_fin_q
        })

    # Invertimos la lista para que el más viejo quede al principio (eje X de la gráfica)
    trimestres_info.reverse()

    # consultar a la BD cuántos eventos cayeron en cada bloque
    datos_grafica = []
    for q in trimestres_info:
        cantidad = db.query(Evento).filter(
            Evento.fecha >= q["inicio"],
            Evento.fecha < q["fin"],
            Evento.activo == True
        ).count()
        
        datos_grafica.append({
            "trimestre": q["label"],
            "eventos": cantidad
        })
        
    return datos_grafica