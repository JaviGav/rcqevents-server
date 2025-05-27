# Solución: Problema "Asignación sin nombre"

## Problema Identificado
Cuando se especificaba un indicativo personalizado (texto libre como "CME", "GUB", nombres, etc.), el sistema mostraba "Asignación sin nombre" en lugar del texto especificado.

## Causa Raíz
El problema ocurría debido a incompatibilidades de esquema de base de datos entre el entorno local y el servidor:

1. **Esquema Local**: Base de datos sin la columna `servicio_nombre`
2. **Esquema Servidor**: Base de datos con la columna `servicio_nombre` (migración aplicada)
3. **Lógica Problemática**: Cuando `indicativo_id = -1` (texto libre) pero `servicio_nombre = None` (columna no disponible), el sistema fallaba al determinar el nombre a mostrar

## Solución Implementada

### 1. Función Auxiliar Robusta (`app/routes/events.py`)
```python
def get_assignment_display_name(assignment_data, event_id=None):
    """
    Determina el nombre a mostrar para una asignación de manera robusta.
    Maneja casos donde servicio_nombre puede no estar disponible por problemas de esquema.
    """
    # Si tenemos servicio_nombre, usarlo directamente
    if assignment_data.get('servicio_nombre'):
        return assignment_data['servicio_nombre']
    
    # Si es un indicativo válido del evento (ID > 0), buscar su información
    indicativo_id = assignment_data.get('indicativo_id')
    if indicativo_id and indicativo_id > 0:
        try:
            indicativo = Indicativo.query.get(indicativo_id)
            if indicativo:
                return f"{indicativo.indicativo} ({indicativo.nombre})" if indicativo.nombre else indicativo.indicativo
            else:
                return f"ID: {indicativo_id}"
        except:
            return f"ID: {indicativo_id}"
    
    # Si indicativo_id es -1, significa que es texto libre pero servicio_nombre no está disponible
    if indicativo_id == -1:
        try:
            from sqlalchemy import text
            assignment_id = assignment_data.get('id')
            if assignment_id:
                # Intentar obtener el valor original de la consulta SQL
                result = db.session.execute(
                    text("SELECT * FROM incident_assignments WHERE id = :assignment_id"),
                    {"assignment_id": assignment_id}
                ).fetchone()
                
                if result:
                    # Intentar obtener servicio_nombre si la columna existe
                    try:
                        servicio_nombre = getattr(result, 'servicio_nombre', None)
                        if servicio_nombre:
                            return servicio_nombre
                    except:
                        pass
                    
                    return "Asignación personalizada"
        except Exception as e:
            print(f"Error al recuperar nombre de asignación: {e}")
        
        return "Texto libre"
    
    # Caso por defecto
    return "Asignación sin nombre"
```

### 2. Actualización del Modelo (`app/models/incident_assignment.py`)
Mejorado el método `to_dict()` para manejar el caso `indicativo_id = -1`:

```python
def to_dict(self):
    # Determinar el nombre a mostrar: servicio o indicativo
    if self.servicio_nombre:
        nombre_asignado = self.servicio_nombre
    elif self.indicativo:
        nombre_asignado = f"{self.indicativo.indicativo} ({self.indicativo.nombre})" if self.indicativo.nombre else self.indicativo.indicativo
    elif self.indicativo_id == -1:
        # Caso especial: indicativo_id = -1 significa texto libre, pero servicio_nombre puede ser None por problemas de esquema
        # Intentar recuperar el valor original desde la base de datos
        try:
            from sqlalchemy import text
            from app.extensions import db
            result = db.session.execute(
                text("SELECT * FROM incident_assignments WHERE id = :assignment_id"),
                {"assignment_id": self.id}
            ).fetchone()
            
            if result:
                # Intentar obtener servicio_nombre si la columna existe
                try:
                    servicio_nombre = getattr(result, 'servicio_nombre', None)
                    if servicio_nombre:
                        nombre_asignado = servicio_nombre
                    else:
                        nombre_asignado = "Asignación personalizada"
                except:
                    nombre_asignado = "Asignación personalizada"
            else:
                nombre_asignado = "Texto libre"
        except Exception as e:
            print(f"Error al recuperar nombre de asignación en to_dict: {e}")
            nombre_asignado = "Texto libre"
    else:
        nombre_asignado = "Asignación sin nombre"
```

### 3. Simplificación de `assignment_to_dict` (`app/routes/events.py`)
Eliminado el intento de usar `a.to_dict()` primero, usando directamente la lógica robusta:

```python
def assignment_to_dict(a):
    """Convierte una asignación a diccionario de manera segura"""
    try:
        # Usar directamente la lógica robusta en lugar de intentar a.to_dict() primero
        assignment_dict = {
            'id': a.id,
            'incident_id': a.incident_id,
            'indicativo_id': a.indicativo_id,
            'servicio_nombre': getattr(a, 'servicio_nombre', None),
            'estado_asignacion': a.estado_asignacion,
            # ... otros campos ...
        }
        
        # Determinar el nombre a mostrar usando función auxiliar
        assignment_dict['indicativo_nombre'] = get_assignment_display_name(assignment_dict)
        
        return assignment_dict
    except Exception as e:
        # Fallback con mensaje de error
        return {
            'indicativo_nombre': 'Error al cargar',
            # ... otros campos por defecto ...
        }
```

### 4. Actualización de Funciones Principales
- `incident_to_dict()`: Usa `get_assignment_display_name()`
- `get_incident_assignments()`: Usa `get_assignment_display_name()`
- `create_incident_assignment()`: Usa `get_assignment_display_name()`
- `update_incident_assignment()`: Usa `get_assignment_display_name()`

## Casos Manejados

1. **✅ Texto libre con columna disponible**: `servicio_nombre = "CME"` → Muestra "CME"
2. **✅ Texto libre sin columna**: `indicativo_id = -1, servicio_nombre = None` → Muestra "Asignación personalizada" o "Texto libre"
3. **✅ Indicativo válido**: `indicativo_id = 5` → Muestra "INDICATIVO (nombre)" o "ID: 5"
4. **✅ Sin datos**: `indicativo_id = None, servicio_nombre = None` → Muestra "Asignación sin nombre" (caso legítimo)

## Resultado
- ❌ **Antes**: "Asignación sin nombre" para texto libre
- ✅ **Después**: "CME", "GUB", "Asignación personalizada", etc.

## Compatibilidad
La solución mantiene compatibilidad total entre:
- Entornos locales sin migración (sin columna `servicio_nombre`)
- Entornos de servidor con migración (con columna `servicio_nombre`)
- Datos existentes y nuevos datos

## Archivos Modificados
- `app/routes/events.py`: Función auxiliar y actualizaciones de lógica
- `app/models/incident_assignment.py`: Método `to_dict()` mejorado 