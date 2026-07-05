# Especificación BrewMaster — Sistema de Gestión para Cervecerías Artesanales

A continuación tienes una **especificación directa** para BrewMaster, un sistema web de gestión integral para cervecerías artesanales, coherente entre módulos, tablas y endpoints.

# 0. Supuesto general del sistema

Sistema web para gestionar:

Insumos, recetas, producción de lotes, calidad, mermas, inventario de productos terminados, ventas, clientes, órdenes de compra, proveedores, equipos, finanzas operativas, reportes, dashboard y alertas por correo.

Arquitectura recomendada:

`/api/v1`

Regla general de endpoints:

`GET` consulta, `POST` crea, `PUT/PATCH` actualiza, `DELETE` elimina lógico, endpoints de acción solo para cambios de estado.

Ejemplo correcto:

`POST /api/v1/batches/{id}/complete`

No recomendado:

`POST /api/v1/completarLote`

---

# A. Casos de uso con flujos

## 1. Gestión de insumos y proveedores

### UC-INS-01 Registrar insumo

Actor: Responsable de compras / administrador.

Flujo:

1. Usuario abre módulo Insumos.
2. Selecciona Nuevo insumo.
3. Ingresa código, nombre, tipo, unidad de medida, proveedor, bodega, costos y umbrales de stock.
4. Sistema valida código único y campos obligatorios.
5. Sistema guarda insumo en estado activo.
6. Sistema registra auditoría.

Alternos:

- Si el código ya existe, bloquea guardado.
- Si faltan campos obligatorios, muestra errores por campo.
- Si costo unitario es negativo, bloquea guardado.

### UC-INS-02 Registrar entrada de insumo

Flujo:

1. Usuario abre Entradas de insumos.
2. Selecciona insumo, cantidad, costo, proveedor y referencia.
3. Sistema valida cantidad mayor a cero.
4. Sistema actualiza stock actual del insumo.
5. Sistema registra movimiento en Kardex con tipo ENTRADA.
6. Sistema verifica umbral de alerta: si stock recuperado, resetea `last_alert_sent_at`.
7. Sistema registra auditoría.

Alternos:

- Insumo inactivo bloquea entrada.
- Costo negativo bloquea operación.

### UC-INS-03 Gestionar alertas de stock bajo

Flujo:

1. Sistema ejecuta proceso programado tras cada movimiento de inventario.
2. Evalúa stock actual contra umbral configurado.
3. Si stock cayó bajo umbral, encola notificación.
4. Worker envía correo a destinatarios configurados.
5. Sistema registra intento en `notification_queue`.

Alternos:

- Stock en cero: envío inmediato sin respetar intervalo.
- No reenvía antes de 24 horas salvo stock en cero.
- Tras 5 intentos fallidos, queda en error definitivo.

### UC-INS-04 Editar insumo

Flujo:

1. Usuario abre listado de insumos.
2. Selecciona insumo y abre ficha.
3. Modifica campos permitidos: nombre, tipo, costo, umbrales y alertas.
4. Sistema valida cambios.
5. Sistema actualiza insumo.
6. Sistema registra auditoría.

Alternos:

- No permite cambiar unidad de medida si el insumo tiene movimientos.
- No permite editar insumos eliminados.

### UC-INS-05 Inactivar insumo

Flujo:

1. Usuario selecciona insumo.
2. Presiona Inactivar.
3. Sistema valida que no haya recetas activas que lo usen.
4. Sistema cambia estado a inactivo.
5. Sistema registra auditoría.

Alternos:

- Insumo usado en receta activa no puede inactivarse.
- Insumo inactivo no puede recibir nuevas entradas.

### UC-INS-06 Registrar proveedor

Flujo:

1. Usuario abre módulo Proveedores.
2. Selecciona Nuevo proveedor.
3. Ingresa código, razón social, correo, teléfono, dirección, contacto y condición de pago.
4. Sistema valida código único.
5. Sistema guarda proveedor en estado activo.
6. Sistema registra auditoría.

Alternos:

- Código duplicado bloquea guardado.
- Correo inválido bloquea guardado si se ingresa.

---

## 2. Gestión de recetas

### UC-REC-01 Crear receta

Actor: Jefe de producción / administrador.

Flujo:

1. Usuario abre módulo Recetas.
2. Selecciona Nueva receta.
3. Ingresa nombre, descripción, tipo de cerveza, ABV estimado, volumen por lote y pasos de elaboración.
4. Agrega ingredientes: insumo, cantidad y unidad.
5. Sistema valida al menos un ingrediente activo.
6. Sistema calcula costo estimado según costos unitarios actuales.
7. Sistema guarda receta en estado activo.

Alternos:

- No permite receta sin ingredientes.
- Insumo inactivo no puede agregarse como ingrediente.
- Si la receta ya tiene lotes activos, no puede editarse.

### UC-REC-02 Clonar receta

Flujo:

1. Usuario abre receta existente.
2. Selecciona Clonar receta.
3. Sistema crea copia con nombre modificado y estado en_prueba.
4. Usuario ajusta ingredientes o parámetros.
5. Sistema guarda nueva versión.

Alternos:

- Receta clonada hereda todos los ingredientes.
- No se puede clonar una receta inactiva.

---

## 3. Gestión de producción

### UC-PROD-01 Crear lote de producción

Actor: Jefe de producción / operario.

Flujo:

1. Usuario abre Producción.
2. Selecciona Nueva producción.
3. Elige receta activa y tipo de presentación.
4. Ingresa cantidad a producir, fecha y responsable.
5. Sistema carga ingredientes según receta.
6. Sistema valida stock disponible de insumos.
7. Sistema crea lote en estado en_elaboracion.

Alternos:

- Sin receta activa, bloquea creación.
- Stock insuficiente de insumos muestra alerta pero puede continuar según configuración.

### UC-PROD-02 Completar lote

Flujo:

1. Usuario abre lote en elaboración.
2. Ingresa cantidad producida, horas de mano de obra, kWh, litros de agua y merma.
3. Selecciona Completar lote.
4. Sistema valida stock de insumos suficiente para la receta.
5. Sistema descuenta insumos proporcionales a cantidad producida.
6. Sistema registra salidas en Kardex de insumos con tipo SALIDA_PRODUCCION.
7. Sistema crea o incrementa inventario de productos terminados.
8. Sistema calcula costo total: insumos + mano de obra + energía + agua + merma + indirectos.
9. Sistema calcula costo por litro y costo por unidad.
10. Sistema registra en auditoría y verifica alertas de stock.

Alternos:

- Stock insuficiente bloquea completar salvo política de faltante aprobada.
- Costo total no puede ser negativo.

### UC-PROD-03 Registrar control de calidad

Flujo:

1. Usuario abre lote completado.
2. Accede a Control de calidad.
3. Ingresa densidades (OG/FG), ABV calculado, pH, temperatura, evaluación organoléptica.
4. Indica resultado: aprobado o rechazado.
5. Sistema guarda registro de calidad.
6. Si rechazado, lote puede marcarse como merma.

Alternos:

- Solo un registro de calidad por lote.
- Motivo obligatorio si resultado es rechazado.

### UC-PROD-04 Registrar merma

Flujo:

1. Usuario abre módulo Mermas.
2. Selecciona tipo de entidad: insumo o producto terminado.
3. Ingresa entidad, cantidad, costo unitario, tipo de merma y motivo.
4. Sistema calcula costo total.
5. Sistema descuenta del inventario correspondiente.
6. Sistema registra movimiento en Kardex con tipo MERMA.
7. Sistema actualiza KPI de mermas en dashboard.

Alternos:

- Motivo obligatorio en toda merma.
- No permite cantidad mayor al stock disponible.

---

## 4. Gestión de inventario de productos terminados

### UC-PRO-01 Consultar inventario de productos

Actor: Responsable de ventas / administrador.

Flujo:

1. Usuario abre Inventario de productos terminados.
2. Filtra por receta, presentación, estado o stock.
3. Sistema muestra listado con stock actual, costo y precio de venta.
4. Usuario abre detalle.
5. Sistema muestra Kardex del producto.

Alternos:

- Stock en cero se resalta visualmente.
- Costo visible solo para usuarios con permiso.

### UC-PRO-02 Actualizar precio de venta

Flujo:

1. Usuario abre producto.
2. Edita precio de venta base.
3. Sistema valida precio mayor o igual a cero.
4. Sistema guarda nuevo precio.
5. Sistema registra auditoría.

Alternos:

- Precio menor al costo genera advertencia no bloqueante.
- Solo roles autorizados pueden modificar precios.

---

## 5. Gestión de ventas y clientes

### UC-VTA-01 Registrar cliente

Actor: Responsable de ventas / administrador.

Flujo:

1. Usuario abre módulo Clientes.
2. Selecciona Nuevo cliente.
3. Ingresa nombre, identificador fiscal, correo, tipo de cliente y condiciones comerciales.
4. Sistema valida identificador único.
5. Sistema guarda cliente activo.
6. Sistema registra auditoría.

Alternos:

- Identificador fiscal duplicado bloquea guardado.
- Cliente con ventas no se elimina físicamente.

### UC-VTA-02 Registrar venta

Flujo:

1. Usuario abre Nueva venta.
2. Selecciona cliente (opcional).
3. Agrega productos, cantidades y precios sugeridos según tipo de cliente.
4. Sistema valida stock disponible por producto.
5. Sistema calcula ganancia por línea: `(precio_venta − costo_unitario) × cantidad`.
6. Usuario confirma venta.
7. Sistema descuenta del inventario de productos terminados.
8. Sistema registra en Kardex de productos con tipo VENTA.
9. Sistema registra auditoría.

Alternos:

- No permite vender más que el stock disponible.
- Cliente inactivo bloquea nueva venta.
- Precio en cero genera advertencia.

### UC-VTA-03 Gestionar reservas de stock

Flujo:

1. Usuario abre Reservas.
2. Selecciona cliente, producto, cantidad y fecha de entrega.
3. Sistema valida stock disponible (stock actual menos reservas activas).
4. Sistema crea reserva activa.
5. Usuario puede liberar o convertir en venta cuando corresponda.

Alternos:

- Stock reservado no disponible para otras ventas.
- Reserva vencida queda en estado vencida automáticamente.

### UC-VTA-04 Editar cliente

Flujo:

1. Usuario busca cliente en listado.
2. Abre ficha de cliente.
3. Modifica datos: nombre, correo, teléfono, tipo de cliente y condiciones.
4. Sistema valida cambios.
5. Sistema actualiza cliente.
6. Sistema registra auditoría.

Alternos:

- No permite cambiar identificador fiscal si el cliente tiene ventas.
- No permite editar clientes eliminados.

### UC-VTA-05 Anular venta

Flujo:

1. Usuario abre venta confirmada.
2. Selecciona Anular y proporciona motivo.
3. Sistema valida que la venta no tenga más de 24 horas salvo permiso especial.
4. Sistema revierte stock descargado al inventario.
5. Sistema registra en Kardex con tipo DEVOLUCION.
6. Sistema marca venta como anulada.
7. Sistema registra auditoría.

Alternos:

- Venta con reservas asociadas requiere liberar reservas primero.
- Solo roles autorizados pueden anular ventas antiguas.

---

## 6. Gestión de compras

### UC-COM-01 Crear orden de compra

Actor: Responsable de compras / administrador.

Flujo:

1. Usuario abre Órdenes de compra.
2. Selecciona Nuevo pedido.
3. Elige proveedor y agrega insumos, cantidades y precios.
4. Sistema calcula total estimado.
5. Usuario guarda orden en estado borrador.
6. Usuario envía orden: estado cambia a enviada.

Alternos:

- Proveedor inactivo bloquea creación.
- Precio negativo bloquea línea.
- Cantidad menor o igual a cero bloquea línea.

### UC-COM-02 Recepcionar compra

Flujo:

1. Usuario abre orden enviada.
2. Ingresa cantidades recibidas por insumo.
3. Sistema valida cantidades contra pendiente.
4. Sistema genera entrada de inventario de insumos.
5. Sistema registra en Kardex con tipo ENTRADA.
6. Si recepción parcial, orden queda en parcialmente_recibida.
7. Si recepción total, orden queda en recibida.

Alternos:

- No recibe más de lo solicitado sin aprobación.
- Orden cancelada no permite recepción.

---

## 7. Gestión de equipos

### UC-EQU-01 Registrar equipo

Actor: Jefe de producción / administrador.

Flujo:

1. Usuario abre Equipos.
2. Selecciona Nuevo equipo.
3. Ingresa nombre, tipo, marca, modelo, serie, costo de adquisición y vida útil.
4. Sistema guarda equipo en estado operativo.

Alternos:

- Código de equipo único.
- Costo de adquisición no puede ser negativo.

### UC-EQU-02 Registrar mantenimiento

Flujo:

1. Usuario abre equipo.
2. Selecciona Nuevo movimiento.
3. Elige tipo: mantencion, falla, reparacion, revision o descarte.
4. Ingresa descripción, costo y fecha.
5. Sistema actualiza `ultima_mantencion` y `proxima_revision`.
6. Sistema registra historial.

Alternos:

- Equipo descartado no acepta nuevos movimientos.
- Próxima revisión en el pasado genera alerta.

---

## 8. Gestión financiera básica

### UC-FIN-01 Registrar gasto operativo

Actor: Responsable de finanzas / administrador.

Flujo:

1. Usuario abre Gastos.
2. Ingresa concepto, categoría, monto, fecha y referencia.
3. Sistema valida monto mayor a cero.
4. Sistema guarda gasto.
5. Sistema actualiza reportes financieros.

Alternos:

- Categoría obligatoria.
- Gasto con documentos no puede eliminarse.

### UC-FIN-02 Consultar reportes financieros

Flujo:

1. Usuario abre Reportes financieros.
2. Selecciona tipo: estado de resultados, flujo de caja, cuentas por cobrar o punto de equilibrio.
3. Define rango de fechas.
4. Sistema calcula y muestra resultados.
5. Usuario exporta si tiene permiso.

Alternos:

- Datos sensibles ocultos sin permiso financiero.
- Exportación queda registrada en auditoría.

### UC-FIN-03 Gestionar metas mensuales

Flujo:

1. Usuario abre módulo Metas mensuales.
2. Selecciona mes y año objetivo.
3. Ingresa metas: litros de producción, monto de ventas, número de clientes nuevos y margen esperado.
4. Sistema guarda metas.
5. Dashboard muestra progreso vs meta en tiempo real.

Alternos:

- Solo admin puede crear o modificar metas.
- Meta sin dato numérico no bloquea guardado del resto.

---

## 9. Dashboard y reportes

### UC-REP-01 Ver dashboard general

Actor: Todos los roles según permisos.

Flujo:

