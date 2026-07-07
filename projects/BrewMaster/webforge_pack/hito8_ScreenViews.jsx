import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ClipboardCheck,
  ClipboardList,
  Database,
  Download,
  Factory,
  FileSpreadsheet,
  FlaskConical,
  KeyRound,
  MailCheck,
  PackageCheck,
  PackagePlus,
  RefreshCw,
  Save,
  Send,
  Settings,
  ShieldCheck,
  ShoppingCart,
  Trash2,
  Truck,
  UserPlus,
  Users,
  Warehouse,
  Wrench,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { api, getStoredUser, login, setSession } from '../api/client';

const today = '2026-07-06';

const fallback = {
  me: { email: 'admin@brewmaster.local', role: 'admin', permissions: ['*'] },
  suppliers: [
    { id: 1, codigo: 'SUP-001', nombre: 'Malteria Sur', email: 'ventas@malteria.local', contacto: 'Carla Soto', estado: 'activo' },
    { id: 2, codigo: 'SUP-002', nombre: 'Lupulos Chile', email: 'contacto@lupulos.local', contacto: 'Diego Rios', estado: 'activo' },
  ],
  warehouses: [
    { id: 1, codigo: 'BOD-001', nombre: 'Bodega seca', tipo: 'insumos', capacidad: 1200, temperatura_controlada: false, estado: 'activo' },
    { id: 2, codigo: 'BOD-002', nombre: 'Camara fria', tipo: 'insumos', capacidad: 320, temperatura_controlada: true, estado: 'activo' },
  ],
  supplies: [
    { id: 1, codigo: 'INS-001', nombre: 'Malta Pale', tipo: 'malta', unidad_medida: 'kg', stock_actual: 86, stock_minimo: 40, costo_unitario: 720, estado: 'activo' },
    { id: 2, codigo: 'INS-002', nombre: 'Lupulo Cascade', tipo: 'lupulo', unidad_medida: 'kg', stock_actual: 6, stock_minimo: 8, costo_unitario: 18500, estado: 'activo' },
    { id: 3, codigo: 'INS-003', nombre: 'Levadura Ale', tipo: 'levadura', unidad_medida: 'g', stock_actual: 2400, stock_minimo: 1000, costo_unitario: 42, estado: 'activo' },
  ],
  kardex: [
    { id: 1, tipo_movimiento: 'ENTRADA', cantidad: 35, saldo_resultante: 86, costo_unitario: 720, referencia: 'OC-0001', created_at: `${today}T09:30:00` },
    { id: 2, tipo_movimiento: 'SALIDA_PRODUCCION', cantidad: 14, saldo_resultante: 51, costo_unitario: 720, referencia: 'batch:1', created_at: `${today}T13:10:00` },
  ],
  entries: [
    { id: 1, supply_id: 1, supply_name: 'Malta Pale', cantidad: 35, costo_unitario: 720, documento_referencia: 'FAC-001', created_at: `${today}T09:30:00` },
  ],
  recipes: [
    { id: 1, nombre: 'Pale Ale Casa', tipo: 'ale', estado: 'activo', volumen_por_lote: 50, costo_estimado: 12500, ingredientes: [{ supply_id: 1, nombre_insumo: 'Malta Pale', cantidad: 7, unidad: 'kg' }] },
    { id: 2, nombre: 'Stout Sur', tipo: 'stout', estado: 'en_prueba', volumen_por_lote: 40, costo_estimado: 14800, ingredientes: [{ supply_id: 1, nombre_insumo: 'Malta Pale', cantidad: 6, unidad: 'kg' }] },
  ],
  presentations: [
    { id: 1, nombre: 'Botella 330', volumen: 330, unidad: 'ml', costo_presentacion: 120, estado: 'activo' },
    { id: 2, nombre: 'Botella 500', volumen: 500, unidad: 'ml', costo_presentacion: 160, estado: 'activo' },
  ],
  batches: [
    { id: 1, numero_lote: 'LOT-0001', recipe_id: 1, recipe_name: 'Pale Ale Casa', presentation_name: 'Botella 330', cantidad_producida: 50, estado: 'en_elaboracion', fecha_produccion: today, stock_alerts: [] },
    { id: 2, numero_lote: 'LOT-0002', recipe_id: 2, recipe_name: 'Stout Sur', presentation_name: 'Botella 500', cantidad_producida: 40, estado: 'completado', fecha_produccion: today, costo_total: 128000, costo_por_unidad: 1600, quality_check: null },
  ],
  products: [
    { id: 1, recipe_name: 'Pale Ale Casa', presentation_name: 'Botella 330', cantidad_stock: 128, reservado: 24, disponible: 104, costo_unitario: 620, precio_venta: 950, estado: 'activo' },
    { id: 2, recipe_name: 'Stout Sur', presentation_name: 'Botella 500', cantidad_stock: 64, reservado: 8, disponible: 56, costo_unitario: 780, precio_venta: 1250, estado: 'activo' },
  ],
  waste: [
    { id: 1, tipo_entidad: 'producto', entidad_id: 1, cantidad_perdida: 4, tipo_merma: 'calidad', costo_total: 2480, motivo: 'desviacion sensorial', created_at: `${today}T11:00:00` },
  ],
  customers: [
    { id: 1, nombre: 'Bar Lupulo Sur', identificador_fiscal: 'CL-76000001', email: 'compras@lupulosur.local', tipo_cliente: 'mayorista', estado: 'activo', limite_credito: 400000 },
    { id: 2, nombre: 'Tienda Malta Norte', identificador_fiscal: 'CL-76000002', email: 'ventas@maltanorte.local', tipo_cliente: 'minorista', estado: 'activo', limite_credito: 120000 },
  ],
  sales: [
    { id: 1, cliente_nombre: 'Bar Lupulo Sur', estado: 'confirmada', total: 11400, ganancia_total: 3960, created_at: `${today}T10:00:00`, items: [{ product_id: 1, cantidad: 12, precio_unitario: 950 }] },
  ],
  reservations: [
    { id: 1, cliente_id: 1, customer_name: 'Bar Lupulo Sur', product_id: 1, product_name: 'Pale Ale Casa', cantidad_reservada: 24, fecha_entrega_prometida: today, precio: 920, estado: 'activa' },
  ],
  purchaseOrders: [
    { id: 1, numero_orden: 'OC-0001', proveedor_id: 1, proveedor_nombre: 'Malteria Sur', estado: 'enviada', total_estimado: 25200, fecha_esperada_recepcion: today, items: [{ supply_id: 1, nombre_insumo: 'Malta Pale', cantidad_solicitada: 35, cantidad_recibida: 0, precio_unitario: 720 }] },
  ],
  dashboard: {
    kpis: { litros_producidos: 90, stock_libre: 160, monto_ventas: 11400, margen_bruto: 3960, alertas_operacionales: 3, gastos_operativos: 55000, flujo_caja_operativo: -43600 },
    charts: {
      ventas_por_mes: [{ label: 'May', value: 38 }, { label: 'Jun', value: 56 }, { label: 'Jul', value: 72 }],
      stock_por_producto: [{ label: 'Pale Ale', value: 104 }, { label: 'Stout', value: 56 }],
      gastos_por_categoria: [{ label: 'Mantencion', value: 55000 }, { label: 'Servicios', value: 120000 }],
    },
    alerts: [
      { type: 'stock', severity: 'warning', message: 'low_stock', entity: 'supplies', entity_id: 2 },
      { type: 'compra', severity: 'info', message: 'purchase_order_pending', entity: 'purchase_orders', entity_id: 1 },
      { type: 'equipo', severity: 'warning', message: 'equipment_review_overdue', entity: 'equipment', entity_id: 1 },
    ],
    monthly_goal: { month: '2026-07', progress: { litros_produccion: { target: 100, actual: 90, pct: 90 }, monto_ventas: { target: 100000, actual: 11400, pct: 11.4 } } },
    deployment_status: { dockerized: true, ec2_ready: true, proxy_tls_prepared: true, deploy_executed: false, real_secrets_used: false },
  },
  reports: {
    reports: [
      { type: 'produccion', formats: ['csv', 'xlsx', 'pdf'], row_count: 2 },
      { type: 'ventas', formats: ['csv', 'xlsx', 'pdf'], row_count: 1 },
      { type: 'inventario', formats: ['csv', 'xlsx', 'pdf'], row_count: 2 },
      { type: 'financiero', formats: ['csv', 'xlsx', 'pdf'], row_count: 1 },
    ],
    export_jobs: [],
  },
  equipment: {
    types: [{ id: 1, nombre: 'Fermentador' }, { id: 2, nombre: 'Bomba' }],
    equipment: [
      { id: 1, codigo: 'EQ-001', nombre: 'Fermentador piloto', tipo: 'Fermentador', estado: 'operativo', proxima_revision: '2026-07-01', revision_vencida: true, movements: [] },
      { id: 2, codigo: 'EQ-002', nombre: 'Bomba trasvasije', tipo: 'Bomba', estado: 'mantenimiento', proxima_revision: '2026-07-18', revision_vencida: false, movements: [] },
    ],
  },
  expenses: {
    categories: [{ id: 1, nombre: 'Insumos indirectos' }, { id: 2, nombre: 'Mantencion' }, { id: 3, nombre: 'Servicios' }],
    expenses: [
      { id: 1, concepto: 'Mantencion bomba', categoria_nombre: 'Mantencion', monto: 55000, fecha: today, proveedor: 'Servicio local' },
      { id: 2, concepto: 'Servicios julio', categoria_nombre: 'Servicios', monto: 120000, fecha: today, proveedor: 'Proveedor local' },
    ],
    total: 175000,
  },
  smtp: { host: 'localhost', port: 1025, username: 'sandbox', enabled: true, from_email: 'alerts@brewmaster.local', password_configured: false },
  notifications: [
    { id: 1, type: 'stock', estado: 'pendiente', attempts: 0, recipient: 'stock@brewmaster.local', message: 'low_stock' },
  ],
  goals: [
    { month: '2026-07', litros_produccion: 100, monto_ventas: 100000, num_clientes: 3, margen_promedio_pct: 20, progress: { litros_produccion: { pct: 90 } } },
  ],
  jobs: { policy: { scheduler: 'APScheduler', jobs: ['stock_alerts', 'email_retries', 'reservation_expiration', 'deferred_exports', 'low_activity_backup'], backup_jobs: true }, low_activity_backup_enabled: true },
  backups: { backups: [{ id: 1, job: 'low_activity_backup', estado: 'completado', archivo_url: 'local://sandbox/backups/brewmaster-0001.sql.gz', external_write: false, deploy_executed: false }], policy: { backup_jobs: true } },
  users: [
    { id: 1, nombre: 'Admin', email: 'admin@brewmaster.local', role: 'admin', estado: 'activo' },
  ],
  audit: [
    { id: 1, action: 'login_success', entity: 'users', entity_id: 1, created_at: `${today}T08:00:00` },
  ],
};

