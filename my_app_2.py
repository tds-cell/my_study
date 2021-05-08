import tkinter as tk
import cv2
import numpy as np
import os, sys , os.path
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox

class Model(object):
    def __init__(self):
        #動画オブジェクト参照用
        #これは動画ファイルそのモノ
        self.video = None
        #読み込んだフレーム 
        #これは動画の1フレームのこと
        self.frames = None

    #動画作成関数    
    #動画のパスを引数して動画オブジェクトを作成している
    def create_video(self, path):
        self.video = cv2.VideoCapture(path)

   # 
    def advance_frame(self):

        if not self.video:
            return
        ret, self.frame = self.video.read() 

        return ret
    #動画を先頭に戻す。
    # こんなのいつ使う？ 
    def back_to_video_head(self):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def create_image(self, size):

        #フレームを読み込む
        frame = self.frame
        if frame is None:
            print("None")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)

        ratio_x = size[0] / pil_image.width
        ratio_y = size[1] / pil_image.height

        if ratio_x < ratio_y:
            ratio = ratio_x
        else:
            ratio = ratio_y
            
        #リサイズ
        self.image = pil_image.resize(
            int(ratio * pil_image.width),
            int(ratio * pil_image.height)
        )
        
    def get_image(self):

        if self.image is not None:
            self.image_tk = ImageTk.PhotoImage((self.image))
        return self.image_tk

    def get_fps(self):

        if self.video is None:
            return None

        return self.video.get(cv2.CAP_PROP_FPS)

class View(object):
    def __init__(self, app, model):
        self.master = app
        self.model = model

        self.create_widgets()

    def create_widgets(self):
       #メインフレームへの実装
        #動画表示枠
        self.movie_frame = tk.Frame(
            self.master, padx=10, pady=10
            , relief=tk.SUNKEN, bd=2, width=10)
        self.movie_frame.grid(row=0, column=0, rowspan=3
        )
        #動画表示枠
        # 動画表示部
        self.canvas_video = tk.Canvas(
            self.movie_frame
            ,width=600, height=600
            )
        self.canvas_video.pack()

        #あとでスケールバーは実装する

        #メインフレームへの実装
        # ボタン配置枠
        self.button_frame = tk.Frame(
            self.master, padx=10, pady=10
            ,relief=tk.SUNKEN, bd=2, width=100
            )
        self.button_frame.grid(row=1, column=1)
        #ボタン配置枠
        # 動画のロード
        self.load_button = tk.Button(self.button_frame, text=u'load', width=10)
        self.load_button.pack()
        #ボタン配置枠
        # 再生ボタン
        self.play_button = tk.Button(self.button_frame, text=u'▶', width=10)
        self.play_button.pack()   
        #ボタン配置枠
        # 停止ボタン
        self.stop_button = tk.Button(self.button_frame, text=u'■', width=10)
        self.stop_button.pack()
        #ボタン配置枠
        # １コマ送りボタン
        self.play_1_frame_button = tk.Button(self.button_frame, text=u'>>', width=10)
        self.play_1_frame_button.pack()
        #ボタン配置枠
        # １コマ戻りボタン
        self.back_1_frame_button = tk.Button(self.button_frame, text=u'<<', width=10)
        self.back_1_frame_button.pack()
 
#メインフレームの作成
main_frame = tk.Tk()
#メインフレームのタイトル
main_frame.title('Test')
model = Model()
view = View(main_frame, model)

main_frame.mainloop()
 
