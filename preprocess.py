import re
import unicodedata

# Shared noise tokens (stopwords / fillers / family-role words you don't want as "risky")
NOISE_TOKENS = {
    "ට", "ද", "ත්", "එත්", "සහ", "නේද", "මන්", "මම", "ඔයා", "ඔබ", "අපි", "අපේ", "මේක",
    "eka", "meka", "oya", "oba", "api", "ape", "dan", "ai", "one", "ona", "kiyala", "wage",
    "අප්පච්චි", "තාත්තා", "අම්මා", "මල්ලි", "අක්කා", "නංගි", "අයියා",
    "amma", "appa", "appachchi", "thaththa", "taththa", "bf", "gf", "bro", "sis", "mn", "mata", "එයා", "කුත්", 
}


def normalize_sinhala_singlish_v2(text: str) -> str:
    if not isinstance(text, str):
        return ""

    # unicode normalize + lowercase
    text = unicodedata.normalize("NFKC", text.lower())

    # --- Variant mapping (Singlish) ---
    SINGLISH_VARIANTS = [
        (r"\b(marenne|maranne|marenawa|merenna)\b", "marenna"),
        (r"\b(jeewithe\s*epa|jeewithe\s*epawela)\b", "jeewithe_epa"),
        (r"\b(siyadiwi\s*nasaganna)\b", "siyadiwi_nasaganna"),
        (r"\b(me\s*loken\s*yanna|loken\s*yanna)\b", "loken_yanna"),
        (r"\b(waha\s*kanna)\b", "waha_kanna"),
        (r"\b(jeewath\s*wenna\s*baa|jeewath\s*wenna\s*ba)\b", "jeewath_wenna_baha"),
        (r"\b(daraganna\s*baa|daraganna\s*ba)\b", "daraganna_baha"),
        (r"\b(manasika\s*peedanaya|manasikawa\s*watila)\b", "manasika_peedanaya"),
        (r"\b(papuwa\s*ridenawa|hadawatha\s*ridenawa)\b", "papuwa_ridenawa"),
        (r"\b(waira\s*karanawa)\b", "waira_karanawa"),
        (r"\b(puduma\s*dukak|pudumai\s*dukak|poduma\s*dukak)\b", "puduma_dukak"),
        (r"\b(mage\s*hitha\s*ridena(wa)?|hitha\s*ridena(wa)?)\b", "hitha_ridenawa"),
    ]

    # --- Variant mapping (Sinhala) ---
    SINHALA_VARIANTS = [
        (r"(මැරෙන්න|මැරෙනවා|මරන්න|මැරුණා)", "මැරෙන්න"),
        (r"ජීවිතේ\s*එපා", "ජීවිතේ_එපා"),
        (r"ජීවිතේම\s*එපා\s*වෙලා", "ජීවිතේ_එපා"),
        (r"සියදිවි\s*නසාගන්න", "සියදිවි_නසාගන්න"),
        (r"ලෝකෙන්\s*යන්න", "ලෝකෙන්_යන්න"),
        (r"වහ\s*කන්න", "වහ_කන්න"),
        (r"වහ\s*කනවා", "වහ_කන්න"),
        (r"ජීවත්\s*වෙන්න\s*බෑ", "ජීවත්_වෙන්න_බෑ"),
        (r"දරාගන්න\s*බෑ", "දරාගන්න_බෑ"),
        (r"දරාගන්න\s*අමාරුයි", "දරාගන්න_බෑ"),
        (r"මානසික\s*පීඩනය", "මානසික_පීඩනය"),
        (r"මානසික\s*පීඩනේක\s*ඉන්නේ", "මානසික_පීඩනය"),
        (r"පීඩනේක\s*ඉන්නේ", "මානසික_පීඩනය"),
        (r"ඔලුව\s*විකාරයි", "ඔලුව_විකාරයි"),
        (r"පපුව\s*රිදෙනවා", "පපුව_රිදෙනවා"),
        (r"හදවත\s*රිදෙනවා", "හදවත_රිදෙනවා"),
        (r"වෛර\s*කරනවා", "වෛර_කරනවා"),
        (r"පුදුම\s*දුකක්", "පුදුම_දුකක්"),
        (r"හිත\s*රිදෙනවා", "හිත_රිදෙනවා"),
    ]

    for pattern, standard in SINGLISH_VARIANTS:
        text = re.sub(pattern, standard, text, flags=re.IGNORECASE)

    for pattern, standard in SINHALA_VARIANTS:
        text = re.sub(pattern, standard, text)

    # -----------------------------
    # Remove NOISE_TOKENS after variant standardization
    # -----------------------------
    words = [w for w in text.split() if w not in NOISE_TOKENS]
    text = " ".join(words)

    # --- Generalization rules ---
    SINGLISH_RULES = [
        (r"\b(ba|baa+|baha)\b", "baha"),
        (r"\b(epa|epaa+)\b", "epa"),
        (r"\b(na|naa)\b", "na"),
        (r"\b(duka|duki)\b", "duka"),
        (r"\b(dukai+|dukak)\b", "dukak"),
        (r"\b(wedana[a-z]*)\b", "wedanawa"),
        (r"\b(riden[a-z]*)\b", "ridenawa"),
        (r"\b(thani[a-z]*)\b", "thani"),
        (r"\b(thanikama[a-z]*)\b", "thanikama"),
        (r"\b(hithenawa|hithenav[a-z]*)\b", "hithenawa"),
        (r"\b(bari|beri)\b", "bari"),
    ]

    SINHALA_RULES = [
        (r"(බෑ|බැ|බැහැ)", "බැහැ"),
        (r"එපා+", "එපා"),
        (r"දුකයි", "දුක"),
        (r"තනියෙන්", "තනි"),
        (r"\bනෙමෙයි\b", "නෙවෙයි"),
        (r"\bමොකක්ද\b", "මොකද්ද"),
        (r"\bකොහොමද\b", "කොහොම"),
    ]

    for pattern, repl in SINGLISH_RULES:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    for pattern, repl in SINHALA_RULES:
        text = re.sub(pattern, repl, text)

    # remove urls, normalize spaces
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
