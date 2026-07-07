from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent
from typing import Any

from .docs import _json


def _asset_text(name: str) -> str:
    return (Path(__file__).resolve().parent / name).read_text(encoding="utf-8").strip()

def _frontend_package_json() -> str:
    return _json(
        {
            "name": "brewmaster-frontend",
            "version": "0.1.0",
            "private": True,
            "dependencies": {"@vitejs/plugin-react": "latest", "bootstrap": "latest", "vite": "latest", "react": "latest", "react-dom": "latest", "lucide-react": "latest"},
            "scripts": {"dev": "vite", "build": "vite build"},
        }
    )


def _index_html() -> str:
    return dedent(
        """
        <!doctype html>
        <html lang="es">
          <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>BrewMaster</title>
          </head>
          <body>
            <div id="root"></div>
            <script type="module" src="/src/main.jsx"></script>
          </body>
        </html>
        """
    ).strip()


def _main_jsx() -> str:
    return dedent(
        """
        import React from 'react';
        import { createRoot } from 'react-dom/client';
        import App from './App.jsx';

        createRoot(document.getElementById('root')).render(
          <React.StrictMode>
            <App />
          </React.StrictMode>
        );
        """
    ).strip()


def _screen_views_jsx(blueprint: dict[str, Any] | None = None) -> str:
    if blueprint and blueprint.get("milestone_id") == "HITO-008":
        return _asset_text("hito8_ScreenViews.jsx")
    return dedent(
        """
        import { AlertTriangle, BarChart3, ClipboardList, Download, Factory, PackageCheck, PackagePlus, ShoppingCart, Truck, Users } from 'lucide-react';

        const kpis = [
          { label: 'Litros', value: 520, note: 'produccion', icon: Factory, tone: 'text-bg-primary' },
          { label: 'Stock libre', value: 312, note: 'unidades', icon: PackageCheck, tone: 'text-bg-success' },
          { label: 'Ventas', value: '$842K', note: 'confirmadas', icon: ShoppingCart, tone: 'text-bg-info' },
          { label: 'Alertas', value: 4, note: 'operacionales', icon: AlertTriangle, tone: 'text-bg-warning' },
        ];

        const chart = [
          { label: 'Feb', value: 42 },
          { label: 'Mar', value: 58 },
          { label: 'Abr', value: 48 },
          { label: 'May', value: 66 },
          { label: 'Jun', value: 74 },
          { label: 'Jul', value: 83 },
        ];

        const stock = [
          { sku: 'PROD-001', name: 'Pale Ale Casa 330', available: 120, reserved: 24 },
          { sku: 'PROD-002', name: 'Stout Sur 500', available: 60, reserved: 12 },
          { sku: 'PROD-003', name: 'IPA Norte 330', available: 96, reserved: 18 },
        ];

        const customers = [
          { name: 'Bar Lupulo Sur', type: 'mayorista', status: 'activo' },
          { name: 'Tienda Malta Norte', type: 'minorista', status: 'activo' },
          { name: 'Distribuidora Costa', type: 'distribuidor', status: 'inactivo' },
        ];

        const reports = [
          { type: 'produccion', formats: 'CSV XLSX PDF', rows: 18 },
          { type: 'ventas', formats: 'CSV XLSX PDF', rows: 24 },
          { type: 'inventario', formats: 'CSV XLSX PDF', rows: 32 },
          { type: 'kardex', formats: 'CSV XLSX PDF', rows: 44 },
          { type: 'mermas', formats: 'CSV XLSX PDF', rows: 6 },
          { type: 'compras', formats: 'CSV XLSX PDF', rows: 9 },
          { type: 'financiero', formats: 'CSV XLSX PDF', rows: 12 },
        ];
        const equipment = [
          { code: 'EQ-001', name: 'Fermentador piloto', state: 'operativo', next: '2026-08-01' },
          { code: 'EQ-002', name: 'Bomba trasvasije', state: 'mantenimiento', next: '2026-07-12' },
          { code: 'EQ-003', name: 'Chiller compacto', state: 'operativo', next: '2026-07-20' },
        ];
        const expenses = [
          { concept: 'Mantencion bomba', category: 'Mantencion', amount: '$55K' },
          { concept: 'Servicios julio', category: 'Servicios', amount: '$120K' },
          { concept: 'Insumos indirectos', category: 'Operacion', amount: '$38K' },
        ];

        function Bars({ items, max = 100 }) {
          return (
            <div className="d-grid gap-2">
              {items.map((item) => (
                <div className="d-grid gap-1" key={item.label}>
                  <div className="d-flex justify-content-between small">
                    <span>{item.label}</span>
                    <strong>{item.value}</strong>
                  </div>
                  <div className="progress" style={{ height: '10px' }}>
                    <div className="progress-bar" style={{ width: `${Math.min((item.value / max) * 100, 100)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          );
        }

        function Table({ columns, rows }) {
          return (
            <div className="table-responsive border rounded-2">
              <table className="table table-sm align-middle mb-0">
                <thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
                <tbody>{rows}</tbody>
              </table>
            </div>
          );
        }

        export function DashboardScreen() {
          return (
            <div className="d-grid gap-3">
              <section className="row g-3">
                {kpis.map((item) => {
                  const Icon = item.icon;
                  return (
                    <article className="col-12 col-md-6 col-xl-3" key={item.label}>
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">{item.label}</h2>
                          <Icon size={20} aria-label={item.label} />
                        </div>
                        <p className="display-6 fs-3 mb-1">{item.value}</p>
                        <span className={`badge ${item.tone}`}>{item.note}</span>
                      </div>
                    </article>
                  );
                })}
              </section>
              <section className="row g-3">
                <div className="col-12 col-xl-7"><div className="border rounded-2 p-3 h-100"><h2 className="h6">Ventas ultimos meses</h2><Bars items={chart} /></div></div>
                <div className="col-12 col-xl-5"><div className="border rounded-2 p-3 h-100"><h2 className="h6">Stock operativo</h2><Bars items={stock.map((item) => ({ label: item.name, value: item.available }))} max={160} /></div></div>
              </section>
            </div>
          );
        }

        export function CustomersScreen() {
          return <Table columns={['Cliente', 'Tipo', 'Estado']} rows={customers.map((item) => <tr key={item.name}><td>{item.name}</td><td>{item.type}</td><td><span className={`badge ${item.status === 'activo' ? 'text-bg-success' : 'text-bg-secondary'}`}>{item.status}</span></td></tr>)} />;
        }

        export function SalesScreen() {
          return (
            <form className="border rounded-2 p-3">
              <h2 className="h6 mb-3">Venta</h2>
              <label className="form-label" htmlFor="sale-customer">Cliente</label>
              <select className="form-select mb-2" id="sale-customer">{customers.filter((item) => item.status === 'activo').map((item) => <option key={item.name}>{item.name}</option>)}</select>
              <label className="form-label" htmlFor="sale-product">Producto</label>
              <select className="form-select mb-2" id="sale-product">{stock.map((item) => <option key={item.sku}>{item.name}</option>)}</select>
              <label className="form-label" htmlFor="sale-qty">Cantidad</label>
              <input className="form-control mb-3" id="sale-qty" type="number" defaultValue="12" />
              <button className="btn btn-primary" type="button"><ShoppingCart size={16} aria-hidden="true" /> Confirmar</button>
            </form>
          );
        }

        export function ReservationsScreen() {
          return <Table columns={['Producto', 'Disponible', 'Reservado']} rows={stock.map((item) => <tr key={item.sku}><td>{item.name}</td><td>{item.available}</td><td>{item.reserved}</td></tr>)} />;
        }

        export function PurchaseOrdersScreen() {
          const orders = [{ code: 'OC-0001', supplier: 'Malteria Sur', status: 'parcialmente_recibida' }, { code: 'OC-0002', supplier: 'Lupulos Chile', status: 'enviada' }];
          return <Table columns={['Orden', 'Proveedor', 'Estado']} rows={orders.map((item) => <tr key={item.code}><td>{item.code}</td><td>{item.supplier}</td><td><span className="badge text-bg-warning">{item.status}</span></td></tr>)} />;
        }

        export function ReportsScreen() {
          return <Table columns={['Tipo', 'Formatos', 'Filas', '']} rows={reports.map((item) => <tr key={item.type}><td>{item.type}</td><td>{item.formats}</td><td>{item.rows}</td><td className="text-end"><button className="btn btn-sm btn-outline-primary" type="button"><Download size={15} aria-hidden="true" /></button></td></tr>)} />;
        }

        export function EquipmentScreen() {
          return <Table columns={['Codigo', 'Equipo', 'Estado', 'Proxima revision']} rows={equipment.map((item) => <tr key={item.code}><td>{item.code}</td><td>{item.name}</td><td><span className={`badge ${item.state === 'operativo' ? 'text-bg-success' : 'text-bg-warning'}`}>{item.state}</span></td><td>{item.next}</td></tr>)} />;
        }

        export function ExpensesScreen() {
          return <Table columns={['Concepto', 'Categoria', 'Monto']} rows={expenses.map((item) => <tr key={item.concept}><td>{item.concept}</td><td>{item.category}</td><td>{item.amount}</td></tr>)} />;
        }

        export function GenericScreen({ screen }) {
          return (
            <div className="border rounded-2 p-3">
              <h2 className="h5">{screen.name}</h2>
              <p className="text-secondary mb-2">{screen.module}</p>
              <span className="badge text-bg-light">{screen.route}</span>
            </div>
          );
        }

        export function screenComponentFor(screen) {
          if (screen.id === 'P-03') return DashboardScreen;
          if (screen.id === 'P-20' || screen.id === 'P-21') return CustomersScreen;
          if (screen.id === 'P-22') return SalesScreen;
          if (screen.id === 'P-23') return ReservationsScreen;
          if (screen.id === 'P-24' || screen.id === 'P-25' || screen.id === 'P-26') return PurchaseOrdersScreen;
          if (screen.id === 'P-27') return EquipmentScreen;
          if (screen.id === 'P-28') return ExpensesScreen;
          if (screen.id === 'P-29') return ReportsScreen;
          return GenericScreen;
        }
        """
    ).strip()


