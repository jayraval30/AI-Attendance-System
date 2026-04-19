import streamlit as st

st.set_page_config(page_title="AI Attendance System", layout="wide")

st.markdown("""
<style>

/* -------- APP BACKGROUND -------- */
.stApp {
    background: radial-gradient(circle at 20% 20%, #020617, #020617, #000814);
    color: #E2E8F0;
    font-family: 'Segoe UI', sans-serif;
}

/* -------- SIDEBAR -------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1120, #020617);
    color: white;
    transition: 0.3s ease;
}

/* FULL SIDEBAR HOVER */
[data-testid="stSidebar"]:hover {
    box-shadow:
        inset 0 0 35px rgba(56,189,248,0.25),
        0 0 20px rgba(56,189,248,0.25);
}

/* SIDEBAR TEXT */
[data-testid="stSidebar"] * {
    color: white !important;
}

/* -------- TITLE -------- */
.title-text {
    font-size: 50px;
    font-weight: 800;
    text-align: center;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #38BDF8, #60A5FA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 25px rgba(56,189,248,0.35);
}

/* TITLE UNDERLINE */
.title-line {
    height: 4px;
    width: 200px;
    margin: 12px auto 25px auto;
    border-radius: 10px;
    background: linear-gradient(90deg, #38BDF8, #60A5FA);
    animation: growLine 2s infinite alternate;
}

@keyframes growLine {
    0% { width: 150px; opacity: 0.7; }
    100% { width: 280px; opacity: 1; }
}

/* -------- GLASS CARDS -------- */
.glass-card {
    background: rgba(15,23,42,0.6);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 26px;
    margin: 22px auto;
    width: 80%;
    border: 1px solid rgba(56,189,248,0.2);
    transition: 0.3s ease;
}

/* CARD HOVER */
.glass-card:hover {
    transform: scale(1.02);
    box-shadow:
        0 0 25px rgba(56,189,248,0.35),
        inset 0 0 12px rgba(56,189,248,0.25);
    border: 1px solid #38BDF8;
}

/* CARD TEXT */
.glass-card p {
    font-size: 18px;
    font-weight: 500;
    color: #E2E8F0;
}

/* HIDE DEFAULT STREAMLIT HEADER */
header {visibility: hidden;}
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# -------- HEADER --------
st.markdown("<div class='title-text'>AI Attendance System</div>", unsafe_allow_html=True)
st.markdown("<div class='title-line'></div>", unsafe_allow_html=True)

# -------- LOAD MODEL --------
with st.spinner("Loading Model..."):
    import face_rec

st.markdown("""
<div class='glass-card'>
<p>Face Recognition Model Loaded Successfully</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='glass-card'>
<p>Redis Database Connected Successfully</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='glass-card'>
<p>Use Sidebar to Start Real-Time Attendance or Registration</p>
</div>
""", unsafe_allow_html=True)
