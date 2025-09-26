import numpy as np
import json
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# --- Nombres para mostrar en la UI ---
BODEGAS = ['Sevilla', 'Tuluá', 'Caicedonia']
CAFES = ['Castillo', 'Caturra', 'Borbón']

# --- Funciones para manejar datos (igual que antes) ---
def cargar_datos():
    with open('inventario.json', 'r') as f:
        inventario = np.array(json.load(f))
    with open('precios.json', 'r') as f:
        precios = np.array(json.load(f))
    return inventario, precios

def guardar_inventario(inventario):
    with open('inventario.json', 'w') as f:
        json.dump(inventario.tolist(), f)

def guardar_precios(precios):
    with open('precios.json', 'w') as f:
        json.dump(precios.tolist(), f)
        
def registrar_movimiento(mensaje):
    with open('historial.log', 'a') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensaje}\n")

# --- Rutas de la Aplicación Web ---

@app.route('/')
def index():
    # Cargar datos frescos
    inventario, precios = cargar_datos()
    
    # --- ¡LA MAGIA DEL ÁLGEBRA LINEAL! ---
    # Multiplicamos la matriz de inventario (3x3) por el vector de precios (3x1)
    valor_por_bodega = np.dot(inventario, precios)
    valor_total = np.sum(valor_por_bodega)
    
    # Pasamos todos los datos a la plantilla HTML para que los muestre
    return render_template('index.html', 
                           bodegas=BODEGAS, 
                           cafes=CAFES, 
                           inventario=inventario, 
                           precios=precios,
                           valor_por_bodega=valor_por_bodega,
                           valor_total=valor_total)

@app.route('/actualizar-precios', methods=['POST'])
def actualizar_precios():
    # Obtenemos los nuevos precios del formulario
    nuevos_precios = [
        int(request.form['precio_castillo']),
        int(request.form['precio_caturra']),
        int(request.form['precio_borbon'])
    ]
    guardar_precios(np.array(nuevos_precios))
    return redirect(url_for('index')) # Redirigimos a la página principal

@app.route('/mover-inventario', methods=['POST'])
def mover_inventario():
    # Obtenemos los datos del formulario de movimiento
    bodega_origen_idx = int(request.form['origen'])
    bodega_destino_idx = int(request.form['destino'])
    cafe_idx = int(request.form['cafe'])
    cantidad = int(request.form['cantidad'])
    
    inventario, _ = cargar_datos()
    
    # Validamos que haya suficiente café para mover
    if inventario[bodega_origen_idx, cafe_idx] >= cantidad:
        # --- Operación matricial ---
        inventario[bodega_origen_idx, cafe_idx] -= cantidad
        inventario[bodega_destino_idx, cafe_idx] += cantidad
        guardar_inventario(inventario)
        # Log
        mensaje = f"Movimiento de {cantidad} sacos de {CAFES[cafe_idx]} desde {BODEGAS[bodega_origen_idx]} a {BODEGAS[bodega_destino_idx]}"
        registrar_movimiento(mensaje)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) # El modo debug ayuda a ver errores al instante