1. Usuario ingresa al sistema.
2. Sistema carga KPIs según rol y permisos.
3. Muestra producción, inventario, ventas, compras, mermas y alertas.
4. Usuario filtra por fecha o bodega.

Alternos:

- Sin permisos, oculta KPIs financieros.
- Sin datos, muestra indicadores en cero.

### UC-REP-02 Exportar reporte

Flujo:

1. Usuario abre módulo Reportes.
2. Selecciona tipo: producción, ventas, inventario, Kardex, mermas, costos, financiero o auditoría.
3. Define filtros y formato: CSV, XLSX o PDF.
4. Sistema genera y entrega archivo.
5. Sistema registra exportación.

Alternos:

- Reporte de auditoría solo para admin y auditor.
- Rango amplio puede generar reporte diferido.

---

## 10. Gestión de configuración y alertas

### UC-ALT-01 Configurar alertas por correo

Actor: Administrador.

Flujo:

1. Usuario abre Configuración SMTP.
2. Ingresa parámetros: servidor, puerto, usuario, contraseña y correo remitente.
3. Sistema valida configuración.
4. Sistema guarda encriptado.
5. Usuario puede enviar correo de prueba.

Alternos:

- Solo admin puede editar SMTP.
- Credenciales nunca visibles en texto plano.

### UC-ALT-02 Configurar metas mensuales

Flujo:

1. Usuario abre Metas mensuales.
2. Selecciona mes y año.
3. Ingresa metas: litros de producción, monto de ventas, número de clientes y margen esperado.
4. Sistema guarda metas.
5. Dashboard muestra progreso vs meta.

Alternos:

- Solo admin puede definir metas.
- Meta sin dato no bloquea guardado del resto.

### UC-ALT-03 Gestionar usuarios y roles

Flujo:

1. Administrador abre módulo Usuarios.
2. Crea o edita usuario con nombre, correo, contraseña temporal y rol.
3. Sistema valida correo único y contraseña mínima.
4. Sistema guarda usuario activo.
5. Sistema registra auditoría.

Alternos:

- Rol obligatorio para guardar usuario.
- Correo duplicado bloquea creación.
- Solo admin puede gestionar usuarios y roles.

---

# B. Especificación de pantallas

## 30 pantallas

### P-01 Login

Campos: correo, contraseña.  
Acciones: ingresar, recuperar contraseña.  
Validaciones: credenciales válidas, usuario activo.

### P-02 Recuperar contraseña

Campos: correo.  
Acciones: enviar enlace de restablecimiento.  
Validaciones: formato de correo válido.

### P-03 Dashboard general

Muestra: KPIs de producción, inventario, ventas y finanzas. Gráfico de ventas últimos 6 meses, gráficos de stock, flujo de caja, meta vs real.  
Acciones: filtrar por fecha, abrir detalle de alerta.

### P-04 Listado de insumos

Campos filtro: código, nombre, tipo, bodega, estado.  
Muestra: badge de bajo stock.  
Acciones: crear, editar, exportar, abrir Kardex.

### P-05 Formulario de insumo

Campos: código, nombre, descripción, tipo, unidad de medida, proveedor, bodega, costo unitario, stock mínimo, stock máximo, fecha vencimiento, alertas email.  
Acciones: guardar, cancelar.

### P-06 Kardex de insumo

Campos filtro: fecha de inicio, fecha de fin, tipo de movimiento.  
Muestra: fecha, tipo, cantidad, costo, saldo resultante, referencia, usuario.  
Acciones: exportar.

### P-07 Entrada de insumos

Campos: insumo, cantidad, costo unitario, proveedor, referencia, observación.  
Acciones: registrar entrada.

### P-08 Listado de proveedores

Campos filtro: nombre, estado, tipo de insumo.  
Acciones: crear, editar, activar/desactivar.

### P-09 Formulario de proveedor

Campos: código, razón social, correo, teléfono, dirección, contacto principal, tipo de insumos, condición de pago.  
Acciones: guardar, cancelar.

### P-10 Listado de recetas

Campos filtro: nombre, tipo de cerveza, estado.  
Acciones: crear, editar, clonar, consultar costo.

### P-11 Formulario de receta

Campos de cabecera: nombre, descripción, tipo, ABV estimado, volumen por lote, pasos de elaboración.  
Sub-tabla de ingredientes: insumo, cantidad, unidad.  
Acciones: agregar ingrediente, guardar, cancelar.

### P-12 Listado de bodegas

Campos: código, nombre, tipo, responsable, capacidad.  
Acciones: crear, editar.

### P-13 Tipos de presentación

Campos: nombre, volumen, unidad, costo de presentación.  
Acciones: crear, editar.

### P-14 Listado de lotes de producción

Campos filtro: receta, estado, fecha de producción.  
Acciones: crear, completar, cancelar, ver detalle, control de calidad.

### P-15 Formulario de lote de producción

Campos: receta, tipo de presentación, cantidad a producir, fecha, responsable, horas de mano de obra, kWh, litros de agua, merma, costo indirecto, observaciones.  
Acciones: guardar, completar, cancelar.

### P-16 Detalle de lote

Muestra: datos del lote, insumos consumidos, costo total calculado, costo por litro, costo por unidad, resultado de calidad.  
Acciones: ver Kardex de insumos afectados.

### P-17 Control de calidad de lote

Campos: OG, FG, ABV calculado, ABV esperado, pH, temperatura de fermentación, apariencia, nota de aroma, nota de sabor, observaciones organolépticas, resultado, motivo de rechazo.  
Acciones: guardar.

### P-18 Inventario de productos terminados

Campos filtro: receta, presentación, estado, stock.  
Muestra: stock actual, costo unitario, precio de venta.  
Acciones: actualizar precio, ver Kardex, exportar.

### P-19 Registro de mermas

Campos: tipo de entidad (insumo/producto), entidad, cantidad, costo unitario, tipo de merma, motivo, fecha, lote asociado.  
Acciones: registrar.

### P-20 Listado de clientes

Campos filtro: nombre, identificador fiscal, tipo de cliente, estado.  
Acciones: crear, editar, activar/desactivar, ver historial de ventas.

### P-21 Formulario de cliente

Campos: nombre/razón social, identificador fiscal, correo, teléfono, dirección, tipo de cliente, forma de pago habitual, límite de crédito.  
Acciones: guardar, cancelar.

### P-22 Formulario de venta

Campos: cliente (opcional), fecha, responsable, observación.  
Líneas: producto, cantidad, precio sugerido por tipo de cliente, ganancia estimada.  
Acciones: agregar línea, confirmar venta.

### P-23 Reservas de stock

Campos: cliente, producto, cantidad, fecha de entrega prometida, precio.  
Acciones: crear, liberar, convertir en venta.

### P-24 Órdenes de compra

Campos filtro: proveedor, estado, fecha.  
Acciones: crear, editar, enviar, recepcionar, cancelar.

### P-25 Formulario de orden de compra

Campos: proveedor, fecha de emisión, fecha esperada de recepción, observación.  
Líneas: insumo, cantidad solicitada, precio unitario.  
Acciones: guardar, enviar.

### P-26 Recepción de compra

Campos: orden de compra, cantidades recibidas por insumo, bodega de destino.  
Acciones: recepcionar parcial, recepcionar total.

### P-27 Gestión de equipos

Campos filtro: tipo, estado, revisión vencida.  
Acciones: crear, editar, registrar movimiento, ver historial.

### P-28 Gastos operativos

Campos filtro: categoría, fecha, responsable.  
Acciones: crear, editar, eliminar, exportar.

### P-29 Reportes

Opciones: producción, ventas, inventario, Kardex, mermas, costos, financiero, auditoría.  
Campos filtro: fecha de inicio, fecha de fin, entidad específica.  
Acciones: generar, exportar CSV/XLSX/PDF.

### P-30 Configuración y alertas

Secciones: configuración SMTP, notificaciones enviadas, metas mensuales, gestión de usuarios y roles.  
Acciones: guardar SMTP, enviar prueba, definir meta, crear usuario, asignar rol.

---

# C. Reglas de negocio

## 60 reglas de negocio

1. Todo registro operativo debe pertenecer a una empresa.
2. Todo usuario debe tener un rol asignado y activo.
3. Todo cambio crítico debe registrarse en auditoría con usuario, fecha, entidad, acción e IP.
4. Los registros con historial operativo no se eliminan físicamente.
5. La eliminación lógica cambia estado a inactivo o cancelado.
6. Las contraseñas deben almacenarse siempre encriptadas con bcrypt o equivalente.
7. Un usuario inactivo no puede iniciar sesión.
8. Solo el rol admin puede gestionar usuarios y roles.
9. Los permisos se evalúan por rol en cada operación de API.
10. Un usuario sin permiso recibe HTTP 403, nunca datos parciales.
11. El código de insumo debe ser único por empresa.
12. Un insumo inactivo no puede recibir entradas ni usarse en recetas o lotes.
13. El costo unitario de un insumo no puede ser negativo.
14. El stock mínimo de un insumo no puede ser negativo.
15. El stock actual de un insumo no puede ser negativo.
16. Un insumo con movimientos de inventario no se elimina físicamente.
17. Toda entrada de insumo actualiza el stock actual y registra en Kardex.
18. Toda salida de insumo valida que haya stock suficiente antes de procesar.
19. El sistema no permite stock negativo salvo configuración explícita.
20. Las alertas de stock bajo se envían solo si el insumo tiene alertas habilitadas.
21. No se reenvía alerta de stock bajo antes de 24 horas para el mismo insumo.
22. Stock en cero fuerza envío de alerta inmediato sin respetar intervalo.
23. Stock recuperado sobre mínimo resetea el temporizador de alerta.
24. Tras 5 intentos fallidos de correo, la notificación queda en estado de error definitivo.
25. Una receta debe tener al menos un ingrediente activo.
26. Una receta con lotes activos en producción no puede editarse.
27. El costo estimado de una receta se calcula automáticamente con los costos unitarios vigentes.
28. Una receta solo puede clonarse si está activa o en prueba.
29. Un lote de producción creado queda en estado en_elaboracion.
30. Un lote no puede completarse sin stock suficiente de insumos de la receta.
31. Al completar un lote, los insumos se descuentan proporcionalmente a la cantidad producida.
32. Al completar un lote, el inventario de productos terminados se crea o incrementa.
33. El costo total de un lote incluye insumos, mano de obra, energía, agua, merma e indirectos.
34. El costo por unidad incluye el costo de la presentación (envase, tapa, etiqueta).
35. Un lote cancelado no afecta inventario ni Kardex.
36. Solo puede existir un registro de control de calidad por lote.
37. El resultado de control de calidad aprobado o rechazado es obligatorio al guardar.
38. Un lote rechazado en calidad puede registrarse completamente como merma.
39. Toda merma debe tener motivo detallado obligatorio.
40. La merma descuenta del inventario correspondiente y registra en Kardex.
41. El porcentaje de merma se compara contra el umbral del 5% para alertas en dashboard.
42. El nombre de la receta debe ser único por empresa.
43. El identificador fiscal del cliente debe ser único por empresa.
44. Un cliente inactivo no puede asignarse a una nueva venta.
45. Un cliente con ventas no puede eliminarse físicamente.
46. El precio de venta sugerido en la venta se toma según tipo de cliente y lista vigente.
47. El stock disponible para ventas es stock actual menos reservas activas.
48. No se puede vender más que el stock disponible.
49. Una reserva activa no puede usarse en otra venta hasta liberarse o vencerse.
50. El proveedor de una orden de compra debe estar activo.
51. Una orden de compra en borrador puede editarse; una enviada no puede modificarse sin permiso.
52. La recepción de compra no puede superar la cantidad solicitada salvo tolerancia configurada.
53. La recepción total cierra la orden; la recepción parcial la deja en estado parcialmente_recibida.
54. Una orden cancelada no acepta recepción de mercadería.
55. El código de equipo debe ser único por empresa.
56. Un equipo descartado no acepta nuevos movimientos de mantenimiento.
57. La próxima revisión vencida genera alerta en dashboard y en listado de equipos.
58. Los gastos operativos con documentos asociados no pueden eliminarse.
59. El monto de un gasto operativo debe ser mayor a cero.
60. Solo admin y auditor pueden acceder al reporte de auditoría.

---

# D. Validaciones y CHECK

## 100 validaciones

