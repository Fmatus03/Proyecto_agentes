from __future__ import annotations

import json
from textwrap import dedent
from typing import Any

from .brewmaster_docs import _json

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


def _app_jsx(blueprint: dict[str, Any] | None = None) -> str:
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


def _client_js() -> str:
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


def _routes_js() -> str:
    return "import { SCREENS } from './screens/catalog';\n\nexport const ROUTES = SCREENS.map((screen) => ({ path: screen.route, screen }));\n"


def _screens_js(blueprint: dict[str, Any]) -> str:
    return "export const SCREENS = " + json.dumps(blueprint["screens"], ensure_ascii=True, indent=2) + ";\n"
