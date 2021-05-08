#2021.05.05
#新しくコードを書き換える。大幅に。

#2021.05.09
#このままだとうまく行かないので
#１から作り直す
import tkinter as tk
import cv2
import numpy as np
import os, sys , os.path
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox

#動画を扱う
#データの処理(取得、作成、更新、削除)
#CRUD処理(生成、読み込み、更新、削除)
"""
今はデータベースとのやりとりがないので
Modelクラスはからのままでいいのでは？？
"""
class Model():
    def __init__(self):
        pass
            
#アプリの表示を担う
#アプリ内にウィジェットを作成・配置する
class View(object):
    def __init__(self, app, model):
        #メインフレーム
        self.main_frame = app
        self.model = model
        #画像の幅と高さを規定しておく。
        #大きくなった時にリサイズするため
        self.img_width_max = 600
        self.img_height_max = 600

        #アプリ内のウィジットを作成
        self.create_widgets()

    def create_widgets(self):
        #メインフレームへの実装
        #動画表示枠
        self.movie_frame = tk.Frame(
            self.main_frame, padx=10, pady=10
            , relief=tk.SUNKEN, bd=2, width=10)
        self.movie_frame.grid(row=0, column=0, rowspan=3
        )
        #動画表示枠
        # 動画表示部
        self.canvas_video = tk.Canvas(
            self.movie_frame
            ,width=self.img_width_max, height=self.img_height_max
            )
        self.canvas_video.pack()
        #動画表示枠
        # スケールバー
        """
        ここにslide_numがあるせいでうまく行かない
        これならMVCで作らないほうがいいのか？
        無理やりmodelにmain_frameを入れてもいいが
        それだと目的と手段がごっちゃになっている
        つまり最初のままでよかったのでは？
        となってしまう
        """
        self.scale_bar = tk.Scale(
            self.movie_frame
            ,orient="h"
            ,from_=self.model.first_frame, to=self.model.frame_count
            ,variable=self.model.slide_num
            ,command=self.model.slide_movie(self.model.slide_num)
            )
        self.scale_bar.pack(fill=tk.X, anchor=tk.SW)

        #メインフレームへの実装
        # ボタン配置枠
        self.button_frame = tk.Frame(
            self.main_frame, padx=10, pady=10
            ,relief=tk.SUNKEN, bd=2, width=100
            )
        self.button_frame.grid(row=1, column=1)
        #ボタン配置枠
        # 動画のパス表示テキストボックス
        self.text_box = tk.Entry(
            self.button_frame, textvariable=self.model.file_name, width=30
            )
        self.text_box.pack()
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
        pass

