import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import uvicorn
import re
import unicodedata

from xai import explain_risky_words

app = FastAPI(title="MindShield Prediction + XAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "./model"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

try:
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH,
        use_fast=True,               # ✅ IMPORTANT
        fix_mistral_regex=True
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_PATH,
        attn_implementation="eager"
    )
    model.eval()
    model.to(device)
    print(f"✓ Model loaded on {device}")
    print("✓ Fast tokenizer:", tokenizer.is_fast)
except Exception as e:
    print("✗ Model load failed:", e)
    tokenizer = None
    model = None


from starlette.middleware.base import BaseHTTPMiddleware

class FixJSONMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and "/predict" in request.url.path:
            body = await request.body()
            body_str = body.decode("utf-8", errors="ignore")

            def fix(match):
                txt = match.group(1)
                txt = txt.replace("\n", "\\n").replace("\r", "\\r")
                return f"\"{txt}\""

            request._body = re.sub(r"\"([^\"]*)\"", fix, body_str).encode("utf-8")

        return await call_next(request)

app.add_middleware(FixJSONMiddleware)


def normalize_text(text):
    if not isinstance(text, str):
        return ""

    text = re.sub(r"[\x00-\x1F\x7F-\x9F]", " ", text)
    text = re.sub(r"\.{2,}", " ", text)

    # ✅ prevent glue like "ඉන්නේ.මට"
    text = re.sub(r"([.!?])", r"\1 ", text)

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[!?;:]", " ", text)
    text = unicodedata.normalize("NFKC", text)
    return text.strip()


class PredictionRequest(BaseModel):
    text: str


@app.post("/predict")
async def predict(request: PredictionRequest):
    try:
        if model is None or tokenizer is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        norm_text = normalize_text(request.text)

        if not norm_text or len(norm_text) < 3:
            return {
                "prediction": "No Risk",
                "confidence": "0%",
                "normalized_text": norm_text,
                "highlights": []
            }

        inputs = tokenizer(
            norm_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        ).to(device)

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            conf, pred = torch.max(probs, dim=-1)

        labels = {0: "High Risk", 1: "Medium Risk", 2: "No Risk"}
        label = labels[pred.item()]

        response = {
            "prediction": label,
            "confidence": f"{round(conf.item() * 100, 2)}%",
            "normalized_text": norm_text,
            "highlights": []
        }

        if label != "No Risk":
            response["highlights"] = explain_risky_words(
                text=norm_text,
                tokenizer=tokenizer,
                model=model,
                device=device,
                target_label=pred.item(),
                top_k=10,
                max_length=128
            )

        return response

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "device": str(device)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