1. V001: `user_id` obligatorio en todas las operaciones manuales.
2. V002: `created_at` obligatorio y con zona horaria del sistema.
3. V003: `updated_at` obligatorio en entidades modificables.
4. V004: `status` obligatorio en toda entidad con ciclo de vida.
5. V005: IDs deben ser enteros positivos o UUID según entidad.
6. V006: Fechas deben rechazar formatos inválidos.
7. V007: No aceptar campos de texto con solo espacios en blanco.
8. V008: Longitud máxima de texto respetar límites definidos por campo.
9. V009: Correos deben tener formato válido RFC 5321.
10. V010: Teléfonos deben tener longitud mínima de 7 dígitos.
11. V011: Campos monetarios deben tener exactamente dos decimales.
12. V012: Montos no pueden ser NaN ni nulos si participan en totales.
13. V013: Cantidades deben ser numéricas y no NaN.
14. V014: Cantidades deben tener máximo cuatro decimales.
15. V015: Usuario autenticado obligatorio en toda llamada protegida.
16. V016: Usuario inactivo debe recibir HTTP 401 al autenticar.
17. V017: Contraseña debe tener mínimo 8 caracteres.
18. V018: Contraseña nunca almacenable en texto plano.
19. V019: Token JWT expirado debe rechazarse con HTTP 401.
20. V020: Rol obligatorio para usuario activo.
21. V021: Rol inactivo no puede asignarse a usuario.
22. V022: Correo de usuario único por empresa.
23. V023: Intentos fallidos de login deben registrarse en auditoría.
24. V024: Cambio de contraseña exige contraseña actual correcta.
25. V025: Código de insumo obligatorio.
26. V026: Código de insumo único por empresa.
27. V027: Nombre de insumo obligatorio.
28. V028: Tipo de insumo obligatorio (lista cerrada).
29. V029: Unidad de medida de insumo obligatoria.
30. V030: Costo unitario de insumo mayor o igual a cero.
31. V031: Stock mínimo mayor o igual a cero.
32. V032: Stock máximo mayor o igual a stock mínimo si ambos definidos.
33. V033: Stock actual mayor o igual a cero salvo configuración explícita.
34. V034: Insumo inactivo no puede recibir entradas de inventario.
35. V035: Insumo inactivo no puede incluirse en receta.
36. V036: Alerta de insumo requiere al menos un correo destinatario válido.
37. V037: Umbral personalizado de alerta mayor a cero si definido.
38. V038: Intervalo mínimo entre alertas mayor a cero horas.
39. V039: Máximo de reintentos de correo mayor a cero.
40. V040: Código de proveedor único por empresa.
41. V041: Razón social de proveedor obligatoria.
42. V042: Correo de proveedor debe ser válido si se ingresa.
43. V043: Proveedor con órdenes de compra no puede eliminarse físicamente.
44. V044: Proveedor inactivo no puede asignarse a nueva orden de compra.
45. V045: Nombre de receta obligatorio.
46. V046: Nombre de receta único por empresa.
47. V047: Tipo de cerveza obligatorio en receta.
48. V048: Volumen por lote mayor a cero.
49. V049: ABV estimado mayor o igual a cero.
50. V050: Receta debe tener al menos un ingrediente.
51. V051: Cantidad de ingrediente en receta mayor a cero.
52. V052: Unidad de ingrediente de receta obligatoria.
53. V053: Receta con lotes activos no puede editarse.
54. V054: Receta inactiva no puede asignarse a nuevo lote.
55. V055: Número de lote único por empresa.
56. V056: Receta de lote obligatoria.
57. V057: Tipo de presentación de lote obligatorio.
58. V058: Cantidad producida en lote mayor a cero.
59. V059: Fecha de producción de lote obligatoria.
60. V060: Responsable de lote obligatorio.
61. V061: Horas de mano de obra mayor o igual a cero.
62. V062: kWh consumidos mayor o igual a cero.
63. V063: Litros de agua mayor o igual a cero.
64. V064: Porcentaje de merma entre 0 y 100.
65. V065: Costo total de lote mayor o igual a cero.
66. V066: Lote no puede completarse sin stock suficiente de insumos.
67. V067: Lote en estado completado no puede editarse.
68. V068: Lote cancelado no puede completarse.
69. V069: Control de calidad requiere resultado aprobado o rechazado.
70. V070: Motivo de rechazo en calidad obligatorio si resultado es rechazado.
71. V071: Notas organolépticas entre 1 y 10.
72. V072: OG mayor a cero.
73. V073: FG mayor a cero y menor a OG.
74. V074: pH entre 0 y 14.
75. V075: Tipo de merma obligatorio (lista cerrada).
76. V076: Motivo detallado de merma obligatorio.
77. V077: Cantidad de merma mayor a cero.
78. V078: Cantidad de merma no puede superar stock disponible de la entidad.
79. V079: Identificador fiscal de cliente único por empresa.
80. V080: Nombre de cliente obligatorio.
81. V081: Tipo de cliente obligatorio (lista cerrada).
82. V082: Límite de crédito mayor o igual a cero.
83. V083: Cliente inactivo no puede asignarse a venta.
84. V084: Venta debe tener al menos una línea.
85. V085: Línea de venta requiere producto activo.
86. V086: Cantidad en línea de venta mayor a cero.
87. V087: Precio en línea de venta mayor o igual a cero.
88. V088: Cantidad vendida no puede superar stock disponible.
89. V089: Ganancia por línea calculada automáticamente.
90. V090: Reserva requiere cliente, producto, cantidad y fecha de entrega.
91. V091: Cantidad de reserva mayor a cero.
92. V092: Cantidad de reserva no puede superar stock disponible libre.
93. V093: Número de orden de compra único por empresa.
94. V094: Orden de compra requiere proveedor activo.
95. V095: Orden de compra requiere al menos una línea.
96. V096: Cantidad solicitada en orden mayor a cero.
97. V097: Precio unitario en orden mayor o igual a cero.
98. V098: Cantidad recibida no puede superar solicitada más tolerancia.
99. V099: Código de equipo único por empresa.
100. V100: Monto de gasto operativo mayor a cero.

---

# F. Endpoints REST

## Base

`/api/v1`

## 40 endpoints

1. `POST /api/v1/auth/login` — iniciar sesión, retorna token JWT.
2. `POST /api/v1/auth/logout` — cerrar sesión.
3. `GET /api/v1/auth/me` — obtener usuario autenticado.
4. `POST /api/v1/auth/change-password` — cambiar contraseña.
5. `GET /api/v1/users` — listar usuarios con filtros por rol y estado.
6. `POST /api/v1/users` — crear usuario (solo admin).
7. `GET /api/v1/users/{id}` — obtener detalle de usuario.
8. `PUT /api/v1/users/{id}` — editar usuario.
9. `PATCH /api/v1/users/{id}/toggle-status` — activar o desactivar usuario.
10. `GET /api/v1/suppliers` — listar proveedores.
11. `POST /api/v1/suppliers` — crear proveedor.
12. `PUT /api/v1/suppliers/{id}` — actualizar proveedor.
13. `PATCH /api/v1/suppliers/{id}/toggle-status` — activar o desactivar proveedor.
14. `GET /api/v1/supplies` — listar insumos con filtros.
15. `POST /api/v1/supplies` — crear insumo.
16. `GET /api/v1/supplies/{id}` — obtener insumo.
17. `PUT /api/v1/supplies/{id}` — actualizar insumo.
18. `PATCH /api/v1/supplies/{id}/toggle-status` — activar o desactivar insumo.
19. `GET /api/v1/supplies/{id}/kardex` — Kardex del insumo.
20. `GET /api/v1/supplies/low-stock` — insumos bajo stock mínimo.
21. `POST /api/v1/supply-entries` — registrar entrada de insumo.
22. `GET /api/v1/supply-entries` — listar entradas de insumos.
23. `GET /api/v1/recipes` — listar recetas.
24. `POST /api/v1/recipes` — crear receta.
25. `GET /api/v1/recipes/{id}` — obtener receta con ingredientes.
26. `PUT /api/v1/recipes/{id}` — actualizar receta.
27. `POST /api/v1/recipes/{id}/clone` — clonar receta.
28. `GET /api/v1/batches` — listar lotes de producción.
29. `POST /api/v1/batches` — crear lote.
30. `GET /api/v1/batches/{id}` — obtener lote con detalle de insumos.
31. `PUT /api/v1/batches/{id}` — editar lote en elaboración.
32. `POST /api/v1/batches/{id}/complete` — completar lote.
33. `POST /api/v1/batches/{id}/cancel` — cancelar lote.
34. `POST /api/v1/batches/{id}/quality-check` — registrar control de calidad.
35. `GET /api/v1/products` — listar inventario de productos terminados.
36. `PUT /api/v1/products/{id}/price` — actualizar precio de venta.
37. `POST /api/v1/sales` — registrar venta.
38. `GET /api/v1/sales` — listar ventas con filtros.
39. `GET /api/v1/customers` — listar clientes.
40. `POST /api/v1/customers` — crear cliente.

---

# G. Estados recomendados por módulo

## Usuarios

`active`, `inactive`

## Insumos y proveedores

`active`, `inactive`

## Recetas

`active`, `inactive`, `en_prueba`

## Lotes de producción

`en_elaboracion`, `completado`, `cancelado`

## Control de calidad

`aprobado`, `rechazado`

## Inventario de productos

`active`, `inactive`

## Ventas

`completada`, `anulada`

## Reservas de stock

`activa`, `consumida`, `liberada`, `vencida`

## Órdenes de compra

`borrador`, `enviada`, `parcialmente_recibida`, `recibida`, `cancelada`

## Equipos

`operativo`, `mantenimiento`, `fuera_servicio`, `descartado`

## Notificaciones

`queued`, `sent`, `failed`

---

# H. Modelo básico de permisos

1. `supplies.read`
2. `supplies.create`
3. `supplies.update`
4. `supplies.toggle-status`
5. `supply-entries.create`
6. `recipes.read`
7. `recipes.create`
8. `recipes.update`
9. `recipes.clone`
10. `batches.read`
11. `batches.create`
12. `batches.complete`
13. `batches.cancel`
14. `batches.quality-check`
15. `waste.create`
16. `waste.read`
17. `products.read`
18. `products.update-price`
19. `sales.read`
20. `sales.create`
21. `customers.read`
22. `customers.create`
23. `customers.update`
24. `reservations.create`
25. `reservations.manage`
26. `purchase-orders.read`
27. `purchase-orders.create`
28. `purchase-orders.receive`
29. `purchase-orders.cancel`
30. `suppliers.read`
31. `suppliers.create`
32. `suppliers.update`
33. `equipment.read`
34. `equipment.create`
35. `equipment.movement`
36. `expenses.read`
37. `expenses.create`
38. `reports.read`
39. `reports.export`
40. `admin.users`
41. `admin.settings`
42. `audit.read`

---

# I. Endpoint recomendado como patrón principal

El mejor patrón para BrewMaster es:

```http
POST /api/v1/{resource}/{id}/{action}
```

Solo para acciones de negocio que cambian estado.

Ejemplos correctos:

```http
POST /api/v1/batches/{id}/complete
POST /api/v1/batches/{id}/cancel
POST /api/v1/batches/{id}/quality-check
POST /api/v1/purchase-orders/{id}/send
POST /api/v1/purchase-orders/{id}/receive
POST /api/v1/reservations/{id}/consume
POST /api/v1/reservations/{id}/release
```

Para CRUD normal:

```http
GET    /api/v1/supplies
POST   /api/v1/supplies
GET    /api/v1/supplies/{id}
PUT    /api/v1/supplies/{id}
PATCH  /api/v1/supplies/{id}/toggle-status
```

Este diseño es simple, consistente y escalable para web, móvil o integraciones futuras.

---

# J. Desarrollo SDD para BREWMASTER

## J.1 Metadatos de control

| campo | valor |
|---|---|
| proyecto | `BREWMASTER` |
| producto | Sistema web de gestión para cervecerías artesanales |
| version_spec | `sdd-2026-06-24` |
| workflow | `sdd-extended-1.0` |
| arnes | obligatorio |
| orquestador | obligatorio |
| entrada valida | `harness.run_agent(agent_id, state)` |
| estado objetivo | especificacion lista para planificacion e implementacion |
| costo externo permitido | `0.000000 USD` en modo local deterministico |
| no_inventar | `true` |

## J.2 Alcance cerrado para MVP

Incluye:

1. Autenticación JWT, usuarios, roles, permisos y auditoría.
2. Proveedores, insumos, bodegas, tipos de presentación y Kardex de insumos.
3. Entradas de insumos, alertas de stock bajo por correo y cola de notificaciones.
4. Recetas con ingredientes, costo estimado y clonado.
5. Lotes de producción, completar lote, control de calidad y mermas.
6. Inventario de productos terminados, precios de venta y Kardex de productos.
7. Clientes, ventas, reservas de stock y precios por tipo de cliente.
8. Proveedores, órdenes de compra, recepción parcial y total.
9. Equipos, historial de mantenimientos y alertas de revisión vencida.
10. Gastos operativos, reportes financieros básicos y metas mensuales.
11. Dashboard con KPIs reales, gráficos y alertas operacionales.
12. Reportes exportables: producción, ventas, inventario, Kardex, mermas, costos, financiero y auditoría.

Excluye del MVP:

1. Integración con sistemas tributarios externos o facturación electrónica.
2. Contabilidad completa y conciliación bancaria.
3. Aplicación móvil nativa.
4. POS fiscal certificado.
5. Multiempresa con consolidación.
6. Deploy productivo, lectura de secretos o acceso a datos reales sin aprobación.

## J.3 Supuestos funcionales

1. La empresa opera con una moneda base y zona horaria configurables.
2. El stock disponible se calcula como stock actual menos reservas activas.
3. La eliminación física no se usa para entidades con historial operativo.
4. El costo por unidad de producto incluye costo de producción más costo de presentación.
5. Las alertas de stock por correo respetan un intervalo mínimo configurable de 24 horas.
6. El dashboard carga datos reales en tiempo real o con caché de corta duración.
7. Las exportaciones de reportes quedan registradas en auditoría.
8. La configuración SMTP se almacena encriptada.

## J.4 Arquitectura objetivo

Capas:

1. Frontend web: aplicación responsive con rutas protegidas por rol, formularios con validación local, tablas paginadas y estados de carga, vacío y error.
2. API REST: `/api/v1`, validación de entrada, permisos por acción, transacciones por caso de uso y respuestas JSON consistentes.
3. Dominio: servicios por módulo con reglas de negocio puras y eventos de auditoría.
4. Persistencia: base relacional con constraints, índices y eliminación lógica.
5. Jobs: alertas de stock, reintentos de correo, vencimientos de reservas y backups.
6. Observabilidad: logs estructurados, auditoría funcional y métricas de errores.

Stack tecnológico:

| capa | tecnología |
|---|---|
| frontend | React + Bootstrap |
| backend | Python 3 + FastAPI |
| ORM | SQLAlchemy + Alembic |
| base de datos | MySQL o MariaDB |
| jobs | APScheduler |
| autenticación | JWT con refresh token |
| reportes | CSV / XLSX / PDF |
| documentación API | Swagger / OpenAPI automático con FastAPI |
| archivos exportados | almacenamiento local o compatible S3 |

## J.5 Modelo de dominio canónico

Usuarios y seguridad:

| entidad | propósito | campos clave |
|---|---|---|
| `users` | identidad operativa | `id`, `nombre`, `email`, `password_hash`, `rol`, `estado`, `created_at` |
| `roles` | roles del sistema | `id`, `nombre`, `descripcion`, `estado` |
| `permissions` | permisos por acción | `id`, `codigo`, `descripcion`, `modulo` |
| `role_permissions` | relación rol-permiso | `role_id`, `permission_id` |
| `audit_logs` | historial de acciones | `user_id`, `action`, `entity`, `entity_id`, `detail`, `ip_address`, `created_at` |
| `settings` | configuración global | `key`, `value` (encriptado si sensible) |

Insumos y proveedores:

| entidad | propósito | campos clave |
|---|---|---|
| `suppliers` | proveedores | `codigo`, `nombre`, `email`, `telefono`, `contacto`, `condicion_pago`, `estado` |
| `warehouses` | bodegas | `codigo`, `nombre`, `tipo`, `responsable`, `capacidad`, `temperatura_controlada`, `estado` |
| `supply_categories` | categorías de insumos | `id`, `nombre`, `descripcion`, `estado` |
| `supplies` | insumos | `codigo`, `nombre`, `tipo`, `unidad_medida`, `proveedor_id`, `bodega_id`, `costo_unitario`, `stock_minimo`, `stock_actual`, `enable_email_alerts`, `alert_emails`, `last_alert_sent_at`, `estado` |
| `supply_movements` | Kardex de insumos | `supply_id`, `tipo_movimiento`, `cantidad`, `costo_unitario`, `saldo_resultante`, `referencia`, `user_id`, `created_at` |
| `supply_entries` | entradas de insumos | `supply_id`, `cantidad`, `costo_unitario`, `proveedor_id`, `referencia`, `user_id` |
| `notification_queue` | cola de correos | `supply_id`, `recipients`, `subject`, `body_html`, `status`, `attempts`, `sent_at`, `error_message` |