#イベント処理
#viewの入力を受取りそれに対する処理をする場所
#この処理を元にデータが動く
#動いたデータはviewで表示される
class Control(object):
    def __init__(self, app, model, view):
        self.main_frame = app
        self.model = model
        self.view = view
        #読み込むファイルの種類はデフォルトで全てにしておく
        self.fTyp = [("", "*")]
        #エラー対策。拡張子の初期化
        self.ext = None
        #動画を更新する時間
        self.delay = 5
        #動画ファイルを停止するフラグ変数
        #0=再生、1=停止
        self.flag = 0
        #描画された画像のフレーム番号
        self.img_num = 0
        #スライダー変数の初期化
        #動画の最初のフレームと総フレーム数を保存するインスタンス
        self.first_frame = tk.DoubleVar(value=1.0)
        self.frame_count = tk.DoubleVar(value=1.0)
        #スライダーの位置変数
        self.slide_num = tk.DoubleVar(value=1.0)

        self.set_events()

    def set_events(self):
        #動画ロード実行
        self.view.load_button.configure(command=self.load_movie_file)
        #再生実行
        self.view.play_button.configure(command=self.play_func)
        #停止実行
        self.view.stop_button.configure(command=self.stop_func)
        #１コマ送り実行
        self.view.play_1_frame_button.configure(command=self.play_1_frame_func)
        #１コマ戻り実行
        self.view.back_1_frame_button.configure(command=self.back_1_frame_func)

    #動画load実行関数
    def load_movie_file(self):
        #動画を新たに読み込む場合リセットが必要
        if self.ext != None:
            self.scale_bar.pack_forget()
            self.slide_num.set(1.0)
            self.img_num = 0

        self.iDir = os.path.abspath(
            os.path.dirname(__file__))        
        #これで今作業中のディレクトリ(=self.iDir)からのフォルダーダイアログを表示する
        #さらにfiletypeを全てにしておく
        self.filePath = filedialog.askopenfilename(
            filetypes=self.fTyp, initialdir=self.iDir
            )

        #拡張子を取得
        _, self.ext = os.path.splitext(self.filePath)
        
        if self.ext == ".MOV" or ".mp4":
            #setメソッドでテキストボックスに選択したファイルのパスを入れる
            self.file_name.set(self.filePath)
            self.cap = cv2.VideoCapture(self.filePath)
            #読み込んだ動画の最初の画像でサムネイルを表示
            self.cv2ImageTk()
            self.canvas_video.create_image( 
                0, 0, image=self.img, anchor='nw'
            )
            
            #読み込んだ動画の総フレーム数をカウント
            self.frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            self.first_frame = self.frame_count / self.frame_count
            self.scale_bar_button()

        #キャンセル処理の時のエラー対策
        elif self.filePath == "":
            return 
        #動画ファイルじゃない時のエラー対策
        else :
            messagebox.showwarning(
                "waring",
                "filetype is not [.mov]"
            )
            self.ext = None
  
   #cv2で読み込んだ画像をImageTkに変換
    def cv2ImageTk(self):
        ret, img = self.cap.read()
        if not ret:
            return
        else:
            self.img_num = self.img_num + 1     
        img_resize = cv2.resize(img, (337, 600))
        img_BGR2RGB_m = cv2.cvtColor(img_resize, cv2.COLOR_BGR2RGB)
        img_PIL_m = Image.fromarray(img_BGR2RGB_m)
        self.img = ImageTk.PhotoImage(img_PIL_m)       

    #動画再生用関数
    def play_func(self):
        self.error_no_load()

        if self.ext is None:
            self.play_button["state"] = tk.NORMAL
            return
        self.play_button["state"] = tk.DISABLED
        self.stop_button["state"] = tk.NORMAL
        self.cv2ImageTk()

        #動画を描画する事は出来ないので画像にして1つずつ出力
        if self.flag == 0:
            self.canvas_video.create_image( 
                0, 0, image=self.img, anchor='nw'
            )
            self.canvas_video.after(self.delay, self.play_func)
            self.slide_num.set(self.img_num)
        elif self.flag == 1:
            self.play_button["state"] = tk.NORMAL
            self.stop_button["state"] = tk.DISABLED
            self.canvas_video.create_image( 
                0, 0, image=self.img, anchor='nw'
            )
            self.flag = 0
            self.slide_num.set(self.img_num)
        
        self.flag = 0
  
    #停止ボタン。クリック時、実行
    def stop_func(self):
        self.error_no_load()
        self.flag = 1
    
   #動画１コマ送り用関数
    def play_1_frame_func(self):
        self.error_no_load()
        self.flag = 1
        self.cv2ImageTk()
        self.canvas_video.create_image( 
            0, 0, image=self.img, anchor='nw'
        )
        self.flag = 0
        self.slide_num.set(self.img_num)

   #動画１コマ戻し用関数
    def back_1_frame_func(self):
        self.flag = 1
        self.error_no_load()
        self.img_num = self.img_num - 2
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.img_num)
        self.cv2ImageTk()
        self.canvas_video.create_image( 
            0, 0, image=self.img, anchor='nw'
        )        
        self.flag = 0
        self.slide_num.set(self.img_num)

   #動画スライド用関数
    #valueはスライダーが動くと変化する
    def slide_movie(self, value):
        self.img_num = int(value)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.img_num)
        _, img = self.cap.read()
        img_resize = cv2.resize(img, (337, 600))
        img_BGR2RGB_m = cv2.cvtColor(img_resize, cv2.COLOR_BGR2RGB)
        img_PIL_m = Image.fromarray(img_BGR2RGB_m)
        self.img = ImageTk.PhotoImage(img_PIL_m)
        self.canvas_video.create_image( 
            0, 0, image=self.img, anchor='nw'
        )

    #ロード実行時のエラー対応
    def error_no_load(self):
        if self.ext == None:
            messagebox.showwarning(
                "waring",
                "Load file"
            )
            return
 

#########################################
#ここから実行
##########################################

#メインフレームの作成
main_frame = tk.Tk()
#メインフレームのタイトル
main_frame.title('Test')
model = Model()
view = View(main_frame, model)
control = Control(main_frame, model, view)

main_frame.mainloop() 
