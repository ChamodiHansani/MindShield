import { Routes } from '@angular/router';
import { Dashboard } from './components/dashboard/dashboard';
import { RiskDisplay } from './components/risk-display/risk-display';

export const routes: Routes = [
{ path: '', component: Dashboard }, 
  { path: 'analyze', component: RiskDisplay }
];
