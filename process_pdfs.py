import pdfplumber
import pandas as pd
import joblib
import re
import os
import json
from statistics import mean

# -------- Load model and label encoder --------
model = joblib.load("/app/models/headings_model.pkl")
le = joblib.load("/app/models/label_encoder.pkl")

# -------- Input and Output directories --------
input_dir = "/app/input"
output_dir = "/app/output"

# -------- Process each PDF file --------
for filename in os.listdir(input_dir):
    if not filename.lower().endswith(".pdf"):
        continue

    pdf_path = os.path.join(input_dir, filename)
    output_json_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))

    lines_data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(extra_attrs=["fontname", "size"])

            # Group words by y-position
            grouped_lines = {}
            for word in words:
                y = round(word["top"], 1)
                grouped_lines.setdefault(y, []).append(word)

            for y_pos, word_group in grouped_lines.items():
                word_group = sorted(word_group, key=lambda w: w["x0"])

                # Join words with smart spacing
                text = "".join([
                    w["text"] if (i == 0 or w["x0"] - word_group[i - 1]["x1"] < 2) else " " + w["text"]
                    for i, w in enumerate(word_group)
                ]).strip()

                if not text or len(text) < 2:
                    continue

                font_sizes = [w["size"] for w in word_group if "size" in w]
                x_positions = [w["x0"] for w in word_group]

                lines_data.append({
                    "text": text,
                    "page": page_num + 1,
                    "font_size": mean(font_sizes) if font_sizes else 12,
                    "y_position": y_pos,
                    "x_position": min(x_positions) if x_positions else 0,
                    "is_bold": int(any("Bold" in w["fontname"] for w in word_group)),
                    "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text),
                    "text_length": len(text),
                    "is_numbered": int(bool(re.match(r"^\d+(\.\d+)*", text)))
                })

    # Skip empty PDF
    if not lines_data:
        print(f"⚠️ Skipping {filename}: No text found.")
        continue

    # -------- Predict Labels --------
    df = pd.DataFrame(lines_data)
    features = ["font_size", "y_position", "x_position", "text_length", "uppercase_ratio", "is_bold"]
    X = df[features]
    y_pred = model.predict(X)
    df["predicted_label"] = le.inverse_transform(y_pred)

    # -------- Title Detection --------
    first_page = df[df["page"] == 1]
    if not first_page.empty:
        title_candidate = first_page.sort_values(
            by=["font_size", "is_bold", "text_length"],
            ascending=[False, False, False]
        ).iloc[0]["text"]
        title = title_candidate.strip()
    else:
        title = "Untitled Document"

    # -------- Extract Outline --------
    outline = []
    for level in ["H1", "H2", "H3"]:
        for _, row in df[df["predicted_label"] == level].iterrows():
            outline.append({
                "level": level,
                "text": row["text"].strip(),
                "page": int(row["page"])
            })

    # -------- Save JSON --------
    output = {
        "title": title,
        "outline": outline
    }

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"✅ Processed: {filename} → {output_json_path}")
