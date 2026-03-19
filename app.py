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
st.subheader("ULINE S-15580 — 11 × 14 = 154 étiquettes")

# Input
lot_number = st.text_input(
    "Numéro de lot",
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
        # Positions centrées (mesurées)
        groupX = 12.55
        groupY = 16.07
        spacingH = 19.08
        spacingV = 19.0202
        
        # Créer le PDF en mémoire
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=(215.9*mm, 279.4*mm))
        
        # Font
        font_name = "Helvetica-Bold" if font_weight == "bold" else "Helvetica"
        c.setFont(font_name, font_size)
        
        # Générer les 154 étiquettes
        for row in range(14):
            for col in range(11):
                x = groupX + (col * spacingH)
                y = 279.4 - (groupY + (row * spacingV))
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
        st.info("Prêt à imprimer sur ULINE S-15580")

# Instructions
with st.expander("📖 Instructions"):
    st.markdown("""
    1. Rentre le numéro de lot (ex: 2026-10)
    2. Ajuste la taille du texte si besoin
    3. Clique "Générer PDF"
    4. Télécharge et imprime sur les étiquettes ULINE
    
    **Spécifications:**
    - Template: ULINE S-15580
    - Grille: 11 colonnes × 14 rangées = 154 étiquettes
    - Format: 8.5" × 11"
    """)

# Footer
st.divider()
st.caption("Les Mauvaises Herbes 🌿 — Étiquettes de lot automatisées")
