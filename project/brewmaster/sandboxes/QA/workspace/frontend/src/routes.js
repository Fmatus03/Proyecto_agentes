import { SCREENS } from './screens/catalog';

export function normalizePath(path) {
  const raw = path || '/';
  const clean = raw.startsWith('#') ? raw.slice(1) : raw;
  const withoutQuery = clean.split('?')[0] || '/';
  return withoutQuery.startsWith('/') ? withoutQuery : `/${withoutQuery}`;
}

export function concretePath(route) {
  return normalizePath(route.replace(/:id/g, '1'));
}

export function routeToHash(route) {
  return `#${concretePath(route)}`;
}

function routePattern(route) {
  const escaped = normalizePath(route)
    .replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    .replace(/:id/g, '[^/]+');
  return new RegExp(`^${escaped}$`);
}

export const ROUTES = SCREENS.map((screen) => ({
  path: screen.route,
  defaultPath: concretePath(screen.route),
  screen,
  pattern: routePattern(screen.route),
}));

export function screenForPath(path) {
  const normalized = normalizePath(path);
  return ROUTES.find((route) => route.pattern.test(normalized))?.screen || SCREENS.find((screen) => screen.id === 'P-03') || SCREENS[0];
}

export function pathForScreen(screenId) {
  const route = ROUTES.find((item) => item.screen.id === screenId);
  return route?.defaultPath || '/';
}
