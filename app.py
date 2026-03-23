import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
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
        "description": "11 colonnes × 14 rangées = 154 étiquettes"
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
        "description": "7 colonnes × 22 rangées = 154 étiquettes"
    },
}

# Template selection
template_choice = st.selectbox(
    "Quel template?",
    list(templates.keys())
)

template = templates[template_choice]
st.subheader(f"{template['description']}")

# Input
lot_number = st.text_input(
    "Numéro de lot / Autre",
    placeholder="ex: 2026-10",
    max_chars=20
)

# Settings
col1, col2 = st.columns(2)
with col1:
    font_size = st.slider("Taille du texte", 4, 10, 6)
with col2:
    font_weight = st.selectbox("Poids", ["normal", "bold"], index=1)

# Generate button
if st.button("📥 Générer PDF", use_container_width=True, type="primary"):
    if not lot_number.strip():
        st.error("Rentre un numéro de lot!")
    else:
        # Extract template settings
        groupX = template["groupX"]
        groupY = template["groupY"]
        spacingH = template["spacingH"]
        spacingV = template["spacingV"]
        cols = template["cols"]
        rows = template["rows"]
        page_width = template["page_width"]
        page_height = template["page_height"]
        
        # Créer le PDF en mémoire
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=(page_width*mm, page_height*mm))
        
        # Font
        font_name = "Helvetica-Bold" if font_weight == "bold" else "Helvetica"
        c.setFont(font_name, font_size)
        
        # Générer les étiquettes
        for row in range(rows):
            for col in range(cols):
                x = groupX + (col * spacingH)
                y = page_height - (groupY + (row * spacingV))
                c.drawCentredString(x*mm, y*mm, lot_number)
        
        c.save()
        pdf_buffer.seek(0)
        
        # Download button
        st.download_button(
            label="⬇️ Télécharger le PDF",
            data=pdf_buffer,
            file_name=f"{lot_number}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        st.success(f"✅ PDF généré: {lot_number}.pdf")
        st.info(f"Prêt à imprimer sur {template_choice}")

# Instructions
with st.expander("📖 Instructions"):
    st.markdown("""
    1. Sélectionne le template
    2. Rentre le numéro de lot (ex: 2026-10)
    3. Ajuste la taille du texte si besoin
    4. Clique "Générer PDF"
    5. Télécharge et imprime sur tes étiquettes
    
    **Spécifications disponibles:**
    - ULINE S-15580: 11 col × 14 rangées (½" rond)
    - Rectangle 1" × 0.375": 7 col × 22 rangées
    """)

# Footer
st.divider()
st.caption("Les Mauvaises Herbes 🌿 — Étiquettes de lot automatisées")