Recetas y producción:

| entidad | propósito | campos clave |
|---|---|---|
| `beer_styles` | estilos de cerveza | `id`, `nombre`, `descripcion`, `abv_min`, `abv_max`, `ibu_min`, `ibu_max` |
| `presentation_types` | tipos de presentación | `nombre`, `volumen`, `unidad`, `costo_presentacion`, `estado` |
| `recipes` | recetas de cerveza | `nombre`, `tipo`, `abv_estimado`, `volumen_por_lote`, `pasos_elaboracion`, `costo_estimado`, `estado` |
| `recipe_ingredients` | ingredientes de receta | `recipe_id`, `supply_id`, `cantidad`, `unidad` |
| `production_batches` | lotes de producción | `numero_lote`, `recipe_id`, `presentation_type_id`, `cantidad_producida`, `fecha_produccion`, `responsable_id`, `estado`, `horas_mano_obra`, `kwh_consumidos`, `litros_agua`, `porcentaje_merma`, `costo_total`, `costo_por_litro`, `costo_por_unidad` |
| `batch_quality_checks` | control de calidad | `batch_id`, `og`, `fg`, `abv_calculado`, `ph`, `temp_fermentacion`, `nota_aroma`, `nota_sabor`, `resultado`, `motivo_rechazo`, `responsable_id` |
| `waste_records` | mermas | `tipo_entidad`, `entidad_id`, `cantidad_perdida`, `costo_unitario`, `costo_total`, `tipo_merma`, `motivo_detallado`, `responsable_id`, `fecha`, `batch_id` |

Inventario de productos y ventas:

| entidad | propósito | campos clave |
|---|---|---|
| `finished_products` | inventario productos terminados | `recipe_id`, `presentation_type_id`, `cantidad_stock`, `costo_unitario`, `precio_venta`, `fecha_vencimiento_aprox`, `estado` |
| `product_movements` | Kardex de productos | `product_id`, `tipo_movimiento`, `cantidad`, `costo_unitario`, `saldo_resultante`, `referencia`, `user_id` |
| `customer_types` | tipos de cliente | `id`, `nombre`, `descripcion`, `descuento_pct_base` |
| `customers` | clientes | `nombre`, `identificador_fiscal`, `email`, `telefono`, `tipo_cliente`, `forma_pago`, `limite_credito`, `estado` |
| `product_prices` | precios por tipo de cliente | `product_id`, `tipo_cliente`, `precio_unitario`, `precio_por_docena`, `descuento_pct`, `vigente_desde`, `vigente_hasta` |
| `sales` | ventas | `numero_documento`, `cliente_id`, `fecha_venta`, `responsable_id`, `total`, `ganancia_total` |
| `sale_items` | líneas de venta | `sale_id`, `product_id`, `cantidad`, `precio_unitario`, `costo_unitario`, `ganancia_unitaria` |
| `stock_reservations` | reservas de stock | `cliente_id`, `product_id`, `cantidad_reservada`, `fecha_entrega_prometida`, `precio`, `estado` |

Compras, equipos y finanzas:

| entidad | propósito | campos clave |
|---|---|---|
| `purchase_orders` | órdenes de compra | `numero_orden`, `proveedor_id`, `fecha_emision`, `fecha_esperada_recepcion`, `total_estimado`, `estado` |
| `purchase_order_items` | líneas de orden de compra | `order_id`, `supply_id`, `cantidad_solicitada`, `precio_unitario`, `cantidad_recibida` |
| `equipment_types` | tipos de equipo | `id`, `nombre`, `descripcion`, `intervalo_revision_dias` |
| `equipment` | equipos | `codigo`, `nombre`, `tipo`, `marca`, `modelo`, `serie`, `fecha_compra`, `costo_adquisicion`, `estado`, `ultima_mantencion`, `proxima_revision` |
| `equipment_movements` | historial de equipos | `equipment_id`, `tipo_movimiento`, `descripcion`, `costo`, `fecha`, `responsable_id` |
| `expense_categories` | categorías de gastos | `id`, `nombre`, `descripcion`, `estado` |
| `operational_expenses` | gastos operativos | `concepto`, `categoria`, `monto`, `fecha`, `proveedor`, `documento_referencia`, `responsable_id` |
| `monthly_goals` | metas mensuales | `mes`, `litros_produccion`, `monto_ventas`, `num_clientes`, `margen_promedio_pct` |
| `password_reset_tokens` | tokens de recuperación de contraseña | `user_id`, `token_hash`, `expires_at`, `used_at`, `created_at` |
| `export_jobs` | trabajos de exportación diferidos | `id`, `user_id`, `tipo_reporte`, `filtros`, `estado`, `archivo_url`, `created_at`, `completed_at` |
| `smtp_config` | configuración de servidor de correo | `id`, `host`, `port`, `username`, `password_encrypted`, `from_email`, `use_tls`, `updated_by` |
| `batch_supply_snapshots` | snapshot de insumos al completar lote | `batch_id`, `supply_id`, `cantidad_usada`, `costo_unitario_momento`, `nombre_insumo` |

## J.6 Reglas transaccionales críticas

1. Completar un lote debe validar stock, descontar insumos, actualizar inventario de productos y calcular costos en una sola transacción.
2. La entrada de insumo debe actualizar stock y registrar Kardex en la misma transacción.
3. La venta debe validar stock disponible, descontar inventario y registrar Kardex en la misma transacción.
4. La recepción de orden de compra debe generar entrada de inventario y actualizar el estado de la orden en la misma transacción.
5. La reserva de stock debe calcularse siempre sobre stock actual menos suma de reservas activas.
6. La merma debe descontar del inventario y registrar en Kardex de forma atómica.
7. El envío de alertas de correo no debe bloquear el flujo principal; se encola y procesa asíncronamente.
8. El backup de base de datos no debe interrumpir operaciones; se ejecuta en horario de baja actividad.
9. Toda acción de cambio de estado debe ser idempotente o rechazar repetición con el estado actual explícito.
10. El cálculo de costo de lote debe ejecutarse solo al completar y no puede modificarse posterior.

## J.7 Contrato de API

Formato común de respuesta exitosa:

```json
{
  "data": {},
  "meta": {
    "request_id": "REQ-TBD",
    "timestamp": "2026-06-24T00:00:00Z"
  }
}
```

Formato común de error:

```json
{
  "error": {
    "code": "validation_error",
    "message": "La solicitud contiene campos inválidos.",
    "details": [
      {
        "field": "cantidad",
        "issue": "must_be_greater_than_zero"
      }
    ]
  },
  "meta": {
    "request_id": "REQ-TBD"
  }
}
```

Códigos mínimos:

| codigo | uso |
|---|---|
| `validation_error` | input inválido |
| `permission_denied` | permiso insuficiente, HTTP 403 |
| `not_found` | recurso inexistente o inaccesible, HTTP 404 |
| `state_conflict` | acción no permitida por estado actual |
| `stock_unavailable` | stock insuficiente para la operación |
| `inactive_entity` | entidad inactiva no puede usarse |
| `duplicate_record` | unicidad violada |
| `auth_error` | credenciales inválidas o token expirado |

## J.8 Requisitos no funcionales

| id | requisito | criterio |
|---|---|---|
| RNF-01 | Seguridad | contraseñas con bcrypt, JWT expirable, RBAC por rol en cada endpoint |
| RNF-02 | Auditoría | 100% de cambios críticos con actor, fecha, entidad, acción e IP |
| RNF-03 | Rendimiento | listados paginados; API responde bajo 800 ms en consultas comunes con índices |
| RNF-04 | Integridad | transacciones en producción, ventas, compras e inventario |
| RNF-05 | Disponibilidad | jobs reintentables e idempotentes; notificaciones asíncronas |
| RNF-06 | Exportación | reportes exportables con CSV, XLSX y PDF según tipo |
| RNF-07 | Accesibilidad | interfaz responsive en móvil, tablet y escritorio |
| RNF-08 | Observabilidad | logs estructurados con request_id, user_id, módulo y latencia |
| RNF-09 | Privacidad | costos y datos financieros ocultos sin permiso explícito |
| RNF-10 | Mantenibilidad | Swagger/OpenAPI activo, migraciones versionadas con Alembic, tests por módulo |

## J.9 Criterios de aceptación por módulo

| módulo | aceptación mínima |
|---|---|
| Usuarios y auth | login, JWT, roles, CRUD usuarios y auditoría de accesos |
| Insumos | CRUD, Kardex trazable, alertas de stock bajo con correo e intervalo respetado |
| Recetas | CRUD, cálculo de costo, clonado y bloqueo si tiene lotes activos |
| Producción | crear lote, completar con descuento de insumos, calidad, merma y costo calculado |
| Inventario productos | stock actualizado al completar lote, precio editable, Kardex trazable |
| Ventas | registrar venta con stock validado, ganancia calculada y Kardex actualizado |
| Reservas | crear, liberar y convertir en venta con stock disponible correcto |
| Compras | orden, recepción parcial/total y entrada de inventario automática |
| Equipos | CRUD, historial de mantenimientos y alerta de revisión vencida |
| Finanzas | gastos operativos, reportes financieros básicos y metas mensuales |
| Dashboard | KPIs reales, gráficos y alertas operacionales descartables |
| Reportes | todos los tipos exportables con filtros de fecha y permisos aplicados |

## J.10 Estrategia de pruebas

Pruebas unitarias:

1. Validaciones V001 a V100.
2. Cálculo de costo de lote: insumos, mano de obra, energía, agua, merma e indirectos.
3. Cálculo de costo por litro y costo por unidad con costo de presentación.
4. Cálculo de stock disponible: stock actual menos reservas activas.
5. Lógica de disparo de alerta de stock: umbral, intervalo y stock en cero.
6. Transiciones de estado por módulo: lotes, órdenes de compra, reservas.
7. Cálculo de ganancia de venta por línea.

Pruebas de integración:

1. Entrada de insumo actualiza stock y registra Kardex.
2. Completar lote descuenta insumos, actualiza inventario de productos y calcula costo.
3. Venta descuenta inventario de productos y registra Kardex.
4. Recepción de orden de compra genera entrada de inventario y actualiza estado de orden.
5. Merma descuenta inventario y registra Kardex.
6. Alerta de stock bajo encola notificación y respeta intervalo de 24 horas.
7. Stock en cero fuerza alerta inmediata.
8. Worker de correos procesa reintentos y marca error definitivo tras 5 intentos.

Pruebas E2E:

1. Login, crear insumo, registrar entrada, verificar Kardex.
2. Crear receta, crear lote, completar lote, verificar inventario de productos.
3. Registrar venta, verificar stock descontado y Kardex de producto.
4. Crear orden de compra, recepcionar, verificar stock de insumo.
5. Reporte de producción exportado a XLSX con filtros de fecha.

## J.11 Trazabilidad macro

| requisito | fuente | prueba requerida | evidencia |
|---|---|---|---|
| REQ-INS | UC-INS-01..06 | unit + integración insumos | Kardex, stock, alertas, correos |
| REQ-REC | UC-REC-01..02 | unit recetas | ingredientes, costo, clonado |
| REQ-PROD | UC-PROD-01..04 | integración producción | lote, calidad, merma, costo |
| REQ-PRO | UC-PRO-01..02 | integración inventario productos | stock, precio, Kardex |
| REQ-VTA | UC-VTA-01..05 | integración ventas | cliente, venta, reserva, stock |
| REQ-COM | UC-COM-01..02 | integración compras | orden, recepción, inventario |
| REQ-EQU | UC-EQU-01..02 | unit equipos | historial, alertas revisión |
| REQ-FIN | UC-FIN-01..03 | integración finanzas | gastos, reportes, metas |
| REQ-REP | UC-REP-01..02 | E2E reportes | exportación, filtros, permisos |
| REQ-ALT | UC-ALT-01..03 | integración alertas | SMTP, cola, reintentos, metas |

## J.12 Ciclo de desarrollo por hitos

| hito | nombre | entregable principal |
|---|---|---|
| 1 | Fundamentos | Auth JWT, usuarios, roles, auditoría, estructura de proyecto |
| 2 | Maestros | Proveedores, insumos, bodegas, recetas, tipos de presentación |
| 3 | Inventario | Entradas de insumos, Kardex, notificaciones email, configuración SMTP |
| 4 | Producción | Lotes, control de calidad, mermas, inventario de productos terminados |
| 5 | Ventas | Clientes, ventas, reservas de stock, precios por tipo de cliente, órdenes de compra |
| 6 | Dashboard | KPIs reales, gráficos, alertas operacionales, reportes exportables |
| 7 | Cierre | Equipos, finanzas, metas, respaldos automáticos, documentación y pruebas |

## J.13 Registro de consumo y optimización

Política de consumo:

1. Modo de este desarrollo: local determinístico sin llamadas externas.
2. Si se usa API real en el futuro, se debe registrar consumo por fase y modelo.
3. Si falta tarifa oficial, el costo queda como no determinable; no se inventa precio.

Optimizaciones obligatorias:

1. Consultar Kardex con filtros de fecha e índices; nunca cargar tabla completa.
2. Alertas de correo asíncronas; no bloquean el flujo de registro de movimientos.
3. Dashboard calcula KPIs con agregaciones SQL; no itera en Python sobre colecciones grandes.
4. Reportes pesados se ejecutan como jobs con resultado en archivo; no en respuesta HTTP síncrona.
5. Stock disponible se calcula con una consulta que suma reservas activas; no en lógica de aplicación.
6. Exportaciones XLSX y PDF se generan en background y se notifican al usuario cuando están listas.
7. Índices obligatorios en: `supply_id + created_at` en movimientos, `status` en lotes, `cliente_id + fecha` en ventas.
8. Paginación obligatoria en todos los endpoints de listado.

## J.14 Riesgos y decisiones

| riesgo | impacto | mitigación |
|---|---|---|
| Stock concurrente en ventas | sobreventa | transacciones con lock por producto en venta y reserva |
| Correo SMTP no configurado | alertas silenciosas | validar config SMTP al iniciar y mostrar advertencia en dashboard |
| Costo de lote incorrecto | márgenes erróneos | validar todos los componentes antes de permitir completar lote |
| Receta modificada post-lote | inconsistencia histórica | bloquear edición si hay lotes activos; guardar snapshot en lote |
| Reportes de alto volumen | latencia alta | jobs diferidos con archivo exportado; límite de rango de fechas |
| Backups fallidos | pérdida de datos | registrar fallo en auditoría y notificar a admin por correo |

## J.15 Gate de cierre de especificación

La especificación queda lista cuando:

