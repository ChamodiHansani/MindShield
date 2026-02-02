import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, timeout } from 'rxjs/operators';
import { RiskResult } from '../models/risk-result.model';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private predictUrl = 'http://127.0.0.1:8000/predict';
  private explainUrl = 'http://127.0.0.1:8000/explain';

  constructor(private http: HttpClient) {}

  analyzeText(userInput: string): Observable<RiskResult> {
    const headers = new HttpHeaders({
      'accept': 'application/json',
      'Content-Type': 'application/json'
    });

    return this.http.post<RiskResult>(this.predictUrl, { text: userInput }, { headers })
      .pipe(timeout(30000), catchError(this.handleError));
  }

  explainText(text: string, target_label: number) {
    const headers = new HttpHeaders({
      'accept': 'application/json',
      'Content-Type': 'application/json'
    });

    return this.http.post<{ normalized_text: string; highlights: any[] }>(
      this.explainUrl,
      { text, target_label },
      { headers }
    ).pipe(timeout(60000), catchError(this.handleError));
  }

  private handleError(error: HttpErrorResponse) {
    console.error('API Service Error:', error);
    const errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
    return throwError(() => new Error(errorMessage));
  }
}
