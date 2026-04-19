import streamlit as st
import cv2
import face_rec
import time
import tempfile
import numpy as np

st.set_page_config(page_title="Real-Time Attendance System", layout="wide")

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
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.title-text {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #38BDF8, #60A5FA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.title-line {
    height: 4px;
    width: 200px;
    margin: 12px auto 25px auto;
    border-radius: 10px;
    background: linear-gradient(90deg, #38BDF8, #60A5FA);
}

header {visibility:hidden;}
footer {visibility:hidden;}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<div class='title-text'>Real-Time Attendance System</div>", unsafe_allow_html=True)
st.markdown("<div class='title-line'></div>", unsafe_allow_html=True)

# ================= LOAD DATABASE =================
with st.spinner("Loading Face Database..."):
    redis_face_db = face_rec.retrive_data("academy:register")

# ================= LECTURE SELECTION =================

st.subheader("Lecture Details")

period = st.selectbox(
    "Select Lecture",
    [1,2,3,4,5,6]
)

subject = st.selectbox(
    "Select Subject",
    ["AI","ML","CNS","Python","SC","AI"]
)

st.session_state.period = period
st.session_state.subject = subject

# ================= CLASS SELECTION =================

st.subheader("Class Selection")

division = st.selectbox(
    "Select Division",
    ["A","B","C","D"]
)

# Dynamic batch list based on division
batch_dict = {
    "A": ["A1","A2","A3"],
    "B": ["B1","B2","B3"],
    "C": ["C1","C2","C3"],
    "D": ["D1","D2","D3"]
}

batch = st.selectbox(
    "Select Batch",
    batch_dict[division]
)
# ================= FILTER DATABASE =================
filtered_db = redis_face_db[
    (redis_face_db["Division"] == division) &
    (redis_face_db["Batch"] == batch)
]

# ===== SHOW NUMBER OF REGISTERED STUDENTS =====
st.info(f"Registered Students in {division}-{batch}: {filtered_db.shape[0]}")

# ===== CHECK EMPTY DATABASE =====
if filtered_db.shape[0] == 0:
    st.warning("⚠ No students registered in this Division / Batch")
    st.stop()

# ================= SESSION STATE =================
if "realtime" not in st.session_state:
    st.session_state.realtime = face_rec.RealTimePred()

if "running" not in st.session_state:
    st.session_state.running = False

if "cap" not in st.session_state:
    st.session_state.cap = None

if "setTime" not in st.session_state:
    st.session_state.setTime = time.time()

realtime = st.session_state.realtime

# ================= CAMERA SOURCE =================
camera_source = st.radio(
    "Select Source",
    ["Laptop Webcam", "Phone Camera", "Upload Video", "Upload Photo"],
    horizontal=True
)

PHONE_CAM_URL = st.text_input(
    "Phone Camera URL",
    "http://192.168.0.101:8080/video",
    disabled=(camera_source != "Phone Camera")
)

waitTime = 30

col1, col2 = st.columns(2)

FRAME = st.image([])
status = st.empty()

# ================= START BUTTON =================
if col1.button("▶ Start"):

    st.session_state.running = True
    st.session_state.setTime = time.time()

    source = 0 if camera_source == "Laptop Webcam" else PHONE_CAM_URL

    if st.session_state.cap is None:
        st.session_state.cap = cv2.VideoCapture(source)

# ================= STOP BUTTON =================
if col2.button("⏹ Stop"):

    st.session_state.running = False

    if st.session_state.cap is not None:
        st.session_state.cap.release()
        st.session_state.cap = None

    realtime.saveLogs_redis()
    status.success("Camera stopped. Attendance saved.")

# ================= PHOTO =================
if camera_source == "Upload Photo":

    photo_file = st.file_uploader("Upload Photo", type=["jpg","png","jpeg"])

    if photo_file is not None:

        file_bytes = np.asarray(bytearray(photo_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes,1)

        pred_img = realtime.face_prediction(
            frame,
            filtered_db,
            "facial_features",
            ["Name","Role"],
            thresh=0.5
        )

        FRAME.image(pred_img, channels="BGR")

        realtime.saveLogs_redis()
        status.success("Prediction completed")

# ================= VIDEO =================
elif camera_source == "Upload Video":

    video_file = st.file_uploader("Upload Video", type=["mp4","avi","mov"])

    if video_file is not None and st.session_state.running:

        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())

        cap = cv2.VideoCapture(tfile.name)

        while cap.isOpened():

            ret, frame = cap.read()

            if not ret:
                break

            pred_img = realtime.face_prediction(
                frame,
                filtered_db,
                "facial_features",
                ["Name","Role"],
                thresh=0.5
            )

            FRAME.image(pred_img, channels="BGR")

            if time.time() - st.session_state.setTime >= waitTime:
                realtime.saveLogs_redis()
                st.session_state.setTime = time.time()

            time.sleep(0.03)

        cap.release()
        realtime.saveLogs_redis()

        status.success("Video processed")

# ================= WEBCAM =================
elif camera_source in ["Laptop Webcam","Phone Camera"]:

    if st.session_state.running:

        cap = st.session_state.cap

        if cap is None or not cap.isOpened():

            status.error("Camera not available")
            st.session_state.running = False

        else:

            while st.session_state.running:

                ret, frame = cap.read()

                if not ret:
                    status.error("Frame read failed")
                    break

                pred_img = realtime.face_prediction(
                    frame,
                    filtered_db,
                    "facial_features",
                    ["Name","Role"],
                    thresh=0.5
                )

                FRAME.image(pred_img, channels="BGR")

                if time.time() - st.session_state.setTime >= waitTime:

                    realtime.saveLogs_redis()
                    st.session_state.setTime = time.time()

                    status.success("Attendance saved")

                time.sleep(0.03)

            cap.release()
            st.session_state.cap = None