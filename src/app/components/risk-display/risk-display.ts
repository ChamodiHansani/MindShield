import { ChangeDetectorRef, Component } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { FormsModule } from '@angular/forms'; 
import { ApiService } from '../../services/api.service';
import { RiskResult } from '../../models/risk-result.model';
import { RouterLink } from '@angular/router';
import { XaiHighlighter } from '../xai-highlighter/xai-highlighter';import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-risk-display',
  standalone: true,
  imports: [
    CommonModule, 
    FormsModule, 
    RouterLink,
    XaiHighlighter 
  ], 
  templateUrl: './risk-display.html',
  styleUrl: './risk-display.css',
})
export class RiskDisplay {
  userInput: string = '';
  analysisResult?: RiskResult;
  isLoading: boolean = false;

  constructor(
    private apiService: ApiService,
    private cdr: ChangeDetectorRef 
  ) {}

onAnalyze() {
  if (!this.userInput || !this.userInput.trim()) return;

  this.isLoading = true;
  this.analysisResult = undefined;

  const inputText = this.userInput;

  this.apiService.analyzeText(inputText)
    .pipe(
      finalize(() => {
        this.isLoading = false;
        this.cdr.detectChanges();
      })
    )
    .subscribe({
      next: (data) => {
        console.log('Data arrived from Python:', data);
        this.analysisResult = data;
        // no need to set isLoading=false here anymore (finalize will do it)
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('API Error:', err);
        // finalize will still run and stop loading
      }
    });
}

onInputChange() {
  if (!this.userInput?.trim()) {
    this.analysisResult = undefined;
  }
}

}