import re
import torch
from preprocess import NOISE_TOKENS

def is_noise_token(w: str) -> bool:
    """Checks if a word should be ignored for highlighting."""
    w_clean = w.strip().lower()
    if not w_clean:
        return True
    
    # If the word is in our noise list (amma, oya, etc.), it's noise
    if w_clean in NOISE_TOKENS:
        return True
    
    # Very short tokens or tokens with digits are usually noise
    if len(w_clean) <= 1 or bool(re.search(r"\d", w_clean)):
        return True
        
    # Pure punctuation is noise
    if re.fullmatch(r"[\W]+", w_clean):
        return True
        
    return False

def explain_risky_words(
    text,
    tokenizer,
    model,
    device,
    target_label,
    top_k=150,
    max_length=512
):
    model.eval()

    if not getattr(tokenizer, "is_fast", False):
        raise ValueError("Tokenizer must be fast (use_fast=True) for offset_mapping.")

    # Tokenize with offsets to map tokens back to original characters
    enc = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=max_length,
        padding=True,
        return_offsets_mapping=True
    )

    input_ids = enc["input_ids"].to(device)
    attention_mask = enc["attention_mask"].to(device)
    offsets = enc["offset_mapping"][0].tolist()

    # Get Embeddings and enable gradients
    embeddings = model.get_input_embeddings()(input_ids)
    embeddings.requires_grad_(True)

    # Forward pass
    outputs = model(inputs_embeds=embeddings, attention_mask=attention_mask)
    logit = outputs.logits[0, target_label]

    # Calculate Gradients
    grads = torch.autograd.grad(outputs=logit, inputs=embeddings)[0]
    
    # L2 Norm Scoring: Best for identifying importance in long sequences
    token_scores = torch.norm(grads * embeddings, p=2, dim=-1)[0]
    token_scores = token_scores.detach().cpu().tolist()

    # CRITICAL REGEX: 
    # [A-Za-z0-9_]+ handles English/Singlish and underscored phrases
    # [\u0D80-\u0DFF\u200D\u200C_]+ handles Sinhala + ZWJ + ZWNJ (Fixes ප්‍රශ්නේ)
    word_spans = [
        (m.group(), m.start(), m.end())
        for m in re.finditer(r"[A-Za-z0-9_]+|[\u0D80-\u0DFF\u200D\u200C_]+", text)
    ]

    all_word_data = []
    for word, ws, we in word_spans:
        # Match model tokens to this specific word using character offsets
        scores = []
        for (ts, te), sc in zip(offsets, token_scores):
            if ts == te: continue # Skip special tokens like [CLS]
            if ts >= ws and te <= we:
                scores.append(sc)

        if scores:
            avg_score = sum(scores) / len(scores)
            
            # If it's a noise token (amma, mata, etc.), give it a 0 score
            # This ensures it shows up in text but doesn't "glow"
            if is_noise_token(word):
                final_score = 0.0
            else:
                final_score = avg_score
                
            all_word_data.append({"word": word, "score": float(final_score)})

    if not all_word_data:
        return []

    # Normalize scores between 0.0 and 1.0 based on the highest risky word found
    mx = max((w["score"] for w in all_word_data), default=1.0)
    mx = mx if mx > 0 else 1.0
    
    for w in all_word_data:
        w["score"] = round(w["score"] / mx, 3)

    # Prepare final display list
    # We keep the underscores during processing but replace them with spaces for the UI
    final_display = []
    for item in all_word_data[:top_k]:
        final_display.append({
            "word": item["word"].replace("_", " "), 
            "score": item["score"]
        })

    return final_display