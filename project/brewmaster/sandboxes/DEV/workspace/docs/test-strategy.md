# Estrategia de pruebas

Unitarias:

- Validaciones V001 a V100 como reglas puras por servicio.
- Costo de lote, costo por litro, costo por unidad y costo de presentacion.
- Stock disponible como stock actual menos reservas activas.
- Alertas de stock bajo con intervalo de 24 horas y prioridad de stock cero.
- Transiciones de estado en lotes, ordenes de compra y reservas.

Integracion:

- Entrada de insumo actualiza stock y Kardex en la misma transaccion.
- Completar lote consume insumos, crea producto terminado y calcula costo.
- Venta descuenta inventario de productos y registra Kardex.
- Recepcion de compra genera entrada de inventario y actualiza estado.
- Worker de correo reintenta y marca error definitivo tras 5 intentos.

E2E:

- Login, crear insumo, registrar entrada y verificar Kardex.
- Crear receta, crear lote, completar lote y verificar producto terminado.
- Registrar venta y verificar stock y Kardex.
- Crear orden de compra, recepcionar y verificar stock.
- Exportar reporte de produccion a XLSX con filtro de fechas.