1. Los módulos MVP tienen casos de uso, pantallas, reglas, validaciones y endpoints.
2. El modelo de dominio cubre todas las entidades críticas con sus campos y relaciones.
3. Cada requisito macro tiene prueba requerida y evidencia esperada.
4. El plan de hitos de desarrollo está definido y es incremental.
5. Los riesgos principales están identificados con su mitigación.
6. No hay deploy, secretos, correo real ni integraciones externas ejecutadas sin aprobación.

---

# K. Enriquecimiento de ingeniería y trazabilidad

Esta sección complementa las secciones A a J sin reemplazarlas. Su propósito es convertir la especificación en una entrada verificable para diseño, implementación, pruebas y ejecución por una fábrica agéntica. Todo requisito existente se conserva; cuando se agrega un identificador nuevo, este actúa como alias formal y estable sobre el contenido ya definido.

## K.1 Convención de identificadores

| tipo | formato | fuente principal | regla de uso |
|---|---|---|---|
| Módulo | `MOD-###` | Alcance J.2 y secciones A/B/J | Agrupa funcionalidades, pantallas, APIs, reglas y entidades. |
| Caso de uso | `CU-###` | Casos `UC-*` de sección A | Alias formal del caso existente; el ID `UC-*` se mantiene como referencia histórica. |
| Funcionalidad | `FUN-###` | Alcance J.2, pantallas B, APIs F/J | Requisito funcional implementable y verificable. |
| Regla de negocio | `RN-###` | Reglas C.1 a C.60 | Alias formal de cada regla numerada en C. |
| Validación | `V###` | Validaciones D | Se mantiene la numeración `V001` a `V100`. |
| Pantalla | `SCR-###` | Pantallas P-01 a P-30 | Alias formal de cada pantalla. |
| API | `API-###` | Endpoints F y K.6 | Alias formal de cada endpoint REST. |
| Entidad | `ENT-###` | Modelo canónico J.5 | Alias formal de cada tabla o agregado persistente. |
| Criterio de aceptación | `CA-###` | Funcionalidades K.5 | Condición objetiva para validar una funcionalidad. |

## K.2 Catálogo de módulos

| ID | Módulo | Alcance funcional | Casos de uso | Pantallas | Entidades principales |
|---|---|---|---|---|---|
| MOD-001 | Seguridad, usuarios y auditoría | Autenticación, recuperación, roles, permisos, usuarios, auditoría | CU-001, CU-029, CU-031 | SCR-001, SCR-002, SCR-030 | ENT-001..ENT-006, ENT-038 |
| MOD-002 | Proveedores | Alta, edición, activación e inactivación de proveedores | CU-006 | SCR-008, SCR-009 | ENT-007 |
| MOD-003 | Insumos, bodegas y Kardex | Insumos, entradas, bodegas, stock, movimientos y alertas | CU-002..CU-005 | SCR-004..SCR-007, SCR-012 | ENT-008..ENT-014 |
| MOD-004 | Recetas | Recetas, ingredientes, costos estimados y clonado | CU-007, CU-008 | SCR-010, SCR-011 | ENT-015..ENT-019 |
| MOD-005 | Producción y calidad | Lotes, cierre de producción, costos, control de calidad | CU-009..CU-011 | SCR-014..SCR-017 | ENT-017..ENT-020, ENT-022, ENT-040 |
| MOD-006 | Mermas | Registro de pérdidas de insumo o producto, descuento y KPI | CU-012 | SCR-019 | ENT-021 |
| MOD-007 | Inventario de productos terminados | Stock de producto, precio, Kardex y disponibilidad | CU-013, CU-014 | SCR-018 | ENT-022, ENT-023, ENT-026 |
| MOD-008 | Ventas, clientes y reservas | Clientes, ventas, anulación, reservas y precios por tipo de cliente | CU-015..CU-019 | SCR-020..SCR-023 | ENT-024..ENT-029 |
| MOD-009 | Compras | Órdenes de compra, envío, recepción parcial o total | CU-020, CU-021 | SCR-024..SCR-026 | ENT-030, ENT-031 |
| MOD-010 | Equipos y mantenimiento | Equipos, estados, historial, revisión y movimientos | CU-022, CU-023 | SCR-027 | ENT-032..ENT-034 |
| MOD-011 | Finanzas operativas | Gastos, metas mensuales y reportes financieros básicos | CU-024..CU-026, CU-030 | SCR-028, SCR-030 | ENT-035..ENT-037 |
| MOD-012 | Dashboard y reportes | KPIs, alertas operacionales, reportes y exportación | CU-027, CU-028 | SCR-003, SCR-029 | ENT-005, ENT-039, ENT-041 |
| MOD-013 | Configuración y alertas | SMTP, cola de notificaciones, metas desde configuración y jobs | CU-003, CU-029, CU-030 | SCR-030 | ENT-013, ENT-014, ENT-037, ENT-039 |

## K.2.1 Catálogo de entidades

| ENT | Entidad o agregado | Fuente | Módulos principales |
|---|---|---|---|
| ENT-001 | `users` | J.5 Usuarios y seguridad | MOD-001 |
| ENT-002 | `roles` | J.5 Usuarios y seguridad | MOD-001 |
| ENT-003 | `permissions` | J.5 Usuarios y seguridad | MOD-001 |
| ENT-004 | `role_permissions` | J.5 Usuarios y seguridad | MOD-001 |
| ENT-005 | `audit_logs` | J.5 Usuarios y seguridad | MOD-001, MOD-012 |
| ENT-006 | `settings` | J.5 Usuarios y seguridad | MOD-001, MOD-013 |
| ENT-007 | `suppliers` | J.5 Insumos y proveedores | MOD-002, MOD-009 |
| ENT-008 | `warehouses` | J.5 Insumos y proveedores | MOD-003 |
| ENT-009 | `supply_categories` | J.5 Insumos y proveedores | MOD-003 |
| ENT-010 | `supplies` | J.5 Insumos y proveedores | MOD-003 |
| ENT-011 | `supply_movements` | J.5 Insumos y proveedores | MOD-003 |
| ENT-012 | `supply_entries` | J.5 Insumos y proveedores | MOD-003, MOD-009 |
| ENT-013 | `notification_queue` | J.5 Insumos y proveedores | MOD-003, MOD-013 |
| ENT-014 | `smtp_config` | J.5 Compras, equipos y finanzas | MOD-013 |
| ENT-015 | `beer_styles` | J.5 Recetas y producción | MOD-004 |
| ENT-016 | `presentation_types` | J.5 Recetas y producción | MOD-004, MOD-005 |
| ENT-017 | `recipes` | J.5 Recetas y producción | MOD-004 |
| ENT-018 | `recipe_ingredients` | J.5 Recetas y producción | MOD-004 |
| ENT-019 | `production_batches` | J.5 Recetas y producción | MOD-005 |
| ENT-020 | `batch_quality_checks` | J.5 Recetas y producción | MOD-005 |
| ENT-021 | `waste_records` | J.5 Recetas y producción | MOD-006 |
| ENT-022 | `finished_products` | J.5 Inventario de productos y ventas | MOD-005, MOD-007 |
| ENT-023 | `product_movements` | J.5 Inventario de productos y ventas | MOD-007, MOD-008 |
| ENT-024 | `customer_types` | J.5 Inventario de productos y ventas | MOD-008 |
| ENT-025 | `customers` | J.5 Inventario de productos y ventas | MOD-008 |
| ENT-026 | `product_prices` | J.5 Inventario de productos y ventas | MOD-007, MOD-008 |
| ENT-027 | `sales` | J.5 Inventario de productos y ventas | MOD-008 |
| ENT-028 | `sale_items` | J.5 Inventario de productos y ventas | MOD-008 |
| ENT-029 | `stock_reservations` | J.5 Inventario de productos y ventas | MOD-008 |
| ENT-030 | `purchase_orders` | J.5 Compras, equipos y finanzas | MOD-009 |
| ENT-031 | `purchase_order_items` | J.5 Compras, equipos y finanzas | MOD-009 |
| ENT-032 | `equipment_types` | J.5 Compras, equipos y finanzas | MOD-010 |
| ENT-033 | `equipment` | J.5 Compras, equipos y finanzas | MOD-010 |
| ENT-034 | `equipment_movements` | J.5 Compras, equipos y finanzas | MOD-010 |
| ENT-035 | `expense_categories` | J.5 Compras, equipos y finanzas | MOD-011 |
| ENT-036 | `operational_expenses` | J.5 Compras, equipos y finanzas | MOD-011 |
| ENT-037 | `monthly_goals` | J.5 Compras, equipos y finanzas | MOD-011, MOD-013 |
| ENT-038 | `password_reset_tokens` | J.5 Compras, equipos y finanzas | MOD-001 |
| ENT-039 | `export_jobs` | J.5 Compras, equipos y finanzas | MOD-012 |
| ENT-040 | `batch_supply_snapshots` | J.5 Compras, equipos y finanzas | MOD-005 |
| ENT-041 | Vista o agregado de dashboard | J.4/J.13 | MOD-012 |

## K.3 Catálogo formal de actores y RBAC

| ID | Actor | Responsabilidades | Módulos accesibles | Permisos mínimos | Restricciones |
|---|---|---|---|---|---|
| ACT-001 | Administrador | Configurar sistema, gestionar usuarios, roles, permisos, SMTP, metas y auditoría | Todos | Todos los permisos H, incluyendo `admin.users`, `admin.settings`, `audit.read` | No debe operar sin auditoría en cambios críticos. |
| ACT-002 | Responsable de compras | Gestionar proveedores, insumos, entradas y órdenes de compra | MOD-002, MOD-003, MOD-009 | `suppliers.*`, `supplies.*`, `supply-entries.create`, `purchase-orders.*` | No puede administrar usuarios ni ver datos financieros sin permiso. |
| ACT-003 | Jefe de producción | Gestionar recetas, lotes, calidad, equipos y mermas | MOD-004, MOD-005, MOD-006, MOD-010 | `recipes.*`, `batches.*`, `waste.*`, `equipment.*` | No puede saltar reglas de stock salvo política explícita. |
| ACT-004 | Operario de producción | Registrar operaciones asignadas de producción, calidad y mantenimiento | MOD-005, MOD-010 | `batches.read`, `batches.create`, `batches.quality-check`, `equipment.movement` | No puede editar costos, usuarios ni configuración. |
| ACT-005 | Responsable de ventas | Gestionar clientes, ventas, reservas e inventario visible | MOD-007, MOD-008, MOD-012 | `products.read`, `sales.*`, `customers.*`, `reservations.*`, `reports.read` | Costos y márgenes se ocultan sin permiso financiero. |
| ACT-006 | Responsable de finanzas | Registrar gastos, revisar reportes financieros, metas y márgenes | MOD-011, MOD-012 | `expenses.*`, `reports.*`, `products.read`, `sales.read` | No puede modificar producción ni compras sin permiso adicional. |
| ACT-007 | Auditor | Consultar auditoría, reportes y evidencia operativa | MOD-001, MOD-012 | `audit.read`, `reports.read`, `reports.export` | Acceso preferentemente de solo lectura. |
| ACT-008 | Worker del sistema | Ejecutar alertas, reintentos, vencimientos y jobs diferidos | MOD-003, MOD-008, MOD-012, MOD-013 | Permisos internos acotados por job | No inicia sesiones humanas ni omite trazas. |

## K.4 Catálogo formal de casos de uso

Los flujos paso a paso de la sección A siguen siendo la fuente primaria. La tabla siguiente agrega objetivo, disparador, precondiciones, postcondiciones y trazabilidad exigida.

