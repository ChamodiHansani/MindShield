import { ChangeDetectorRef, Component } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { FormsModule } from '@angular/forms'; 
import { ApiService } from '../../services/api.service';
import { RiskResult } from '../../models/risk-result.model';
import { RouterLink } from '@angular/router';
import { XaiHighlighter } from '../xai-highlighter/xai-highlighter';


@Component({
  selector: 'app-risk-display',
  standalone: true,
  imports: [
    CommonModule, 
    FormsModule, 
    RouterLink,
    XaiHighlighter // Add to imports array
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
    console.log('Analyze button clicked');
    
    // Prevent empty submissions
    if (!this.userInput || !this.userInput.trim()) {
      console.log('Input is empty');
      return;
    }
    
    this.isLoading = true;
    this.analysisResult = undefined;
    
    // Save input before clearing (optional)
    const inputText = this.userInput;
    
    console.log('Sending text:', inputText);
    
    this.apiService.analyzeText(inputText).subscribe({
      next: (data) => {
        console.log('Data arrived from Python:', data);
        this.analysisResult = data;
        this.isLoading = false;
        
        // Force change detection
        this.cdr.detectChanges();
        
        console.log('isLoading is now:', this.isLoading);
        console.log('Result set:', this.analysisResult);
      },
      error: (err) => {
        console.error('API Error:', err);
        this.isLoading = false;
        this.cdr.detectChanges(); // Force update on error too
      },
      complete: () => {
        console.log('API call completed');
      }
    });
  }
}