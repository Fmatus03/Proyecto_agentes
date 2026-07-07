import 'bootstrap/dist/css/bootstrap.min.css';
import { Activity, Bell, Database, LogOut, Menu, Route, Search, ShieldCheck, UserCircle } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { getStoredUser, logout } from './api/client';
import { concretePath, pathForScreen, routeToHash, screenForPath } from './routes';
import { SCREENS } from './screens/catalog';
import { screenComponentFor } from './screens/ScreenViews';

const MODULE_TONES = {
  Auth: 'text-bg-dark',
  Dashboard: 'text-bg-success',
  Insumos: 'text-bg-primary',
  Proveedores: 'text-bg-info',
  Recetas: 'text-bg-warning',
  Maestros: 'text-bg-secondary',
  Produccion: 'text-bg-danger',
  'Inventario productos': 'text-bg-success',
  Mermas: 'text-bg-warning',
  Ventas: 'text-bg-primary',
  Compras: 'text-bg-info',
  Equipos: 'text-bg-secondary',
  Finanzas: 'text-bg-success',
  Reportes: 'text-bg-dark',
  Configuracion: 'text-bg-secondary',
};

function currentHashPath() {
  return window.location.hash ? window.location.hash.slice(1) : '/';
}

function useHashPath() {
  const [path, setPath] = useState(currentHashPath());
  useEffect(() => {
    const sync = () => setPath(currentHashPath());
    window.addEventListener('hashchange', sync);
    if (!window.location.hash) window.history.replaceState(null, '', '#/');
    return () => window.removeEventListener('hashchange', sync);
  }, []);
  return [path, (nextPath) => {
    window.location.hash = concretePath(nextPath);
  }];
}

function groupScreens(screens) {
  return screens.reduce((groups, screen) => {
    groups[screen.module] = groups[screen.module] || [];
    groups[screen.module].push(screen);
    return groups;
  }, {});
}

