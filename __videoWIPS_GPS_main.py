import cv2
import sys
import numpy as np
import time
import serial
import datetime  
import os
import shutil
import datetime

import __subMain_outVideoImageWIPS as submain

from parameter import parameter_main
testLoop, interval, tmpFolder, outFolder, accumFolder, videoFileName, imageFileName, imageExtension, camera_index, fps_set, width_set = parameter_main()


"""
##### システム全体の基本設定 ####
testLoop = -1    #テスト用の変数で繰り返し回数を示している．本番時には-1にして無限大にする．
interval = 10 #10秒毎
tmpFolder = './tmp_files/'
outFolder = './upload_files/'
accumFolder = './accum_files/'
if not os.path.exists(tmpFolder):
    os.mkdir(tmpFolder)
if not os.path.exists(outFolder):
    os.mkdir(outFolder)
if not os.path.exists(accumFolder):
    os.mkdir(accumFolder)

##### ビデオ関係のパラメータ設定（ここから） ####
videoFileName = 'video_'
## 画像
imageFileName = 'image_'
## 画像拡張子
imageExtension = '.jpg'
##### ビデオ関係のパラメータ設定（ここまで） ####

##### カメラ関係のパラメータ設定（ここから） ####
camera_index = 0 #高橋のVAIOの場合，0と1が先にあるので2になる．
fps_set = 30
width_set = 640
"""

if not os.path.exists(tmpFolder):
    os.mkdir(tmpFolder)
if not os.path.exists(outFolder):
    os.mkdir(outFolder)
if not os.path.exists(accumFolder):
    os.mkdir(accumFolder)

##### カメラの初期化 ####
def decode_fourcc(v):
  v = int(v)
  return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])

try:
    print("Start camera initialization. Please wait around 3 sec.")
    # Add at 2020.12.31
    # 暗くなることへの対応
    time.sleep(2)

    cap = cv2.VideoCapture(camera_index)  #カメラ番号に注意！！
    
    # Add at 2020.12.31
    # 暗くなることへの対応
    time.sleep(1)
    
except:
    #print("\e[2J")
    # Added by Yagi at 2021.08.31
    sys.exit()

# cameraが開けていることの確認
if (cap.isOpened() != True):
    os.system('clear')
    print("")
    print("Waiting for Camera Initialization.")
    print("")
    ### 後処理 ###
    cap.release()
    print("")
    print("CAP released.")
    print("")    
    ###
    # Added by Yagi at 2021.08.31
    sys.exit()
else:
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'mp4v'))
    cap.set(cv2.CAP_PROP_FPS, fps_set)           # カメラFPSを30FPSに設定
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width_set) # カメラ画像の横幅を1280に設定

    # Add at 2020.2.15
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0) # turn the autofocus off
    
    # Add at 2020.12.31
    ##cap.set(cv2.CAP_PROP_AUTO_WB, 0) # turn the whitebalance off    
    ##cap.set(cv2.CAP_PROP_XI_AUTO_WB, 0) # turn the whitebalance off
    #cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)
    #cap.set(cv2.CAP_PROP_CONTRAST, 0.5)
    #cap.set(cv2.CAP_PROP_GAIN, 0.3)
    
    # Add at 2021.1.8
    cap.set(cv2.CAP_PROP_FOCUS, 0)
    
    print("Camera parameters: ")
    print("\t FOURCC: " + decode_fourcc(cap.get(cv2.CAP_PROP_FOURCC)))
    print("\t FPS: " + str(cap.get(cv2.CAP_PROP_FPS)))
    print("\t FRAME_WIDTH: " + str(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
    if cap.get(cv2.CAP_PROP_AUTOFOCUS) == 0:
        print("\t AUTOFOCUS: OFF")
    else:
        print("\t AUTOFOCUS: ON")
    print("\t BRIGHTNESS: " + str(cap.get(cv2.CAP_PROP_BRIGHTNESS)))
    print("\t CONTRAST: " + str(cap.get(cv2.CAP_PROP_CONTRAST)))
    print("\t GAIN: " + str(cap.get(cv2.CAP_PROP_GAIN)))
    print("\t FOCUS: " + str(cap.get(cv2.CAP_PROP_FOCUS)))

##### ビデオ関係の初期化(ここまで) ####

print("Initialization was finished!! Let's start WIPS calc. and accum.")


##### 残存しているuploadフォルダのファイルを全部upする #####
#print("Start uploading the previous files.")
#upd.upload_data(host, webdav_folder, outFolder, accumFolder)
#print("Upload finished!!")
##############################################

numLoop = 0
dirName = ""
logFile = ""
### システムの中核 ###
while cap.isOpened():
#while False:
    numLoop = numLoop + 1
    dt= datetime.date.today()
    date = dt.strftime('%d%m%y')
    
    ###### ビデオキャプチャーの開始
    ### GPSの取得，静止画の取得，WIPSの計算
    tmp_date, logFile, dirName, rec = submain.subMain_outVideoImageWIPS(date, logFile, dirName, numLoop, cap, videoFileName, imageFileName, imageExtension, fps_set, interval, tmpFolder, outFolder, accumFolder)
    date = tmp_date
    
    ###### ビデオキャプチャーの終了
    cv2.destroyAllWindows()
    rec.release()
    
    ## 繰り返し回数の確認
    mes = "numLoop: " + str(numLoop)
    print(mes)
    print("------ END -----")
    print()
    
    ### 開発テスト用
    if (testLoop > 0):
        testLoop = testLoop - 1
        if (testLoop == 0):
            break

### システムの中核(ここまで) ###



### 後処理 ###
#comport.close()  #GPSは__GPS.pyで実施
cap.release()
###
