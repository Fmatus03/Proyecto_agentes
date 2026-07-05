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


def _app_jsx() -> str:
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