const supplyTypes = ['malta', 'lupulo', 'levadura', 'adjunto', 'envase', 'limpieza', 'otro'];
const customerTypes = ['minorista', 'mayorista', 'distribuidor'];
const reportFormats = ['csv', 'xlsx', 'pdf'];

function money(value) {
  return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(Number(value || 0));
}

function number(value) {
  return new Intl.NumberFormat('es-CL', { maximumFractionDigits: 2 }).format(Number(value || 0));
}

function asList(payload, key) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.[key])) return payload[key];
  return [];
}

function first(items, fallbackItem = {}) {
  return items[0] || fallbackItem;
}

function optionItems(items, labelKey = 'nombre') {
  return items.map((item) => ({ value: item.id, label: item[labelKey] || item.nombre || item.codigo || item.id }));
}

function parseError(error) {
  if (!error) return '';
  return error.message || error.code || String(error);
}

function useResources(requests) {
  const signature = requests.map((request) => `${request.key}:${request.path}`).join('|');
  const [state, setState] = useState({ data: {}, errors: [], loading: true });
  const reload = () => {
    setState((current) => ({ ...current, loading: true }));
    Promise.all(
      requests.map(async (request) => {
        try {
          const data = await api(request.path);
          return { key: request.key, data, error: null, endpoint: request.path };
        } catch (error) {
          return { key: request.key, data: request.fallback, error, endpoint: request.path };
        }
      }),
    ).then((results) => {
      const data = {};
      const errors = [];
      results.forEach((result) => {
        data[result.key] = result.data;
        if (result.error) errors.push({ endpoint: result.endpoint, error: result.error });
      });
      setState({ data, errors, loading: false });
    });
  };
  useEffect(reload, [signature]);
  return { ...state, reload, endpoints: requests.map((request) => request.path) };
}

function collectForm(event, numericFields = [], booleanFields = []) {
  const formData = new FormData(event.currentTarget);
  const payload = {};
  formData.forEach((value, key) => {
    payload[key] = value;
  });
  numericFields.forEach((field) => {
    if (payload[field] !== undefined && payload[field] !== '') payload[field] = Number(payload[field]);
  });
  booleanFields.forEach((field) => {
    payload[field] = formData.get(field) === 'on';
  });
  return payload;
}

function required(payload, fields) {
  return fields.filter((field) => payload[field] === undefined || payload[field] === null || String(payload[field]).trim() === '');
}

function positive(payload, fields) {
  return fields.filter((field) => Number(payload[field]) <= 0 || Number.isNaN(Number(payload[field])));
}

function StatusBadge({ value }) {
  const normalized = String(value || '').toLowerCase();
  const tone = ['activo', 'confirmada', 'completado', 'operativo', 'recibida', 'completada'].includes(normalized)
    ? 'text-bg-success'
    : ['borrador', 'en_elaboracion', 'pendiente', 'activa', 'enviada', 'mantenimiento'].includes(normalized)
      ? 'text-bg-warning'
      : ['inactivo', 'cancelado', 'anulada', 'descartado', 'rechazado'].includes(normalized)
        ? 'text-bg-secondary'
        : 'text-bg-light border';
  return <span className={`badge ${tone}`}>{value || 'sin estado'}</span>;
}

function EndpointStatus({ loading, errors, endpoints }) {
  return (
    <div className="d-flex flex-wrap align-items-center gap-2">
      {loading ? <span className="badge text-bg-light border"><RefreshCw size={13} aria-hidden="true" /> cargando</span> : <span className="badge text-bg-light border"><CheckCircle2 size={13} aria-hidden="true" /> render</span>}
      {endpoints.map((endpoint) => (
        <span className="badge text-bg-light border" key={endpoint}>{endpoint}</span>
      ))}
      {errors.length ? <span className="badge text-bg-warning"><AlertTriangle size={13} aria-hidden="true" /> {errors.length}</span> : null}
    </div>
  );
}

function ScreenFrame({ children, endpoints = [], errors = [], loading = false, actions = null }) {
  return (
    <div className="d-grid gap-3">
      <div className="d-flex flex-wrap align-items-center justify-content-between gap-2">
        <EndpointStatus loading={loading} errors={errors} endpoints={endpoints} />
        {actions}
      </div>
      {errors.length ? (
        <div className="alert alert-warning mb-0" role="alert">
          {errors.map((item) => `${item.endpoint}: ${parseError(item.error)}`).join(' | ')}
        </div>
      ) : null}
      {children}
    </div>
  );
}

function Panel({ title, icon: Icon, children, action = null }) {
  return (
    <section className="bm-panel">
      <div className="d-flex align-items-center justify-content-between gap-2 p-3 border-bottom">
        <h3 className="h6 mb-0">{Icon ? <Icon size={17} aria-hidden="true" /> : null} {title}</h3>
        {action}
      </div>
      <div className="p-3">{children}</div>
    </section>
  );
}

function EmptyState({ message = 'Sin registros' }) {
  return <div className="text-center text-secondary py-4 border rounded-2 bg-light">{message}</div>;
}

