export interface Highlight {
  word: string;
  score: number;
}

export interface RiskResult {
  prediction: string;      
  confidence: string;     
  normalized_text: string; 
  highlights: Highlight[]; 
}