| CU | Caso fuente | Nombre | Actor principal | Actores secundarios | Objetivo y descripción | Disparador y precondiciones | Flujo principal | Alternos y excepciones | Postcondiciones | Trazabilidad |
|---|---|---|---|---|---|---|---|---|---|---|
| CU-001 | UC-ALT-03 | Gestionar usuarios y roles | ACT-001 | ACT-007 | Crear o modificar usuarios con rol activo y auditoría. | Admin autenticado, rol existente, correo no duplicado. | Ver UC-ALT-03. | Rol ausente, correo duplicado, contraseña débil. | Usuario activo/inactivo persistido y auditado. | FUN-003, FUN-004, RN-001..RN-010, API-005..API-009, SCR-030, MOD-001 |
| CU-002 | UC-INS-01 | Registrar insumo | ACT-002 | ACT-001 | Crear insumo activo con costos, unidad, proveedor, bodega y umbrales. | Usuario con `supplies.create`; proveedor/bodega válidos. | Ver UC-INS-01. | Código duplicado, campos obligatorios, costo negativo. | Insumo activo disponible para compras, recetas y stock. | FUN-007, RN-011..RN-016, V025..V033, API-015, SCR-005, MOD-003 |
| CU-003 | UC-INS-02 | Registrar entrada de insumo | ACT-002 | ACT-008 | Incrementar stock, registrar Kardex y evaluar alerta. | Insumo activo, cantidad mayor a cero, costo válido. | Ver UC-INS-02. | Insumo inactivo, costo negativo, cantidad inválida. | Stock actualizado, movimiento ENTRADA y auditoría. | FUN-009, FUN-010, RN-017..RN-024, API-021, SCR-007, MOD-003 |
| CU-004 | UC-INS-03 | Gestionar alertas de stock bajo | ACT-008 | ACT-001, ACT-002 | Encolar y enviar alertas según umbral, intervalo y reintentos. | Movimiento de inventario o job programado; SMTP configurado. | Ver UC-INS-03. | Stock cero, intervalo 24h, quinto fallo definitivo. | Notificación registrada en cola con estado trazable. | FUN-011, FUN-035, RN-020..RN-024, API-020, API-083, SCR-030, MOD-013 |
| CU-005 | UC-INS-04 / UC-INS-05 | Editar o inactivar insumo | ACT-002 | ACT-001 | Mantener datos permitidos o inactivar insumos sin romper historial. | Insumo existente, no eliminado, reglas de uso satisfechas. | Ver UC-INS-04 y UC-INS-05. | Unidad bloqueada con movimientos, receta activa impide inactivación. | Insumo actualizado o inactivo con auditoría. | FUN-008, RN-012, RN-016, API-017, API-018, SCR-004, SCR-005, MOD-003 |
| CU-006 | UC-INS-06 | Registrar proveedor | ACT-002 | ACT-001 | Crear proveedor activo para compras e insumos. | Código único, datos obligatorios y correo válido si existe. | Ver UC-INS-06. | Código duplicado, correo inválido. | Proveedor activo y auditado. | FUN-005, FUN-006, RN-050, V040..V044, API-010..API-013, SCR-008, SCR-009, MOD-002 |
| CU-007 | UC-REC-01 | Crear receta | ACT-003 | ACT-001 | Crear receta con ingredientes activos y costo estimado. | Insumos activos disponibles; usuario con `recipes.create`. | Ver UC-REC-01. | Sin ingredientes, insumo inactivo, receta duplicada. | Receta activa con ingredientes y costo calculado. | FUN-014, RN-025..RN-027, RN-042, V045..V052, API-023..API-026, SCR-011, MOD-004 |
| CU-008 | UC-REC-02 | Clonar receta | ACT-003 | ACT-001 | Crear versión derivada en prueba conservando ingredientes. | Receta activa o en prueba, permiso `recipes.clone`. | Ver UC-REC-02. | Receta inactiva, datos inválidos al ajustar. | Receta clonada en estado `en_prueba`. | FUN-015, RN-028, API-027, SCR-010, SCR-011, MOD-004 |
| CU-009 | UC-PROD-01 | Crear lote de producción | ACT-003 | ACT-004 | Abrir lote en elaboración desde receta y presentación activas. | Receta activa, presentación válida, responsable definido. | Ver UC-PROD-01. | Sin receta activa, stock insuficiente con política configurable. | Lote creado en `en_elaboracion`. | FUN-016, RN-029, V055..V060, API-028..API-031, SCR-014, SCR-015, MOD-005 |
| CU-010 | UC-PROD-02 | Completar lote | ACT-003 | ACT-004, ACT-008 | Descontar insumos, actualizar productos, calcular costos y registrar trazas en una transacción. | Lote en elaboración, stock suficiente o excepción aprobada. | Ver UC-PROD-02. | Stock insuficiente, costo negativo, repetición idempotente. | Lote completado, inventario/Kardex/costos consistentes. | FUN-017, RN-030..RN-035, J.6.1, API-032, SCR-015, SCR-016, MOD-005 |
| CU-011 | UC-PROD-03 | Registrar control de calidad | ACT-003 | ACT-004 | Registrar mediciones y resultado aprobado/rechazado. | Lote completado, sin control previo. | Ver UC-PROD-03. | Resultado rechazado exige motivo; solo un registro por lote. | Registro de calidad asociado al lote. | FUN-018, RN-036..RN-038, V069..V074, API-034, SCR-017, MOD-005 |
| CU-012 | UC-PROD-04 | Registrar merma | ACT-003 | ACT-006 | Descontar pérdida de insumo/producto, calcular costo y registrar Kardex. | Stock disponible y motivo detallado. | Ver UC-PROD-04. | Cantidad mayor a stock, motivo ausente. | Merma persistida, inventario descontado y KPI actualizado. | FUN-019, RN-039..RN-041, V075..V078, API-062, API-063, SCR-019, MOD-006 |
| CU-013 | UC-PRO-01 | Consultar inventario de productos | ACT-005 | ACT-006 | Consultar stock, costo, precio y Kardex de productos. | Usuario con `products.read`; filtros válidos. | Ver UC-PRO-01. | Costos ocultos sin permiso. | Listado/detalle entregado con disponibilidad correcta. | FUN-020, FUN-021, RN-047, API-035, API-047, SCR-018, MOD-007 |
| CU-014 | UC-PRO-02 | Actualizar precio de venta | ACT-005 | ACT-006 | Mantener precio base con advertencia si queda bajo costo. | Producto activo y permiso `products.update-price`. | Ver UC-PRO-02. | Precio negativo, permiso insuficiente. | Precio actualizado y auditado. | FUN-021, RN-046, V087, API-036, SCR-018, MOD-007 |
| CU-015 | UC-VTA-01 | Registrar cliente | ACT-005 | ACT-001 | Crear cliente activo con identificador único y condiciones comerciales. | Usuario con `customers.create`. | Ver UC-VTA-01. | Identificador duplicado, correo inválido. | Cliente activo y auditado. | FUN-022, RN-043..RN-045, V079..V083, API-039, API-040, SCR-021, MOD-008 |
| CU-016 | UC-VTA-02 | Registrar venta | ACT-005 | ACT-006 | Confirmar venta con stock validado, ganancia y Kardex. | Productos activos, stock disponible libre, cliente activo si aplica. | Ver UC-VTA-02. | Stock insuficiente, cliente inactivo, precio cero advertido. | Venta completada, inventario descontado y auditoría. | FUN-024, RN-046..RN-048, V084..V089, API-037, API-038, SCR-022, MOD-008 |
| CU-017 | UC-VTA-03 | Gestionar reservas de stock | ACT-005 | ACT-008 | Crear, liberar o consumir reservas sobre stock libre. | Cliente/producto activos y stock libre suficiente. | Ver UC-VTA-03. | Reserva vencida, cantidad excede stock libre. | Reserva activa, liberada, consumida o vencida. | FUN-026, RN-047, RN-049, V090..V092, API-051..API-054, SCR-023, MOD-008 |
| CU-018 | UC-VTA-04 | Editar cliente | ACT-005 | ACT-001 | Mantener datos comerciales sin romper historial. | Cliente existente no eliminado. | Ver UC-VTA-04. | Identificador bloqueado con ventas, cliente eliminado. | Cliente actualizado y auditado. | FUN-023, RN-043..RN-045, API-048..API-050, SCR-020, SCR-021, MOD-008 |
| CU-019 | UC-VTA-05 | Anular venta | ACT-005 | ACT-001, ACT-006 | Revertir una venta confirmada bajo reglas de plazo y permiso. | Venta completada, motivo informado. | Ver UC-VTA-05. | Venta antigua requiere permiso; reservas asociadas deben liberarse. | Stock revertido, Kardex DEVOLUCION y venta anulada. | FUN-025, RN-003, RN-004, RN-048, API-038, API-087, SCR-022, MOD-008 |
| CU-020 | UC-COM-01 | Crear orden de compra | ACT-002 | ACT-001 | Crear, editar en borrador y enviar orden a proveedor activo. | Proveedor activo, líneas válidas. | Ver UC-COM-01. | Precio negativo, cantidad inválida, proveedor inactivo. | Orden en borrador o enviada. | FUN-027, RN-050, RN-051, V093..V097, API-055..API-059, SCR-024, SCR-025, MOD-009 |
| CU-021 | UC-COM-02 | Recepcionar compra | ACT-002 | ACT-008 | Recibir parcial o total, generar entrada de insumo y actualizar orden. | Orden enviada o parcialmente recibida. | Ver UC-COM-02. | Cantidad excede pendiente sin tolerancia, orden cancelada. | Stock incrementado, Kardex ENTRADA y orden actualizada. | FUN-028, RN-052..RN-054, V098, API-060, SCR-026, MOD-009 |
| CU-022 | UC-EQU-01 | Registrar equipo | ACT-003 | ACT-001 | Crear equipo operativo con código único y datos técnicos. | Código no usado, costo válido. | Ver UC-EQU-01. | Código duplicado, costo negativo. | Equipo operativo persistido. | FUN-029, RN-055, V099, API-064..API-067, SCR-027, MOD-010 |
| CU-023 | UC-EQU-02 | Registrar mantenimiento | ACT-003 | ACT-004 | Agregar movimiento de equipo y recalcular próxima revisión. | Equipo no descartado, fecha válida. | Ver UC-EQU-02. | Equipo descartado, próxima revisión vencida alerta. | Historial actualizado, alertas disponibles. | FUN-030, RN-056, RN-057, API-068, API-069, SCR-027, MOD-010 |
| CU-024 | UC-FIN-01 | Registrar gasto operativo | ACT-006 | ACT-001 | Crear gasto operativo para reportes financieros. | Categoría y monto mayor a cero. | Ver UC-FIN-01. | Sin categoría, monto inválido, documento asociado bloquea eliminación. | Gasto guardado y reportes actualizables. | FUN-031, RN-058, RN-059, V100, API-070..API-073, SCR-028, MOD-011 |
| CU-025 | UC-FIN-02 | Consultar reportes financieros | ACT-006 | ACT-007 | Calcular reportes financieros con filtros y permisos. | Rango de fechas válido y permiso financiero. | Ver UC-FIN-02. | Datos sensibles ocultos; exportación auditada. | Reporte mostrado o exportado con auditoría. | FUN-032, FUN-034, RN-060, API-075, API-076, SCR-029, MOD-011 |
| CU-026 | UC-FIN-03 | Gestionar metas mensuales | ACT-006 | ACT-001 | Definir metas operativas para comparar contra dashboard. | Mes/año objetivo válido, permiso admin para modificar. | Ver UC-FIN-03. | Campo de meta vacío no bloquea el resto. | Metas persistidas y visibles en dashboard. | FUN-036, API-080, API-081, SCR-030, MOD-011 |
| CU-027 | UC-REP-01 | Ver dashboard general | ACT-001..ACT-007 | ACT-008 | Visualizar KPIs reales según rol, permisos y filtros. | Usuario autenticado, permisos de lectura. | Ver UC-REP-01. | KPIs financieros ocultos, sin datos muestra cero. | Dashboard consistente con filtros y permisos. | FUN-033, RN-041, RN-057, API-074, SCR-003, MOD-012 |
| CU-028 | UC-REP-02 | Exportar reporte | ACT-006 | ACT-007, ACT-008 | Generar reportes filtrados en CSV/XLSX/PDF y auditar exportación. | Filtros válidos, permiso `reports.export`. | Ver UC-REP-02. | Auditoría solo admin/auditor; rango amplio diferido. | Export job o archivo generado con registro. | FUN-034, RN-003, RN-060, API-076, API-082, SCR-029, MOD-012 |
| CU-029 | UC-ALT-01 | Configurar alertas por correo | ACT-001 | ACT-008 | Guardar SMTP cifrado y validar envío de prueba. | Admin autenticado, parámetros completos. | Ver UC-ALT-01. | Credenciales no visibles; error SMTP no bloquea operación no relacionada. | Configuración cifrada y prueba registrada. | FUN-035, RN-006, RN-020..RN-024, API-077..API-079, SCR-030, MOD-013 |
| CU-030 | UC-ALT-02 | Configurar metas desde panel de alertas | ACT-001 | ACT-006 | Acceder a metas mensuales desde configuración. No duplica CU-026; es una ruta de administración sobre el mismo concepto. | Admin autenticado. | Ver UC-ALT-02. | Meta sin dato no bloquea el resto. | Misma entidad `monthly_goals` actualizada. | FUN-036, API-080, API-081, SCR-030, MOD-013 |
| CU-031 | P-02 / J.2 | Recuperar contraseña | ACT-001..ACT-007 | ACT-008 | Solicitar y confirmar restablecimiento de contraseña con token seguro. | Correo válido, usuario activo, token no expirado. | Pantalla P-02 solicita enlace; API confirma token y nueva contraseña. | Correo inexistente no filtra información; token usado o expirado se rechaza. | Token usado, contraseña cifrada y auditoría. | FUN-002, RN-006, RN-007, V017..V024, API-085, API-086, SCR-002, MOD-001 |

## K.5 Catálogo completo de funcionalidades y criterios de aceptación