function DataTable({ columns, rows, empty = 'Sin registros' }) {
  if (!rows.length) return <EmptyState message={empty} />;
  return (
    <div className="table-responsive">
      <table className="table table-sm align-middle mb-0">
        <thead>
          <tr>{columns.map((column) => <th key={column.key || column.label}>{column.label}</th>)}</tr>
        </thead>
        <tbody>
        {rows.map((row, index) => (
            <tr key={`${row.id || row.codigo || row.numero_lote || row.numero_orden || 'row'}-${index}`}>
              {columns.map((column) => (
                <td key={column.key || column.label}>{column.render ? column.render(row) : row[column.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function KpiGrid({ items }) {
  return (
    <div className="row g-3">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <article className="col-12 col-sm-6 col-xl-3" key={item.label}>
            <div className="bm-panel p-3 h-100">
              <div className="d-flex align-items-center justify-content-between">
                <span className="text-secondary small">{item.label}</span>
                <Icon size={20} aria-hidden="true" />
              </div>
              <p className="fs-3 fw-semibold mb-0">{item.value}</p>
              <span className={`badge ${item.tone || 'text-bg-light border'}`}>{item.note}</span>
            </div>
          </article>
        );
      })}
    </div>
  );
}

function Bars({ items, max }) {
  const ceiling = max || Math.max(...items.map((item) => Number(item.value || 0)), 1);
  return (
    <div className="d-grid gap-2">
      {items.map((item) => (
        <div className="d-grid gap-1" key={item.label}>
          <div className="d-flex justify-content-between small">
            <span>{item.label}</span>
            <strong>{number(item.value)}</strong>
          </div>
          <div className="progress" style={{ height: 10 }}>
            <div className="progress-bar bg-success" style={{ width: `${Math.min((Number(item.value || 0) / ceiling) * 100, 100)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function RelatedNav({ navigate, items }) {
  return (
    <div className="d-flex flex-wrap gap-2">
      {items.map((item) => (
        <button className="btn btn-sm btn-outline-primary" type="button" key={item.path} onClick={() => navigate(item.path)}>
          {item.icon ? <item.icon size={15} aria-hidden="true" /> : null} {item.label}
        </button>
      ))}
    </div>
  );
}

function ActionForm({ title, icon: Icon = Save, fields, submitLabel, endpoint, method = 'POST', numeric = [], boolean = [], requireFields = [], positiveFields = [], transform, onDone }) {
  const [status, setStatus] = useState(null);
  async function handleSubmit(event) {
    event.preventDefault();
    const payload = collectForm(event, numeric, boolean);
    const missing = required(payload, requireFields);
    const invalidPositive = positive(payload, positiveFields);
    if (missing.length || invalidPositive.length) {
      setStatus({ type: 'warning', text: `Validar: ${[...missing, ...invalidPositive].join(', ')}` });
      return;
    }
    try {
      const body = transform ? transform(payload) : payload;
      await api(typeof endpoint === 'function' ? endpoint(body) : endpoint, { method, body });
      setStatus({ type: 'success', text: 'Guardado local' });
      if (onDone) onDone();
    } catch (error) {
      setStatus({ type: 'danger', text: parseError(error) });
    }
  }
  return (
    <form className="d-grid gap-3" onSubmit={handleSubmit}>
      <div className="d-flex align-items-center gap-2">
        <Icon size={18} aria-hidden="true" />
        <h3 className="h6 mb-0">{title}</h3>
      </div>
      <div className="row g-3">
        {fields.map((field) => (
          <div className={field.wide ? 'col-12' : 'col-12 col-md-6'} key={field.name}>
            {field.type === 'checkbox' ? (
              <div className="form-check mt-4">
                <input className="form-check-input" id={field.name} name={field.name} type="checkbox" defaultChecked={field.defaultChecked} />
                <label className="form-check-label" htmlFor={field.name}>{field.label}</label>
              </div>
            ) : (
              <>
                <label className="form-label" htmlFor={field.name}>{field.label}</label>
                {field.type === 'select' ? (
                  <select className="form-select" id={field.name} name={field.name} defaultValue={field.defaultValue || field.options?.[0]?.value || ''}>
                    {(field.options || []).map((option, index) => <option key={`${option.value}-${index}`} value={option.value}>{option.label}</option>)}
                  </select>
                ) : (
                  <input className="form-control" id={field.name} name={field.name} type={field.type || 'text'} defaultValue={field.defaultValue || ''} min={field.min} step={field.step} />
                )}
              </>
            )}
          </div>
        ))}
      </div>
      {status ? <div className={`alert alert-${status.type} mb-0`}>{status.text}</div> : null}
      <button className="btn btn-primary justify-self-start" type="submit">
        <Icon size={16} aria-hidden="true" /> {submitLabel}
      </button>
    </form>
  );
}

export function LoginScreen({ onSessionChange, navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'me', path: '/auth/me', fallback: getStoredUser() || fallback.me }]);
  const [status, setStatus] = useState(null);
  async function handleLogin(event) {
    event.preventDefault();
    const payload = collectForm(event);
    const missing = required(payload, ['email', 'password']);
    if (missing.length) {
      setStatus({ type: 'warning', text: `Validar: ${missing.join(', ')}` });
      return;
    }
    try {
      const session = await login(payload);
      setSession(session);
      onSessionChange(session.user);
      setStatus({ type: 'success', text: 'Sesion iniciada' });
      reload();
      navigate('/');
    } catch (error) {
      setStatus({ type: 'danger', text: parseError(error) });
    }
  }
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints}>
      <div className="row g-3">
        <div className="col-12 col-xl-5">
          <Panel title="Acceso" icon={KeyRound}>
            <form className="d-grid gap-3" onSubmit={handleLogin}>
              <div>
                <label className="form-label" htmlFor="email">Correo</label>
                <input className="form-control" id="email" name="email" type="email" defaultValue="admin@brewmaster.local" />
              </div>
              <div>
                <label className="form-label" htmlFor="password">Contrasena</label>
                <input className="form-control" id="password" name="password" type="password" autoComplete="current-password" />
              </div>
              {status ? <div className={`alert alert-${status.type} mb-0`}>{status.text}</div> : null}
              <button className="btn btn-primary" type="submit"><ShieldCheck size={16} aria-hidden="true" /> Ingresar</button>
            </form>
          </Panel>
        </div>
        <div className="col-12 col-xl-7">
          <Panel title="Sesion" icon={UserPlus}>
            <DataTable
              columns={[
                { label: 'Correo', key: 'email' },
                { label: 'Rol', key: 'role' },
                { label: 'Permisos', render: (row) => (row.permissions || []).join(', ') || '*' },
              ]}
              rows={[data.me || fallback.me]}
            />
          </Panel>
        </div>
      </div>
    </ScreenFrame>
  );
}

export function PasswordRecoveryScreen() {
  return (
    <ScreenFrame endpoints={['/auth/password-reset/request', '/auth/password-reset/confirm']}>
      <div className="row g-3">
        <div className="col-12 col-xl-6">
          <Panel title="Solicitud" icon={MailCheck}>
            <ActionForm
              title="Enviar token local"
              fields={[{ name: 'email', label: 'Correo', type: 'email', defaultValue: 'admin@brewmaster.local', wide: true }]}
              endpoint="/auth/password-reset/request"
              submitLabel="Solicitar"
              requireFields={['email']}
            />
          </Panel>
        </div>
        <div className="col-12 col-xl-6">
          <Panel title="Confirmacion" icon={KeyRound}>
            <ActionForm
              title="Cambiar contrasena"
              fields={[
                { name: 'token', label: 'Token local', wide: true },
                { name: 'new_password', label: 'Nueva contrasena', type: 'password', wide: true },
              ]}
              endpoint="/auth/password-reset/confirm"
              submitLabel="Confirmar"
              requireFields={['token', 'new_password']}
            />
          </Panel>
        </div>
      </div>
    </ScreenFrame>
  );
}

export function DashboardScreen({ navigate }) {
  const { data, errors, loading, endpoints } = useResources([{ key: 'dashboard', path: '/dashboard', fallback: fallback.dashboard }]);
  const payload = data.dashboard || fallback.dashboard;
  const kpis = payload.kpis || {};
  const charts = payload.charts || {};
  const goals = payload.monthly_goal?.progress || {};
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Reportes', path: '/reports', icon: FileSpreadsheet }, { label: 'Metas', path: '/settings', icon: Settings }]} />}>
      <KpiGrid
        items={[
          { label: 'Litros', value: number(kpis.litros_producidos), note: 'produccion', icon: Factory, tone: 'text-bg-success' },
          { label: 'Stock libre', value: number(kpis.stock_libre), note: 'unidades', icon: PackageCheck, tone: 'text-bg-primary' },
          { label: 'Ventas', value: money(kpis.monto_ventas), note: 'confirmadas', icon: ShoppingCart, tone: 'text-bg-info' },
          { label: 'Alertas', value: number(kpis.alertas_operacionales), note: 'operacionales', icon: AlertTriangle, tone: 'text-bg-warning' },
        ]}
      />
      <div className="row g-3">
        <div className="col-12 col-xl-7"><Panel title="Ventas por mes" icon={BarChart3}><Bars items={charts.ventas_por_mes || []} /></Panel></div>
        <div className="col-12 col-xl-5"><Panel title="Stock por producto" icon={PackageCheck}><Bars items={charts.stock_por_producto || []} /></Panel></div>
        <div className="col-12 col-xl-5">
          <Panel title="Alertas" icon={AlertTriangle}>
            <DataTable
              columns={[{ label: 'Tipo', key: 'type' }, { label: 'Mensaje', key: 'message' }, { label: 'Severidad', render: (row) => <StatusBadge value={row.severity} /> }]}
              rows={payload.alerts || []}
            />
          </Panel>
        </div>
        <div className="col-12 col-xl-7">
          <Panel title="Metas mensuales" icon={ClipboardCheck}>
            <DataTable
              columns={[
                { label: 'Indicador', key: 'label' },
                { label: 'Real', render: (row) => number(row.actual) },
                { label: 'Meta', render: (row) => number(row.target) },
                { label: 'Avance', render: (row) => `${number(row.pct)}%` },
              ]}
              rows={Object.entries(goals).map(([label, value]) => ({ label, ...value }))}
            />
          </Panel>
        </div>
      </div>
    </ScreenFrame>
  );
}

export function SuppliesListScreen({ navigate }) {
  const { data, errors, loading, endpoints } = useResources([
    { key: 'supplies', path: '/supplies', fallback: fallback.supplies },
    { key: 'low', path: '/supplies/low-stock', fallback: fallback.supplies.filter((item) => item.stock_actual < item.stock_minimo) },
  ]);
  const supplies = asList(data.supplies, 'supplies');
  const low = asList(data.low, 'supplies');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Nuevo', path: '/supplies/1', icon: PackagePlus }, { label: 'Kardex', path: '/supplies/1/kardex', icon: ClipboardList }, { label: 'Entrada', path: '/supply-entries/new', icon: Truck }]} />}>
      <KpiGrid
        items={[
          { label: 'Insumos', value: supplies.length, note: 'catalogo', icon: PackageCheck, tone: 'text-bg-primary' },
          { label: 'Bajo minimo', value: low.length, note: 'alertas', icon: AlertTriangle, tone: 'text-bg-warning' },
          { label: 'Stock total', value: number(supplies.reduce((sum, item) => sum + Number(item.stock_actual || 0), 0)), note: 'unidades', icon: Warehouse, tone: 'text-bg-success' },
          { label: 'Activos', value: supplies.filter((item) => item.estado === 'activo').length, note: 'operacion', icon: CheckCircle2, tone: 'text-bg-info' },
        ]}
      />
      <Panel title="Listado" icon={PackageCheck}>
        <DataTable
          columns={[
            { label: 'Codigo', key: 'codigo' },
            { label: 'Insumo', key: 'nombre' },
            { label: 'Tipo', key: 'tipo' },
            { label: 'Stock', render: (row) => `${number(row.stock_actual)} ${row.unidad_medida || ''}` },
            { label: 'Minimo', render: (row) => number(row.stock_minimo) },
            { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> },
          ]}
          rows={supplies}
        />
      </Panel>
    </ScreenFrame>
  );
}

export function SupplyFormScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([
    { key: 'supply', path: '/supplies/1', fallback: first(fallback.supplies) },
    { key: 'suppliers', path: '/suppliers', fallback: fallback.suppliers },
    { key: 'warehouses', path: '/warehouses', fallback: fallback.warehouses },
  ]);
  const supply = data.supply || first(fallback.supplies);
  const suppliers = asList(data.suppliers, 'suppliers');
  const warehouses = asList(data.warehouses, 'warehouses');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Listado', path: '/supplies', icon: PackageCheck }, { label: 'Kardex', path: '/supplies/1/kardex', icon: ClipboardList }]} />}>
      <Panel title="Ficha de insumo" icon={PackagePlus}>
        <ActionForm
          title="Guardar insumo"
          endpoint={(body) => (body.id ? `/supplies/${body.id}` : '/supplies')}
          method="PUT"
          submitLabel="Guardar"
          numeric={['id', 'proveedor_id', 'bodega_id', 'costo_unitario', 'stock_minimo', 'stock_actual']}
          requireFields={['codigo', 'nombre', 'tipo', 'unidad_medida', 'proveedor_id', 'bodega_id']}
          fields={[
            { name: 'id', label: 'ID', type: 'number', defaultValue: supply.id },
            { name: 'codigo', label: 'Codigo', defaultValue: supply.codigo },
            { name: 'nombre', label: 'Nombre', defaultValue: supply.nombre },
            { name: 'tipo', label: 'Tipo', type: 'select', defaultValue: supply.tipo, options: supplyTypes.map((item) => ({ value: item, label: item })) },
            { name: 'unidad_medida', label: 'Unidad', defaultValue: supply.unidad_medida || 'kg' },
            { name: 'proveedor_id', label: 'Proveedor', type: 'select', defaultValue: supply.proveedor_id || suppliers[0]?.id, options: optionItems(suppliers) },
            { name: 'bodega_id', label: 'Bodega', type: 'select', defaultValue: supply.bodega_id || warehouses[0]?.id, options: optionItems(warehouses) },
            { name: 'costo_unitario', label: 'Costo unitario', type: 'number', defaultValue: supply.costo_unitario, min: 0 },
            { name: 'stock_minimo', label: 'Stock minimo', type: 'number', defaultValue: supply.stock_minimo, min: 0 },
            { name: 'stock_actual', label: 'Stock actual', type: 'number', defaultValue: supply.stock_actual, min: 0 },
          ]}
          onDone={reload}
        />
      </Panel>
    </ScreenFrame>
  );
}

export function SupplyKardexScreen({ navigate }) {
  const { data, errors, loading, endpoints } = useResources([
    { key: 'kardex', path: '/supplies/1/kardex', fallback: fallback.kardex },
    { key: 'supplies', path: '/supplies', fallback: fallback.supplies },
  ]);
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Insumos', path: '/supplies', icon: PackageCheck }, { label: 'Entrada', path: '/supply-entries/new', icon: PackagePlus }]} />}>
      <Panel title="Movimientos de insumo" icon={ClipboardList}>
        <DataTable
          columns={[
            { label: 'Fecha', render: (row) => String(row.created_at || '').slice(0, 10) },
            { label: 'Movimiento', key: 'tipo_movimiento' },
            { label: 'Cantidad', render: (row) => number(row.cantidad) },
            { label: 'Saldo', render: (row) => number(row.saldo_resultante) },
            { label: 'Costo', render: (row) => money(row.costo_unitario) },
            { label: 'Referencia', key: 'referencia' },
          ]}
          rows={asList(data.kardex, 'kardex')}
        />
      </Panel>
    </ScreenFrame>
  );
}

export function SupplyEntryScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([
    { key: 'entries', path: '/supply-entries', fallback: fallback.entries },
    { key: 'supplies', path: '/supplies', fallback: fallback.supplies },
  ]);
  const supplies = asList(data.supplies, 'supplies');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Insumos', path: '/supplies', icon: PackageCheck }, { label: 'Kardex', path: '/supplies/1/kardex', icon: ClipboardList }]} />}>
      <div className="row g-3">
        <div className="col-12 col-xl-5">
          <Panel title="Registrar entrada" icon={Truck}>
            <ActionForm
              title="Entrada"
              endpoint="/supply-entries"
              submitLabel="Registrar"
              numeric={['supply_id', 'cantidad', 'costo_unitario']}
              requireFields={['supply_id', 'cantidad', 'costo_unitario']}
              positiveFields={['cantidad']}
              fields={[
                { name: 'supply_id', label: 'Insumo', type: 'select', options: optionItems(supplies), defaultValue: supplies[0]?.id },
                { name: 'cantidad', label: 'Cantidad', type: 'number', defaultValue: 10, min: 0.01, step: 0.01 },
                { name: 'costo_unitario', label: 'Costo unitario', type: 'number', defaultValue: first(supplies).costo_unitario || 0, min: 0 },
                { name: 'documento_referencia', label: 'Documento', defaultValue: 'FAC-LOCAL-001' },
              ]}
              onDone={reload}
            />
          </Panel>
        </div>
        <div className="col-12 col-xl-7">
          <Panel title="Entradas" icon={ClipboardList}>
            <DataTable
              columns={[{ label: 'Fecha', render: (row) => String(row.created_at || '').slice(0, 10) }, { label: 'Insumo', render: (row) => row.supply_name || row.nombre_insumo || row.supply_id }, { label: 'Cantidad', render: (row) => number(row.cantidad) }, { label: 'Costo', render: (row) => money(row.costo_unitario) }, { label: 'Documento', key: 'documento_referencia' }]}
              rows={asList(data.entries, 'entries')}
            />
          </Panel>
        </div>
      </div>
    </ScreenFrame>
  );
}

export function SuppliersListScreen({ navigate }) {
  const { data, errors, loading, endpoints } = useResources([{ key: 'suppliers', path: '/suppliers', fallback: fallback.suppliers }]);
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Formulario', path: '/suppliers/1', icon: UserPlus }]} />}>
      <Panel title="Proveedores" icon={Truck}>
        <DataTable
          columns={[{ label: 'Codigo', key: 'codigo' }, { label: 'Proveedor', key: 'nombre' }, { label: 'Correo', key: 'email' }, { label: 'Contacto', key: 'contacto' }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }]}
          rows={asList(data.suppliers, 'suppliers')}
        />
      </Panel>
    </ScreenFrame>
  );
}

export function SupplierFormScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'suppliers', path: '/suppliers', fallback: fallback.suppliers }]);
  const supplier = first(asList(data.suppliers, 'suppliers'), first(fallback.suppliers));
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Listado', path: '/suppliers', icon: Truck }]} />}>
      <Panel title="Ficha de proveedor" icon={UserPlus}>
        <ActionForm
          title="Guardar proveedor"
          endpoint={(body) => (body.id ? `/suppliers/${body.id}` : '/suppliers')}
          method="PUT"
          submitLabel="Guardar"
          numeric={['id']}
          requireFields={['codigo', 'nombre']}
          fields={[
            { name: 'id', label: 'ID', type: 'number', defaultValue: supplier.id },
            { name: 'codigo', label: 'Codigo', defaultValue: supplier.codigo },
            { name: 'nombre', label: 'Nombre', defaultValue: supplier.nombre },
            { name: 'email', label: 'Correo', type: 'email', defaultValue: supplier.email },
            { name: 'telefono', label: 'Telefono', defaultValue: supplier.telefono || '' },
            { name: 'contacto', label: 'Contacto', defaultValue: supplier.contacto || '' },
          ]}
          onDone={reload}
        />
      </Panel>
    </ScreenFrame>
  );
}

export function RecipesListScreen({ navigate }) {
  const { data, errors, loading, endpoints } = useResources([{ key: 'recipes', path: '/recipes', fallback: fallback.recipes }]);
  const recipes = asList(data.recipes, 'recipes');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Formulario', path: '/recipes/1', icon: FlaskConical }, { label: 'Presentaciones', path: '/presentation-types', icon: PackageCheck }]} />}>
      <Panel title="Recetas" icon={FlaskConical}>
        <DataTable
          columns={[{ label: 'Nombre', key: 'nombre' }, { label: 'Tipo', key: 'tipo' }, { label: 'Volumen', render: (row) => `${number(row.volumen_por_lote)} L` }, { label: 'Costo', render: (row) => money(row.costo_estimado) }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }]}
          rows={recipes}
        />
      </Panel>
    </ScreenFrame>
  );
}

export function RecipeFormScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([
    { key: 'recipe', path: '/recipes/1', fallback: first(fallback.recipes) },
    { key: 'supplies', path: '/supplies', fallback: fallback.supplies },
  ]);
  const recipe = data.recipe || first(fallback.recipes);
  const supplies = asList(data.supplies, 'supplies');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Recetas', path: '/recipes', icon: FlaskConical }]} />}>
      <Panel title="Ficha de receta" icon={FlaskConical}>
        <ActionForm
          title="Guardar receta"
          endpoint={(body) => (body.id ? `/recipes/${body.id}` : '/recipes')}
          method="PUT"
          submitLabel="Guardar"
          numeric={['id', 'volumen_por_lote', 'supply_id', 'cantidad']}
          requireFields={['nombre', 'tipo', 'volumen_por_lote', 'supply_id', 'cantidad']}
          positiveFields={['volumen_por_lote', 'cantidad']}
          transform={(body) => ({ id: body.id, nombre: body.nombre, tipo: body.tipo, volumen_por_lote: body.volumen_por_lote, ingredientes: [{ supply_id: body.supply_id, cantidad: body.cantidad, unidad: body.unidad || 'kg' }] })}
          fields={[
            { name: 'id', label: 'ID', type: 'number', defaultValue: recipe.id },
            { name: 'nombre', label: 'Nombre', defaultValue: recipe.nombre },
            { name: 'tipo', label: 'Tipo', defaultValue: recipe.tipo },
            { name: 'volumen_por_lote', label: 'Volumen por lote', type: 'number', defaultValue: recipe.volumen_por_lote, min: 0.01 },
            { name: 'supply_id', label: 'Insumo principal', type: 'select', options: optionItems(supplies), defaultValue: first(recipe.ingredientes || []).supply_id || supplies[0]?.id },
            { name: 'cantidad', label: 'Cantidad', type: 'number', defaultValue: first(recipe.ingredientes || []).cantidad || 1, min: 0.01, step: 0.01 },
            { name: 'unidad', label: 'Unidad', defaultValue: first(recipe.ingredientes || []).unidad || 'kg' },
          ]}
          onDone={reload}
        />
      </Panel>
    </ScreenFrame>
  );
}

export function WarehousesScreen() {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'warehouses', path: '/warehouses', fallback: fallback.warehouses }]);
  const warehouses = asList(data.warehouses, 'warehouses');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints}>
      <div className="row g-3">
        <div className="col-12 col-xl-7">
          <Panel title="Bodegas" icon={Warehouse}>
            <DataTable columns={[{ label: 'Codigo', key: 'codigo' }, { label: 'Nombre', key: 'nombre' }, { label: 'Tipo', key: 'tipo' }, { label: 'Capacidad', render: (row) => number(row.capacidad) }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }]} rows={warehouses} />
          </Panel>
        </div>
        <div className="col-12 col-xl-5">
          <Panel title="Formulario" icon={Save}>
            <ActionForm
              title="Guardar bodega"
              endpoint="/warehouses"
              submitLabel="Crear"
              numeric={['capacidad']}
              boolean={['temperatura_controlada']}
              requireFields={['codigo', 'nombre', 'tipo']}
              fields={[{ name: 'codigo', label: 'Codigo', defaultValue: 'BOD-LOCAL' }, { name: 'nombre', label: 'Nombre', defaultValue: 'Bodega local' }, { name: 'tipo', label: 'Tipo', defaultValue: 'insumos' }, { name: 'capacidad', label: 'Capacidad', type: 'number', defaultValue: 100 }, { name: 'temperatura_controlada', label: 'Temperatura controlada', type: 'checkbox' }]}
              onDone={reload}
            />
          </Panel>
        </div>
      </div>
    </ScreenFrame>
  );
}

export function PresentationTypesScreen() {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'presentations', path: '/presentation-types', fallback: fallback.presentations }]);
  const presentations = asList(data.presentations, 'presentations');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints}>
      <div className="row g-3">
        <div className="col-12 col-xl-7">
          <Panel title="Presentaciones" icon={PackageCheck}>
            <DataTable columns={[{ label: 'Nombre', key: 'nombre' }, { label: 'Volumen', render: (row) => `${number(row.volumen)} ${row.unidad}` }, { label: 'Costo', render: (row) => money(row.costo_presentacion) }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }]} rows={presentations} />
          </Panel>
        </div>
        <div className="col-12 col-xl-5">
          <Panel title="Formulario" icon={Save}>
            <ActionForm
              title="Guardar presentacion"
              endpoint="/presentation-types"
              submitLabel="Crear"
              numeric={['volumen', 'costo_presentacion']}
              requireFields={['nombre', 'volumen', 'unidad']}
              positiveFields={['volumen']}
              fields={[{ name: 'nombre', label: 'Nombre', defaultValue: 'Botella 355' }, { name: 'volumen', label: 'Volumen', type: 'number', defaultValue: 355, min: 1 }, { name: 'unidad', label: 'Unidad', defaultValue: 'ml' }, { name: 'costo_presentacion', label: 'Costo', type: 'number', defaultValue: 130, min: 0 }]}
              onDone={reload}
            />
          </Panel>
        </div>
      </div>
    </ScreenFrame>
  );
}

export function BatchesListScreen({ navigate }) {
  const { data, errors, loading, endpoints } = useResources([{ key: 'batches', path: '/batches', fallback: fallback.batches }]);
  const batches = asList(data.batches, 'batches');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Formulario', path: '/batches/1', icon: Factory }, { label: 'Detalle', path: '/batches/1/detail', icon: ClipboardList }, { label: 'Calidad', path: '/batches/1/quality', icon: ClipboardCheck }]} />}>
      <Panel title="Lotes" icon={Factory}>
        <DataTable columns={[{ label: 'Lote', key: 'numero_lote' }, { label: 'Receta', key: 'recipe_name' }, { label: 'Presentacion', key: 'presentation_name' }, { label: 'Litros', render: (row) => number(row.cantidad_producida) }, { label: 'Fecha', key: 'fecha_produccion' }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }]} rows={batches} />
      </Panel>
    </ScreenFrame>
  );
}

export function BatchFormScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([
    { key: 'batch', path: '/batches/1', fallback: first(fallback.batches) },
    { key: 'recipes', path: '/recipes', fallback: fallback.recipes },
    { key: 'presentations', path: '/presentation-types', fallback: fallback.presentations },
  ]);
  const batch = data.batch || first(fallback.batches);
  const recipes = asList(data.recipes, 'recipes');
  const presentations = asList(data.presentations, 'presentations');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Lotes', path: '/batches', icon: Factory }, { label: 'Detalle', path: '/batches/1/detail', icon: ClipboardList }]} />}>
      <Panel title="Ficha de lote" icon={Factory}>
        <ActionForm
          title="Guardar lote"
          endpoint={(body) => (body.id ? `/batches/${body.id}` : '/batches')}
          method="PUT"
          submitLabel="Guardar"
          numeric={['id', 'recipe_id', 'presentation_type_id', 'cantidad_producida', 'horas_mano_obra', 'kwh_consumidos', 'litros_agua', 'porcentaje_merma']}
          requireFields={['recipe_id', 'presentation_type_id', 'cantidad_producida', 'fecha_produccion']}
          positiveFields={['cantidad_producida']}
          fields={[
            { name: 'id', label: 'ID', type: 'number', defaultValue: batch.id },
            { name: 'recipe_id', label: 'Receta', type: 'select', options: optionItems(recipes), defaultValue: batch.recipe_id || recipes[0]?.id },
            { name: 'presentation_type_id', label: 'Presentacion', type: 'select', options: optionItems(presentations), defaultValue: batch.presentation_type_id || presentations[0]?.id },
            { name: 'cantidad_producida', label: 'Litros', type: 'number', defaultValue: batch.cantidad_producida, min: 0.01 },
            { name: 'fecha_produccion', label: 'Fecha', type: 'date', defaultValue: batch.fecha_produccion || today },
            { name: 'horas_mano_obra', label: 'Horas mano obra', type: 'number', defaultValue: batch.horas_mano_obra || 0, min: 0 },
            { name: 'kwh_consumidos', label: 'KWh', type: 'number', defaultValue: batch.kwh_consumidos || 0, min: 0 },
            { name: 'litros_agua', label: 'Litros agua', type: 'number', defaultValue: batch.litros_agua || 0, min: 0 },
            { name: 'porcentaje_merma', label: 'Merma %', type: 'number', defaultValue: batch.porcentaje_merma || 0, min: 0 },
          ]}
          onDone={reload}
        />
      </Panel>
    </ScreenFrame>
  );
}

export function BatchDetailScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'batch', path: '/batches/1', fallback: { ...first(fallback.batches), snapshots: fallback.kardex, quality_check: null } }]);
  const batch = data.batch || first(fallback.batches);
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Lotes', path: '/batches', icon: Factory }, { label: 'Calidad', path: '/batches/1/quality', icon: ClipboardCheck }]} />}>
      <KpiGrid items={[{ label: 'Lote', value: batch.numero_lote || `#${batch.id}`, note: batch.estado, icon: Factory, tone: 'text-bg-primary' }, { label: 'Litros', value: number(batch.cantidad_producida), note: 'producidos', icon: PackageCheck, tone: 'text-bg-success' }, { label: 'Costo total', value: money(batch.costo_total), note: 'calculado', icon: FileSpreadsheet, tone: 'text-bg-info' }, { label: 'Alertas stock', value: (batch.stock_alerts || []).length, note: 'insumos', icon: AlertTriangle, tone: 'text-bg-warning' }]} />
      <div className="row g-3">
        <div className="col-12 col-xl-6"><Panel title="Requerimientos" icon={ClipboardList}><DataTable columns={[{ label: 'Insumo', render: (row) => row.nombre_insumo || row.supply_id }, { label: 'Cantidad', render: (row) => number(row.cantidad_usada || row.cantidad) }, { label: 'Costo', render: (row) => money(row.costo_unitario) }]} rows={batch.requirements || batch.snapshots || []} /></Panel></div>
        <div className="col-12 col-xl-6"><Panel title="Acciones" icon={CheckCircle2}><RelatedNav navigate={navigate} items={[{ label: 'Completar', path: '/batches/1/detail', icon: CheckCircle2 }, { label: 'Control calidad', path: '/batches/1/quality', icon: ClipboardCheck }]} /><div className="mt-3"><ActionForm title="Completar lote" endpoint="/batches/1/complete" submitLabel="Completar" numeric={['cantidad_producida', 'unidades_producidas']} positiveFields={['cantidad_producida']} fields={[{ name: 'cantidad_producida', label: 'Litros finales', type: 'number', defaultValue: batch.cantidad_producida || 50 }, { name: 'unidades_producidas', label: 'Unidades', type: 'number', defaultValue: 120 }]} onDone={reload} /></div></Panel></div>
      </div>
    </ScreenFrame>
  );
}

export function BatchQualityScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'batch', path: '/batches/1', fallback: { ...fallback.batches[1], quality_check: null } }]);
  const batch = data.batch || fallback.batches[1];
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Detalle', path: '/batches/1/detail', icon: ClipboardList }, { label: 'Lotes', path: '/batches', icon: Factory }]} />}>
      <div className="row g-3">
        <div className="col-12 col-xl-5"><Panel title="Lote" icon={Factory}><DataTable columns={[{ label: 'Campo', key: 'field' }, { label: 'Valor', key: 'value' }]} rows={[{ field: 'Lote', value: batch.numero_lote }, { field: 'Estado', value: batch.estado }, { field: 'Receta', value: batch.recipe_name }, { field: 'Calidad', value: batch.quality_check?.resultado || 'pendiente' }]} /></Panel></div>
        <div className="col-12 col-xl-7">
          <Panel title="Control de calidad" icon={ClipboardCheck}>
            <ActionForm
              title="Registrar control"
              endpoint="/batches/1/quality-check"
              submitLabel="Guardar"
              numeric={['og', 'fg', 'ph', 'temp_fermentacion', 'nota_aroma', 'nota_sabor']}
              requireFields={['resultado', 'og', 'fg', 'ph']}
              positiveFields={['og', 'fg']}
              fields={[
                { name: 'resultado', label: 'Resultado', type: 'select', options: [{ value: 'aprobado', label: 'aprobado' }, { value: 'rechazado', label: 'rechazado' }] },
                { name: 'og', label: 'OG', type: 'number', defaultValue: 1.05, step: 0.001 },
                { name: 'fg', label: 'FG', type: 'number', defaultValue: 1.01, step: 0.001 },
                { name: 'ph', label: 'pH', type: 'number', defaultValue: 4.3, step: 0.1 },
                { name: 'temp_fermentacion', label: 'Temperatura', type: 'number', defaultValue: 18 },
                { name: 'nota_aroma', label: 'Aroma', type: 'number', defaultValue: 8, min: 1 },
                { name: 'nota_sabor', label: 'Sabor', type: 'number', defaultValue: 8, min: 1 },
                { name: 'motivo_rechazo', label: 'Motivo rechazo', wide: true },
              ]}
              onDone={reload}
            />
          </Panel>
        </div>
      </div>
    </ScreenFrame>
  );
}

export function FinishedProductsScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'products', path: '/products', fallback: fallback.products }, { key: 'kardex', path: '/products/1/kardex', fallback: fallback.kardex }]);
  const products = asList(data.products, 'products');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Venta', path: '/sales/new', icon: ShoppingCart }, { label: 'Merma', path: '/waste-records/new', icon: Trash2 }]} />}>
      <div className="row g-3">
        <div className="col-12 col-xl-8"><Panel title="Productos terminados" icon={PackageCheck}><DataTable columns={[{ label: 'Producto', render: (row) => `${row.recipe_name} ${row.presentation_name}` }, { label: 'Stock', render: (row) => number(row.cantidad_stock) }, { label: 'Disponible', render: (row) => number(row.disponible ?? row.cantidad_stock) }, { label: 'Costo', render: (row) => money(row.costo_unitario) }, { label: 'Precio', render: (row) => money(row.precio_venta) }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }]} rows={products} /></Panel></div>
        <div className="col-12 col-xl-4"><Panel title="Precio" icon={Save}><ActionForm title="Actualizar precio" endpoint="/products/1/price" method="PUT" submitLabel="Guardar" numeric={['precio_venta']} requireFields={['precio_venta']} fields={[{ name: 'precio_venta', label: 'Precio venta', type: 'number', defaultValue: first(products).precio_venta || 0, min: 0 }]} onDone={reload} /></Panel></div>
      </div>
    </ScreenFrame>
  );
}

