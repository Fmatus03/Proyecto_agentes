import { SCREENS } from './screens/catalog';

export const ROUTES = SCREENS.map((screen) => ({ path: screen.route, screen }));
