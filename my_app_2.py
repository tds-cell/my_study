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
            (
                int(ratio * pil_image.width),
                int(ratio * pil_image.height)
            )
        )
        
    def get_image(self):

        if self.image is not None:
            self.image_tk = ImageTk.PhotoImage((self.image))
        return self.image_tk

    #fpsレートを取得
    def get_fps(self):

        if self.video is None:
            return None
        return self.video.get(cv2.CAP_PROP_FPS)

    #現在のフレーム位置を取得    
    def get_frames(self):

        if self.video is None:
            return None
        return self.video.get(cv2.CAP_PROP_POS_FRAMES)

    #現在のフレーム位置をビデオオブジェクトにセット
    def set_frames(self, num):
        
        if self.video is None:
            return None
        return self.video.set(cv2.CAP_PROP_POS_FRAMES, num)

    #オブジェクトの総フレームを取得
    def get_frame_count(self):

        if self.video is None:
            return None
        return self.video.get(cv2.CAP_PROP_FRAME_COUNT)

class View(object):
    def __init__(self, app, model):
        self.master = app
        self.model = model

        #現在のスライダー位置を保存
        #スケールバーの変数には
        #ウィジット変数を使用しないとダメ
        self.slide_num = tk.DoubleVar()
        
        self.create_widgets()

    def create_widgets(self):
        print(self.model.get_frame_count())
       #メインフレームへの実装
        #動画表示枠
        self.movie_frame = tk.Frame(
            self.master, padx=10, pady=10
            , relief=tk.SUNKEN, bd=2, width=10)
        self.movie_frame.grid(row=0, column=0, rowspan=3
        )
        #動画表示枠
        # 動画表示部
        self.canvas = tk.Canvas(
            self.movie_frame
            ,width=600, height=600
            )
        self.canvas.pack()

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
    
    def draw_image(self):

        image = self.model.get_image()

        if image is not None:
            sx = (self.canvas.winfo_width() - image.width()) // 2
            sy = (self.canvas.winfo_height() - image.height()) // 2

            objs = self.canvas.find_withtag("image")
            for obj in objs:
                self.canvas.delete(obj)

            self.canvas.create_image(
                sx, sy,
                image=image,
                anchor=tk.NW,
                tag="image"
            )
            self.slide_num.set(self.model.get_frames())
 
    def select_open_file(self, file_types):
        Dir = os.path.abspath(
            os.path.dirname(__file__)
            ) 

        file_path = tk.filedialog.askopenfilename(
            initialdir=Dir,
            filetypes=file_types
        )
        return file_path

class Controller(object):
    def __init__(self, app, model, view):
        self.master = app
        self.model = model
        self.view = view

        #再生中はTrue, 停止中はFalse
        self.playing = False

        self.frame_timer = 0

        self.draw_timer = 50

        self.set_events()
        
    def set_events(self):
        self.view.load_button['command'] = self.push_load_button
        self.view.play_button['command'] = self.play_button
        self.view.stop_button['command'] = self.stop_button
        self.view.play_1_frame_button['command'] = self.play_1_frame
        self.view.back_1_frame_button['command'] = self.back_1_frame
       
    def draw(self):

        self.master.after(self.draw_timer, self.draw)

        if self.playing:
            self.model.create_image(
                (
                    self.view.canvas.winfo_width(),
                    self.view.canvas.winfo_height()
                )
            )
        self.view.draw_image()
    
    def frame(self):

        self.master.after(self.frame_timer, self.frame)

        if self.playing:
            ret = self.model.advance_frame()

            if not ret:
                self.model.back_to_video_head()
                self.model.advance_frame()

    #動画読み込み用関数
    def push_load_button(self):

        file_types = [
            ("MOV file", "*.mov"),
            ("MP4 file", "*.mp4")
        ]
        file_path = self.view.select_open_file(file_types)
        
        #ファイルパスがあれば以下を実行する
        if len(file_path) != 0:
            #動画オブジェクト作成
            self.model.create_video(file_path)
            #動画フレームの読み込み
            self.model.advance_frame()
            #画像の変換とサイズ調整
            self.model.create_image(
                (
                    self.view.canvas.winfo_width(),
                    self.view.canvas.winfo_height()
                )
            )
            #先頭のフレームを読み込む
            self.model.back_to_video_head()
            #画像の描画を行う
            self.view.draw_image()

            #動画を読み込んでから
            #スケールバーを実装する
            self.scale_bar = tk.Scale(
                self.view.movie_frame
                ,orient="h"
                ,from_=0
                ,to=self.model.get_frame_count()
                ,variable=self.view.slide_num
                ,command=self.slide_movie
            )
            self.scale_bar.pack(fill=tk.X, anchor=tk.SW)

            fps = self.model.get_fps()
            self.frame_timer = int(1 / fps * 1000 + 0.5)

            self.master.after(self.frame_timer, self.frame)

            self.master.after(self.draw_timer, self.draw)

    #動画再生用関数
    def play_button(self):

        if not self.playing:
            self.playing = True

    #動画停止用関数    
    def stop_button(self):

        if self.playing:
            self.playing = False

    #１コマ送り用関数
    def play_1_frame(self):
        
        if self.playing:
            self.playing = False
        
        #フレームを１つ進める
        self.model.advance_frame()

        if self.model.get_frames() == self.model.get_frame_count():
            return self.model.back_to_video_head()

        #イメージを呼び出す
        if self.playing is False:
            self.model.create_image(
                (
                    self.view.canvas.winfo_width(),
                    self.view.canvas.winfo_height()
                )
            )
        #描画を行う
        self.view.draw_image()

    #１コマ戻り用関数
    def back_1_frame(self):

        if self.playing:
            self.playing = False
        if self.model.get_frames() == 0:
            return
        elif self.model.get_frames() == 1:
            return self.model.back_to_video_head()

        #現在のフレームを2個戻す   
        back_num = int(self.model.get_frames()- 2.0)
        self.model.set_frames(back_num)
        #フレームを１つ進める
        self.model.advance_frame()

        #イメージを呼び出す
        if self.playing is False:
            self.model.create_image(
                (
                    self.view.canvas.winfo_width(),
                    self.view.canvas.winfo_height()
                )
            )
        #描画を行う
        self.view.draw_image()

    def slide_movie(self, num):
        self.model.set_frames(float(num))

        self.view.slide_num.set(num)

        self.model.advance_frame()
        #イメージを呼び出す
        if self.playing is False:
            self.model.create_image(
                (
                    self.view.canvas.winfo_width(),
                    self.view.canvas.winfo_height()
                )
            )
        #描画を行う
        self.view.draw_image()


#メインフレームの作成
main_frame = tk.Tk()
#メインフレームのタイトル
main_frame.title('Test')
model = Model()
view = View(main_frame, model)
controller = Controller(main_frame, model, view)

main_frame.mainloop()
 
