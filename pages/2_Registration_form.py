import streamlit as st
import cv2
import numpy as np
import face_rec
import tempfile
import os

st.set_page_config(page_title="Registration Form", layout="wide")

# ================= CSS =================
st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at 20% 20%, #020617, #020617, #000814);
    color: #E2E8F0;
    font-family: 'Segoe UI', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1120, #020617);
    transition: 0.3s ease;
}

[data-testid="stSidebar"]:hover {
    box-shadow:
        inset 0 0 35px rgba(56,189,248,0.25),
        0 0 20px rgba(56,189,248,0.25);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.title-text {
    font-size: 46px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #38BDF8, #60A5FA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.title-line {
    height: 4px;
    width: 200px;
    margin: 12px auto 30px auto;
    border-radius: 10px;
    background: linear-gradient(90deg, #38BDF8, #60A5FA);
    animation: growLine 2s infinite alternate;
}

@keyframes growLine {
    0% { width: 150px; }
    100% { width: 280px; }
}

header {visibility:hidden;}
footer {visibility:hidden;}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<div class='title-text'>Registration Form</div>", unsafe_allow_html=True)
st.markdown("<div class='title-line'></div>", unsafe_allow_html=True)

# ================= FORM =================
reg = face_rec.RegistrationForm()

name = st.text_input("Enter Name")
role = st.selectbox("Select Role", ["Student", "Teacher"])

# ================= MODIFIED =================
batch = st.selectbox(
    "Select Batch",
    [
        "A1","A2","A3",
        "B1","B2","B3",
        "C1","C2","C3",
        "D1","D2","D3"
    ]
)

division = batch[0]
# ===========================================

source = st.radio(
    "Select Input Source",
    ["Upload Image", "Upload Video"],
    horizontal=True
)

FRAME = st.image([])
# ================= IMAGE UPLOAD =================
imgs = st.file_uploader(
    "Upload Face Images",
    ["jpg","png","jpeg"],
    accept_multiple_files=True
)

embeddings_list = []

if imgs:
    for img_file in imgs:
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)

        _, emb = reg.get_embedding(frame)
        if emb is not None:
            embeddings_list.append(emb)

    st.success(f"{len(embeddings_list)} samples collected")

    if st.button("Register Person"):
        if len(embeddings_list) < 5:
            st.warning("Upload at least 5 images")
        else:
            x_array = np.array(embeddings_list)
            x_mean = x_array.mean(axis=0)

            # ================= MODIFIED =================
            # Added division and batch to Redis key
            face_rec.r.hset(
                "academy:register",
                f"{name}@{role}@{division}@{batch}",
                x_mean.tobytes()
            )
            # ===========================================

            st.success("Person Registered Successfully")

# ================= VIDEO UPLOAD =================
if source == "Upload Video":
    vid_file = st.file_uploader("Upload Face Video", type=["mp4","avi","mov"])

    if vid_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(vid_file.read())

        cap = cv2.VideoCapture(tfile.name)
        samples = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            FRAME.image(frame, channels="BGR")
            _, emb = reg.get_embedding(frame)

            if emb is not None:
                with open("face_embedding.txt","ab") as f:
                    np.savetxt(f, emb)
                samples += 1

        cap.release()
        st.success(f"{samples} face samples collected")

        if st.button("Register Video"):

            # ================= MODIFIED =================
            # Added division and batch when saving
            result = reg.save_data_in_redis_db(name, role, division, batch)
            # ===========================================

            if result is True:
                st.success("Registered Successfully")
            else:
                st.error(result)