| FUN | Nombre | Módulo | Prioridad | CU relacionados | APIs relacionadas | Reglas relacionadas | Criterio de aceptación verificable |
|---|---|---|---|---|---|---|---|
| FUN-001 | Autenticar usuario | MOD-001 | Alta | CU-001 | API-001..API-004 | RN-002, RN-006..RN-010 | CA-001: Dado un usuario activo, cuando envía credenciales válidas, entonces recibe JWT; credenciales inválidas o usuario inactivo retornan 401. |
| FUN-002 | Recuperar contraseña | MOD-001 | Alta | CU-031 | API-085, API-086 | RN-006, RN-007 | CA-002: Dado un token válido no usado, cuando confirma nueva contraseña válida, entonces se almacena hash y el token queda usado. |
| FUN-003 | Gestionar usuarios, roles y permisos | MOD-001 | Alta | CU-001 | API-005..API-009 | RN-001..RN-010 | CA-003: Solo admin crea/edita usuarios; todo usuario activo queda con rol activo y correo único. |
| FUN-004 | Registrar auditoría funcional | MOD-001 | Alta | CU-001, CU-019, CU-028 | API-082 | RN-003, RN-004, RN-060 | CA-004: Todo cambio crítico y exportación registra usuario, fecha, entidad, acción e IP. |
| FUN-005 | Registrar proveedor | MOD-002 | Alta | CU-006 | API-010, API-011 | RN-050 | CA-005: Proveedor con código único y correo válido se guarda activo; duplicado o correo inválido se rechaza. |
| FUN-006 | Editar o inactivar proveedor | MOD-002 | Media | CU-006 | API-012, API-013 | RN-004, RN-050 | CA-006: Un proveedor inactivo no puede usarse en nuevas órdenes y el cambio queda auditado. |
| FUN-007 | Registrar insumo | MOD-003 | Alta | CU-002 | API-014..API-016 | RN-011..RN-016 | CA-007: Insumo con código único, unidad y costos válidos queda activo y disponible para Kardex. |
| FUN-008 | Editar o inactivar insumo | MOD-003 | Alta | CU-005 | API-017, API-018 | RN-012, RN-016 | CA-008: No se cambia unidad si hay movimientos ni se inactiva si está en receta activa. |
| FUN-009 | Registrar entrada de insumo | MOD-003 | Alta | CU-003, CU-021 | API-021, API-022 | RN-017..RN-019 | CA-009: Entrada válida incrementa stock y crea movimiento Kardex en la misma transacción. |
| FUN-010 | Consultar Kardex de insumo | MOD-003 | Alta | CU-003, CU-013 | API-019 | RN-017, RN-018 | CA-010: Kardex responde por rango de fechas con saldo resultante y sin cargar tabla completa. |
| FUN-011 | Gestionar alertas de stock bajo | MOD-003/MOD-013 | Alta | CU-004 | API-020, API-083 | RN-020..RN-024 | CA-011: Stock bajo encola notificación; stock cero ignora intervalo; quinto fallo queda en error definitivo. |
| FUN-012 | Gestionar bodegas | MOD-003 | Media | CU-002, CU-003 | API-041..API-043 | RN-001, RN-003 | CA-012: Bodega activa puede asociarse a insumos y entradas; cambios críticos quedan auditados. |
| FUN-013 | Gestionar tipos de presentación | MOD-004/MOD-005 | Media | CU-009, CU-010 | API-044..API-046 | RN-034 | CA-013: Presentación activa con volumen y costo válido puede usarse en lotes y costo por unidad. |
| FUN-014 | Crear receta | MOD-004 | Alta | CU-007 | API-023..API-026 | RN-025..RN-027, RN-042 | CA-014: Receta con al menos un ingrediente activo calcula costo estimado y queda activa. |
| FUN-015 | Clonar o versionar receta | MOD-004 | Media | CU-008 | API-027 | RN-028 | CA-015: Clonado desde receta activa/en prueba genera nueva receta `en_prueba` con ingredientes heredados. |
| FUN-016 | Crear lote de producción | MOD-005 | Alta | CU-009 | API-028..API-031 | RN-029 | CA-016: Lote creado desde receta activa queda `en_elaboracion` con número único. |
| FUN-017 | Completar lote y calcular costo | MOD-005 | Alta | CU-010 | API-032 | RN-030..RN-035 | CA-017: Completar lote valida stock, descuenta insumos, actualiza producto y calcula costos en una transacción. |
| FUN-018 | Registrar control de calidad | MOD-005 | Alta | CU-011 | API-034 | RN-036..RN-038 | CA-018: Un solo control por lote registra resultado; rechazo exige motivo. |
| FUN-019 | Registrar merma | MOD-006 | Alta | CU-012 | API-062, API-063 | RN-039..RN-041 | CA-019: Merma válida descuenta inventario, registra Kardex y actualiza KPI sin permitir stock negativo. |
| FUN-020 | Consultar inventario de productos | MOD-007 | Alta | CU-013 | API-035, API-047 | RN-047 | CA-020: Listado muestra stock actual, costo visible según permiso y precio de venta. |
| FUN-021 | Actualizar precio y Kardex de producto | MOD-007 | Alta | CU-013, CU-014 | API-036, API-047 | RN-046, RN-047 | CA-021: Precio negativo se rechaza; precio bajo costo advierte y audita. |
| FUN-022 | Registrar cliente | MOD-008 | Alta | CU-015 | API-039, API-040 | RN-043..RN-045 | CA-022: Cliente con identificador fiscal único queda activo; duplicado se rechaza. |
| FUN-023 | Editar o inactivar cliente | MOD-008 | Media | CU-018 | API-048..API-050 | RN-044, RN-045 | CA-023: Cliente con ventas no se elimina físicamente ni cambia identificador fiscal sin regla explícita. |
| FUN-024 | Registrar venta | MOD-008 | Alta | CU-016 | API-037, API-038 | RN-046..RN-048 | CA-024: Venta confirmada valida stock libre, descuenta producto, calcula ganancia y registra Kardex. |
| FUN-025 | Anular venta | MOD-008 | Alta | CU-019 | API-087 | RN-003, RN-004, RN-048 | CA-025: Venta anulada revierte stock, crea Kardex DEVOLUCION, exige motivo y respeta permiso por antigüedad. |
| FUN-026 | Gestionar reservas | MOD-008 | Alta | CU-017 | API-051..API-054 | RN-047, RN-049 | CA-026: Reserva solo usa stock libre; liberar/consumir cambia estado sin doble consumo. |
| FUN-027 | Crear y enviar orden de compra | MOD-009 | Alta | CU-020 | API-055..API-059 | RN-050, RN-051 | CA-027: Orden con proveedor activo y líneas válidas puede pasar de borrador a enviada. |
| FUN-028 | Recepcionar compra | MOD-009 | Alta | CU-021 | API-060, API-061 | RN-052..RN-054 | CA-028: Recepción parcial/total genera entrada de insumo y actualiza estado en una transacción. |
| FUN-029 | Registrar equipo | MOD-010 | Media | CU-022 | API-064..API-067 | RN-055 | CA-029: Equipo con código único y costo no negativo queda operativo. |
| FUN-030 | Registrar mantenimiento | MOD-010 | Media | CU-023 | API-068, API-069 | RN-056, RN-057 | CA-030: Equipo no descartado acepta movimiento y recalcula próxima revisión; vencida genera alerta. |
| FUN-031 | Registrar gasto operativo | MOD-011 | Alta | CU-024 | API-070..API-073 | RN-058, RN-059 | CA-031: Gasto con monto positivo y categoría se guarda; con documentos asociados no se elimina. |
| FUN-032 | Consultar reportes financieros | MOD-011 | Alta | CU-025 | API-075 | RN-060 | CA-032: Reporte financiero aplica permisos; usuario sin permiso no ve datos sensibles. |
| FUN-033 | Ver dashboard general | MOD-012 | Alta | CU-027 | API-074 | RN-041, RN-057 | CA-033: Dashboard muestra KPIs reales según rol; sin datos presenta cero y no error. |
| FUN-034 | Exportar reportes | MOD-012 | Alta | CU-025, CU-028 | API-076, API-082 | RN-003, RN-060 | CA-034: Exportación CSV/XLSX/PDF respeta filtros, permisos y deja registro en auditoría. |
| FUN-035 | Configurar SMTP y cola de notificaciones | MOD-013 | Alta | CU-004, CU-029 | API-077..API-079, API-083 | RN-006, RN-020..RN-024 | CA-035: Configuración SMTP se cifra; prueba registra resultado; cola reintenta y marca fallos. |
| FUN-036 | Gestionar metas mensuales | MOD-011/MOD-013 | Media | CU-026, CU-030 | API-080, API-081 | RN-003 | CA-036: Admin actualiza metas por mes; dashboard refleja progreso contra metas guardadas. |
| FUN-037 | Ejecutar jobs operativos | MOD-013 | Media | CU-004, CU-017, CU-028 | API-083, API-076 | RN-021..RN-024, J.6.7, J.6.8 | CA-037: Jobs son idempotentes, trazables y no bloquean la operación principal. |
| FUN-038 | Aplicar RBAC por endpoint | MOD-001 | Alta | Todos | API-001..API-087 | RN-008..RN-010 | CA-038: Toda llamada protegida valida JWT, usuario activo y permiso; permiso insuficiente retorna 403 sin datos parciales. |

## K.6 Catálogo API normalizado y cierre de cobertura

La sección F define un catálogo base de 40 endpoints. Para que el alcance cerrado de J.2 quede implementable sin módulos huérfanos, se agregan endpoints complementarios derivados de funcionalidades ya existentes en A, B, H y J. No agregan módulos nuevos; cierran brechas de cobertura.

| API | Método y ruta | Funcionalidad | Pantalla/CU |
|---|---|---|---|
| API-001..API-040 | Endpoints base definidos en F.1 a F.40 | FUN-001, FUN-003, FUN-005..FUN-024 | Ver sección F y K.4 |
| API-041 | `GET /api/v1/warehouses` | FUN-012 | SCR-012 |
| API-042 | `POST /api/v1/warehouses` | FUN-012 | SCR-012 |
| API-043 | `PUT /api/v1/warehouses/{id}` | FUN-012 | SCR-012 |
| API-044 | `GET /api/v1/presentation-types` | FUN-013 | SCR-013, SCR-015 |
| API-045 | `POST /api/v1/presentation-types` | FUN-013 | SCR-013 |
| API-046 | `PUT /api/v1/presentation-types/{id}` | FUN-013 | SCR-013 |
| API-047 | `GET /api/v1/products/{id}/kardex` | FUN-020, FUN-021 | SCR-018 |
| API-048 | `GET /api/v1/customers/{id}` | FUN-022, FUN-023 | SCR-020, SCR-021 |
| API-049 | `PUT /api/v1/customers/{id}` | FUN-023 | SCR-021 |
| API-050 | `PATCH /api/v1/customers/{id}/toggle-status` | FUN-023 | SCR-020 |
| API-051 | `GET /api/v1/reservations` | FUN-026 | SCR-023 |
| API-052 | `POST /api/v1/reservations` | FUN-026 | SCR-023 |
| API-053 | `POST /api/v1/reservations/{id}/consume` | FUN-026 | SCR-023 |
| API-054 | `POST /api/v1/reservations/{id}/release` | FUN-026 | SCR-023 |
| API-055 | `GET /api/v1/purchase-orders` | FUN-027 | SCR-024 |
| API-056 | `POST /api/v1/purchase-orders` | FUN-027 | SCR-025 |
| API-057 | `GET /api/v1/purchase-orders/{id}` | FUN-027 | SCR-024, SCR-025 |
| API-058 | `PUT /api/v1/purchase-orders/{id}` | FUN-027 | SCR-025 |
| API-059 | `POST /api/v1/purchase-orders/{id}/send` | FUN-027 | SCR-024, SCR-025 |
| API-060 | `POST /api/v1/purchase-orders/{id}/receive` | FUN-028 | SCR-026 |
| API-061 | `POST /api/v1/purchase-orders/{id}/cancel` | FUN-027 | SCR-024 |
| API-062 | `GET /api/v1/waste-records` | FUN-019 | SCR-019 |
| API-063 | `POST /api/v1/waste-records` | FUN-019 | SCR-019 |
| API-064 | `GET /api/v1/equipment` | FUN-029, FUN-030 | SCR-027 |
| API-065 | `POST /api/v1/equipment` | FUN-029 | SCR-027 |
| API-066 | `GET /api/v1/equipment/{id}` | FUN-029, FUN-030 | SCR-027 |
| API-067 | `PUT /api/v1/equipment/{id}` | FUN-029 | SCR-027 |
| API-068 | `POST /api/v1/equipment/{id}/movements` | FUN-030 | SCR-027 |
| API-069 | `GET /api/v1/equipment/{id}/movements` | FUN-030 | SCR-027 |
| API-070 | `GET /api/v1/expenses` | FUN-031 | SCR-028 |
| API-071 | `POST /api/v1/expenses` | FUN-031 | SCR-028 |
| API-072 | `PUT /api/v1/expenses/{id}` | FUN-031 | SCR-028 |
| API-073 | `DELETE /api/v1/expenses/{id}` | FUN-031 | SCR-028 |
| API-074 | `GET /api/v1/dashboard` | FUN-033 | SCR-003 |
| API-075 | `GET /api/v1/reports` | FUN-032, FUN-034 | SCR-029 |
| API-076 | `POST /api/v1/reports/export` | FUN-034 | SCR-029 |
| API-077 | `GET /api/v1/settings/smtp` | FUN-035 | SCR-030 |
| API-078 | `PUT /api/v1/settings/smtp` | FUN-035 | SCR-030 |
| API-079 | `POST /api/v1/settings/smtp/test` | FUN-035 | SCR-030 |
| API-080 | `GET /api/v1/monthly-goals` | FUN-036 | SCR-003, SCR-030 |
| API-081 | `PUT /api/v1/monthly-goals/{month}` | FUN-036 | SCR-030 |
| API-082 | `GET /api/v1/audit-logs` | FUN-004, FUN-034 | SCR-029, SCR-030 |
| API-083 | `GET /api/v1/notifications` | FUN-011, FUN-035 | SCR-030 |
| API-084 | `POST /api/v1/notifications/{id}/retry` | FUN-035, FUN-037 | SCR-030 |
| API-085 | `POST /api/v1/auth/password-reset/request` | FUN-002 | SCR-002 |
| API-086 | `POST /api/v1/auth/password-reset/confirm` | FUN-002 | SCR-002 |
| API-087 | `POST /api/v1/sales/{id}/void` | FUN-025 | SCR-022 |

## K.7 Catálogo formal de reglas de negocio

Las reglas RN-001 a RN-060 son alias formales de las reglas C.1 a C.60. La descripción normativa completa permanece en la sección C.

