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
