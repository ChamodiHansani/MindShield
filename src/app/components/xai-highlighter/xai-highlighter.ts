import { Component, Input, OnInit, OnChanges, SimpleChanges, ViewEncapsulation, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

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
 
  isPopupOpen: boolean = false;
  highlightedHtml: SafeHtml = '';
 
  constructor(
    private sanitizer: DomSanitizer,
    private cdr: ChangeDetectorRef
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
    this.isPopupOpen = true;
    document.body.style.overflow = 'hidden';
    // Force re-generation and detection when popup opens (fixes any timing issues)
    this.updateHighlightedText();
  }

  closePopup() {
    this.isPopupOpen = false;
    document.body.style.overflow = 'auto';
  }

  private updateHighlightedText() {
    const html = this.getHighlightedText();
    this.highlightedHtml = this.sanitizer.bypassSecurityTrustHtml(html);
    this.cdr.detectChanges(); // Ensures immediate render
  }

  getHighlightedText(): string {
    if (!this.normalizedText) return this.normalizedText || '';
    if (!this.highlights || this.highlights.length === 0) return this.normalizedText;

    let highlightedText = this.normalizedText;

    const sortedHighlights = [...this.highlights].sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      return b.word.length - a.word.length;
    });

    const processedWords = new Set<string>();

   sortedHighlights.forEach((highlight) => {
  const word = highlight.word.trim();
  const score = highlight.score;
  if (!word || processedWords.has(word)) return;

  const intensityClass = this.getIntensityClass(score);
  
  // 1. Escape the word for RegEx
  let pattern = this.escapeRegExp(word);

  // 2. Replace escaped spaces with a "match any connector" pattern
  // This matches spaces, underscores, or dashes: [\s\-_]+
  pattern = pattern.replace(/\s+/g, '[\\s\\-_]+');

  const regex = new RegExp(`(${pattern})`, 'g');

  if (highlightedText.match(regex)) {
    highlightedText = highlightedText.replace(
      regex,
      `<mark class="highlight ${intensityClass}" data-score="${score.toFixed(2)}" title="Risk score: ${score.toFixed(2)}">$1</mark>`
    );
  }
  processedWords.add(word);
});

    return highlightedText;
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