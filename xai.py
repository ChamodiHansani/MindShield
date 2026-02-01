import re
import torch
from preprocess import NOISE_TOKENS


def looks_like_number(w: str) -> bool:
    # If token contains any digit, ignore it (25, 25ක, 26යි, Rs500, 3rd etc.)
    return bool(re.search(r"\d", w))


def is_noise_token(w: str) -> bool:
    w_clean = w.strip().lower()
    if not w_clean:
        return True

    # Keep underscore phrases like "දරාගන්න_බෑ"
    if "_" in w_clean:
        return False

    if looks_like_number(w_clean):
        return True

    if w_clean in NOISE_TOKENS:
        return True

    if len(w_clean) <= 2:
        return True

    if re.fullmatch(r"[\W]+", w_clean):
        return True

    return False


def explain_risky_words(
    text,
    tokenizer,
    model,
    device,
    target_label,
    top_k=10,
    max_length=512
):
    model.eval()

    if not getattr(tokenizer, "is_fast", False):
        raise ValueError("Tokenizer must be fast (use_fast=True) to use offset_mapping correctly.")

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

    embeddings = model.get_input_embeddings()(input_ids)
    embeddings.requires_grad_(True)

    outputs = model(inputs_embeds=embeddings, attention_mask=attention_mask)
    logit = outputs.logits[0, target_label]

    grads = torch.autograd.grad(outputs=logit, inputs=embeddings)[0]
    token_scores = (grads * embeddings).abs().sum(dim=-1)[0]
    token_scores = token_scores.detach().cpu().tolist()

    # Better spans: Sinhala / Latin / underscores / digits (digits will be filtered anyway)
    word_spans = [
        (m.group(), m.start(), m.end())
        for m in re.finditer(r"[A-Za-z_]+|[\u0D80-\u0DFF_]+|\d+", text)
    ]

    word_scores_raw = []
    for word, ws, we in word_spans:
        scores = []
        for (ts, te), sc in zip(offsets, token_scores):
            if ts == te:
                continue
            if ts >= ws and te <= we:
                scores.append(sc)

        if scores:
            word_scores_raw.append({"word": word, "score": float(sum(scores) / len(scores))})

    if not word_scores_raw:
        return []

    mx = max(w["score"] for w in word_scores_raw)
    mx = mx if mx > 0 else 1.0
    for w in word_scores_raw:
        w["score"] = w["score"] / mx

    filtered = [w for w in word_scores_raw if not is_noise_token(w["word"])]

    if not filtered:
        return []

    # Deduplicate (keep max score)
    best = {}
    for item in filtered:
        k = item["word"]
        best[k] = max(best.get(k, 0.0), item["score"])

    deduped = [{"word": k, "score": round(v, 3)} for k, v in best.items()]
    deduped.sort(key=lambda x: x["score"], reverse=True)

    # Display: underscore -> space
    final = []
    for item in deduped[:top_k]:
        raw_word = item["word"]
        display_word = raw_word.replace("_", " ")
        final.append({"word": display_word, "score": item["score"]})

    return final
