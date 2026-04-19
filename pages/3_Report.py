import pandas as pd
import streamlit as st
from Home import face_rec
import datetime

# ================= PAGE CONFIG =================
st.set_page_config(page_title='Reporting', layout='wide')

# ================= UI DESIGN =================
st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at 20% 20%, #020617, #020617, #000814);
    color: #E2E8F0;
    font-family: 'Segoe UI', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1120, #020617);
    color: white;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

header {visibility: hidden;}
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

st.subheader("Attendance Reporting")

# ================= REDIS LOGS =================
name = "attendance:logs"

def load_logs(name, end=-1):
    logs_list = face_rec.r.lrange(name, start=0, end=end)
    return logs_list

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(
    ['Registered Data','Logs','Attendance Report']
)

# =========================================================
# TAB 1 : REGISTERED STUDENTS
# =========================================================

with tab1:

    if st.button("Refresh Data"):

        with st.spinner("Retrieving data from Redis..."):

            redis_face_db = face_rec.retrive_data(
                name="academy:register"
            )

            st.dataframe(
                redis_face_db[
                    ['Name','Role','Division','Batch']
                ]
            )

# =========================================================
# TAB 2 : RAW LOGS
# =========================================================

with tab2:

    if st.button("Refresh Logs"):

        logs = load_logs(name)

        st.write(logs)

# =========================================================
# TAB 3 : ATTENDANCE REPORT
# =========================================================

with tab3:

    st.subheader("Lecture Attendance Report")

    logs_list = load_logs(name)

    if len(logs_list) == 0:
        st.warning("No attendance logs found")
        st.stop()

    # ================= DECODE REDIS BYTES =================

    convert = lambda x: x.decode('utf-8')

    logs_string = list(map(convert, logs_list))

    split = lambda x: x.split('@')

    logs_nested = list(map(split, logs_string))

    # ===== FIX OLD LOG FORMAT =====
    fixed_logs = []

    for row in logs_nested:

        if len(row) == 3:
            # old format
            name, role, time = row
            fixed_logs.append([name, role, "0", "Unknown", time])

        elif len(row) == 5:
            # new format
            fixed_logs.append(row)

    logs_df = pd.DataFrame(
        fixed_logs,
        columns=[
            'Name',
            'Role',
            'Lecture',
            'Subject',
            'Timestamp'
        ]
    )

    # ================= LOAD REGISTERED STUDENTS =================

    redis_face_db = face_rec.retrive_data(
        name="academy:register"
    )

    logs_df = pd.merge(
        logs_df,
        redis_face_db[['Name','Division','Batch']],
        how='left',
        on='Name'
    )

    # ================= TIME PROCESSING =================

    logs_df['Timestamp'] = logs_df['Timestamp'].apply(
        lambda x: x.split('.')[0]
    )

    logs_df['Timestamp'] = pd.to_datetime(
        logs_df['Timestamp']
    )

    logs_df['Date'] = logs_df['Timestamp'].dt.date

    logs_df['Lecture'] = logs_df['Lecture'].astype(int)

    # ================= GROUP LECTURE ATTENDANCE =================

    report_df = logs_df.groupby(
        ['Date','Name','Division','Batch','Lecture','Subject']
    ).agg(
        In_time=pd.NamedAgg(
            column='Timestamp',
            aggfunc='min'
        ),
        Out_time=pd.NamedAgg(
            column='Timestamp',
            aggfunc='max'
        )
    ).reset_index()

    # ================= DURATION =================

    report_df['Duration'] = (
        report_df['Out_time'] - report_df['In_time']
    )

    report_df['Duration_seconds'] = (
        report_df['Duration'].dt.seconds
    )

    report_df['Duration_minutes'] = (
        report_df['Duration_seconds'] / 60
    )

    # ================= STATUS LOGIC =================

    def lecture_status(x):

        if pd.isnull(x):
            return "Absent"

        elif x < 5:
            return "Absent"

        else:
            return "Present"

    report_df['Status'] = report_df[
        'Duration_minutes'
    ].apply(lecture_status)

    # ================= COMPLETE STUDENT + LECTURE MATRIX =================

    students = redis_face_db[
        ['Name','Division','Batch']
    ].drop_duplicates()

    lectures = [1,2,3,4,5,6]

    all_records = []

    for date in report_df['Date'].unique():

        for _, student in students.iterrows():

            for lec in lectures:

                all_records.append([
                    date,
                    student['Name'],
                    student['Division'],
                    student['Batch'],
                    lec
                ])

    full_df = pd.DataFrame(
        all_records,
        columns=[
            'Date',
            'Name',
            'Division',
            'Batch',
            'Lecture'
        ]
    )

    # ================= MERGE =================

    final_report = pd.merge(
        full_df,
        report_df,
        how='left',
        on=[
            'Date',
            'Name',
            'Division',
            'Batch',
            'Lecture'
        ]
    )

    final_report['Status'] = final_report[
        'Status'
    ].fillna("Absent")

    # ================= DISPLAY =================

    st.subheader("Complete Attendance")

    st.dataframe(final_report)

    # ================= FILTER SYSTEM =================

    st.subheader("Search Records")

    col1,col2,col3 = st.columns(3)

    date_in = col1.date_input(
        "Select Date",
        datetime.datetime.now().date()
    )

    name_list = final_report['Name'].unique().tolist()

    name_in = col2.selectbox(
        "Select Student",
        ['ALL'] + name_list
    )

    division_list = final_report['Division'].unique().tolist()

    division_in = col3.selectbox(
        "Division",
        ['ALL'] + division_list
    )

    if st.button("Filter"):

        df = final_report.copy()

        df = df[df['Date'] == date_in]

        if name_in != "ALL":
            df = df[df['Name'] == name_in]

        if division_in != "ALL":
            df = df[df['Division'] == division_in]

        st.dataframe(df)