export function WasteRecordsScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'waste', path: '/waste-records', fallback: fallback.waste }, { key: 'supplies', path: '/supplies', fallback: fallback.supplies }, { key: 'products', path: '/products', fallback: fallback.products }]);
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Productos', path: '/finished-products', icon: PackageCheck }, { label: 'Insumos', path: '/supplies', icon: PackagePlus }]} />}>
      <div className="row g-3">
        <div className="col-12 col-xl-5"><Panel title="Registrar merma" icon={Trash2}><ActionForm title="Merma" endpoint="/waste-records" submitLabel="Registrar" numeric={['entidad_id', 'cantidad_perdida', 'batch_id']} requireFields={['tipo_entidad', 'entidad_id', 'cantidad_perdida', 'tipo_merma', 'motivo']} positiveFields={['cantidad_perdida']} fields={[{ name: 'tipo_entidad', label: 'Entidad', type: 'select', options: [{ value: 'insumo', label: 'insumo' }, { value: 'producto', label: 'producto' }] }, { name: 'entidad_id', label: 'ID entidad', type: 'number', defaultValue: 1 }, { name: 'cantidad_perdida', label: 'Cantidad', type: 'number', defaultValue: 1, min: 0.01 }, { name: 'tipo_merma', label: 'Tipo', defaultValue: 'calidad' }, { name: 'motivo', label: 'Motivo', defaultValue: 'registro local', wide: true }, { name: 'batch_id', label: 'Lote', type: 'number', defaultValue: 1 }]} onDone={reload} /></Panel></div>
        <div className="col-12 col-xl-7"><Panel title="Mermas" icon={ClipboardList}><DataTable columns={[{ label: 'Fecha', render: (row) => String(row.created_at || '').slice(0, 10) }, { label: 'Entidad', key: 'tipo_entidad' }, { label: 'ID', key: 'entidad_id' }, { label: 'Cantidad', render: (row) => number(row.cantidad_perdida) }, { label: 'Costo', render: (row) => money(row.costo_total) }, { label: 'Motivo', render: (row) => row.motivo || row.motivo_detallado }]} rows={asList(data.waste, 'waste')} /></Panel></div>
      </div>
    </ScreenFrame>
  );
}