| RN | Regla fuente | Justificación | Entidades afectadas | CU afectados | Restricción verificable | Prioridad |
|---|---|---|---|---|---|---|
| RN-001 | C.1 | Asegurar aislamiento operativo por empresa. | Todas las entidades operativas | Todos | Toda fila operativa referencia empresa cuando aplique. | Alta |
| RN-002 | C.2 | Evitar usuarios sin autoridad definida. | `users`, `roles` | CU-001 | Usuario activo requiere rol activo. | Alta |
| RN-003 | C.3 | Permitir auditoría y reconstrucción. | `audit_logs` | Todos los cambios críticos | Cambio crítico crea auditoría con usuario, fecha, entidad, acción e IP. | Alta |
| RN-004 | C.4 | Preservar historial operacional. | Entidades con movimientos | CU-005, CU-015, CU-024 | No hay eliminación física con historial. | Alta |
| RN-005 | C.5 | Mantener ciclos de vida explícitos. | Entidades con `estado` | Todos | Eliminación lógica cambia estado. | Alta |
| RN-006 | C.6 | Proteger credenciales. | `users`, `smtp_config`, `password_reset_tokens` | CU-001, CU-029, CU-031 | Secretos se almacenan cifrados/hash. | Alta |
| RN-007 | C.7 | Bloquear acceso inválido. | `users` | FUN-001 | Usuario inactivo no inicia sesión. | Alta |
| RN-008 | C.8 | Centralizar administración sensible. | `users`, `roles` | CU-001 | Solo admin gestiona usuarios y roles. | Alta |
| RN-009 | C.9 | Aplicar RBAC consistentemente. | `permissions`, APIs | Todos | Cada endpoint protegido evalúa permiso. | Alta |
| RN-010 | C.10 | Evitar filtración parcial. | APIs | Todos | Permiso insuficiente retorna 403 sin datos parciales. | Alta |
| RN-011 | C.11 | Evitar duplicidad de insumos. | `supplies` | CU-002 | Código único por empresa. | Alta |
| RN-012 | C.12 | Evitar uso de insumos no vigentes. | `supplies`, recetas, lotes | CU-005, CU-007, CU-009 | Insumo inactivo no recibe entradas ni se usa. | Alta |
| RN-013 | C.13 | Mantener costos válidos. | `supplies` | CU-002, CU-003 | Costo unitario no negativo. | Alta |
| RN-014 | C.14 | Evitar umbrales inválidos. | `supplies` | CU-002 | Stock mínimo no negativo. | Media |
| RN-015 | C.15 | Proteger inventario. | `supplies` | CU-003, CU-010 | Stock actual no negativo salvo configuración explícita. | Alta |
| RN-016 | C.16 | Preservar trazabilidad de insumos. | `supplies`, `supply_movements` | CU-005 | Insumo con movimientos no se elimina físicamente. | Alta |
| RN-017 | C.17 | Garantizar Kardex completo. | `supply_entries`, `supply_movements` | CU-003 | Entrada actualiza stock y Kardex. | Alta |
| RN-018 | C.18 | Evitar salidas imposibles. | `supplies`, `supply_movements` | CU-010 | Toda salida valida stock suficiente. | Alta |
| RN-019 | C.19 | Controlar política excepcional de faltante. | `supplies`, settings | CU-010 | Stock negativo solo con configuración explícita. | Alta |
| RN-020 | C.20 | Evitar alertas no configuradas. | `supplies`, `notification_queue` | CU-004 | Solo se alerta con email habilitado. | Media |
| RN-021 | C.21 | Evitar ruido operativo. | `notification_queue` | CU-004 | No se reenvía antes de 24 horas. | Media |
| RN-022 | C.22 | Priorizar quiebre total. | `supplies`, `notification_queue` | CU-004 | Stock cero fuerza alerta inmediata. | Alta |
| RN-023 | C.23 | Reiniciar ciclo de alerta al recuperar stock. | `supplies` | CU-003, CU-004 | Stock sobre mínimo resetea temporizador. | Media |
| RN-024 | C.24 | Cerrar fallos repetidos. | `notification_queue` | CU-004 | Quinto fallo queda en error definitivo. | Media |
| RN-025 | C.25 | Evitar recetas vacías. | `recipes`, `recipe_ingredients` | CU-007 | Receta requiere ingrediente activo. | Alta |
| RN-026 | C.26 | Preservar consistencia con lotes. | `recipes`, `production_batches` | CU-007, CU-008 | Receta con lotes activos no se edita. | Alta |
| RN-027 | C.27 | Calcular costo trazable. | `recipes`, `supplies` | CU-007 | Costo estimado usa costos unitarios vigentes. | Media |
| RN-028 | C.28 | Controlar versionado de recetas. | `recipes` | CU-008 | Solo receta activa/en prueba puede clonarse. | Media |
| RN-029 | C.29 | Fijar estado inicial de lote. | `production_batches` | CU-009 | Lote nuevo queda `en_elaboracion`. | Alta |
| RN-030 | C.30 | Evitar producción sin insumos. | `production_batches`, `supplies` | CU-010 | No se completa sin stock suficiente. | Alta |
| RN-031 | C.31 | Trazar consumo proporcional. | `supply_movements`, `batch_supply_snapshots` | CU-010 | Descuento proporcional al completar. | Alta |
| RN-032 | C.32 | Reflejar producción en inventario. | `finished_products` | CU-010 | Completar crea/incrementa producto. | Alta |
| RN-033 | C.33 | Calcular costo total completo. | `production_batches` | CU-010 | Costo incluye insumos, mano de obra, energía, agua, merma e indirectos. | Alta |
| RN-034 | C.34 | Incluir presentación en costo unitario. | `presentation_types`, `production_batches` | CU-010 | Costo por unidad incluye envase/tapa/etiqueta. | Media |
| RN-035 | C.35 | Evitar efectos de lotes cancelados. | `production_batches` | CU-009, CU-010 | Lote cancelado no afecta inventario ni Kardex. | Alta |
| RN-036 | C.36 | Evitar múltiples veredictos de calidad. | `batch_quality_checks` | CU-011 | Solo un control por lote. | Alta |
| RN-037 | C.37 | Forzar resultado explícito. | `batch_quality_checks` | CU-011 | Resultado aprobado/rechazado obligatorio. | Alta |
| RN-038 | C.38 | Conectar rechazo con merma. | `production_batches`, `waste_records` | CU-011, CU-012 | Lote rechazado puede registrarse como merma. | Media |
| RN-039 | C.39 | Exigir explicación de pérdida. | `waste_records` | CU-012 | Toda merma requiere motivo detallado. | Alta |
| RN-040 | C.40 | Mantener inventario consistente. | `waste_records`, movimientos | CU-012 | Merma descuenta inventario y registra Kardex. | Alta |
| RN-041 | C.41 | Visibilizar desviación operacional. | `waste_records`, dashboard | CU-012, CU-027 | Merma sobre 5% alerta en dashboard. | Media |
| RN-042 | C.42 | Evitar recetas duplicadas. | `recipes` | CU-007 | Nombre único por empresa. | Media |
| RN-043 | C.43 | Evitar clientes duplicados. | `customers` | CU-015, CU-018 | Identificador fiscal único por empresa. | Alta |
| RN-044 | C.44 | Evitar ventas a clientes no vigentes. | `customers`, `sales` | CU-016 | Cliente inactivo bloquea venta. | Alta |
| RN-045 | C.45 | Preservar historial comercial. | `customers`, `sales` | CU-015, CU-018 | Cliente con ventas no se elimina físicamente. | Alta |
| RN-046 | C.46 | Aplicar política de precios. | `product_prices`, `sale_items` | CU-016 | Precio sugerido usa tipo de cliente y lista vigente. | Media |
| RN-047 | C.47 | Reservar stock correctamente. | `finished_products`, `stock_reservations` | CU-013, CU-017 | Stock disponible = stock actual - reservas activas. | Alta |
| RN-048 | C.48 | Evitar sobreventa. | `sale_items`, `finished_products` | CU-016, CU-019 | No se vende más que stock disponible. | Alta |
| RN-049 | C.49 | Respetar reservas activas. | `stock_reservations` | CU-017 | Reserva activa no se usa en otra venta. | Alta |
| RN-050 | C.50 | Bloquear compras a proveedor inactivo. | `suppliers`, `purchase_orders` | CU-006, CU-020 | Proveedor de orden debe estar activo. | Alta |
| RN-051 | C.51 | Controlar edición de órdenes. | `purchase_orders` | CU-020 | Borrador editable; enviada no se modifica sin permiso. | Alta |
| RN-052 | C.52 | Evitar recepción excesiva. | `purchase_order_items` | CU-021 | Recepción no supera cantidad solicitada salvo tolerancia. | Alta |
| RN-053 | C.53 | Cerrar estado de compra correctamente. | `purchase_orders` | CU-021 | Total cierra; parcial queda parcialmente recibida. | Alta |
| RN-054 | C.54 | Bloquear órdenes canceladas. | `purchase_orders` | CU-021 | Orden cancelada no recibe mercadería. | Alta |
| RN-055 | C.55 | Identificar equipos inequívocamente. | `equipment` | CU-022 | Código de equipo único por empresa. | Media |
| RN-056 | C.56 | Evitar movimientos sobre descartados. | `equipment`, `equipment_movements` | CU-023 | Equipo descartado no acepta movimientos. | Media |
| RN-057 | C.57 | Anticipar mantenimiento vencido. | `equipment`, dashboard | CU-023, CU-027 | Próxima revisión vencida genera alerta. | Media |
| RN-058 | C.58 | Preservar respaldo documental. | `operational_expenses` | CU-024 | Gasto con documentos no se elimina. | Media |
| RN-059 | C.59 | Evitar gastos inválidos. | `operational_expenses` | CU-024 | Monto debe ser mayor a cero. | Alta |
| RN-060 | C.60 | Proteger auditoría. | `audit_logs`, reportes | CU-025, CU-028 | Solo admin/auditor accede reporte de auditoría. | Alta |

## K.8 Matriz de trazabilidad funcional

| Funcionalidad | Casos de uso | Reglas | APIs | Pantallas | Entidades | Módulo |
|---|---|---|---|---|---|---|
| FUN-001 | CU-001 | RN-002, RN-006..RN-010 | API-001..API-004 | SCR-001 | ENT-001..ENT-004 | MOD-001 |
| FUN-002 | CU-031 | RN-006, RN-007 | API-085, API-086 | SCR-002 | ENT-001, ENT-038 | MOD-001 |
| FUN-003 | CU-001 | RN-001..RN-010 | API-005..API-009 | SCR-030 | ENT-001..ENT-004 | MOD-001 |
| FUN-004 | CU-001, CU-019, CU-028 | RN-003, RN-004, RN-060 | API-082 | SCR-029, SCR-030 | ENT-005 | MOD-001 |
| FUN-005..FUN-006 | CU-006 | RN-004, RN-050 | API-010..API-013 | SCR-008, SCR-009 | ENT-007 | MOD-002 |
| FUN-007..FUN-012 | CU-002..CU-005 | RN-011..RN-024 | API-014..API-022, API-041..API-043, API-083 | SCR-004..SCR-007, SCR-012, SCR-030 | ENT-007..ENT-014 | MOD-003 |
| FUN-013..FUN-015 | CU-007..CU-010 | RN-025..RN-028, RN-034, RN-042 | API-023..API-027, API-044..API-046 | SCR-010, SCR-011, SCR-013 | ENT-015..ENT-018 | MOD-004 |
| FUN-016..FUN-018 | CU-009..CU-011 | RN-029..RN-038 | API-028..API-034 | SCR-014..SCR-017 | ENT-017..ENT-020, ENT-022, ENT-040 | MOD-005 |
| FUN-019 | CU-012 | RN-039..RN-041 | API-062, API-063 | SCR-019 | ENT-021, ENT-022, ENT-023 | MOD-006 |
| FUN-020..FUN-021 | CU-013, CU-014 | RN-046, RN-047 | API-035, API-036, API-047 | SCR-018 | ENT-022, ENT-023, ENT-026 | MOD-007 |
| FUN-022..FUN-026 | CU-015..CU-019 | RN-043..RN-049 | API-037..API-040, API-048..API-054, API-087 | SCR-020..SCR-023 | ENT-024..ENT-029 | MOD-008 |
| FUN-027..FUN-028 | CU-020, CU-021 | RN-050..RN-054 | API-055..API-061 | SCR-024..SCR-026 | ENT-030, ENT-031, ENT-007, ENT-012 | MOD-009 |
| FUN-029..FUN-030 | CU-022, CU-023 | RN-055..RN-057 | API-064..API-069 | SCR-027 | ENT-032..ENT-034 | MOD-010 |
| FUN-031..FUN-032, FUN-036 | CU-024..CU-026, CU-030 | RN-003, RN-058..RN-060 | API-070..API-081 | SCR-028, SCR-030 | ENT-035..ENT-037, ENT-039 | MOD-011 |
| FUN-033..FUN-034 | CU-025, CU-027, CU-028 | RN-003, RN-041, RN-057, RN-060 | API-074..API-076, API-082 | SCR-003, SCR-029 | ENT-005, ENT-039, ENT-041 | MOD-012 |
| FUN-035, FUN-037 | CU-004, CU-017, CU-029 | RN-020..RN-024, J.6.7, J.6.8 | API-077..API-084 | SCR-030 | ENT-013, ENT-014, ENT-039 | MOD-013 |
| FUN-038 | Todos | RN-008..RN-010 | API-001..API-087 | Todas las protegidas | ENT-001..ENT-004 | MOD-001 |

## K.9 Cobertura de pantallas

| Pantallas | Funcionalidades cubiertas | Estado de cobertura |
|---|---|---|
| SCR-001 P-01 Login | FUN-001 | Cubierta |
| SCR-002 P-02 Recuperar contraseña | FUN-002 | Cubierta con API-085 y API-086 |
| SCR-003 P-03 Dashboard general | FUN-033, FUN-036 | Cubierta |
| SCR-004..SCR-007 P-04 a P-07 | FUN-007..FUN-011 | Cubierta |
| SCR-008..SCR-009 P-08 a P-09 | FUN-005, FUN-006 | Cubierta |
| SCR-010..SCR-011 P-10 a P-11 | FUN-014, FUN-015 | Cubierta |
| SCR-012 P-12 Listado de bodegas | FUN-012 | Cubierta con API-041..API-043 |
| SCR-013 P-13 Tipos de presentación | FUN-013 | Cubierta con API-044..API-046 |
| SCR-014..SCR-017 P-14 a P-17 | FUN-016..FUN-018 | Cubierta |
| SCR-018 P-18 Inventario de productos | FUN-020, FUN-021 | Cubierta |
| SCR-019 P-19 Registro de mermas | FUN-019 | Cubierta con API-062 y API-063 |
| SCR-020..SCR-023 P-20 a P-23 | FUN-022..FUN-026 | Cubierta |
| SCR-024..SCR-026 P-24 a P-26 | FUN-027, FUN-028 | Cubierta |
| SCR-027 P-27 Gestión de equipos | FUN-029, FUN-030 | Cubierta |
| SCR-028 P-28 Gastos operativos | FUN-031 | Cubierta |
| SCR-029 P-29 Reportes | FUN-032, FUN-034 | Cubierta |
| SCR-030 P-30 Configuración y alertas | FUN-003, FUN-035, FUN-036 | Cubierta |

## K.10 Matriz de consistencia y correcciones aplicadas

| Hallazgo | Resolución documental | Impacto |
|---|---|---|
| Varias funciones del alcance J.2 no tenían endpoint en los 40 endpoints base. | Se agregó K.6 con API-041..API-087 como extensión obligatoria de cobertura. | El alcance queda implementable sin módulos huérfanos. |
| `UC-FIN-03` y `UC-ALT-02` describían metas mensuales desde dos secciones. | Se preservan ambos; CU-026 queda como caso financiero principal y CU-030 como acceso administrativo desde configuración. | Se elimina ambigüedad sin borrar información. |
| Las reglas C.1..C.60 no tenían ID formal trazable. | Se agregó RN-001..RN-060 como alias formal con entidad, CU, restricción y prioridad. | Las reglas pueden convertirse en pruebas y validadores. |
| Las pantallas P-01..P-30 no tenían alias de ingeniería. | Se agregó SCR-001..SCR-030 y matriz de cobertura. | Cada pantalla queda vinculada a funcionalidad y API. |
| Los casos de uso tenían flujos, pero no todos tenían pre/postcondiciones y trazabilidad completa. | Se agregó K.4 con objetivo, actor, disparador, precondiciones, postcondiciones y relaciones. | La fábrica puede generar tareas, pruebas y gates a partir del documento. |

## K.11 Compatibilidad con fábrica agéntica

La especificación debe ser consumida por una fábrica bajo las siguientes reglas:

1. Intake: usar J.1, J.2 y K.1 como contrato de entrada.
2. Contexto/RAG: indexar por IDs `MOD`, `CU`, `FUN`, `RN`, `SCR`, `API`, `ENT` y conservar procedencia de sección.
3. Planificación: descomponer trabajo por `FUN-###` y por hito J.12.
4. Implementación: ningún agente debe implementar una funcionalidad si no puede citar su CU, RN, API, pantalla y entidad asociada.
5. Validación: todo gate de cierre debe comprobar K.8, K.9, D, J.6, J.8, J.9 y J.15.
6. Seguridad: aplicar RBAC según H, ACT-001..ACT-008, RN-008..RN-010 y FUN-038.
7. Reproducibilidad: registrar versión de especificación, hash del documento, IDs implementados y evidencia de pruebas.

## K.12 Gate ampliado de cierre de especificación

Además del gate J.15, la especificación se considera lista para implementación cuando:

1. Todo `FUN-###` tiene al menos un CU, una regla, una API, una pantalla, una entidad y un módulo.
2. Todo CU tiene actor principal, precondiciones, flujo de referencia, alternos, postcondiciones y trazabilidad.
3. Toda pantalla `SCR-###` aparece en K.9 con funcionalidad cubierta.
4. Toda regla `RN-###` aparece en K.7 con restricción verificable.
5. Toda API `API-###` tiene propósito funcional y pantalla o CU relacionado.
6. Las funcionalidades con efectos de inventario, ventas, compras, producción y mermas citan una regla transaccional J.6.
7. Los criterios CA-001..CA-038 pueden convertirse en pruebas unitarias, integración o E2E.
