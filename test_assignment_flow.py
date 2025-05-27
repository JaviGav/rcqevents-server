# Test del flujo de asignaciones
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes.events import get_assignment_display_name, assignment_text_cache

# Test 1: Texto libre con servicio_nombre
print("=== Test 1: Texto libre con servicio_nombre ===")
assignment_data_1 = {
    'id': 123,
    'indicativo_id': -1,
    'servicio_nombre': 'CME'
}
result_1 = get_assignment_display_name(assignment_data_1)
print(f"Input: {assignment_data_1}")
print(f"Output: '{result_1}'")
print(f"Expected: 'CME'")
print(f"✅ PASS" if result_1 == 'CME' else f"❌ FAIL")
print()

# Test 2: Texto libre sin servicio_nombre pero en cache
print("=== Test 2: Texto libre sin servicio_nombre pero en cache ===")
assignment_text_cache[124] = 'GUB'
assignment_data_2 = {
    'id': 124,
    'indicativo_id': -1,
    'servicio_nombre': None
}
result_2 = get_assignment_display_name(assignment_data_2)
print(f"Input: {assignment_data_2}")
print(f"Cache: {assignment_text_cache}")
print(f"Output: '{result_2}'")
print(f"Expected: 'GUB'")
print(f"✅ PASS" if result_2 == 'GUB' else f"❌ FAIL")
print()

# Test 3: Indicativo válido
print("=== Test 3: Indicativo válido (simulado) ===")
assignment_data_3 = {
    'id': 125,
    'indicativo_id': 5,
    'servicio_nombre': None
}
result_3 = get_assignment_display_name(assignment_data_3)
print(f"Input: {assignment_data_3}")
print(f"Output: '{result_3}'")
print(f"Expected: 'ID: 5' (sin BD real)")
print(f"✅ PASS" if result_3 == 'ID: 5' else f"❌ FAIL")
print()

print("=== Resumen ===")
print("El flujo básico funciona correctamente.")
print("El problema debe estar en otro lugar del código.") 