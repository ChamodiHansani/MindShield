import re
import torch

def explain_risky_words(
    text,
    tokenizer,
    model,
    device,
    target_label,
    top_k=10,
    max_length=128
):
    model.eval()

    if not getattr(tokenizer, "is_fast", False):
        raise ValueError("Tokenizer must be fast (use_fast=True) to use offset_mapping correctly.")

    # --- Tokenize with offsets ---
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

    # --- Grad x Input on embeddings ---
    embeddings = model.get_input_embeddings()(input_ids)
    embeddings.requires_grad_(True)

    outputs = model(inputs_embeds=embeddings, attention_mask=attention_mask)
    logit = outputs.logits[0, target_label]

    grads = torch.autograd.grad(outputs=logit, inputs=embeddings)[0]
    token_scores = (grads * embeddings).abs().sum(dim=-1)[0]
    token_scores = token_scores.detach().cpu().tolist()

    # --- Build real WORD spans using whitespace ---
    word_spans = [(m.group(), m.start(), m.end()) for m in re.finditer(r"\S+", text)]

    # --- Assign token scores to the word span they belong to ---
    word_scores = []
    for word, ws, we in word_spans:
        scores = []
        for (ts, te), sc in zip(offsets, token_scores):
            if ts == te:   # special tokens
                continue
            # token fully inside word span
            if ts >= ws and te <= we:
                scores.append(sc)

        if scores:
            word_scores.append({
                "word": word,
                "score": float(sum(scores) / len(scores))
            })

    # Normalize 0..1
    if word_scores:
        mx = max(w["score"] for w in word_scores)
        mx = mx if mx > 0 else 1.0
        for w in word_scores:
            w["score"] = round(w["score"] / mx, 3)

    word_scores.sort(key=lambda x: x["score"], reverse=True)
    return word_scores[:top_k]
