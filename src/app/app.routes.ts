import { Routes } from '@angular/router';
import { Dashboard } from './components/dashboard/dashboard';
import { RiskDisplay } from './components/risk-display/risk-display';
import { Features } from './components/features/features';

export const routes: Routes = [
{ path: '', component: Dashboard, title: 'MindShield - Home' },
  { path: 'analyze', component: RiskDisplay, title: 'MindShield - Intelligence' },
  { path: 'features', component: Features, title: 'MindShield - Features' },
  { path: '**', redirectTo: '' }
];