export default function App() {
  const [path, navigate] = useHashPath();
  const [filter, setFilter] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);
  const [sessionUser, setSessionUser] = useState(getStoredUser());
  const activeScreen = screenForPath(path);
  const ActiveScreen = screenComponentFor(activeScreen);
  const normalizedFilter = filter.trim().toLowerCase();
  const visibleScreens = useMemo(
    () => SCREENS.filter((screen) => {
      const haystack = `${screen.id} ${screen.name} ${screen.module} ${screen.route}`.toLowerCase();
      return !normalizedFilter || haystack.includes(normalizedFilter);
    }),
    [normalizedFilter],
  );
  const modules = groupScreens(visibleScreens);
  const activePath = pathForScreen(activeScreen.id);

  async function handleLogout() {
    await logout();
    setSessionUser(null);
    navigate('/login');
  }

  return (
    <main className="bm-app min-vh-100">
      <style>{`
        :root {
          --bm-ink: #18211f;
          --bm-muted: #61706c;
          --bm-line: #dce4df;
          --bm-soft: #f4f8f5;
          --bm-accent: #157347;
        }
        body { background: #f7faf8; color: var(--bm-ink); }
        .bm-app { display: grid; grid-template-rows: auto 1fr; }
        .bm-topbar { background: #ffffff; border-bottom: 1px solid var(--bm-line); position: sticky; top: 0; z-index: 20; }
        .bm-shell { display: grid; grid-template-columns: minmax(260px, 320px) minmax(0, 1fr); }
        .bm-sidebar { border-right: 1px solid var(--bm-line); background: #ffffff; min-height: calc(100vh - 73px); }
        .bm-content { min-width: 0; }
        .bm-panel { background: #ffffff; border: 1px solid var(--bm-line); border-radius: 8px; }
        .bm-nav-link { border-radius: 6px; color: var(--bm-ink); text-decoration: none; }
        .bm-nav-link:hover { background: var(--bm-soft); color: var(--bm-ink); }
        .bm-nav-link.active { background: var(--bm-accent); color: #ffffff; }
        .bm-icon-btn { width: 38px; height: 38px; display: inline-flex; align-items: center; justify-content: center; }
        .bm-route { word-break: break-word; }
        @media (max-width: 991.98px) {
          .bm-shell { grid-template-columns: 1fr; }
          .bm-sidebar { min-height: 0; border-right: 0; border-bottom: 1px solid var(--bm-line); display: ${menuOpen ? 'block' : 'none'}; }
        }
      `}</style>

      <header className="bm-topbar">
        <div className="container-fluid py-3">
          <div className="d-flex align-items-center justify-content-between gap-3">
            <div className="d-flex align-items-center gap-2 min-w-0">
              <button className="btn btn-outline-secondary bm-icon-btn d-lg-none" type="button" onClick={() => setMenuOpen((value) => !value)} aria-label="menu">
                <Menu size={18} aria-hidden="true" />
              </button>
              <div className="d-flex align-items-center gap-2 min-w-0">
                <span className="d-inline-flex align-items-center justify-content-center rounded-2 text-bg-success" style={{ width: 40, height: 40 }}>
                  <Database size={21} aria-hidden="true" />
                </span>
                <div className="min-w-0">
                  <h1 className="h4 mb-0 text-truncate">BrewMaster</h1>
                  <div className="d-flex align-items-center gap-2 text-secondary small">
                    <Route size={14} aria-hidden="true" />
                    <span className="bm-route">{activeScreen.id} - {activeScreen.name}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="d-none d-md-flex align-items-center gap-2">
              <span className="badge text-bg-light border"><Activity size={14} aria-hidden="true" /> HITO-008</span>
              <span className="badge text-bg-light border"><ShieldCheck size={14} aria-hidden="true" /> /api/v1</span>
              <span className="badge text-bg-light border"><Bell size={14} aria-hidden="true" /> local</span>
            </div>
            <div className="d-flex align-items-center gap-2">
              <span className="d-none d-sm-inline text-secondary small">{sessionUser?.email || 'sin sesion'}</span>
              <UserCircle size={22} aria-label="usuario" />
              {sessionUser ? (
                <button className="btn btn-outline-secondary bm-icon-btn" type="button" onClick={handleLogout} aria-label="salir">
                  <LogOut size={17} aria-hidden="true" />
                </button>
              ) : null}
            </div>
          </div>
        </div>
      </header>

      <div className="bm-shell">
        <aside className="bm-sidebar p-3">
          <div className="input-group input-group-sm mb-3">
            <span className="input-group-text"><Search size={15} aria-hidden="true" /></span>
            <input className="form-control" value={filter} onChange={(event) => setFilter(event.target.value)} placeholder="Buscar pantalla" aria-label="Buscar pantalla" />
          </div>
          <nav className="d-grid gap-3" aria-label="Pantallas BrewMaster">
            {Object.entries(modules).map(([module, screens]) => (
              <section key={module}>
                <div className="d-flex align-items-center justify-content-between mb-2">
                  <h2 className="h6 mb-0">{module}</h2>
                  <span className={`badge ${MODULE_TONES[module] || 'text-bg-light'}`}>{screens.length}</span>
                </div>
                <div className="d-grid gap-1">
                  {screens.map((screen) => {
                    const href = routeToHash(screen.route);
                    const selected = screen.id === activeScreen.id;
                    return (
                      <a
                        className={`bm-nav-link px-2 py-2 small ${selected ? 'active' : ''}`}
                        href={href}
                        key={screen.id}
                        onClick={(event) => {
                          event.preventDefault();
                          navigate(concretePath(screen.route));
                          setMenuOpen(false);
                        }}
                      >
                        <span className="fw-semibold me-2">{screen.id}</span>
                        <span>{screen.name}</span>
                      </a>
                    );
                  })}
                </div>
              </section>
            ))}
          </nav>
        </aside>

        <section className="bm-content p-3 p-xl-4">
          <div className="d-flex flex-wrap align-items-start justify-content-between gap-3 mb-3">
            <div>
              <div className="d-flex flex-wrap align-items-center gap-2 mb-1">
                <span className={`badge ${MODULE_TONES[activeScreen.module] || 'text-bg-light'}`}>{activeScreen.module}</span>
                <span className="badge text-bg-light border bm-route">{activePath}</span>
              </div>
              <h2 className="h3 mb-0">{activeScreen.name}</h2>
            </div>
          </div>
          <ActiveScreen
            currentPath={path}
            navigate={navigate}
            screen={activeScreen}
            sessionUser={sessionUser}
            onSessionChange={setSessionUser}
          />
        </section>
      </div>
    </main>
  );
}
