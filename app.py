import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import io
from PIL import Image

st.set_page_config(
    page_title="Etiquettes LMH",
    page_icon="🏷️",
    layout="centered"
)

# Custom colors LMH
colors = {
    "melon": "#f8b1ae",
    "peche": "#fcd1b6",
    "turquoise": "#78c9b1",
    "mauve": "#cbbcdc",
    "vert": "#deedcc",
    "jaune": "#f4d898"
}

# Logo en haut
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        logo = Image.open("/mnt/user-data/uploads/nouveau_logo_noir.png")
        st.image(logo, width=150)
    except:
        pass

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
        "is_circular": True
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
        "is_circular": False
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
    placeholder="ex: 2026-10"
)

# Settings
col1, col2 = st.columns(2)
with col1:
    font_size = st.slider("Taille du texte", 4, 14, 6)
with col2:
    font_weight = st.selectbox("Poids", ["normal", "bold"], index=1)

# Fonction pour wrapper le texte (pour rectangles)
def wrap_text(text, max_chars_per_line=20):
    """Wrap le texte intelligemment sur plusieurs lignes"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars_per_line:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines[:4]  # Max 4 lignes

# Afficher un aperçu textuel
if lot_number.strip():
    st.divider()
    st.subheader("📋 Aperçu")
    
    if template["is_circular"]:
        st.info(f"Texte: {lot_number}")
        if len(lot_number) > 15:
            st.warning("⚠️ Le texte est long pour un cercle. Considère réduire la font.")
    else:
        # Rectangle - montrer comment ça wrap
        lines = wrap_text(lot_number)
        preview_text = "\n".join(lines)
        
        st.code(preview_text, language="text")
        
        if len(lines) <= 2:
            st.success(f"✅ Parfait! ({len(lines)} ligne{'s' if len(lines) > 1 else ''})")
        elif len(lines) <= 4:
            st.info(f"✅ Bon! ({len(lines)} lignes)")
        else:
            st.warning(f"⚠️ Trop de lignes ({len(lines)})! Réduis le texte.")

st.divider()

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
        
        # CONFETTI! 🎉
        st.balloons()

# Instructions
with st.expander("📖 Instructions"):
    st.markdown("""
    1. Sélectionne le template
    2. Rentre le numéro de lot (ex: 2026-10)
    3. Ajuste la taille du texte si besoin
    4. Regarde l'aperçu pour vérifier le wrapping
    5. Clique "Générer PDF" quand c'est bon
    6. Télécharge et imprime sur tes étiquettes
    
    **Spécifications disponibles:**
    - Étiquettes de lot rondes: texte sur 1 ligne
    - Étiquette rectangle Erratum: texte peut wrap sur 2-4 lignes
    """)

# Footer
st.divider()
st.caption("Les Mauvaises Herbes 🌿 — Étiquettes de lot automatisées")
