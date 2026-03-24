import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
import io

st.set_page_config(
    page_title="Etiquettes LMH",
    page_icon="🏷️",
    layout="centered"
)
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
        "label_width_mm": 25.4,   # 1 inch
        "label_height_mm": 9.525, # 0.375 inch
        "margin_h_mm": 1.2,
        "margin_v_mm": 0.8,
    },
}


def fit_text_to_label(text, font_name, max_width_mm, max_height_mm, font_size_start, min_font_size=4):
    """
    Wraps text word-by-word using actual rendered widths (stringWidth).
    Reduces font size until the text block fits within the label.
    Returns (lines, font_size, line_height_pts).
    """
    max_width_pts = max_width_mm * mm
    max_height_pts = max_height_mm * mm
    words = text.split()

    for fs in range(font_size_start, min_font_size - 1, -1):
        line_height = fs * 1.15  # tight but readable line spacing

        lines = []
        current_line = []

        for word in words:
            test = ' '.join(current_line + [word])
            if stringWidth(test, font_name, fs) <= max_width_pts:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                # If a single word is wider than the label, force it on its own line
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        total_height = len(lines) * line_height
        if total_height <= max_height_pts:
            return lines, fs, line_height

    # Fallback: return whatever we have at min font size
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
    "Numéro de lot",
    placeholder="ex: 2026-10",
    max_chars=200
)

# Settings
col1, col2 = st.columns(2)
with col1:
    font_size = st.slider("Taille du texte", 4, 10, 6)
with col2:
    font_weight = st.selectbox("Poids", ["normal", "bold"], index=1)

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

        font_name = "Helvetica-Bold" if font_weight == "bold" else "Helvetica"

        if template["multiline"]:
            # Rectangle label: fit text with auto line-wrap and auto font-size
            max_w = template["label_width_mm"] - 2 * template["margin_h_mm"]
            max_h = template["label_height_mm"] - 2 * template["margin_v_mm"]

            lines, actual_fs, line_height = fit_text_to_label(
                lot_number, font_name, max_w, max_h, font_size
            )
            c.setFont(font_name, actual_fs)

            n = len(lines)
            # Vertical center: offset first baseline up by half the total block height
            # line_height covers one line; block = n lines
            v_offset = ((n - 1) * line_height) / 2

            for row in range(rows):
                for col in range(cols):
                    x = (groupX + col * spacingH) * mm
                    y = (page_height - (groupY + row * spacingV)) * mm

                    for i, line in enumerate(lines):
                        c.drawCentredString(x, y + v_offset - i * line_height, line)
        else:
            # Round label: single line, unchanged behaviour
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