export function CustomersListScreen({ navigate }) {
  const { data, errors, loading, endpoints } = useResources([{ key: 'customers', path: '/customers', fallback: fallback.customers }]);
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Formulario', path: '/customers/1', icon: Users }, { label: 'Venta', path: '/sales/new', icon: ShoppingCart }]} />}>
      <Panel title="Clientes" icon={Users}><DataTable columns={[{ label: 'Cliente', key: 'nombre' }, { label: 'Fiscal', key: 'identificador_fiscal' }, { label: 'Correo', key: 'email' }, { label: 'Tipo', key: 'tipo_cliente' }, { label: 'Credito', render: (row) => money(row.limite_credito) }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }]} rows={asList(data.customers, 'customers')} /></Panel>
    </ScreenFrame>
  );
}

export function CustomerFormScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'customer', path: '/customers/1', fallback: { ...first(fallback.customers), sales: fallback.sales } }]);
  const customer = data.customer || first(fallback.customers);
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Clientes', path: '/customers', icon: Users }, { label: 'Reservas', path: '/reservations', icon: PackageCheck }]} />}>
      <div className="row g-3">
        <div className="col-12 col-xl-6"><Panel title="Ficha cliente" icon={Users}><ActionForm title="Guardar cliente" endpoint={(body) => (body.id ? `/customers/${body.id}` : '/customers')} method="PUT" submitLabel="Guardar" numeric={['id', 'limite_credito']} requireFields={['nombre', 'identificador_fiscal', 'tipo_cliente']} fields={[{ name: 'id', label: 'ID', type: 'number', defaultValue: customer.id }, { name: 'nombre', label: 'Nombre', defaultValue: customer.nombre }, { name: 'identificador_fiscal', label: 'Fiscal', defaultValue: customer.identificador_fiscal }, { name: 'email', label: 'Correo', type: 'email', defaultValue: customer.email }, { name: 'tipo_cliente', label: 'Tipo', type: 'select', defaultValue: customer.tipo_cliente, options: customerTypes.map((item) => ({ value: item, label: item })) }, { name: 'limite_credito', label: 'Credito', type: 'number', defaultValue: customer.limite_credito || 0, min: 0 }]} onDone={reload} /></Panel></div>
        <div className="col-12 col-xl-6"><Panel title="Historial comercial" icon={ShoppingCart}><DataTable columns={[{ label: 'Venta', key: 'id' }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }, { label: 'Total', render: (row) => money(row.total) }, { label: 'Fecha', render: (row) => String(row.created_at || '').slice(0, 10) }]} rows={customer.sales || []} /></Panel></div>
      </div>
    </ScreenFrame>
  );
}

