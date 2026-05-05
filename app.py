import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth, registerFont
from reportlab.pdfbase.ttfonts import TTFont
import os
import io

# Enregistrement de la police Lato si disponible, sinon fallback Helvetica
_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_LATO_REGULAR = os.path.join(_FONT_DIR, "Lato-Regular.ttf")
_LATO_BOLD = os.path.join(_FONT_DIR, "Lato-Bold.ttf")

if os.path.exists(_LATO_REGULAR) and os.path.exists(_LATO_BOLD):
    registerFont(TTFont("Lato", _LATO_REGULAR))
    registerFont(TTFont("Lato-Bold", _LATO_BOLD))
    FONT_NORMAL = "Lato"
    FONT_BOLD = "Lato-Bold"
else:
    FONT_NORMAL = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

st.set_page_config(
    page_title="Etiquettes LMH",
    page_icon="🏷️",
    layout="centered"
)

# Logo
_LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
if os.path.exists(_LOGO_PATH):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(_LOGO_PATH, use_container_width=True)
    st.title("Générateur d'étiquettes")
else:
    st.title("🏷️ Générateur d'étiquettes")

# Templates definition
templates = {
    "Étiquettes de lot rondes (ULINE S-15580 ½\" rond)": {
        "groupX": 12.55,
        "groupY": 16.07,
        "spacingH": 19.08,
        "spacingV": 19.0202,
        "cols": 11,
        "rows": 14,
        "page_width": 215.9,
        "page_height": 279.4,
        "total": 154,
        "description": "11 colonnes × 14 rangées = 154 étiquettes",
        "multiline": False,
    },
    "Étiquette rectangle Erratum (1\" × 0.375\")": {
        "groupX": 24.077,
        "groupY": 13.529,
        "spacingH": 27.958,
        "spacingV": 12.015,
        "cols": 7,
        "rows": 22,
        "page_width": 215.9,
        "page_height": 279.4,
        "total": 154,
        "description": "7 colonnes × 22 rangées = 154 étiquettes",
        "multiline": True,
        "label_width_mm": 25.4,
        "label_height_mm": 9.525,
        "margin_h_mm": 1.2,
        "margin_v_mm": 0.8,
    },
    "Étiquette rectangle Avery 5167 (1.75\" × 0.5\")": {
        "groupX": 30.525,
        "groupY": 19.45,
        "spacingH": 52.2,
        "spacingV": 12.7,
        "cols": 4,
        "rows": 20,
        "page_width": 215.9,
        "page_height": 279.4,
        "total": 80,
        "description": "4 colonnes × 20 rangées = 80 étiquettes",
        "multiline": True,
        "label_width_mm": 44.45,
        "label_height_mm": 12.7,
        "margin_h_mm": 2.5,
        "margin_v_mm": 1.5,
    },
}


def fit_text_to_label(text, font_name, max_width_mm, max_height_mm, font_size_start, min_font_size=3):
    max_width_pts = max_width_mm * mm
    max_height_pts = max_height_mm * mm
    words = text.split()

    for fs in range(font_size_start, min_font_size - 1, -1):
        line_height = fs * 1.15

        lines = []
        current_line = []

        for word in words:
            test = ' '.join(current_line + [word])
            if stringWidth(test, font_name, fs) <= max_width_pts:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        total_height = len(lines) * line_height
        if total_height <= max_height_pts:
            return lines, fs, line_height

    return lines, min_font_size, min_font_size * 1.15


# Template selection
template_choice = st.selectbox(
    "Quel template?",
    list(templates.keys())
)
template = templates[template_choice]
st.subheader(f"{template['description']}")

# Input
lot_number = st.text_input(
    "Écris ton numéro de lot ou erratum (ou autre):",
    placeholder="ex: 2026-10",
)

# Settings
col1, col2 = st.columns(2)
with col1:
    font_size = st.slider("Taille du texte", 3, 10, 6)
with col2:
    font_weight = st.selectbox("Poids", ["normal", "bold"], index=0)

if template["multiline"] and lot_number and len(lot_number.strip()) > 20:
    st.info("Pour les textes longs, la taille de police s'ajuste automatiquement pour que tout rentre sur l'étiquette. Le slider indique la taille maximale souhaitée.")

# Generate button
if st.button("📥 Générer PDF", use_container_width=True, type="primary"):
    if not lot_number.strip():
        st.error("Rentre un numéro de lot!")
    else:
        groupX = template["groupX"]
        groupY = template["groupY"]
        spacingH = template["spacingH"]
        spacingV = template["spacingV"]
        cols = template["cols"]
        rows = template["rows"]
        page_width = template["page_width"]
        page_height = template["page_height"]

        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=(page_width*mm, page_height*mm))

        font_name = FONT_BOLD if font_weight == "bold" else FONT_NORMAL

        if template["multiline"]:
            max_w = template["label_width_mm"] - 2 * template["margin_h_mm"]
            max_h = template["label_height_mm"] - 2 * template["margin_v_mm"]

            lines, actual_fs, line_height = fit_text_to_label(
                lot_number, font_name, max_w, max_h, font_size
            )
            c.setFont(font_name, actual_fs)

            n = len(lines)
            v_offset = ((n - 1) * line_height) / 2

            for row in range(rows):
                for col in range(cols):
                    x = (groupX + col * spacingH) * mm
                    y = (page_height - (groupY + row * spacingV)) * mm

                    for i, line in enumerate(lines):
                        c.drawCentredString(x, y + v_offset - i * line_height, line)
        else:
            c.setFont(font_name, font_size)
            for row in range(rows):
                for col in range(cols):
                    x = groupX + (col * spacingH)
                    y = page_height - (groupY + (row * spacingV))
                    c.drawCentredString(x*mm, y*mm, lot_number)

        c.save()
        pdf_buffer.seek(0)

        st.download_button(
            label="⬇️ Télécharger le PDF",
            data=pdf_buffer,
            file_name=f"{lot_number[:40]}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.success(f"✅ PDF généré: {lot_number[:40]}.pdf")
        st.info(f"Prêt à imprimer sur {template_choice}")

# Instructions
with st.expander("📖 Instructions"):
    st.markdown("""
    1. Sélectionne le template
    2. Rentre le texte à imprimer
    3. Ajuste la taille du texte si besoin (le texte rétrécira automatiquement si nécessaire)
    4. Clique "Générer PDF"
    5. Télécharge et imprime sur tes étiquettes

    **Spécifications disponibles:**
    - ULINE S-15580: 11 col × 14 rangées (½" rond)
    - Rectangle 1" × 0.375": 7 col × 22 rangées
    """)

# Footer
st.divider()
st.caption("Les Mauvaises Herbes 🌿 — Étiquettes de lot automatisées")