def _hito6_app_jsx() -> str:
    return dedent(
        """
        import 'bootstrap/dist/css/bootstrap.min.css';
        import { BarChart3, FileSpreadsheet, LayoutList, Truck } from 'lucide-react';
        import { useMemo, useState } from 'react';
        import { SCREENS } from './screens/catalog';
        import { screenComponentFor } from './screens/ScreenViews';

        export default function App() {
          const screens = useMemo(() => SCREENS.filter((screen) => !['P-27', 'P-28'].includes(screen.id)), []);
          const [activeId, setActiveId] = useState('P-03');
          const activeScreen = screens.find((screen) => screen.id === activeId) || screens[0];
          const ActiveScreen = screenComponentFor(activeScreen);
          const modules = [...new Set(screens.map((screen) => screen.module))];
          return (
            <main className="container-fluid py-3">
              <header className="d-flex flex-wrap align-items-center justify-content-between gap-3 border-bottom pb-3 mb-3">
                <div>
                  <h1 className="h3 mb-1">BrewMaster</h1>
                  <p className="text-secondary mb-0">Dashboard y reportes</p>
                </div>
                <div className="d-flex gap-2">
                  <BarChart3 aria-label="dashboard" />
                  <FileSpreadsheet aria-label="reportes" />
                  <LayoutList aria-label="pantallas" />
                  <Truck aria-label="operaciones" />
                </div>
              </header>

              <section className="row g-3">
                <aside className="col-12 col-xl-3">
                  <div className="border rounded-2">
                    {modules.map((module) => (
                      <div className="border-bottom p-2" key={module}>
                        <h2 className="h6 px-2 pt-2">{module}</h2>
                        <div className="d-grid gap-1">
                          {screens.filter((screen) => screen.module === module).map((screen) => (
                            <button
                              className={`btn btn-sm text-start ${screen.id === activeId ? 'btn-primary' : 'btn-outline-secondary'}`}
                              key={screen.id}
                              onClick={() => setActiveId(screen.id)}
                              type="button"
                            >
                              {screen.id} {screen.name}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </aside>
                <section className="col-12 col-xl-9">
                  <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
                    <div>
                      <h2 className="h4 mb-1">{activeScreen.name}</h2>
                      <span className="badge text-bg-light">{activeScreen.route}</span>
                    </div>
                    <span className="text-secondary">{activeScreen.module}</span>
                  </div>
                  <ActiveScreen screen={activeScreen} />
                </section>
              </section>
            </main>
          );
        }
        """
    ).strip()


def _hito7_app_jsx() -> str:
    return _hito6_app_jsx().replace(
        "const screens = useMemo(() => SCREENS.filter((screen) => !['P-27', 'P-28'].includes(screen.id)), []);",
        "const screens = useMemo(() => SCREENS, []);",
    ).replace(
        "<p className=\"text-secondary mb-0\">Dashboard y reportes</p>",
        "<p className=\"text-secondary mb-0\">Cierre operativo y despliegue preparado</p>",
    )


def _hito8_app_jsx() -> str:
    return _asset_text("hito8_App.jsx")


