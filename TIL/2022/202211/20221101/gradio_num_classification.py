
'''
2022. 10. 31 안문주 작성
            mnist 데이터를 이용한 숫자 이미지 분류 데모
'''

import os
import gradio as gr
from loguru import logger
import tensorflow_addons as tfa
import numpy as np
import skimage.io
import cv2

import tensorflow as tf
import tensorflow.keras as tfk
tfkm = tfk.models
tfkp = tfk.preprocessing


os.environ["CUDA_VISIBLE_DEVICES"]= "-1"

model = tfkm.load_model('./cnn_model')


# ---------- Settings ----------
SERVER_PORT = 8125
SERVER_NAME = "0.0.0.0"



# ---------- Logging ----------
logger.add('app.log', mode='a')
logger.info('===== App restarted =====')



def select(img):

    logger.info('CNN model로 예측 시작')
    image = cv2.resize(img, dsize=(28, 28)).reshape(1, 28, 28, 1)
    prob = model.predict(image)[0]
    pred_dict = {}
    for i, p in zip(range(10), prob):
        pred_dict[f'{i}'] = float(p)
    logger.info('CNN model 예측 종료')

    return pred_dict



iface = gr.Interface(
    select,
    title='숫자 이미지 분류 (0~9)',
    description='이미지 파일을 첨부하면 어떤 숫자인지 예측해주는 분류 모델',
    inputs="sketchpad",
    outputs=gr.Label(num_top_classes=3),
    article='Last updated: 2022-10-31',
)

if __name__ == '__main__':
    iface.launch(debug=True,
                 server_name=SERVER_NAME,
                 server_port=SERVER_PORT,
                 enable_queue=False)