export function SalesFormScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'customers', path: '/customers', fallback: fallback.customers }, { key: 'products', path: '/products', fallback: fallback.products }, { key: 'sales', path: '/sales', fallback: fallback.sales }]);
  const customers = asList(data.customers, 'customers');
  const products = asList(data.products, 'products');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Clientes', path: '/customers', icon: Users }, { label: 'Reservas', path: '/reservations', icon: PackageCheck }]} />}>
      <div className="row g-3">
        <div className="col-12 col-xl-5"><Panel title="Registrar venta" icon={ShoppingCart}><ActionForm title="Venta" endpoint="/sales" submitLabel="Confirmar" numeric={['cliente_id', 'product_id', 'cantidad']} requireFields={['cliente_id', 'product_id', 'cantidad']} positiveFields={['cantidad']} transform={(body) => ({ cliente_id: body.cliente_id, items: [{ product_id: body.product_id, cantidad: body.cantidad }], observacion: body.observacion })} fields={[{ name: 'cliente_id', label: 'Cliente', type: 'select', options: optionItems(customers), defaultValue: customers[0]?.id }, { name: 'product_id', label: 'Producto', type: 'select', options: products.map((item) => ({ value: item.id, label: `${item.recipe_name} ${item.presentation_name}` })), defaultValue: products[0]?.id }, { name: 'cantidad', label: 'Cantidad', type: 'number', defaultValue: 6, min: 0.01 }, { name: 'observacion', label: 'Observacion', defaultValue: 'venta local', wide: true }]} onDone={reload} /></Panel></div>
        <div className="col-12 col-xl-7"><Panel title="Ventas" icon={ClipboardList}><DataTable columns={[{ label: 'ID', key: 'id' }, { label: 'Cliente', render: (row) => row.cliente_nombre || row.cliente_id }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }, { label: 'Total', render: (row) => money(row.total) }, { label: 'Ganancia', render: (row) => money(row.ganancia_total) }]} rows={asList(data.sales, 'sales')} /></Panel></div>
      </div>
    </ScreenFrame>
  );
}