def _app_jsx(blueprint: dict[str, Any] | None = None) -> str:
    if blueprint and blueprint.get("milestone_id") == "HITO-008":
        return _hito8_app_jsx()
    if blueprint and blueprint.get("milestone_id") == "HITO-007":
        return _hito7_app_jsx()
    if blueprint and blueprint.get("milestone_id") == "HITO-006":
        return _hito6_app_jsx()
    if blueprint and blueprint.get("milestone_id") == "HITO-001":
        return dedent(
            """
            import 'bootstrap/dist/css/bootstrap.min.css';
            import { KeyRound, ShieldCheck, UserCog } from 'lucide-react';
            import { SCREENS } from './screens/catalog';

            export default function App() {
              return (
                <main className="container-fluid py-3">
                  <header className="d-flex align-items-center justify-content-between border-bottom pb-3 mb-3">
                    <div>
                      <h1 className="h3 mb-1">BrewMaster</h1>
                      <p className="text-secondary mb-0">Fundamentos</p>
                    </div>
                    <div className="d-flex gap-2">
                      <ShieldCheck aria-label="seguridad" />
                      <UserCog aria-label="usuarios" />
                      <KeyRound aria-label="acceso" />
                    </div>
                  </header>
                  <section className="row g-3">
                    {SCREENS.map((screen) => (
                      <article className="col-12 col-lg-4" key={screen.id}>
                        <div className="border rounded-2 p-3 h-100">
                          <h2 className="h6 mb-2">{screen.name}</h2>
                          <span className="badge text-bg-light">{screen.route}</span>
                        </div>
                      </article>
                    ))}
                  </section>
                  <section className="row g-3 mt-1">
                    <div className="col-12 col-xl-5">
                      <form className="border rounded-2 p-3">
                        <label className="form-label" htmlFor="email">Correo</label>
                        <input className="form-control mb-2" id="email" type="email" defaultValue="admin@brewmaster.local" />
                        <label className="form-label" htmlFor="pwd">Contrasena</label>
                        <input className="form-control mb-3" id="pwd" type="password" defaultValue="Admin123!" />
                        <button className="btn btn-primary w-100" type="button">Ingresar</button>
                      </form>
                    </div>
                    <div className="col-12 col-xl-7">
                      <div className="table-responsive border rounded-2">
                        <table className="table table-sm align-middle mb-0">
                          <thead><tr><th>Usuario</th><th>Rol</th><th>Estado</th><th>Permisos</th></tr></thead>
                          <tbody>
                            <tr><td>admin@brewmaster.local</td><td>admin</td><td>activo</td><td>*</td></tr>
                            <tr><td>auditor</td><td>auditor</td><td>activo</td><td>audit.read</td></tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </section>
                </main>
              );
            }
            """
        ).strip()
    if blueprint and blueprint.get("milestone_id") == "HITO-002":
        return dedent(
            """
            import 'bootstrap/dist/css/bootstrap.min.css';
            import { Boxes, FlaskConical, KeyRound, PackagePlus, ShieldCheck, Warehouse } from 'lucide-react';
            import { SCREENS } from './screens/catalog';

            const masters = [
              { label: 'Proveedores', count: 12, icon: PackagePlus, route: '/suppliers' },
              { label: 'Insumos', count: 48, icon: Boxes, route: '/supplies' },
              { label: 'Bodegas', count: 4, icon: Warehouse, route: '/warehouses' },
              { label: 'Recetas', count: 9, icon: FlaskConical, route: '/recipes' },
            ];

            const supplies = [
              { code: 'INS-001', name: 'Malta Pale', type: 'malta', warehouse: 'Bodega seca', status: 'activo' },
              { code: 'INS-002', name: 'Lupulo Cascade', type: 'lupulo', warehouse: 'Frio', status: 'activo' },
              { code: 'INS-003', name: 'Levadura Ale', type: 'levadura', warehouse: 'Frio', status: 'inactivo' },
            ];

            export default function App() {
              const visibleScreens = SCREENS.filter((screen) => !['P-06', 'P-07'].includes(screen.id));
              return (
                <main className="container-fluid py-3">
                  <header className="d-flex flex-wrap align-items-center justify-content-between gap-3 border-bottom pb-3 mb-3">
                    <div>
                      <h1 className="h3 mb-1">BrewMaster</h1>
                      <p className="text-secondary mb-0">Maestros</p>
                    </div>
                    <div className="d-flex gap-2">
                      <ShieldCheck aria-label="seguridad" />
                      <KeyRound aria-label="acceso" />
                      <Boxes aria-label="maestros" />
                    </div>
                  </header>

                  <section className="row g-3 mb-3">
                    {masters.map((item) => {
                      const Icon = item.icon;
                      return (
                        <article className="col-12 col-sm-6 col-xl-3" key={item.label}>
                          <div className="border rounded-2 p-3 h-100">
                            <div className="d-flex align-items-center justify-content-between">
                              <h2 className="h6 mb-0">{item.label}</h2>
                              <Icon aria-label={item.label} size={20} />
                            </div>
                            <p className="display-6 fs-3 mb-1">{item.count}</p>
                            <span className="badge text-bg-light">{item.route}</span>
                          </div>
                        </article>
                      );
                    })}
                  </section>

                  <section className="row g-3">
                    <div className="col-12 col-xl-7">
                      <div className="border rounded-2">
                        <div className="d-flex align-items-center justify-content-between p-3 border-bottom">
                          <h2 className="h6 mb-0">Insumos maestros</h2>
                          <button className="btn btn-sm btn-primary" type="button">
                            <PackagePlus size={16} aria-hidden="true" /> Nuevo
                          </button>
                        </div>
                        <div className="table-responsive">
                          <table className="table table-sm align-middle mb-0">
                            <thead><tr><th>Codigo</th><th>Nombre</th><th>Tipo</th><th>Bodega</th><th>Estado</th></tr></thead>
                            <tbody>
                              {supplies.map((item) => (
                                <tr key={item.code}>
                                  <td>{item.code}</td>
                                  <td>{item.name}</td>
                                  <td>{item.type}</td>
                                  <td>{item.warehouse}</td>
                                  <td><span className={`badge ${item.status === 'activo' ? 'text-bg-success' : 'text-bg-secondary'}`}>{item.status}</span></td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                    <div className="col-12 col-xl-5">
                      <form className="border rounded-2 p-3">
                        <h2 className="h6 mb-3">Receta base</h2>
                        <label className="form-label" htmlFor="recipe-name">Nombre</label>
                        <input className="form-control mb-2" id="recipe-name" defaultValue="Pale Ale Casa" />
                        <label className="form-label" htmlFor="recipe-type">Tipo</label>
                        <select className="form-select mb-2" id="recipe-type" defaultValue="ale">
                          <option value="ale">ale</option>
                          <option value="lager">lager</option>
                          <option value="stout">stout</option>
                        </select>
                        <label className="form-label" htmlFor="batch-volume">Volumen por lote</label>
                        <div className="input-group mb-3">
                          <input className="form-control" id="batch-volume" type="number" defaultValue="50" />
                          <span className="input-group-text">L</span>
                        </div>
                        <button className="btn btn-outline-primary w-100" type="button">Guardar maestro</button>
                      </form>
                    </div>
                  </section>

                  <section className="row g-3 mt-1">
                    {visibleScreens.map((screen) => (
                      <article className="col-12 col-md-6 col-xl-3" key={screen.id}>
                        <div className="border rounded-2 p-3 h-100">
                          <h2 className="h6 mb-2">{screen.id} - {screen.name}</h2>
                          <span className="badge text-bg-light">{screen.route}</span>
                        </div>
                      </article>
                    ))}
                  </section>
                </main>
              );
            }
            """
        ).strip()
    if blueprint and blueprint.get("milestone_id") == "HITO-003":
        return dedent(
            """
            import 'bootstrap/dist/css/bootstrap.min.css';
            import { Bell, Boxes, ClipboardList, MailCheck, PackagePlus, ShieldCheck, Warehouse } from 'lucide-react';
            import { SCREENS } from './screens/catalog';

            const supplies = [
              { code: 'INS-001', name: 'Malta Pale', stock: 5, min: 10, unit: 'kg', status: 'bajo' },
              { code: 'INS-002', name: 'Lupulo Cascade', stock: 2, min: 3, unit: 'kg', status: 'bajo' },
              { code: 'INS-003', name: 'Levadura Ale', stock: 18, min: 6, unit: 'u', status: 'ok' },
            ];

            const kardex = [
              { date: '2026-07-05', type: 'ENTRADA', qty: 25, balance: 25, ref: 'FAC-190' },
              { date: '2026-07-06', type: 'ENTRADA', qty: 3, balance: 5, ref: 'FAC-LOCAL' },
            ];

            const notifications = [
              { subject: 'Stock bajo: Malta Pale', status: 'queued', attempts: 0 },
              { subject: 'Prueba SMTP BrewMaster', status: 'sent', attempts: 1 },
            ];

            export default function App() {
              const visibleScreens = SCREENS.filter((screen) => !['P-03'].includes(screen.id));
              return (
                <main className="container-fluid py-3">
                  <header className="d-flex flex-wrap align-items-center justify-content-between gap-3 border-bottom pb-3 mb-3">
                    <div>
                      <h1 className="h3 mb-1">BrewMaster</h1>
                      <p className="text-secondary mb-0">Inventario</p>
                    </div>
                    <div className="d-flex gap-2">
                      <ShieldCheck aria-label="seguridad" />
                      <Boxes aria-label="insumos" />
                      <ClipboardList aria-label="kardex" />
                      <MailCheck aria-label="smtp" />
                    </div>
                  </header>

                  <section className="row g-3 mb-3">
                    <article className="col-12 col-md-4">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">Bajo stock</h2>
                          <Bell size={20} aria-label="alertas" />
                        </div>
                        <p className="display-6 fs-3 mb-1">{supplies.filter((item) => item.status === 'bajo').length}</p>
                        <span className="badge text-bg-warning">alertas locales</span>
                      </div>
                    </article>
                    <article className="col-12 col-md-4">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">Entradas</h2>
                          <PackagePlus size={20} aria-label="entradas" />
                        </div>
                        <p className="display-6 fs-3 mb-1">2</p>
                        <span className="badge text-bg-light">Kardex ENTRADA</span>
                      </div>
                    </article>
                    <article className="col-12 col-md-4">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">SMTP</h2>
                          <MailCheck size={20} aria-label="smtp" />
                        </div>
                        <p className="display-6 fs-3 mb-1">mock</p>
                        <span className="badge text-bg-success">sin envio externo</span>
                      </div>
                    </article>
                  </section>

                  <section className="row g-3">
                    <div className="col-12 col-xl-7">
                      <div className="border rounded-2">
                        <div className="d-flex align-items-center justify-content-between p-3 border-bottom">
                          <h2 className="h6 mb-0">Insumos</h2>
                          <Warehouse size={18} aria-label="bodegas" />
                        </div>
                        <div className="table-responsive">
                          <table className="table table-sm align-middle mb-0">
                            <thead><tr><th>Codigo</th><th>Nombre</th><th>Stock</th><th>Minimo</th><th>Estado</th></tr></thead>
                            <tbody>
                              {supplies.map((item) => (
                                <tr key={item.code}>
                                  <td>{item.code}</td>
                                  <td>{item.name}</td>
                                  <td>{item.stock} {item.unit}</td>
                                  <td>{item.min} {item.unit}</td>
                                  <td><span className={`badge ${item.status === 'bajo' ? 'text-bg-warning' : 'text-bg-success'}`}>{item.status}</span></td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                    <div className="col-12 col-xl-5">
                      <form className="border rounded-2 p-3">
                        <h2 className="h6 mb-3">Entrada de insumo</h2>
                        <label className="form-label" htmlFor="supply">Insumo</label>
                        <select className="form-select mb-2" id="supply" defaultValue="INS-001">
                          {supplies.map((item) => <option value={item.code} key={item.code}>{item.name}</option>)}
                        </select>
                        <label className="form-label" htmlFor="qty">Cantidad</label>
                        <input className="form-control mb-2" id="qty" type="number" defaultValue="3" />
                        <label className="form-label" htmlFor="cost">Costo unitario</label>
                        <input className="form-control mb-2" id="cost" type="number" defaultValue="720" />
                        <label className="form-label" htmlFor="ref">Referencia</label>
                        <input className="form-control mb-3" id="ref" defaultValue="FAC-LOCAL" />
                        <button className="btn btn-primary w-100" type="button">
                          <PackagePlus size={16} aria-hidden="true" /> Registrar entrada
                        </button>
                      </form>
                    </div>
                  </section>

                  <section className="row g-3 mt-1">
                    <div className="col-12 col-xl-7">
                      <div className="border rounded-2">
                        <div className="p-3 border-bottom">
                          <h2 className="h6 mb-0">Kardex de insumo</h2>
                        </div>
                        <div className="table-responsive">
                          <table className="table table-sm align-middle mb-0">
                            <thead><tr><th>Fecha</th><th>Tipo</th><th>Cantidad</th><th>Saldo</th><th>Referencia</th></tr></thead>
                            <tbody>
                              {kardex.map((item) => (
                                <tr key={`${item.date}-${item.ref}`}>
                                  <td>{item.date}</td>
                                  <td>{item.type}</td>
                                  <td>{item.qty}</td>
                                  <td>{item.balance}</td>
                                  <td>{item.ref}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                    <div className="col-12 col-xl-5">
                      <div className="border rounded-2 p-3 h-100">
                        <h2 className="h6 mb-3">SMTP y cola</h2>
                        <label className="form-label" htmlFor="smtp-host">Host</label>
                        <input className="form-control mb-2" id="smtp-host" defaultValue="smtp.local" />
                        <label className="form-label" htmlFor="smtp-from">Remitente</label>
                        <input className="form-control mb-3" id="smtp-from" type="email" defaultValue="alerts@brewmaster.local" />
                        <button className="btn btn-outline-primary w-100 mb-3" type="button">
                          <MailCheck size={16} aria-hidden="true" /> Probar SMTP
                        </button>
                        <ul className="list-group list-group-flush">
                          {notifications.map((item) => (
                            <li className="list-group-item px-0 d-flex justify-content-between align-items-center" key={item.subject}>
                              <span>{item.subject}</span>
                              <span className={`badge ${item.status === 'sent' ? 'text-bg-success' : 'text-bg-secondary'}`}>{item.status} {item.attempts}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </section>

                  <section className="row g-3 mt-1">
                    {visibleScreens.map((screen) => (
                      <article className="col-12 col-md-6 col-xl-3" key={screen.id}>
                        <div className="border rounded-2 p-3 h-100">
                          <h2 className="h6 mb-2">{screen.id} - {screen.name}</h2>
                          <span className="badge text-bg-light">{screen.route}</span>
                        </div>
                      </article>
                    ))}
                  </section>
                </main>
              );
            }
            """
        ).strip()
    if blueprint and blueprint.get("milestone_id") == "HITO-004":
        return dedent(
            """
            import 'bootstrap/dist/css/bootstrap.min.css';
            import { Beaker, ClipboardCheck, Factory, PackageCheck, Recycle, ShieldCheck } from 'lucide-react';
            import { SCREENS } from './screens/catalog';

            const batches = [
              { number: 'LOT-0001', recipe: 'Pale Ale Casa', state: 'en_elaboracion', liters: 50, alerts: 0 },
              { number: 'LOT-0002', recipe: 'Stout Sur', state: 'completado', liters: 40, alerts: 0 },
            ];

            const products = [
              { sku: 'PROD-001', name: 'Pale Ale Casa 330', stock: 144, cost: 620, price: 900 },
              { sku: 'PROD-002', name: 'Stout Sur 500', stock: 72, cost: 780, price: 1100 },
            ];

            const quality = [
              { batch: 'LOT-0002', result: 'aprobado', ph: 4.2, aroma: 8 },
            ];

            export default function App() {
              const visibleScreens = SCREENS.filter((screen) => !['P-03', 'P-20', 'P-21', 'P-22', 'P-23', 'P-24', 'P-25', 'P-26', 'P-27', 'P-28', 'P-29'].includes(screen.id));
              return (
                <main className="container-fluid py-3">
                  <header className="d-flex flex-wrap align-items-center justify-content-between gap-3 border-bottom pb-3 mb-3">
                    <div>
                      <h1 className="h3 mb-1">BrewMaster</h1>
                      <p className="text-secondary mb-0">Produccion</p>
                    </div>
                    <div className="d-flex gap-2">
                      <ShieldCheck aria-label="seguridad" />
                      <Factory aria-label="lotes" />
                      <ClipboardCheck aria-label="calidad" />
                      <PackageCheck aria-label="productos" />
                    </div>
                  </header>

                  <section className="row g-3 mb-3">
                    <article className="col-12 col-md-3">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">Lotes</h2>
                          <Factory size={20} aria-label="lotes" />
                        </div>
                        <p className="display-6 fs-3 mb-1">{batches.length}</p>
                        <span className="badge text-bg-light">HITO-004</span>
                      </div>
                    </article>
                    <article className="col-12 col-md-3">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">Calidad</h2>
                          <Beaker size={20} aria-label="calidad" />
                        </div>
                        <p className="display-6 fs-3 mb-1">{quality.length}</p>
                        <span className="badge text-bg-success">aprobado</span>
                      </div>
                    </article>
                    <article className="col-12 col-md-3">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">Productos</h2>
                          <PackageCheck size={20} aria-label="productos" />
                        </div>
                        <p className="display-6 fs-3 mb-1">{products.reduce((total, item) => total + item.stock, 0)}</p>
                        <span className="badge text-bg-light">unidades</span>
                      </div>
                    </article>
                    <article className="col-12 col-md-3">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">Mermas</h2>
                          <Recycle size={20} aria-label="mermas" />
                        </div>
                        <p className="display-6 fs-3 mb-1">0</p>
                        <span className="badge text-bg-secondary">sin fuga</span>
                      </div>
                    </article>
                  </section>

                  <section className="row g-3">
                    <div className="col-12 col-xl-7">
                      <div className="border rounded-2">
                        <div className="d-flex align-items-center justify-content-between p-3 border-bottom">
                          <h2 className="h6 mb-0">Lotes de produccion</h2>
                          <button className="btn btn-sm btn-primary" type="button">
                            <Factory size={16} aria-hidden="true" /> Nuevo
                          </button>
                        </div>
                        <div className="table-responsive">
                          <table className="table table-sm align-middle mb-0">
                            <thead><tr><th>Lote</th><th>Receta</th><th>Litros</th><th>Estado</th><th>Alertas</th></tr></thead>
                            <tbody>
                              {batches.map((item) => (
                                <tr key={item.number}>
                                  <td>{item.number}</td>
                                  <td>{item.recipe}</td>
                                  <td>{item.liters}</td>
                                  <td><span className={`badge ${item.state === 'completado' ? 'text-bg-success' : 'text-bg-warning'}`}>{item.state}</span></td>
                                  <td>{item.alerts}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                    <div className="col-12 col-xl-5">
                      <form className="border rounded-2 p-3">
                        <h2 className="h6 mb-3">Completar lote</h2>
                        <label className="form-label" htmlFor="batch">Lote</label>
                        <select className="form-select mb-2" id="batch" defaultValue="LOT-0001">
                          {batches.map((item) => <option value={item.number} key={item.number}>{item.number}</option>)}
                        </select>
                        <label className="form-label" htmlFor="liters">Litros producidos</label>
                        <input className="form-control mb-2" id="liters" type="number" defaultValue="50" />
                        <label className="form-label" htmlFor="labor">Horas mano de obra</label>
                        <input className="form-control mb-2" id="labor" type="number" defaultValue="4" />
                        <label className="form-label" htmlFor="waste">Merma %</label>
                        <input className="form-control mb-3" id="waste" type="number" defaultValue="2" />
                        <button className="btn btn-primary w-100" type="button">
                          <ClipboardCheck size={16} aria-hidden="true" /> Completar
                        </button>
                      </form>
                    </div>
                  </section>

                  <section className="row g-3 mt-1">
                    <div className="col-12 col-xl-7">
                      <div className="border rounded-2">
                        <div className="p-3 border-bottom">
                          <h2 className="h6 mb-0">Productos terminados</h2>
                        </div>
                        <div className="table-responsive">
                          <table className="table table-sm align-middle mb-0">
                            <thead><tr><th>SKU</th><th>Producto</th><th>Stock</th><th>Costo</th><th>Precio</th></tr></thead>
                            <tbody>
                              {products.map((item) => (
                                <tr key={item.sku}>
                                  <td>{item.sku}</td>
                                  <td>{item.name}</td>
                                  <td>{item.stock}</td>
                                  <td>{item.cost}</td>
                                  <td>{item.price}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                    <div className="col-12 col-xl-5">
                      <div className="border rounded-2 p-3 h-100">
                        <h2 className="h6 mb-3">Control y merma</h2>
                        <div className="d-flex gap-2 mb-3">
                          <button className="btn btn-outline-primary flex-fill" type="button">
                            <Beaker size={16} aria-hidden="true" /> Calidad
                          </button>
                          <button className="btn btn-outline-secondary flex-fill" type="button">
                            <Recycle size={16} aria-hidden="true" /> Merma
                          </button>
                        </div>
                        <ul className="list-group list-group-flush">
                          {quality.map((item) => (
                            <li className="list-group-item px-0 d-flex justify-content-between align-items-center" key={item.batch}>
                              <span>{item.batch}</span>
                              <span className="badge text-bg-success">{item.result} pH {item.ph}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </section>

                  <section className="row g-3 mt-1">
                    {visibleScreens.map((screen) => (
                      <article className="col-12 col-md-6 col-xl-3" key={screen.id}>
                        <div className="border rounded-2 p-3 h-100">
                          <h2 className="h6 mb-2">{screen.id} - {screen.name}</h2>
                          <span className="badge text-bg-light">{screen.route}</span>
                        </div>
                      </article>
                    ))}
                  </section>
                </main>
              );
            }
            """
        ).strip()
    if blueprint and blueprint.get("milestone_id") == "HITO-005":
        return dedent(
            """
            import 'bootstrap/dist/css/bootstrap.min.css';
            import { CalendarCheck, ClipboardList, PackageCheck, PackagePlus, ShieldCheck, ShoppingCart, Truck, Users } from 'lucide-react';
            import { SCREENS } from './screens/catalog';

            const customers = [
              { name: 'Bar Lupulo Sur', type: 'mayorista', fiscal: 'CL-76000111-1', status: 'activo' },
              { name: 'Tienda Malta Norte', type: 'minorista', fiscal: 'CL-76000222-2', status: 'activo' },
              { name: 'Distribuidora Costa', type: 'distribuidor', fiscal: 'CL-76000333-3', status: 'inactivo' },
            ];

            const products = [
              { sku: 'PROD-001', name: 'Pale Ale Casa 330', stock: 144, reserved: 24, cost: 620, price: 900 },
              { sku: 'PROD-002', name: 'Stout Sur 500', stock: 72, reserved: 12, cost: 780, price: 1100 },
            ];

            const sales = [
              { folio: 'VTA-0001', customer: 'Bar Lupulo Sur', status: 'confirmada', units: 36, total: 29160 },
              { folio: 'VTA-0002', customer: 'Tienda Malta Norte', status: 'anulada', units: 12, total: 0 },
            ];

            const reservations = [
              { code: 'RES-0001', customer: 'Bar Lupulo Sur', product: 'Pale Ale Casa 330', qty: 24, status: 'activa' },
              { code: 'RES-0002', customer: 'Tienda Malta Norte', product: 'Stout Sur 500', qty: 12, status: 'activa' },
            ];

            const purchaseOrders = [
              { code: 'OC-0001', supplier: 'Malteria Sur', status: 'parcialmente_recibida', pending: 40 },
              { code: 'OC-0002', supplier: 'Lupulos Chile', status: 'enviada', pending: 8 },
            ];

            export default function App() {
              const visibleScreens = SCREENS.filter((screen) => !['P-03', 'P-27', 'P-28', 'P-29'].includes(screen.id));
              const freeStock = products.reduce((total, item) => total + item.stock - item.reserved, 0);
              return (
                <main className="container-fluid py-3">
                  <header className="d-flex flex-wrap align-items-center justify-content-between gap-3 border-bottom pb-3 mb-3">
                    <div>
                      <h1 className="h3 mb-1">BrewMaster</h1>
                      <p className="text-secondary mb-0">Ventas y compras</p>
                    </div>
                    <div className="d-flex gap-2">
                      <ShieldCheck aria-label="seguridad" />
                      <ShoppingCart aria-label="ventas" />
                      <CalendarCheck aria-label="reservas" />
                      <Truck aria-label="compras" />
                    </div>
                  </header>

                  <section className="row g-3 mb-3">
                    <article className="col-12 col-md-3">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">Clientes</h2>
                          <Users size={20} aria-label="clientes" />
                        </div>
                        <p className="display-6 fs-3 mb-1">{customers.filter((item) => item.status === 'activo').length}</p>
                        <span className="badge text-bg-light">tipos activos</span>
                      </div>
                    </article>
                    <article className="col-12 col-md-3">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">Ventas</h2>
                          <ShoppingCart size={20} aria-label="ventas" />
                        </div>
                        <p className="display-6 fs-3 mb-1">{sales.filter((item) => item.status === 'confirmada').length}</p>
                        <span className="badge text-bg-success">Kardex VENTA</span>
                      </div>
                    </article>
                    <article className="col-12 col-md-3">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">Stock libre</h2>
                          <PackageCheck size={20} aria-label="productos" />
                        </div>
                        <p className="display-6 fs-3 mb-1">{freeStock}</p>
                        <span className="badge text-bg-light">unidades</span>
                      </div>
                    </article>
                    <article className="col-12 col-md-3">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between">
                          <h2 className="h6 mb-0">Ordenes</h2>
                          <ClipboardList size={20} aria-label="ordenes" />
                        </div>
                        <p className="display-6 fs-3 mb-1">{purchaseOrders.length}</p>
                        <span className="badge text-bg-warning">recepcion local</span>
                      </div>
                    </article>
                  </section>

                  <section className="row g-3">
                    <div className="col-12 col-xl-7">
                      <div className="border rounded-2">
                        <div className="d-flex align-items-center justify-content-between p-3 border-bottom">
                          <h2 className="h6 mb-0">Clientes</h2>
                          <button className="btn btn-sm btn-primary" type="button">
                            <Users size={16} aria-hidden="true" /> Nuevo
                          </button>
                        </div>
                        <div className="table-responsive">
                          <table className="table table-sm align-middle mb-0">
                            <thead><tr><th>Cliente</th><th>Tipo</th><th>Fiscal</th><th>Estado</th></tr></thead>
                            <tbody>
                              {customers.map((item) => (
                                <tr key={item.fiscal}>
                                  <td>{item.name}</td>
                                  <td>{item.type}</td>
                                  <td>{item.fiscal}</td>
                                  <td><span className={`badge ${item.status === 'activo' ? 'text-bg-success' : 'text-bg-secondary'}`}>{item.status}</span></td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                    <div className="col-12 col-xl-5">
                      <form className="border rounded-2 p-3">
                        <h2 className="h6 mb-3">Venta</h2>
                        <label className="form-label" htmlFor="customer">Cliente</label>
                        <select className="form-select mb-2" id="customer" defaultValue="Bar Lupulo Sur">
                          {customers.filter((item) => item.status === 'activo').map((item) => <option value={item.name} key={item.fiscal}>{item.name}</option>)}
                        </select>
                        <label className="form-label" htmlFor="product">Producto</label>
                        <select className="form-select mb-2" id="product" defaultValue="PROD-001">
                          {products.map((item) => <option value={item.sku} key={item.sku}>{item.name}</option>)}
                        </select>
                        <label className="form-label" htmlFor="qty">Cantidad</label>
                        <input className="form-control mb-2" id="qty" type="number" defaultValue="12" />
                        <label className="form-label" htmlFor="price">Precio</label>
                        <input className="form-control mb-3" id="price" type="number" defaultValue="810" />
                        <button className="btn btn-primary w-100" type="button">
                          <ShoppingCart size={16} aria-hidden="true" /> Confirmar venta
                        </button>
                      </form>
                    </div>
                  </section>

                  <section className="row g-3 mt-1">
                    <div className="col-12 col-xl-6">
                      <div className="border rounded-2">
                        <div className="p-3 border-bottom">
                          <h2 className="h6 mb-0">Reservas</h2>
                        </div>
                        <div className="table-responsive">
                          <table className="table table-sm align-middle mb-0">
                            <thead><tr><th>Codigo</th><th>Cliente</th><th>Producto</th><th>Cantidad</th><th>Estado</th></tr></thead>
                            <tbody>
                              {reservations.map((item) => (
                                <tr key={item.code}>
                                  <td>{item.code}</td>
                                  <td>{item.customer}</td>
                                  <td>{item.product}</td>
                                  <td>{item.qty}</td>
                                  <td><span className="badge text-bg-warning">{item.status}</span></td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                    <div className="col-12 col-xl-6">
                      <div className="border rounded-2">
                        <div className="d-flex align-items-center justify-content-between p-3 border-bottom">
                          <h2 className="h6 mb-0">Ordenes de compra</h2>
                          <PackagePlus size={18} aria-label="recepcion" />
                        </div>
                        <div className="table-responsive">
                          <table className="table table-sm align-middle mb-0">
                            <thead><tr><th>Orden</th><th>Proveedor</th><th>Estado</th><th>Pendiente</th></tr></thead>
                            <tbody>
                              {purchaseOrders.map((item) => (
                                <tr key={item.code}>
                                  <td>{item.code}</td>
                                  <td>{item.supplier}</td>
                                  <td><span className={`badge ${item.status === 'enviada' ? 'text-bg-info' : 'text-bg-warning'}`}>{item.status}</span></td>
                                  <td>{item.pending}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </section>

                  <section className="row g-3 mt-1">
                    {visibleScreens.map((screen) => (
                      <article className="col-12 col-md-6 col-xl-3" key={screen.id}>
                        <div className="border rounded-2 p-3 h-100">
                          <h2 className="h6 mb-2">{screen.id} - {screen.name}</h2>
                          <span className="badge text-bg-light">{screen.route}</span>
                        </div>
                      </article>
                    ))}
                  </section>
              </main>
            );
          }
            """
        ).strip()
    if blueprint and blueprint.get("milestone_id") == "HITO-006":
        return dedent(
            """
            import 'bootstrap/dist/css/bootstrap.min.css';
            import { AlertTriangle, BarChart3, Download, Factory, FileSpreadsheet, PackageCheck, ShoppingCart, Truck } from 'lucide-react';
            import { SCREENS } from './screens/catalog';

            const kpis = [
              { label: 'Litros', value: 520, note: 'produccion', icon: Factory, tone: 'text-bg-primary' },
              { label: 'Stock libre', value: 312, note: 'unidades', icon: PackageCheck, tone: 'text-bg-success' },
              { label: 'Ventas', value: '$842K', note: 'confirmadas', icon: ShoppingCart, tone: 'text-bg-info' },
              { label: 'Alertas', value: 4, note: 'operacionales', icon: AlertTriangle, tone: 'text-bg-warning' },
            ];

            const salesChart = [
              { label: 'Feb', value: 42 },
              { label: 'Mar', value: 58 },
              { label: 'Abr', value: 48 },
              { label: 'May', value: 66 },
              { label: 'Jun', value: 74 },
              { label: 'Jul', value: 83 },
            ];

            const stockChart = [
              { label: 'Pale Ale', value: 144 },
              { label: 'Stout', value: 72 },
              { label: 'IPA', value: 96 },
              { label: 'Porter', value: 36 },
            ];

            const alerts = [
              { type: 'Stock', detail: 'Malta Pale bajo minimo', severity: 'warning' },
              { type: 'Merma', detail: 'Lote LOT-0007 supera 5%', severity: 'warning' },
              { type: 'Compra', detail: 'OC-0002 pendiente de recepcion', severity: 'info' },
              { type: 'Reserva', detail: 'RES-0011 vence hoy', severity: 'warning' },
            ];

            const reports = [
              { type: 'produccion', formats: 'CSV XLSX PDF', rows: 18 },
              { type: 'ventas', formats: 'CSV XLSX PDF', rows: 24 },
              { type: 'inventario', formats: 'CSV XLSX PDF', rows: 32 },
              { type: 'kardex', formats: 'CSV XLSX PDF', rows: 44 },
              { type: 'mermas', formats: 'CSV XLSX PDF', rows: 6 },
              { type: 'compras', formats: 'CSV XLSX PDF', rows: 9 },
            ];

            function Bars({ items, max = 100 }) {
              return (
                <div className="d-grid gap-2">
                  {items.map((item) => (
                    <div className="d-grid gap-1" key={item.label}>
                      <div className="d-flex justify-content-between small">
                        <span>{item.label}</span>
                        <strong>{item.value}</strong>
                      </div>
                      <div className="progress" style={{ height: '10px' }}>
                        <div className="progress-bar" style={{ width: `${Math.min((item.value / max) * 100, 100)}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              );
            }

            export default function App() {
              const visibleScreens = SCREENS.filter((screen) => !['P-27', 'P-28'].includes(screen.id));
              return (
                <main className="container-fluid py-3">
                  <header className="d-flex flex-wrap align-items-center justify-content-between gap-3 border-bottom pb-3 mb-3">
                    <div>
                      <h1 className="h3 mb-1">BrewMaster</h1>
                      <p className="text-secondary mb-0">Dashboard y reportes</p>
                    </div>
                    <div className="d-flex gap-2">
                      <BarChart3 aria-label="dashboard" />
                      <FileSpreadsheet aria-label="reportes" />
                      <Download aria-label="exportar" />
                      <Truck aria-label="operaciones" />
                    </div>
                  </header>

                  <section className="row g-3 mb-3">
                    {kpis.map((item) => {
                      const Icon = item.icon;
                      return (
                        <article className="col-12 col-md-6 col-xl-3" key={item.label}>
                          <div className="border rounded-2 p-3 h-100">
                            <div className="d-flex align-items-center justify-content-between">
                              <h2 className="h6 mb-0">{item.label}</h2>
                              <Icon size={20} aria-label={item.label} />
                            </div>
                            <p className="display-6 fs-3 mb-1">{item.value}</p>
                            <span className={`badge ${item.tone}`}>{item.note}</span>
                          </div>
                        </article>
                      );
                    })}
                  </section>

                  <section className="row g-3">
                    <div className="col-12 col-xl-7">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between mb-3">
                          <h2 className="h6 mb-0">Ventas ultimos meses</h2>
                          <BarChart3 size={18} aria-label="ventas" />
                        </div>
                        <Bars items={salesChart} />
                      </div>
                    </div>
                    <div className="col-12 col-xl-5">
                      <div className="border rounded-2 p-3 h-100">
                        <div className="d-flex align-items-center justify-content-between mb-3">
                          <h2 className="h6 mb-0">Stock por producto</h2>
                          <PackageCheck size={18} aria-label="stock" />
                        </div>
                        <Bars items={stockChart} max={160} />
                      </div>
                    </div>
                  </section>

                  <section className="row g-3 mt-1">
                    <div className="col-12 col-xl-5">
                      <div className="border rounded-2">
                        <div className="p-3 border-bottom">
                          <h2 className="h6 mb-0">Alertas</h2>
                        </div>
                        <div className="list-group list-group-flush">
                          {alerts.map((item) => (
                            <div className="list-group-item d-flex align-items-start justify-content-between gap-3" key={`${item.type}-${item.detail}`}>
                              <div>
                                <strong className="d-block">{item.type}</strong>
                                <span className="text-secondary small">{item.detail}</span>
                              </div>
                              <span className={`badge ${item.severity === 'info' ? 'text-bg-info' : 'text-bg-warning'}`}>{item.severity}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="col-12 col-xl-7">
                      <div className="border rounded-2">
                        <div className="d-flex align-items-center justify-content-between p-3 border-bottom">
                          <h2 className="h6 mb-0">Reportes</h2>
                          <Download size={18} aria-label="exportar" />
                        </div>
                        <div className="table-responsive">
                          <table className="table table-sm align-middle mb-0">
                            <thead><tr><th>Tipo</th><th>Formatos</th><th>Filas</th><th></th></tr></thead>
                            <tbody>
                              {reports.map((item) => (
                                <tr key={item.type}>
                                  <td>{item.type}</td>
                                  <td>{item.formats}</td>
                                  <td>{item.rows}</td>
                                  <td className="text-end"><button className="btn btn-sm btn-outline-primary" type="button"><Download size={15} aria-hidden="true" /></button></td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </section>

                  <section className="row g-3 mt-1">
                    {visibleScreens.map((screen) => (
                      <article className="col-12 col-md-6 col-xl-3" key={screen.id}>
                        <div className="border rounded-2 p-3 h-100">
                          <h2 className="h6 mb-2">{screen.id} - {screen.name}</h2>
                          <span className="badge text-bg-light">{screen.route}</span>
                        </div>
                      </article>
                    ))}
                  </section>
                </main>
              );
            }
            """
        ).strip()
    return dedent(
        """
        import 'bootstrap/dist/css/bootstrap.min.css';
        import { BarChart3, Factory, PackageCheck, ShoppingCart } from 'lucide-react';
        import { SCREENS } from './screens/catalog';

        export default function App() {
          const modules = [...new Set(SCREENS.map((screen) => screen.module))];
          return (
            <main className="container-fluid py-3">
              <header className="d-flex align-items-center justify-content-between border-bottom pb-3 mb-3">
                <div>
                  <h1 className="h3 mb-1">BrewMaster</h1>
                  <p className="text-secondary mb-0">Gestion integral para cervecerias artesanales</p>
                </div>
                <div className="d-flex gap-2">
                  <BarChart3 aria-label="dashboard" />
                  <Factory aria-label="produccion" />
                  <PackageCheck aria-label="inventario" />
                  <ShoppingCart aria-label="ventas" />
                </div>
              </header>
              <section className="row g-3">
                {modules.map((module) => (
                  <article className="col-12 col-md-6 col-xl-3" key={module}>
                    <div className="border rounded-2 p-3 h-100">
                      <h2 className="h6">{module}</h2>
                      <ul className="list-unstyled mb-0 small">
                        {SCREENS.filter((screen) => screen.module === module).map((screen) => (
                          <li className="py-1" key={screen.id}>{screen.id} - {screen.name}</li>
                        ))}
                      </ul>
                    </div>
                  </article>
                ))}
              </section>
            </main>
          );
        }
        """
    ).strip()


def _client_js(blueprint: dict[str, Any] | None = None) -> str:
    if blueprint and blueprint.get("milestone_id") == "HITO-008":
        return _asset_text("hito8_client.js")
    return dedent(
        """
        export async function api(path, options = {}) {
          const response = await fetch(`/api/v1${path}`, {
            ...options,
            headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
          });
          const payload = await response.json();
          if (!response.ok) throw payload.error || new Error('api_error');
          return payload.data;
        }
        """
    ).strip()


def _routes_js(blueprint: dict[str, Any] | None = None) -> str:
    if blueprint and blueprint.get("milestone_id") == "HITO-008":
        return _asset_text("hito8_routes.js")
    return "import { SCREENS } from './screens/catalog';\n\nexport const ROUTES = SCREENS.map((screen) => ({ path: screen.route, screen }));\n"


def _screens_js(blueprint: dict[str, Any]) -> str:
    return "export const SCREENS = " + json.dumps(blueprint["screens"], ensure_ascii=True, indent=2) + ";\n"
