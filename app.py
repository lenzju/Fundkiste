import streamlit as st
from firebase_config import db, bucket
from ml_model import predict_category
from utils import generate_filename, get_current_date
from PIL import Image
import io

st.set_page_config(page_title="Digitale Fundkiste", layout="centered")

st.title("📦 Digitale Fundkiste")

# Navigation
page = st.radio("Auswahl", ["Startseite", "Gefunden melden", "Suchen"])

# ------------------- STARTSEITE -------------------
if page == "Startseite":
    st.subheader("Was möchtest du tun?")
    col1, col2 = st.columns(2)FIREBASE_KEY

    with col1:
        if st.button("Ich habe etwas gefunden"):
            st.session_state.page = "Gefunden melden"

    with col2:
        if st.button("Ich suche etwas"):
            st.session_state.page = "Suchen"

# ------------------- MELDEN -------------------
elif page == "Gefunden melden":

    st.subheader("Neuen Eintrag erstellen")

    typ = st.selectbox("Typ", ["gefunden", "gesucht"])

    uploaded_file = st.file_uploader("Bild hochladen", type=["jpg", "png", "jpeg"])
    description = st.text_area("Beschreibung")

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Vorschau", use_column_width=True)

        category = predict_category(image)
        st.success(f"Automatisch erkannte Kategorie: {category}")

    if st.button("Speichern") and uploaded_file:

        filename = generate_filename()
        blob = bucket.blob(f"images/{filename}")

        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        blob.upload_from_string(image_bytes.getvalue(), content_type="image/jpeg")

        blob.make_public()

        db.collection("fundkiste").add({
            "bild_url": blob.public_url,
            "kategorie": category,
            "beschreibung": description,
            "typ": typ,
            "datum": get_current_date()
        })

        st.success("Eintrag gespeichert!")

# ------------------- SUCHEN -------------------
elif page == "Suchen":

    st.subheader("Einträge durchsuchen")

    filter_typ = st.selectbox("Typ filtern", ["gefunden", "gesucht"])
    filter_category = st.selectbox("Kategorie", ["Alle", "Hose", "Mütze", "Pullover", "Sonstiges"])
    search_text = st.text_input("Beschreibung durchsuchen")

    docs = db.collection("fundkiste").stream()

    for doc in docs:
        data = doc.to_dict()
FIREBASE_KEY
        if data["typ"] != filter_typ:
            continue

        if filter_category != "Alle" and data["kategorie"] != filter_category:
            continue

        if search_text.lower() not in data["beschreibung"].lower():
            continue

        st.image(data["bild_url"], width=200)
        st.write(f"**Kategorie:** {data['kategorie']}")
        st.write(f"**Beschreibung:** {data['beschreibung']}")
        st.write(f"**Datum:** {data['datum']}")

        if st.button("Löschen", key=doc.id):
            db.collection("fundkiste").document(doc.id).delete()
            st.warning("Eintrag gelöscht!")
