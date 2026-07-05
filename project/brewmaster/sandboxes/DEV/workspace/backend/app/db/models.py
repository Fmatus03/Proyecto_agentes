from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    rol = Column(String(255), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Permissions(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    codigo = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    modulo = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class RolePermissions(Base):
    __tablename__ = 'role_permissions'
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer(), nullable=True)
    permission_id = Column(Integer(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class AuditLogs(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer(), nullable=True)
    action = Column(String(255), nullable=True)
    entity = Column(String(255), nullable=True)
    entity_id = Column(Integer(), nullable=True)
    detail = Column(String(255), nullable=True)
    ip_address = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=True)
    value = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Suppliers(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    codigo = Column(String(255), nullable=True)
    nombre = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    telefono = Column(String(255), nullable=True)
    contacto = Column(String(255), nullable=True)
    condicion_pago = Column(String(255), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Warehouses(Base):
    __tablename__ = 'warehouses'
    id = Column(Integer, primary_key=True)
    codigo = Column(String(255), nullable=True)
    nombre = Column(String(255), nullable=True)
    tipo = Column(String(255), nullable=True)
    responsable = Column(String(255), nullable=True)
    capacidad = Column(Numeric(12, 4), nullable=True)
    temperatura_controlada = Column(Boolean(), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class SupplyCategories(Base):
    __tablename__ = 'supply_categories'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Supplies(Base):
    __tablename__ = 'supplies'
    id = Column(Integer, primary_key=True)
    codigo = Column(String(255), nullable=True)
    nombre = Column(String(255), nullable=True)
    tipo = Column(String(255), nullable=True)
    unidad_medida = Column(String(255), nullable=True)
    proveedor_id = Column(Integer(), nullable=True)
    bodega_id = Column(Integer(), nullable=True)
    costo_unitario = Column(Numeric(12, 4), nullable=True)
    stock_minimo = Column(Numeric(12, 4), nullable=True)
    stock_actual = Column(Numeric(12, 4), nullable=True)
    enable_email_alerts = Column(Boolean(), nullable=True)
    alert_emails = Column(String(255), nullable=True)
    last_alert_sent_at = Column(DateTime(), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class SupplyMovements(Base):
    __tablename__ = 'supply_movements'
    id = Column(Integer, primary_key=True)
    supply_id = Column(Integer(), nullable=True)
    tipo_movimiento = Column(String(255), nullable=True)
    cantidad = Column(Numeric(12, 4), nullable=True)
    costo_unitario = Column(Numeric(12, 4), nullable=True)
    saldo_resultante = Column(String(255), nullable=True)
    referencia = Column(String(255), nullable=True)
    user_id = Column(Integer(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class SupplyEntries(Base):
    __tablename__ = 'supply_entries'
    id = Column(Integer, primary_key=True)
    supply_id = Column(Integer(), nullable=True)
    cantidad = Column(Numeric(12, 4), nullable=True)
    costo_unitario = Column(Numeric(12, 4), nullable=True)
    proveedor_id = Column(Integer(), nullable=True)
    referencia = Column(String(255), nullable=True)
    user_id = Column(Integer(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class NotificationQueue(Base):
    __tablename__ = 'notification_queue'
    id = Column(Integer, primary_key=True)
    supply_id = Column(Integer(), nullable=True)
    recipients = Column(String(255), nullable=True)
    subject = Column(String(255), nullable=True)
    body_html = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    attempts = Column(Integer(), nullable=True)
    sent_at = Column(DateTime(), nullable=True)
    error_message = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class BeerStyles(Base):
    __tablename__ = 'beer_styles'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    abv_min = Column(Numeric(12, 4), nullable=True)
    abv_max = Column(Numeric(12, 4), nullable=True)
    ibu_min = Column(Numeric(12, 4), nullable=True)
    ibu_max = Column(Numeric(12, 4), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class PresentationTypes(Base):
    __tablename__ = 'presentation_types'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    volumen = Column(Numeric(12, 4), nullable=True)
    unidad = Column(String(255), nullable=True)
    costo_presentacion = Column(Numeric(12, 4), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Recipes(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    tipo = Column(String(255), nullable=True)
    abv_estimado = Column(Numeric(12, 4), nullable=True)
    volumen_por_lote = Column(Numeric(12, 4), nullable=True)
    pasos_elaboracion = Column(String(255), nullable=True)
    costo_estimado = Column(Numeric(12, 4), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class RecipeIngredients(Base):
    __tablename__ = 'recipe_ingredients'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer(), nullable=True)
    supply_id = Column(Integer(), nullable=True)
    cantidad = Column(Numeric(12, 4), nullable=True)
    unidad = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class ProductionBatches(Base):
    __tablename__ = 'production_batches'
    id = Column(Integer, primary_key=True)
    numero_lote = Column(String(255), nullable=True)
    recipe_id = Column(Integer(), nullable=True)
    presentation_type_id = Column(Integer(), nullable=True)
    cantidad_producida = Column(Numeric(12, 4), nullable=True)
    fecha_produccion = Column(DateTime(), nullable=True)
    responsable_id = Column(Integer(), nullable=True)
    estado = Column(String(255), nullable=True)
    horas_mano_obra = Column(String(255), nullable=True)
    kwh_consumidos = Column(Numeric(12, 4), nullable=True)
    litros_agua = Column(Numeric(12, 4), nullable=True)
    porcentaje_merma = Column(Numeric(12, 4), nullable=True)
    costo_total = Column(Numeric(12, 4), nullable=True)
    costo_por_litro = Column(Numeric(12, 4), nullable=True)
    costo_por_unidad = Column(Numeric(12, 4), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class BatchQualityChecks(Base):
    __tablename__ = 'batch_quality_checks'
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer(), nullable=True)
    og = Column(Numeric(12, 4), nullable=True)
    fg = Column(Numeric(12, 4), nullable=True)
    abv_calculado = Column(Numeric(12, 4), nullable=True)
    ph = Column(Numeric(12, 4), nullable=True)
    temp_fermentacion = Column(Numeric(12, 4), nullable=True)
    nota_aroma = Column(String(255), nullable=True)
    nota_sabor = Column(String(255), nullable=True)
    resultado = Column(String(255), nullable=True)
    motivo_rechazo = Column(String(255), nullable=True)
    responsable_id = Column(Integer(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class WasteRecords(Base):
    __tablename__ = 'waste_records'
    id = Column(Integer, primary_key=True)
    tipo_entidad = Column(String(255), nullable=True)
    entidad_id = Column(Integer(), nullable=True)
    cantidad_perdida = Column(Numeric(12, 4), nullable=True)
    costo_unitario = Column(Numeric(12, 4), nullable=True)
    costo_total = Column(Numeric(12, 4), nullable=True)
    tipo_merma = Column(String(255), nullable=True)
    motivo_detallado = Column(String(255), nullable=True)
    responsable_id = Column(Integer(), nullable=True)
    fecha = Column(DateTime(), nullable=True)
    batch_id = Column(Integer(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class FinishedProducts(Base):
    __tablename__ = 'finished_products'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer(), nullable=True)
    presentation_type_id = Column(Integer(), nullable=True)
    cantidad_stock = Column(Numeric(12, 4), nullable=True)
    costo_unitario = Column(Numeric(12, 4), nullable=True)
    precio_venta = Column(Numeric(12, 4), nullable=True)
    fecha_vencimiento_aprox = Column(DateTime(), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class ProductMovements(Base):
    __tablename__ = 'product_movements'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer(), nullable=True)
    tipo_movimiento = Column(String(255), nullable=True)
    cantidad = Column(Numeric(12, 4), nullable=True)
    costo_unitario = Column(Numeric(12, 4), nullable=True)
    saldo_resultante = Column(String(255), nullable=True)
    referencia = Column(String(255), nullable=True)
    user_id = Column(Integer(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class CustomerTypes(Base):
    __tablename__ = 'customer_types'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    descuento_pct_base = Column(Numeric(12, 4), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Customers(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    identificador_fiscal = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    telefono = Column(String(255), nullable=True)
    tipo_cliente = Column(String(255), nullable=True)
    forma_pago = Column(String(255), nullable=True)
    limite_credito = Column(Numeric(12, 4), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class ProductPrices(Base):
    __tablename__ = 'product_prices'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer(), nullable=True)
    tipo_cliente = Column(String(255), nullable=True)
    precio_unitario = Column(Numeric(12, 4), nullable=True)
    precio_por_docena = Column(Numeric(12, 4), nullable=True)
    descuento_pct = Column(Numeric(12, 4), nullable=True)
    vigente_desde = Column(String(255), nullable=True)
    vigente_hasta = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Sales(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    numero_documento = Column(String(255), nullable=True)
    cliente_id = Column(Integer(), nullable=True)
    fecha_venta = Column(DateTime(), nullable=True)
    responsable_id = Column(Integer(), nullable=True)
    total = Column(Numeric(12, 4), nullable=True)
    ganancia_total = Column(Numeric(12, 4), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class SaleItems(Base):
    __tablename__ = 'sale_items'
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer(), nullable=True)
    product_id = Column(Integer(), nullable=True)
    cantidad = Column(Numeric(12, 4), nullable=True)
    precio_unitario = Column(Numeric(12, 4), nullable=True)
    costo_unitario = Column(Numeric(12, 4), nullable=True)
    ganancia_unitaria = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class StockReservations(Base):
    __tablename__ = 'stock_reservations'
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer(), nullable=True)
    product_id = Column(Integer(), nullable=True)
    cantidad_reservada = Column(Numeric(12, 4), nullable=True)
    fecha_entrega_prometida = Column(DateTime(), nullable=True)
    precio = Column(Numeric(12, 4), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class PurchaseOrders(Base):
    __tablename__ = 'purchase_orders'
    id = Column(Integer, primary_key=True)
    numero_orden = Column(String(255), nullable=True)
    proveedor_id = Column(Integer(), nullable=True)
    fecha_emision = Column(DateTime(), nullable=True)
    fecha_esperada_recepcion = Column(DateTime(), nullable=True)
    total_estimado = Column(Numeric(12, 4), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class PurchaseOrderItems(Base):
    __tablename__ = 'purchase_order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer(), nullable=True)
    supply_id = Column(Integer(), nullable=True)
    cantidad_solicitada = Column(Numeric(12, 4), nullable=True)
    precio_unitario = Column(Numeric(12, 4), nullable=True)
    cantidad_recibida = Column(Numeric(12, 4), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class EquipmentTypes(Base):
    __tablename__ = 'equipment_types'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    intervalo_revision_dias = Column(DateTime(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Equipment(Base):
    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True)
    codigo = Column(String(255), nullable=True)
    nombre = Column(String(255), nullable=True)
    tipo = Column(String(255), nullable=True)
    marca = Column(String(255), nullable=True)
    modelo = Column(String(255), nullable=True)
    serie = Column(String(255), nullable=True)
    fecha_compra = Column(DateTime(), nullable=True)
    costo_adquisicion = Column(Numeric(12, 4), nullable=True)
    estado = Column(String(255), nullable=True)
    ultima_mantencion = Column(String(255), nullable=True)
    proxima_revision = Column(DateTime(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class EquipmentMovements(Base):
    __tablename__ = 'equipment_movements'
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer(), nullable=True)
    tipo_movimiento = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    costo = Column(Numeric(12, 4), nullable=True)
    fecha = Column(DateTime(), nullable=True)
    responsable_id = Column(Integer(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class ExpenseCategories(Base):
    __tablename__ = 'expense_categories'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class OperationalExpenses(Base):
    __tablename__ = 'operational_expenses'
    id = Column(Integer, primary_key=True)
    concepto = Column(String(255), nullable=True)
    categoria = Column(String(255), nullable=True)
    monto = Column(Numeric(12, 4), nullable=True)
    fecha = Column(DateTime(), nullable=True)
    proveedor = Column(String(255), nullable=True)
    documento_referencia = Column(String(255), nullable=True)
    responsable_id = Column(Integer(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class MonthlyGoals(Base):
    __tablename__ = 'monthly_goals'
    id = Column(Integer, primary_key=True)
    mes = Column(String(255), nullable=True)
    litros_produccion = Column(Numeric(12, 4), nullable=True)
    monto_ventas = Column(Numeric(12, 4), nullable=True)
    num_clientes = Column(Integer(), nullable=True)
    margen_promedio_pct = Column(Numeric(12, 4), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class PasswordResetTokens(Base):
    __tablename__ = 'password_reset_tokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer(), nullable=True)
    token_hash = Column(String(255), nullable=True)
    expires_at = Column(DateTime(), nullable=True)
    used_at = Column(DateTime(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class ExportJobs(Base):
    __tablename__ = 'export_jobs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer(), nullable=True)
    tipo_reporte = Column(String(255), nullable=True)
    filtros = Column(String(255), nullable=True)
    estado = Column(String(255), nullable=True)
    archivo_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    completed_at = Column(DateTime(), nullable=True)
    updated_at = Column(DateTime(), nullable=False)

class SmtpConfig(Base):
    __tablename__ = 'smtp_config'
    id = Column(Integer, primary_key=True)
    host = Column(String(255), nullable=True)
    port = Column(Integer(), nullable=True)
    username = Column(String(255), nullable=True)
    password_encrypted = Column(String(255), nullable=True)
    from_email = Column(String(255), nullable=True)
    use_tls = Column(Boolean(), nullable=True)
    updated_by = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class BatchSupplySnapshots(Base):
    __tablename__ = 'batch_supply_snapshots'
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer(), nullable=True)
    supply_id = Column(Integer(), nullable=True)
    cantidad_usada = Column(Numeric(12, 4), nullable=True)
    costo_unitario_momento = Column(Numeric(12, 4), nullable=True)
    nombre_insumo = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)
