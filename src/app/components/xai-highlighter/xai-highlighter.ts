import { Component, Input, OnInit, OnChanges, SimpleChanges, ViewEncapsulation, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ApiService } from '../../services/api.service';

interface Highlight {
  word: string;
  score: number;
}

@Component({
  selector: 'app-xai-highlighter',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './xai-highlighter.html',
  styleUrl: './xai-highlighter.css',
  encapsulation: ViewEncapsulation.None
})
export class XaiHighlighter implements OnInit, OnChanges {
  @Input() normalizedText: string = '';
  @Input() highlights: Highlight[] = [];
  @Input() riskLevel: string = '';
  @Input() targetLabel: number = 2;

  isPopupOpen: boolean = false;
  highlightedHtml: SafeHtml = '';
  isExplaining: boolean = false;   
  explainError: string = '';

  constructor(
    private sanitizer: DomSanitizer,
    private cdr: ChangeDetectorRef,
    private apiService: ApiService
  ) {}

  ngOnInit() {
    this.updateHighlightedText();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['normalizedText'] || changes['highlights'] || changes['riskLevel']) {
      this.updateHighlightedText();
    }
  }

  openPopup() {
  // Only for Medium/High
  if (!(this.riskLevel === 'Medium Risk' || this.riskLevel === 'High Risk')) {
    return;
  }

  // If already have highlights, open instantly
  if (this.highlights && this.highlights.length > 0) {
    this.isPopupOpen = true;
    document.body.style.overflow = 'hidden';
    this.updateHighlightedText();
    return;
  }

  // Otherwise: fetch first, then open
  this.isExplaining = true;
  this.explainError = '';
  this.cdr.detectChanges();

  this.apiService.explainText(this.normalizedText, this.targetLabel).subscribe({
    next: (res) => {
      this.highlights = res.highlights as any;
      this.isExplaining = false;

      // open only AFTER highlights loaded
      this.isPopupOpen = true;
      document.body.style.overflow = 'hidden';
      this.updateHighlightedText();
    },
    error: (err) => {
      console.error(err);
      this.isExplaining = false;
      this.explainError = 'Could not load explainability right now.';
      this.cdr.detectChanges();
    }
  });
}


  closePopup() {
    this.isPopupOpen = false;
    document.body.style.overflow = 'auto';
  }

  private updateHighlightedText() {
    const html = this.getHighlightedText();
    this.highlightedHtml = this.sanitizer.bypassSecurityTrustHtml(html);
    this.cdr.detectChanges();
  }

  getHighlightedText(): string {
  if (!this.normalizedText) return '';
  if (!this.highlights || this.highlights.length === 0) return this.normalizedText;

  // 1. Create a Map for quick lookup of word -> score
  const scoreMap = new Map<string, number>();
  this.highlights.forEach(h => {
    // Normalize word for matching (lowercase and trim)
    const key = h.word.trim().toLowerCase();
    scoreMap.set(key, h.score);
  });

  // 2. Split the text but KEEP the delimiters (spaces/punctuation) 
  // This regex handles English and Sinhala (including ZWJ)
  const tokens = this.normalizedText.split(/(\s+|[.,!?;()]+)/);

  // 3. Map tokens to highlighted HTML
  const result = tokens.map(token => {
    const cleanToken = token.trim().toLowerCase();
    
    // Check if this specific token is a risky word
    if (scoreMap.has(cleanToken)) {
      const score = scoreMap.get(cleanToken)!;
      
      // Only highlight if the score is actually risky (e.g., > 0.1)
      if (score > 0.1) {
        const intensityClass = this.getIntensityClass(score);
        return `<mark class="highlight ${intensityClass}" title="Risk score: ${score.toFixed(2)}">${token}</mark>`;
      }
    }
    
    // Otherwise, return the plain token (noise or non-risky word)
    return token;
  });

  return result.join('');
}

  private escapeRegExp(text: string): string {
    return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  private getIntensityClass(score: number): string {
    if (score >= 0.8) return 'intensity-high';
    if (score >= 0.5) return 'intensity-medium';
    return 'intensity-low';
  }

  onBackdropClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (target.classList.contains('popup-overlay')) {
      this.closePopup();
    }
  }

  onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      this.closePopup();
    }
  }
}