export function ReservationsScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'reservations', path: '/reservations', fallback: fallback.reservations }, { key: 'customers', path: '/customers', fallback: fallback.customers }, { key: 'products', path: '/products', fallback: fallback.products }]);
  const customers = asList(data.customers, 'customers');
  const products = asList(data.products, 'products');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Venta', path: '/sales/new', icon: ShoppingCart }, { label: 'Productos', path: '/finished-products', icon: PackageCheck }]} />}>
      <div className="row g-3">
        <div className="col-12 col-xl-5"><Panel title="Nueva reserva" icon={PackageCheck}><ActionForm title="Reservar" endpoint="/reservations" submitLabel="Reservar" numeric={['cliente_id', 'product_id', 'cantidad_reservada']} requireFields={['cliente_id', 'product_id', 'cantidad_reservada', 'fecha_entrega_prometida']} positiveFields={['cantidad_reservada']} fields={[{ name: 'cliente_id', label: 'Cliente', type: 'select', options: optionItems(customers), defaultValue: customers[0]?.id }, { name: 'product_id', label: 'Producto', type: 'select', options: products.map((item) => ({ value: item.id, label: `${item.recipe_name} ${item.presentation_name}` })), defaultValue: products[0]?.id }, { name: 'cantidad_reservada', label: 'Cantidad', type: 'number', defaultValue: 12, min: 0.01 }, { name: 'fecha_entrega_prometida', label: 'Entrega', type: 'date', defaultValue: today }]} onDone={reload} /></Panel></div>
        <div className="col-12 col-xl-7"><Panel title="Reservas" icon={ClipboardList}><DataTable columns={[{ label: 'ID', key: 'id' }, { label: 'Cliente', render: (row) => row.customer_name || row.cliente_id }, { label: 'Producto', render: (row) => row.product_name || row.product_id }, { label: 'Cantidad', render: (row) => number(row.cantidad_reservada) }, { label: 'Entrega', key: 'fecha_entrega_prometida' }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }]} rows={asList(data.reservations, 'reservations')} /></Panel></div>
      </div>
    </ScreenFrame>
  );
}

export function PurchaseOrdersListScreen({ navigate }) {
  const { data, errors, loading, endpoints } = useResources([{ key: 'orders', path: '/purchase-orders', fallback: fallback.purchaseOrders }]);
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Formulario', path: '/purchase-orders/1', icon: ClipboardList }, { label: 'Recepcion', path: '/purchase-orders/1/receive', icon: Truck }]} />}>
      <Panel title="Ordenes de compra" icon={ClipboardList}><DataTable columns={[{ label: 'Orden', key: 'numero_orden' }, { label: 'Proveedor', render: (row) => row.proveedor_nombre || row.proveedor_id }, { label: 'Total', render: (row) => money(row.total_estimado) }, { label: 'Recepcion', key: 'fecha_esperada_recepcion' }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }]} rows={asList(data.orders, 'orders')} /></Panel>
    </ScreenFrame>
  );
}

export function PurchaseOrderFormScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'order', path: '/purchase-orders/1', fallback: first(fallback.purchaseOrders) }, { key: 'suppliers', path: '/suppliers', fallback: fallback.suppliers }, { key: 'supplies', path: '/supplies', fallback: fallback.supplies }]);
  const order = data.order || first(fallback.purchaseOrders);
  const suppliers = asList(data.suppliers, 'suppliers');
  const supplies = asList(data.supplies, 'supplies');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Ordenes', path: '/purchase-orders', icon: ClipboardList }, { label: 'Recepcion', path: '/purchase-orders/1/receive', icon: Truck }]} />}>
      <Panel title="Orden de compra" icon={ClipboardList}><ActionForm title="Guardar orden" endpoint={(body) => (body.id ? `/purchase-orders/${body.id}` : '/purchase-orders')} method="PUT" submitLabel="Guardar" numeric={['id', 'proveedor_id', 'supply_id', 'cantidad_solicitada', 'precio_unitario']} requireFields={['proveedor_id', 'supply_id', 'cantidad_solicitada', 'precio_unitario']} positiveFields={['cantidad_solicitada']} transform={(body) => ({ id: body.id, proveedor_id: body.proveedor_id, fecha_esperada_recepcion: body.fecha_esperada_recepcion, observacion: body.observacion, items: [{ supply_id: body.supply_id, cantidad_solicitada: body.cantidad_solicitada, precio_unitario: body.precio_unitario }] })} fields={[{ name: 'id', label: 'ID', type: 'number', defaultValue: order.id }, { name: 'proveedor_id', label: 'Proveedor', type: 'select', options: optionItems(suppliers), defaultValue: order.proveedor_id || suppliers[0]?.id }, { name: 'supply_id', label: 'Insumo', type: 'select', options: optionItems(supplies), defaultValue: first(order.items || []).supply_id || supplies[0]?.id }, { name: 'cantidad_solicitada', label: 'Cantidad', type: 'number', defaultValue: first(order.items || []).cantidad_solicitada || 10, min: 0.01 }, { name: 'precio_unitario', label: 'Precio', type: 'number', defaultValue: first(order.items || []).precio_unitario || 0, min: 0 }, { name: 'fecha_esperada_recepcion', label: 'Recepcion', type: 'date', defaultValue: order.fecha_esperada_recepcion || today }, { name: 'observacion', label: 'Observacion', defaultValue: order.observacion || 'compra local', wide: true }]} onDone={reload} /></Panel>
    </ScreenFrame>
  );
}

export function PurchaseReceiptScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'order', path: '/purchase-orders/1', fallback: first(fallback.purchaseOrders) }]);
  const order = data.order || first(fallback.purchaseOrders);
  const lines = order.items || [];
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Orden', path: '/purchase-orders/1', icon: ClipboardList }, { label: 'Ordenes', path: '/purchase-orders', icon: ClipboardList }]} />}>
      <div className="row g-3">
        <div className="col-12 col-xl-7"><Panel title="Lineas pendientes" icon={ClipboardList}><DataTable columns={[{ label: 'Insumo', render: (row) => row.nombre_insumo || row.supply_id }, { label: 'Solicitado', render: (row) => number(row.cantidad_solicitada) }, { label: 'Recibido', render: (row) => number(row.cantidad_recibida) }, { label: 'Precio', render: (row) => money(row.precio_unitario) }]} rows={lines} /></Panel></div>
        <div className="col-12 col-xl-5"><Panel title="Recepcion" icon={Truck}><ActionForm title="Recibir" endpoint="/purchase-orders/1/receive" submitLabel="Recibir" numeric={['supply_id', 'cantidad_recibida', 'precio_unitario']} requireFields={['supply_id', 'cantidad_recibida']} positiveFields={['cantidad_recibida']} transform={(body) => ({ items: [{ supply_id: body.supply_id, cantidad_recibida: body.cantidad_recibida, precio_unitario: body.precio_unitario }] })} fields={[{ name: 'supply_id', label: 'Insumo', type: 'select', options: lines.map((item) => ({ value: item.supply_id, label: item.nombre_insumo || item.supply_id })), defaultValue: first(lines).supply_id }, { name: 'cantidad_recibida', label: 'Cantidad', type: 'number', defaultValue: 5, min: 0.01 }, { name: 'precio_unitario', label: 'Precio', type: 'number', defaultValue: first(lines).precio_unitario || 0, min: 0 }]} onDone={reload} /></Panel></div>
      </div>
    </ScreenFrame>
  );
}

export function EquipmentScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'equipment', path: '/equipment', fallback: fallback.equipment }, { key: 'movements', path: '/equipment/1/movements', fallback: [] }]);
  const payload = data.equipment || fallback.equipment;
  const equipment = asList(payload, 'equipment');
  const types = asList(payload, 'types');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Dashboard', path: '/', icon: BarChart3 }, { label: 'Finanzas', path: '/expenses', icon: FileSpreadsheet }]} />}>
      <div className="row g-3">
        <div className="col-12 col-xl-8"><Panel title="Equipos" icon={Wrench}><DataTable columns={[{ label: 'Codigo', key: 'codigo' }, { label: 'Equipo', key: 'nombre' }, { label: 'Tipo', key: 'tipo' }, { label: 'Revision', key: 'proxima_revision' }, { label: 'Vencida', render: (row) => row.revision_vencida ? <StatusBadge value="warning" /> : <StatusBadge value="ok" /> }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }]} rows={equipment} /></Panel></div>
        <div className="col-12 col-xl-4"><Panel title="Movimiento" icon={Wrench}><ActionForm title="Registrar" endpoint="/equipment/1/movements" submitLabel="Guardar" numeric={['costo']} requireFields={['tipo_movimiento', 'descripcion']} fields={[{ name: 'tipo_movimiento', label: 'Tipo', type: 'select', options: ['mantencion', 'revision', 'traslado', 'descarte', 'reparacion'].map((item) => ({ value: item, label: item })) }, { name: 'descripcion', label: 'Descripcion', defaultValue: 'revision local', wide: true }, { name: 'costo', label: 'Costo', type: 'number', defaultValue: 0, min: 0 }, { name: 'fecha', label: 'Fecha', type: 'date', defaultValue: today }]} onDone={reload} /></Panel></div>
        <div className="col-12"><Panel title="Nuevo equipo" icon={PackagePlus}><ActionForm title="Equipo" endpoint="/equipment" submitLabel="Crear" numeric={['tipo_id', 'costo_adquisicion']} requireFields={['codigo', 'nombre', 'tipo_id']} fields={[{ name: 'codigo', label: 'Codigo', defaultValue: 'EQ-LOCAL' }, { name: 'nombre', label: 'Nombre', defaultValue: 'Equipo local' }, { name: 'tipo_id', label: 'Tipo', type: 'select', options: optionItems(types), defaultValue: types[0]?.id || 1 }, { name: 'estado', label: 'Estado', type: 'select', options: ['operativo', 'mantenimiento', 'fuera_servicio'].map((item) => ({ value: item, label: item })) }, { name: 'fecha_compra', label: 'Compra', type: 'date', defaultValue: today }, { name: 'costo_adquisicion', label: 'Costo', type: 'number', defaultValue: 0, min: 0 }]} onDone={reload} /></Panel></div>
      </div>
    </ScreenFrame>
  );
}

