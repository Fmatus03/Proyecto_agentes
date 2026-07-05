from alembic import op
import sqlalchemy as sa

revision = '0001_brewmaster_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('rol', sa.String(255), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_estado', 'users', ['estado'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])

    op.create_table('roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('descripcion', sa.String(255), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_roles_estado', 'roles', ['estado'])
    op.create_index('ix_roles_created_at', 'roles', ['created_at'])

    op.create_table('permissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('codigo', sa.String(255), nullable=True),
        sa.Column('descripcion', sa.String(255), nullable=True),
        sa.Column('modulo', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_permissions_created_at', 'permissions', ['created_at'])

    op.create_table('role_permissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('permission_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_role_permissions_created_at', 'role_permissions', ['created_at'])

    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(255), nullable=True),
        sa.Column('entity', sa.String(255), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('detail', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    op.create_table('settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(255), nullable=True),
        sa.Column('value', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_settings_created_at', 'settings', ['created_at'])

    op.create_table('suppliers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('codigo', sa.String(255), nullable=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('telefono', sa.String(255), nullable=True),
        sa.Column('contacto', sa.String(255), nullable=True),
        sa.Column('condicion_pago', sa.String(255), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_suppliers_estado', 'suppliers', ['estado'])
    op.create_index('ix_suppliers_created_at', 'suppliers', ['created_at'])

    op.create_table('warehouses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('codigo', sa.String(255), nullable=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('tipo', sa.String(255), nullable=True),
        sa.Column('responsable', sa.String(255), nullable=True),
        sa.Column('capacidad', sa.Numeric(12, 4), nullable=True),
        sa.Column('temperatura_controlada', sa.Boolean(), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_warehouses_estado', 'warehouses', ['estado'])
    op.create_index('ix_warehouses_created_at', 'warehouses', ['created_at'])

    op.create_table('supply_categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('descripcion', sa.String(255), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_supply_categories_estado', 'supply_categories', ['estado'])
    op.create_index('ix_supply_categories_created_at', 'supply_categories', ['created_at'])

    op.create_table('supplies',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('codigo', sa.String(255), nullable=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('tipo', sa.String(255), nullable=True),
        sa.Column('unidad_medida', sa.String(255), nullable=True),
        sa.Column('proveedor_id', sa.Integer(), nullable=True),
        sa.Column('bodega_id', sa.Integer(), nullable=True),
        sa.Column('costo_unitario', sa.Numeric(12, 4), nullable=True),
        sa.Column('stock_minimo', sa.Numeric(12, 4), nullable=True),
        sa.Column('stock_actual', sa.Numeric(12, 4), nullable=True),
        sa.Column('enable_email_alerts', sa.Boolean(), nullable=True),
        sa.Column('alert_emails', sa.String(255), nullable=True),
        sa.Column('last_alert_sent_at', sa.DateTime(), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_supplies_estado', 'supplies', ['estado'])
    op.create_index('ix_supplies_created_at', 'supplies', ['created_at'])

    op.create_table('supply_movements',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('supply_id', sa.Integer(), nullable=True),
        sa.Column('tipo_movimiento', sa.String(255), nullable=True),
        sa.Column('cantidad', sa.Numeric(12, 4), nullable=True),
        sa.Column('costo_unitario', sa.Numeric(12, 4), nullable=True),
        sa.Column('saldo_resultante', sa.String(255), nullable=True),
        sa.Column('referencia', sa.String(255), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_supply_movements_created_at', 'supply_movements', ['created_at'])

    op.create_table('supply_entries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('supply_id', sa.Integer(), nullable=True),
        sa.Column('cantidad', sa.Numeric(12, 4), nullable=True),
        sa.Column('costo_unitario', sa.Numeric(12, 4), nullable=True),
        sa.Column('proveedor_id', sa.Integer(), nullable=True),
        sa.Column('referencia', sa.String(255), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_supply_entries_created_at', 'supply_entries', ['created_at'])

    op.create_table('notification_queue',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('supply_id', sa.Integer(), nullable=True),
        sa.Column('recipients', sa.String(255), nullable=True),
        sa.Column('subject', sa.String(255), nullable=True),
        sa.Column('body_html', sa.String(255), nullable=True),
        sa.Column('status', sa.String(255), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_notification_queue_created_at', 'notification_queue', ['created_at'])

    op.create_table('beer_styles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('descripcion', sa.String(255), nullable=True),
        sa.Column('abv_min', sa.Numeric(12, 4), nullable=True),
        sa.Column('abv_max', sa.Numeric(12, 4), nullable=True),
        sa.Column('ibu_min', sa.Numeric(12, 4), nullable=True),
        sa.Column('ibu_max', sa.Numeric(12, 4), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_beer_styles_created_at', 'beer_styles', ['created_at'])

    op.create_table('presentation_types',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('volumen', sa.Numeric(12, 4), nullable=True),
        sa.Column('unidad', sa.String(255), nullable=True),
        sa.Column('costo_presentacion', sa.Numeric(12, 4), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_presentation_types_estado', 'presentation_types', ['estado'])
    op.create_index('ix_presentation_types_created_at', 'presentation_types', ['created_at'])

    op.create_table('recipes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('tipo', sa.String(255), nullable=True),
        sa.Column('abv_estimado', sa.Numeric(12, 4), nullable=True),
        sa.Column('volumen_por_lote', sa.Numeric(12, 4), nullable=True),
        sa.Column('pasos_elaboracion', sa.String(255), nullable=True),
        sa.Column('costo_estimado', sa.Numeric(12, 4), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_recipes_estado', 'recipes', ['estado'])
    op.create_index('ix_recipes_created_at', 'recipes', ['created_at'])

    op.create_table('recipe_ingredients',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('recipe_id', sa.Integer(), nullable=True),
        sa.Column('supply_id', sa.Integer(), nullable=True),
        sa.Column('cantidad', sa.Numeric(12, 4), nullable=True),
        sa.Column('unidad', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_recipe_ingredients_created_at', 'recipe_ingredients', ['created_at'])

    op.create_table('production_batches',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('numero_lote', sa.String(255), nullable=True),
        sa.Column('recipe_id', sa.Integer(), nullable=True),
        sa.Column('presentation_type_id', sa.Integer(), nullable=True),
        sa.Column('cantidad_producida', sa.Numeric(12, 4), nullable=True),
        sa.Column('fecha_produccion', sa.DateTime(), nullable=True),
        sa.Column('responsable_id', sa.Integer(), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('horas_mano_obra', sa.String(255), nullable=True),
        sa.Column('kwh_consumidos', sa.Numeric(12, 4), nullable=True),
        sa.Column('litros_agua', sa.Numeric(12, 4), nullable=True),
        sa.Column('porcentaje_merma', sa.Numeric(12, 4), nullable=True),
        sa.Column('costo_total', sa.Numeric(12, 4), nullable=True),
        sa.Column('costo_por_litro', sa.Numeric(12, 4), nullable=True),
        sa.Column('costo_por_unidad', sa.Numeric(12, 4), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_production_batches_estado', 'production_batches', ['estado'])
    op.create_index('ix_production_batches_created_at', 'production_batches', ['created_at'])

    op.create_table('batch_quality_checks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('og', sa.Numeric(12, 4), nullable=True),
        sa.Column('fg', sa.Numeric(12, 4), nullable=True),
        sa.Column('abv_calculado', sa.Numeric(12, 4), nullable=True),
        sa.Column('ph', sa.Numeric(12, 4), nullable=True),
        sa.Column('temp_fermentacion', sa.Numeric(12, 4), nullable=True),
        sa.Column('nota_aroma', sa.String(255), nullable=True),
        sa.Column('nota_sabor', sa.String(255), nullable=True),
        sa.Column('resultado', sa.String(255), nullable=True),
        sa.Column('motivo_rechazo', sa.String(255), nullable=True),
        sa.Column('responsable_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_batch_quality_checks_created_at', 'batch_quality_checks', ['created_at'])

    op.create_table('waste_records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tipo_entidad', sa.String(255), nullable=True),
        sa.Column('entidad_id', sa.Integer(), nullable=True),
        sa.Column('cantidad_perdida', sa.Numeric(12, 4), nullable=True),
        sa.Column('costo_unitario', sa.Numeric(12, 4), nullable=True),
        sa.Column('costo_total', sa.Numeric(12, 4), nullable=True),
        sa.Column('tipo_merma', sa.String(255), nullable=True),
        sa.Column('motivo_detallado', sa.String(255), nullable=True),
        sa.Column('responsable_id', sa.Integer(), nullable=True),
        sa.Column('fecha', sa.DateTime(), nullable=True),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_waste_records_created_at', 'waste_records', ['created_at'])

    op.create_table('finished_products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('recipe_id', sa.Integer(), nullable=True),
        sa.Column('presentation_type_id', sa.Integer(), nullable=True),
        sa.Column('cantidad_stock', sa.Numeric(12, 4), nullable=True),
        sa.Column('costo_unitario', sa.Numeric(12, 4), nullable=True),
        sa.Column('precio_venta', sa.Numeric(12, 4), nullable=True),
        sa.Column('fecha_vencimiento_aprox', sa.DateTime(), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_finished_products_estado', 'finished_products', ['estado'])
    op.create_index('ix_finished_products_created_at', 'finished_products', ['created_at'])

    op.create_table('product_movements',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('tipo_movimiento', sa.String(255), nullable=True),
        sa.Column('cantidad', sa.Numeric(12, 4), nullable=True),
        sa.Column('costo_unitario', sa.Numeric(12, 4), nullable=True),
        sa.Column('saldo_resultante', sa.String(255), nullable=True),
        sa.Column('referencia', sa.String(255), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_product_movements_created_at', 'product_movements', ['created_at'])

    op.create_table('customer_types',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('descripcion', sa.String(255), nullable=True),
        sa.Column('descuento_pct_base', sa.Numeric(12, 4), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_customer_types_created_at', 'customer_types', ['created_at'])

    op.create_table('customers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('identificador_fiscal', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('telefono', sa.String(255), nullable=True),
        sa.Column('tipo_cliente', sa.String(255), nullable=True),
        sa.Column('forma_pago', sa.String(255), nullable=True),
        sa.Column('limite_credito', sa.Numeric(12, 4), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_customers_estado', 'customers', ['estado'])
    op.create_index('ix_customers_created_at', 'customers', ['created_at'])

    op.create_table('product_prices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('tipo_cliente', sa.String(255), nullable=True),
        sa.Column('precio_unitario', sa.Numeric(12, 4), nullable=True),
        sa.Column('precio_por_docena', sa.Numeric(12, 4), nullable=True),
        sa.Column('descuento_pct', sa.Numeric(12, 4), nullable=True),
        sa.Column('vigente_desde', sa.String(255), nullable=True),
        sa.Column('vigente_hasta', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_product_prices_created_at', 'product_prices', ['created_at'])

    op.create_table('sales',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('numero_documento', sa.String(255), nullable=True),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('fecha_venta', sa.DateTime(), nullable=True),
        sa.Column('responsable_id', sa.Integer(), nullable=True),
        sa.Column('total', sa.Numeric(12, 4), nullable=True),
        sa.Column('ganancia_total', sa.Numeric(12, 4), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_sales_created_at', 'sales', ['created_at'])

    op.create_table('sale_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sale_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('cantidad', sa.Numeric(12, 4), nullable=True),
        sa.Column('precio_unitario', sa.Numeric(12, 4), nullable=True),
        sa.Column('costo_unitario', sa.Numeric(12, 4), nullable=True),
        sa.Column('ganancia_unitaria', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_sale_items_created_at', 'sale_items', ['created_at'])

    op.create_table('stock_reservations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('cantidad_reservada', sa.Numeric(12, 4), nullable=True),
        sa.Column('fecha_entrega_prometida', sa.DateTime(), nullable=True),
        sa.Column('precio', sa.Numeric(12, 4), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_stock_reservations_estado', 'stock_reservations', ['estado'])
    op.create_index('ix_stock_reservations_created_at', 'stock_reservations', ['created_at'])

    op.create_table('purchase_orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('numero_orden', sa.String(255), nullable=True),
        sa.Column('proveedor_id', sa.Integer(), nullable=True),
        sa.Column('fecha_emision', sa.DateTime(), nullable=True),
        sa.Column('fecha_esperada_recepcion', sa.DateTime(), nullable=True),
        sa.Column('total_estimado', sa.Numeric(12, 4), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_purchase_orders_estado', 'purchase_orders', ['estado'])
    op.create_index('ix_purchase_orders_created_at', 'purchase_orders', ['created_at'])

    op.create_table('purchase_order_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('supply_id', sa.Integer(), nullable=True),
        sa.Column('cantidad_solicitada', sa.Numeric(12, 4), nullable=True),
        sa.Column('precio_unitario', sa.Numeric(12, 4), nullable=True),
        sa.Column('cantidad_recibida', sa.Numeric(12, 4), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_purchase_order_items_created_at', 'purchase_order_items', ['created_at'])

    op.create_table('equipment_types',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('descripcion', sa.String(255), nullable=True),
        sa.Column('intervalo_revision_dias', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_equipment_types_created_at', 'equipment_types', ['created_at'])

    op.create_table('equipment',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('codigo', sa.String(255), nullable=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('tipo', sa.String(255), nullable=True),
        sa.Column('marca', sa.String(255), nullable=True),
        sa.Column('modelo', sa.String(255), nullable=True),
        sa.Column('serie', sa.String(255), nullable=True),
        sa.Column('fecha_compra', sa.DateTime(), nullable=True),
        sa.Column('costo_adquisicion', sa.Numeric(12, 4), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('ultima_mantencion', sa.String(255), nullable=True),
        sa.Column('proxima_revision', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_equipment_estado', 'equipment', ['estado'])
    op.create_index('ix_equipment_created_at', 'equipment', ['created_at'])

    op.create_table('equipment_movements',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('equipment_id', sa.Integer(), nullable=True),
        sa.Column('tipo_movimiento', sa.String(255), nullable=True),
        sa.Column('descripcion', sa.String(255), nullable=True),
        sa.Column('costo', sa.Numeric(12, 4), nullable=True),
        sa.Column('fecha', sa.DateTime(), nullable=True),
        sa.Column('responsable_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_equipment_movements_created_at', 'equipment_movements', ['created_at'])

    op.create_table('expense_categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('descripcion', sa.String(255), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_expense_categories_estado', 'expense_categories', ['estado'])
    op.create_index('ix_expense_categories_created_at', 'expense_categories', ['created_at'])

    op.create_table('operational_expenses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('concepto', sa.String(255), nullable=True),
        sa.Column('categoria', sa.String(255), nullable=True),
        sa.Column('monto', sa.Numeric(12, 4), nullable=True),
        sa.Column('fecha', sa.DateTime(), nullable=True),
        sa.Column('proveedor', sa.String(255), nullable=True),
        sa.Column('documento_referencia', sa.String(255), nullable=True),
        sa.Column('responsable_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_operational_expenses_created_at', 'operational_expenses', ['created_at'])

    op.create_table('monthly_goals',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('mes', sa.String(255), nullable=True),
        sa.Column('litros_produccion', sa.Numeric(12, 4), nullable=True),
        sa.Column('monto_ventas', sa.Numeric(12, 4), nullable=True),
        sa.Column('num_clientes', sa.Integer(), nullable=True),
        sa.Column('margen_promedio_pct', sa.Numeric(12, 4), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_monthly_goals_created_at', 'monthly_goals', ['created_at'])

    op.create_table('password_reset_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('token_hash', sa.String(255), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_password_reset_tokens_created_at', 'password_reset_tokens', ['created_at'])

    op.create_table('export_jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('tipo_reporte', sa.String(255), nullable=True),
        sa.Column('filtros', sa.String(255), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('archivo_url', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_export_jobs_estado', 'export_jobs', ['estado'])
    op.create_index('ix_export_jobs_created_at', 'export_jobs', ['created_at'])

    op.create_table('smtp_config',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('host', sa.String(255), nullable=True),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(255), nullable=True),
        sa.Column('password_encrypted', sa.String(255), nullable=True),
        sa.Column('from_email', sa.String(255), nullable=True),
        sa.Column('use_tls', sa.Boolean(), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_smtp_config_created_at', 'smtp_config', ['created_at'])

    op.create_table('batch_supply_snapshots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('supply_id', sa.Integer(), nullable=True),
        sa.Column('cantidad_usada', sa.Numeric(12, 4), nullable=True),
        sa.Column('costo_unitario_momento', sa.Numeric(12, 4), nullable=True),
        sa.Column('nombre_insumo', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_batch_supply_snapshots_created_at', 'batch_supply_snapshots', ['created_at'])


def downgrade():
    op.drop_index('ix_batch_supply_snapshots_created_at', table_name='batch_supply_snapshots')
    op.drop_table('batch_supply_snapshots')
    op.drop_index('ix_smtp_config_created_at', table_name='smtp_config')
    op.drop_table('smtp_config')
    op.drop_index('ix_export_jobs_created_at', table_name='export_jobs')
    op.drop_index('ix_export_jobs_estado', table_name='export_jobs')
    op.drop_table('export_jobs')
    op.drop_index('ix_password_reset_tokens_created_at', table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_index('ix_monthly_goals_created_at', table_name='monthly_goals')
    op.drop_table('monthly_goals')
    op.drop_index('ix_operational_expenses_created_at', table_name='operational_expenses')
    op.drop_table('operational_expenses')
    op.drop_index('ix_expense_categories_created_at', table_name='expense_categories')
    op.drop_index('ix_expense_categories_estado', table_name='expense_categories')
    op.drop_table('expense_categories')
    op.drop_index('ix_equipment_movements_created_at', table_name='equipment_movements')
    op.drop_table('equipment_movements')
    op.drop_index('ix_equipment_created_at', table_name='equipment')
    op.drop_index('ix_equipment_estado', table_name='equipment')
    op.drop_table('equipment')
    op.drop_index('ix_equipment_types_created_at', table_name='equipment_types')
    op.drop_table('equipment_types')
    op.drop_index('ix_purchase_order_items_created_at', table_name='purchase_order_items')
    op.drop_table('purchase_order_items')
    op.drop_index('ix_purchase_orders_created_at', table_name='purchase_orders')
    op.drop_index('ix_purchase_orders_estado', table_name='purchase_orders')
    op.drop_table('purchase_orders')
    op.drop_index('ix_stock_reservations_created_at', table_name='stock_reservations')
    op.drop_index('ix_stock_reservations_estado', table_name='stock_reservations')
    op.drop_table('stock_reservations')
    op.drop_index('ix_sale_items_created_at', table_name='sale_items')
    op.drop_table('sale_items')
    op.drop_index('ix_sales_created_at', table_name='sales')
    op.drop_table('sales')
    op.drop_index('ix_product_prices_created_at', table_name='product_prices')
    op.drop_table('product_prices')
    op.drop_index('ix_customers_created_at', table_name='customers')
    op.drop_index('ix_customers_estado', table_name='customers')
    op.drop_table('customers')
    op.drop_index('ix_customer_types_created_at', table_name='customer_types')
    op.drop_table('customer_types')
    op.drop_index('ix_product_movements_created_at', table_name='product_movements')
    op.drop_table('product_movements')
    op.drop_index('ix_finished_products_created_at', table_name='finished_products')
    op.drop_index('ix_finished_products_estado', table_name='finished_products')
    op.drop_table('finished_products')
    op.drop_index('ix_waste_records_created_at', table_name='waste_records')
    op.drop_table('waste_records')
    op.drop_index('ix_batch_quality_checks_created_at', table_name='batch_quality_checks')
    op.drop_table('batch_quality_checks')
    op.drop_index('ix_production_batches_created_at', table_name='production_batches')
    op.drop_index('ix_production_batches_estado', table_name='production_batches')
    op.drop_table('production_batches')
    op.drop_index('ix_recipe_ingredients_created_at', table_name='recipe_ingredients')
    op.drop_table('recipe_ingredients')
    op.drop_index('ix_recipes_created_at', table_name='recipes')
    op.drop_index('ix_recipes_estado', table_name='recipes')
    op.drop_table('recipes')
    op.drop_index('ix_presentation_types_created_at', table_name='presentation_types')
    op.drop_index('ix_presentation_types_estado', table_name='presentation_types')
    op.drop_table('presentation_types')
    op.drop_index('ix_beer_styles_created_at', table_name='beer_styles')
    op.drop_table('beer_styles')
    op.drop_index('ix_notification_queue_created_at', table_name='notification_queue')
    op.drop_table('notification_queue')
    op.drop_index('ix_supply_entries_created_at', table_name='supply_entries')
    op.drop_table('supply_entries')
    op.drop_index('ix_supply_movements_created_at', table_name='supply_movements')
    op.drop_table('supply_movements')
    op.drop_index('ix_supplies_created_at', table_name='supplies')
    op.drop_index('ix_supplies_estado', table_name='supplies')
    op.drop_table('supplies')
    op.drop_index('ix_supply_categories_created_at', table_name='supply_categories')
    op.drop_index('ix_supply_categories_estado', table_name='supply_categories')
    op.drop_table('supply_categories')
    op.drop_index('ix_warehouses_created_at', table_name='warehouses')
    op.drop_index('ix_warehouses_estado', table_name='warehouses')
    op.drop_table('warehouses')
    op.drop_index('ix_suppliers_created_at', table_name='suppliers')
    op.drop_index('ix_suppliers_estado', table_name='suppliers')
    op.drop_table('suppliers')
    op.drop_index('ix_settings_created_at', table_name='settings')
    op.drop_table('settings')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index('ix_role_permissions_created_at', table_name='role_permissions')
    op.drop_table('role_permissions')
    op.drop_index('ix_permissions_created_at', table_name='permissions')
    op.drop_table('permissions')
    op.drop_index('ix_roles_created_at', table_name='roles')
    op.drop_index('ix_roles_estado', table_name='roles')
    op.drop_table('roles')
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_estado', table_name='users')
    op.drop_table('users')
