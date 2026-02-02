import { Routes } from '@angular/router';
import { Dashboard } from './components/dashboard/dashboard';
import { RiskDisplay } from './components/risk-display/risk-display';

export const routes: Routes = [
{ path: '', component: Dashboard, title: 'MindShield - Home' }, 
  { path: 'analyze', component: RiskDisplay, title: 'MindShield - Intelligence' },
  { path: '**', redirectTo: '' }
];
