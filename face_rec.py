import streamlit as st
import numpy as np
import pandas as pd
import cv2
import redis
import os
import time
from datetime import datetime


# insight face
from insightface.app import FaceAnalysis
from sklearn.metrics import pairwise


# ================= REDIS CONNECTION =================
r = redis.StrictRedis(
    host='redis-12072.c92.us-east-1-3.ec2.cloud.redislabs.com',
    port=12072,
    password='zjefqIKhAZqzAkUCYpJtgas5RYyMEobi'
)


# ================= RETRIEVE DATA =================
def retrive_data(name):

    retrive_dict = r.hgetall(name)

    if len(retrive_dict) == 0:
        return pd.DataFrame(columns=['Name','Role','Division','Batch','facial_features'])

    retrive_series = pd.Series(retrive_dict)

    retrive_series = retrive_series.apply(
        lambda x: np.frombuffer(x, dtype=np.float32)
    )

    index = retrive_series.index
    index = list(map(lambda x: x.decode(), index))

    retrive_series.index = index

    retrive_df = retrive_series.to_frame().reset_index()

    retrive_df.columns = ['name_role','facial_features']

    # ===== MODIFIED =====
    retrive_df[['Name','Role','Division','Batch']] = retrive_df['name_role'].str.split('@', expand=True)
    # ====================

    return retrive_df[['Name','Role','Division','Batch','facial_features']]


# ================= FACE ANALYSIS MODEL =================
faceapp = FaceAnalysis(
    name='buffalo_sc',
    root='insightface_model',
    providers=['CPUExecutionProvider']
)

faceapp.prepare(ctx_id=0, det_size=(640,640), det_thresh=0.5)


# ================= ML SEARCH ALGORITHM =================
def ml_search_algorithm(dataframe, feature_column, test_vector,
                        name_role=['Name','Role'], thresh=0.5):

    dataframe = dataframe.copy()

    # ===== ADD THIS SAFETY CHECK =====
    if len(dataframe) == 0:
        return "Unknown", "Unknown"
    # =================================

    
    X_list = dataframe[feature_column].tolist()
    x = np.asarray(X_list)

    similar = pairwise.cosine_similarity(x, test_vector.reshape(1,-1))
    similar_arr = np.array(similar).flatten()

    dataframe['cosine'] = similar_arr

    data_filter = dataframe.query(f'cosine >= {thresh}')

    if len(data_filter) > 0:

        data_filter.reset_index(drop=True, inplace=True)

        argmax = data_filter['cosine'].argmax()

        person_name, person_role = data_filter.loc[argmax][name_role]

    else:

        person_name = 'Unknown'
        person_role = 'Unknown'

    return person_name, person_role


# ================= REAL TIME PREDICTION =================
class RealTimePred:

    def __init__(self):

        self.logs = dict(name=[], role=[], current_time=[])


    def reset_dict(self):

        self.logs = dict(name=[], role=[], current_time=[])


    def saveLogs_redis(self):

        try:

            dataframe = pd.DataFrame(self.logs)

            if dataframe.empty:
                return

            dataframe.drop_duplicates('name', keep='last', inplace=True)

            name_list = dataframe['name'].tolist()
            role_list = dataframe['role'].tolist()
            ctime_list = dataframe['current_time'].tolist()

            # GET LECTURE + SUBJECT FROM STREAMLIT
            period = st.session_state.get("period", 0)
            subject = st.session_state.get("subject", "Unknown")

            encoded_data = []

            for name, role, ctime in zip(name_list, role_list, ctime_list):

                if name != 'Unknown':

                    concat_string = f"{name}@{role}@{period}@{subject}@{ctime}"

                    encoded_data.append(concat_string)

            if len(encoded_data) > 0:
                r.lpush('attendance:logs', *encoded_data)

            self.reset_dict()

        except Exception as e:

            print(f"Redis save failed: {e}")


    def face_prediction(self, test_image, dataframe, feature_column,
                        name_role=['Name','Role'], thresh=0.5):

        current_time = str(datetime.now())

        results = faceapp.get(test_image)

        test_copy = test_image.copy()

        for res in results:

            x1,y1,x2,y2 = res['bbox'].astype(int)

            embeddings = res['embedding']

            person_name, person_role = ml_search_algorithm(
                dataframe,
                feature_column,
                test_vector=embeddings,
                name_role=name_role,
                thresh=thresh
            )

            color = (0,0,255) if person_name == 'Unknown' else (0,255,0)

            cv2.rectangle(test_copy,(x1,y1),(x2,y2),color,2)

            cv2.putText(test_copy, person_name,(x1,y1-10),
                        cv2.FONT_HERSHEY_DUPLEX,0.7,color,2)

            cv2.putText(test_copy,current_time,(x1,y2+20),
                        cv2.FONT_HERSHEY_DUPLEX,0.5,color,1)

            self.logs['name'].append(person_name)
            self.logs['role'].append(person_role)
            self.logs['current_time'].append(current_time)

        return test_copy


# ================= REGISTRATION FORM =================
class RegistrationForm:

    def __init__(self):

        self.sample = 0


    def reset(self):

        self.sample = 0


    def get_embedding(self, frame):

        results = faceapp.get(frame, max_num=1)

        embeddings = None

        for res in results:

            self.sample += 1

            x1,y1,x2,y2 = res['bbox'].astype(int)

            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),1)

            cv2.putText(frame,f"samples = {self.sample}",
                        (x1,y1),cv2.FONT_HERSHEY_DUPLEX,0.6,(255,255,0),2)

            embeddings = res['embedding']

        return frame, embeddings


    # ===== MODIFIED =====
    def save_data_in_redis_db(self, name, role, division, batch):
    # ====================

        if name is not None:

            if name.strip() != '':

                # ===== MODIFIED =====
                key = f'{name}@{role}@{division}@{batch}'
                # ====================

            else:

                return 'name_false'

        else:

            return 'name_false'


        if 'face_embedding.txt' not in os.listdir():

            return 'file_false'


        x_array = np.loadtxt('face_embedding.txt', dtype=np.float32)

        received_samples = int(x_array.size / 512)

        x_array = x_array.reshape(received_samples,512)

        x_mean = x_array.mean(axis=0).astype(np.float32)

        r.hset(
            name='academy:register',
            key=key,
            value=x_mean.tobytes()
        )

        os.remove('face_embedding.txt')

        self.reset()

        return True