export function ExpensesScreen({ navigate }) {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'expenses', path: '/expenses', fallback: fallback.expenses }, { key: 'goals', path: '/monthly-goals', fallback: fallback.goals }]);
  const payload = data.expenses || fallback.expenses;
  const expenses = asList(payload, 'expenses');
  const categories = asList(payload, 'categories');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints} actions={<RelatedNav navigate={navigate} items={[{ label: 'Reportes', path: '/reports', icon: FileSpreadsheet }, { label: 'Configuracion', path: '/settings', icon: Settings }]} />}>
      <KpiGrid items={[{ label: 'Gastos', value: money(payload.total || expenses.reduce((sum, item) => sum + Number(item.monto || 0), 0)), note: 'operativo', icon: FileSpreadsheet, tone: 'text-bg-success' }, { label: 'Registros', value: expenses.length, note: 'mes', icon: ClipboardList, tone: 'text-bg-primary' }, { label: 'Metas', value: asList(data.goals, 'goals').length, note: 'mensuales', icon: ClipboardCheck, tone: 'text-bg-info' }, { label: 'Categorias', value: categories.length, note: 'catalogo', icon: Warehouse, tone: 'text-bg-secondary' }]} />
      <div className="row g-3">
        <div className="col-12 col-xl-7"><Panel title="Gastos" icon={FileSpreadsheet}><DataTable columns={[{ label: 'Fecha', key: 'fecha' }, { label: 'Concepto', key: 'concepto' }, { label: 'Categoria', render: (row) => row.categoria_nombre || row.categoria_id }, { label: 'Proveedor', key: 'proveedor' }, { label: 'Monto', render: (row) => money(row.monto) }]} rows={expenses} /></Panel></div>
        <div className="col-12 col-xl-5"><Panel title="Nuevo gasto" icon={Save}><ActionForm title="Gasto" endpoint="/expenses" submitLabel="Guardar" numeric={['categoria_id', 'monto']} requireFields={['concepto', 'categoria_id', 'monto']} positiveFields={['monto']} fields={[{ name: 'concepto', label: 'Concepto', defaultValue: 'Gasto local' }, { name: 'categoria_id', label: 'Categoria', type: 'select', options: optionItems(categories), defaultValue: categories[0]?.id || 1 }, { name: 'monto', label: 'Monto', type: 'number', defaultValue: 1000, min: 1 }, { name: 'fecha', label: 'Fecha', type: 'date', defaultValue: today }, { name: 'proveedor', label: 'Proveedor', defaultValue: 'Proveedor local' }]} onDone={reload} /></Panel></div>
      </div>
    </ScreenFrame>
  );
}

export function ReportsScreen() {
  const { data, errors, loading, endpoints, reload } = useResources([{ key: 'reports', path: '/reports', fallback: fallback.reports }]);
  const payload = data.reports || fallback.reports;
  const reports = asList(payload, 'reports');
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints}>
      <div className="row g-3">
        <div className="col-12 col-xl-7"><Panel title="Catalogo" icon={FileSpreadsheet}><DataTable columns={[{ label: 'Tipo', key: 'type' }, { label: 'Formatos', render: (row) => Array.isArray(row.formats) ? row.formats.join(', ') : 'csv, xlsx, pdf' }, { label: 'Filas', render: (row) => row.row_count || row.rows || 0 }]} rows={reports} /></Panel></div>
        <div className="col-12 col-xl-5"><Panel title="Exportar" icon={Download}><ActionForm title="Reporte" endpoint="/reports/export" submitLabel="Exportar" requireFields={['tipo_reporte', 'formato']} fields={[{ name: 'tipo_reporte', label: 'Tipo', type: 'select', options: reports.map((item) => ({ value: item.type, label: item.type })), defaultValue: reports[0]?.type }, { name: 'formato', label: 'Formato', type: 'select', options: reportFormats.map((item) => ({ value: item, label: item })) }]} onDone={reload} /></Panel></div>
        <div className="col-12"><Panel title="Exportaciones" icon={ClipboardList}><DataTable columns={[{ label: 'ID', key: 'id' }, { label: 'Tipo', key: 'tipo_reporte' }, { label: 'Formato', key: 'formato' }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }, { label: 'Archivo', key: 'archivo_url' }]} rows={asList(payload, 'export_jobs')} /></Panel></div>
      </div>
    </ScreenFrame>
  );
}

export function SettingsScreen() {
  const { data, errors, loading, endpoints, reload } = useResources([
    { key: 'smtp', path: '/settings/smtp', fallback: fallback.smtp },
    { key: 'notifications', path: '/notifications', fallback: fallback.notifications },
    { key: 'goals', path: '/monthly-goals', fallback: fallback.goals },
    { key: 'jobs', path: '/jobs', fallback: fallback.jobs },
    { key: 'backups', path: '/backups', fallback: fallback.backups },
    { key: 'users', path: '/users', fallback: fallback.users },
    { key: 'audit', path: '/audit-logs', fallback: fallback.audit },
  ]);
  const smtp = data.smtp || fallback.smtp;
  const jobs = data.jobs || fallback.jobs;
  const backups = data.backups || fallback.backups;
  return (
    <ScreenFrame loading={loading} errors={errors} endpoints={endpoints}>
      <div className="row g-3">
        <div className="col-12 col-xl-6"><Panel title="SMTP local" icon={MailCheck}><ActionForm title="Configuracion SMTP" endpoint="/settings/smtp" method="PUT" submitLabel="Guardar" numeric={['port']} boolean={['enabled']} requireFields={['host', 'port', 'from_email']} fields={[{ name: 'host', label: 'Host', defaultValue: smtp.host }, { name: 'port', label: 'Puerto', type: 'number', defaultValue: smtp.port || 1025 }, { name: 'username', label: 'Usuario', defaultValue: smtp.username || '' }, { name: 'from_email', label: 'Remitente', type: 'email', defaultValue: smtp.from_email || 'alerts@brewmaster.local' }, { name: 'enabled', label: 'Activo', type: 'checkbox', defaultChecked: smtp.enabled }]} onDone={reload} /></Panel></div>
        <div className="col-12 col-xl-6"><Panel title="Metas mensuales" icon={ClipboardCheck}><ActionForm title="Meta" endpoint="/monthly-goals/2026-07" method="PUT" submitLabel="Guardar" numeric={['litros_produccion', 'monto_ventas', 'num_clientes', 'margen_promedio_pct']} fields={[{ name: 'litros_produccion', label: 'Litros', type: 'number', defaultValue: 100 }, { name: 'monto_ventas', label: 'Ventas', type: 'number', defaultValue: 100000 }, { name: 'num_clientes', label: 'Clientes', type: 'number', defaultValue: 3 }, { name: 'margen_promedio_pct', label: 'Margen %', type: 'number', defaultValue: 20 }]} onDone={reload} /></Panel></div>
        <div className="col-12 col-xl-6"><Panel title="Notificaciones" icon={AlertTriangle}><DataTable columns={[{ label: 'ID', key: 'id' }, { label: 'Tipo', key: 'type' }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }, { label: 'Intentos', key: 'attempts' }, { label: 'Destino', key: 'recipient' }]} rows={asList(data.notifications, 'notifications')} /></Panel></div>
        <div className="col-12 col-xl-6"><Panel title="Scheduler y respaldos" icon={Settings}><DataTable columns={[{ label: 'Clave', key: 'field' }, { label: 'Valor', key: 'value' }]} rows={[{ field: 'scheduler', value: jobs.policy?.scheduler }, { field: 'jobs', value: (jobs.policy?.jobs || []).join(', ') }, { field: 'backup_jobs', value: String(jobs.policy?.backup_jobs) }, { field: 'backup local', value: String(jobs.low_activity_backup_enabled) }]} /><div className="mt-3"><ActionForm title="Registrar respaldo" endpoint="/backups" submitLabel="Crear respaldo" numeric={['retention_days']} fields={[{ name: 'retention_days', label: 'Retencion dias', type: 'number', defaultValue: 14, min: 1 }]} onDone={reload} /></div></Panel></div>
        <div className="col-12 col-xl-6"><Panel title="Backups" icon={Database}><DataTable columns={[{ label: 'ID', key: 'id' }, { label: 'Estado', render: (row) => <StatusBadge value={row.estado} /> }, { label: 'Archivo', key: 'archivo_url' }, { label: 'Externo', render: (row) => String(row.external_write) }, { label: 'Deploy', render: (row) => String(row.deploy_executed) }]} rows={asList(backups, 'backups')} /></Panel></div>
        <div className="col-12 col-xl-6"><Panel title="Usuarios y auditoria" icon={Users}><DataTable columns={[{ label: 'Usuario', render: (row) => row.email || row.action }, { label: 'Rol/Entidad', render: (row) => row.role || row.entity }, { label: 'Estado/Fecha', render: (row) => row.estado || String(row.created_at || '').slice(0, 10) }]} rows={[...asList(data.users, 'users'), ...asList(data.audit, 'audit')]} /></Panel></div>
      </div>
    </ScreenFrame>
  );
}

const screenMap = {
  'P-01': LoginScreen,
  'P-02': PasswordRecoveryScreen,
  'P-03': DashboardScreen,
  'P-04': SuppliesListScreen,
  'P-05': SupplyFormScreen,
  'P-06': SupplyKardexScreen,
  'P-07': SupplyEntryScreen,
  'P-08': SuppliersListScreen,
  'P-09': SupplierFormScreen,
  'P-10': RecipesListScreen,
  'P-11': RecipeFormScreen,
  'P-12': WarehousesScreen,
  'P-13': PresentationTypesScreen,
  'P-14': BatchesListScreen,
  'P-15': BatchFormScreen,
  'P-16': BatchDetailScreen,
  'P-17': BatchQualityScreen,
  'P-18': FinishedProductsScreen,
  'P-19': WasteRecordsScreen,
  'P-20': CustomersListScreen,
  'P-21': CustomerFormScreen,
  'P-22': SalesFormScreen,
  'P-23': ReservationsScreen,
  'P-24': PurchaseOrdersListScreen,
  'P-25': PurchaseOrderFormScreen,
  'P-26': PurchaseReceiptScreen,
  'P-27': EquipmentScreen,
  'P-28': ExpensesScreen,
  'P-29': ReportsScreen,
  'P-30': SettingsScreen,
};

export function screenComponentFor(screen) {
  return screenMap[screen.id] || DashboardScreen;
}
