import cv2
import sys
import numpy as np
import time
import serial
import datetime
import os
import shutil

import threading

import __GPS as gps
import __upload_data as upd
import __calWIPS as cwips

from parameter import parameter_submain

(
    height,
    width,
    surface_area_Ytop,
    surface_area_Ybottom,
    surface_area_Xleft,
    surface_area_Xright,
    surface_resize_width,
    surface_resize_height,
    noon_model_start,
    noon_model_end,
    WIPS_area_Ytop,
    WIPS_area_Ybottom,
    WIPS_area_Xleft,
    WIPS_area_Xright,
    carNumber,
    freeWord,
    gps_device_name,
    rate,
    dataNum,
    file_name,
    host,
    webdav_folder,
    rec_interval,
) = parameter_submain()

"""
#---------------------------------------------------------------
from tensorflow.keras.models import load_model
model_path = "./roadSurface_model/__takase_models/noon.h5"
model = load_model(model_path)
#---------------------------------------------------------------
"""
# ---------------------------------------------------------------
# 2021/8/25_add_by_sato
from tensorflow.keras.models import load_model

# ---------------------------------------------------------------
# 昼モデル
model_path_noon = "./roadSurface_model/__takase_models/noon_all_80200.h5"
model_noon = load_model(model_path_noon)
# ---------------------------------------------------------------
# 夜モデル
model_path_night = "./roadSurface_model/__takase_models/night_all_80200.h5"
model_night = load_model(model_path_night)
# ---------------------------------------------------------------


def videoInitialization(cap, videoFileName, fps_set, mode):
    ## 書き込みまでの処理落ちを考慮した数値
    rate = 0.5

    ret, frame = cap.read()
    # Edited by Yagi at 2021.08.30
    # frame = cv2.flip(frame,-1)

    ### Windows+OpenCV以外の環境の場合には解放が必要
    # actualSized_frame = cv2.resize(frame, (width, height))
    # height, width, channels = actualSized_frame.shape
    height, width, channels = frame.shape
    rec = cv2.VideoWriter(
        videoFileName,
        cv2.VideoWriter_fourcc(
            *"mp4v"
        ),  # cv2.VideoWriter_fourcc('H', '2', '6', '4'), \
        (fps_set * rate),
        (width, height),
        True,
    )

    if mode == 1:
        numFrame = 0
        while True:
            ret, frame = cap.read()
            if numFrame >= 2:
                break
            numFrame = numFrame + 1

    return ret, frame, rec


def threading_WIPS_upload(
    numFrame,
    fps_set,
    imageName,
    carNumber,
    imageExtension,
    imageList,
    frame,
    workFlag,
    flag_log,
    imageFileName,
    currentDate,
    currentTime,
    freeWord,
    csv_data,
    velocity,
    csv_data_log0,
    csv_data_log1,
    out_fileName,
    out_fileName_log,
    host,
    webdav_folder,
    outFolder,
    accumFolder,
):
    if numFrame <= fps_set * 1.0:
        if numFrame == 0:
            outImage = imageName + "_1_" + carNumber + imageExtension
            cv2.imwrite(outImage, frame)
            imageList.append(outImage)

        if numFrame == fps_set / 2:
            outImage = imageName + "_2_" + carNumber + imageExtension
            cv2.imwrite(outImage, frame)
            imageList.append(outImage)

        if numFrame == fps_set * 1.0:
            outImage = imageName + "_3_" + carNumber + imageExtension
            cv2.imwrite(outImage, frame)
            imageList.append(outImage)
            workFlag = 1

    if workFlag == 1:
        ## 複数枚に対するWIPS算出とその最小値となる画像の特定
        WIPS, minIndex = cwips.calWIPS(imageList)
        WIPS_imageName = imageFileName + currentDate + "_" + currentTime
        WIPS_imageName = (
            WIPS_imageName + "_" + str(minIndex + 1) + "_" + freeWord + ".jpg"
        )

        print("WIPS: ", WIPS)
        ## WIPSが最小となる画像に対する路面状態判別
        # jpeg画像を読み込む(カラー画像)
        frame = cv2.imread(imageList[minIndex])
        """
        height = 480
        width = 640
        """
        # --- 処理対象の領域を切り出す　-----
        image = frame[
            surface_area_Ytop:surface_area_Ybottom,
            surface_area_Xleft:surface_area_Xright,
        ]
        image = np.array(
            cv2.resize(image, (surface_resize_width, surface_resize_height))
        )

        # 2021/8/25_add_by_sato
        # 昼の定義
        """
        noon_start = 6
        noon_end = 14
        """
        # 2021/10/1_add_by_sato
        # 昼モデル
        if noon_model_start < int(currentTime[0:2]) < noon_model_end:
            result_1_value = model_noon.predict(np.array([(image / 127.5) - 1.0]))

            # Mobile Netsの最終層の値
            print("dry: ", result_1_value[0, 0])
            print("semi-wet: ", result_1_value[0, 1])
            print("wet: ", result_1_value[0, 2])
            print("slush: ", result_1_value[0, 3])
            print("ice: ", result_1_value[0, 4])
            print("fresh: ", result_1_value[0, 5])

            # 第１ラベル
            result_dir_1 = ["dry", "semi-wet", "wet", "slush", "ice", "fresh"]
            result_1_label = np.argmax(result_1_value[0, :])
            result_chr_1 = result_dir_1[result_1_label]
            out_road_1 = "Road surface 1: " + result_chr_1
            print(out_road_1)

            # 第２ラベル
            result_2_value = np.delete(result_1_value, result_1_label)
            result_dir_2 = np.delete(result_dir_1, result_1_label)
            result_2_label = np.argmax(result_2_value)
            result_chr_2 = result_dir_2[result_2_label]
            out_road_2 = "Road surface 2: " + result_chr_2
            print(out_road_2)

        # 夜モデル
        else:
            result_1_value = model_night.predict(np.array([(image / 127.5) - 1.0]))

            # Mobile Netsの最終層の値
            print("dry: ", result_1_value[0, 0])
            print("semi-wet: ", result_1_value[0, 1])
            print("wet: ", result_1_value[0, 2])
            print("slush: ", result_1_value[0, 3])
            print("ice: ", result_1_value[0, 4])
            print("fresh: ", result_1_value[0, 5])

            # 第１ラベル
            result_dir_1 = ["dry", "semi-wet", "wet", "slush", "ice", "fresh"]
            result_1_label = np.argmax(result_1_value[0, :])
            result_chr_1 = result_dir_1[result_1_label]
            out_road_1 = "Road surface 1: " + result_chr_1
            print(out_road_1)

            # 第２ラベル
            result_2_value = np.delete(result_1_value, result_1_label)
            result_dir_2 = np.delete(result_dir_1, result_1_label)
            result_2_label = np.argmax(result_2_value)
            result_chr_2 = result_dir_2[result_2_label]
            out_road_2 = "Road surface 2: " + result_chr_2
            print(out_road_2)

            """
            result = model_night.predict(np.array([(image/127.5)-1.0]))
            result = np.argmax(result[0,:])
            result_dir = ['dry','semi-wet','wet','slush','ice','fresh']
            #0: dry, 1: semi-wet, 2: wet, 3: slush, 4: snow
            result_chr = result_dir[result]
            #result_chr = "test"
            out_road = "Road surface: " + result_chr
            print(out_road)
            """
        # ---------------------------------------------------------------
        """
        #-----------------------------
        result = model.predict(np.array([(image/127.5)-1.0]))
        result = np.argmax(result[0,:])
        result_dir = ['dry','semi-wet','wet','slush','snow']
        #0: dry, 1: semi-wet, 2: wet, 3: slush, 4: snow
        result_chr = result_dir[result]
        #result_chr = "test"
        out_road = "Road surface: " + result_chr
        print(out_road)
        #-----------------------------
        """
        #
        result_chr = result_chr_1

        ## WIPS算出の対象ファイルをuploadする処理 ##
        if os.path.exists(imageList[minIndex]):
            shutil.copy(imageList[minIndex], "./upload_files")

        # add at 2020.09.13 by ST.
        removeList = np.delete(list(range(3)), minIndex)
        if os.path.exists(imageList[removeList[0]]):
            os.remove(imageList[removeList[0]])
        if os.path.exists(imageList[removeList[1]]):
            os.remove(imageList[removeList[1]])

        ##### CSVの書き出し(to uploadFiles)
        # CSVファイルデータの生成
        csv_data = csv_data + str(WIPS) + "," + WIPS_imageName + ","
        csv_data = csv_data + velocity + "," + result_chr + ","
        csv_data = (
            csv_data
            + str(result_1_value[0, 0])
            + ","
            + str(result_1_value[0, 1])
            + ","
            + str(result_1_value[0, 2])
            + ","
            + str(result_1_value[0, 3])
            + ","
            + str(result_1_value[0, 4])
            + ","
            + str(result_1_value[0, 5])
            + ","
        )# Edited by HAYASHI at 2023.7.18
        csv_data = csv_data + freeWord + "[FIN]\n"

        # if((numLoop % 360)==1):
        if flag_log:
            csv_data_log = csv_data_log0 + csv_data_log1
            csv_data_log = csv_data_log + str(WIPS) + "," + WIPS_imageName + ","
            csv_data_log = (
                csv_data_log + velocity + "," + result_chr + ","
            )  # Edited by HAYASHI at 2023.6.28
            csv_data_log = (
                csv_data_log
                + str(result_1_value[0, 0])
                + ","
                + str(result_1_value[0, 1])
                + ","
                + str(result_1_value[0, 2])
                + ","
                + str(result_1_value[0, 3])
                + ","
                + str(result_1_value[0, 4])
                + ","
                + str(result_1_value[0, 5])
                + ","
                + freeWord
                + "[FIN]\n"
            )
        else:
            csv_data_log = csv_data_log1
            csv_data_log = csv_data_log + str(WIPS) + "," + WIPS_imageName + ","
            csv_data_log = (
                csv_data_log + velocity + "," + result_chr + ","
            )  # Edited by HAYASHI at 2023.6.28
            csv_data_log = (
                csv_data_log
                + str(result_1_value[0, 0])
                + ","
                + str(result_1_value[0, 1])
                + ","
                + str(result_1_value[0, 2])
                + ","
                + str(result_1_value[0, 3])
                + ","
                + str(result_1_value[0, 4])
                + ","
                + str(result_1_value[0, 5])
                + ","
                + freeWord
                + "[FIN]\n"
            )

        # CSVファイルデータの出力
        with open(out_fileName, "w") as csvFile:
            csvFile.write(csv_data)  # プログラム完成時にはここのコメントアウトを外す！！！！
            csvFile.close()
        with open(out_fileName_log, "a") as csvFile_log:
            csvFile_log.write(csv_data_log)  # プログラム完成時にはここのコメントアウトを外す！！！！
            csvFile_log.close()

        print("Progressing upload function.")

        ###### uploadの処理
        if csvFile.closed:
            upd.upload_data(host, webdav_folder, outFolder, accumFolder)
        else:
            csvFile.close()
            upd.upload_data(host, webdav_folder, outFolder, accumFolder)

        print("Finished upload function.")


def subMain_outVideoImageWIPS(
    date,
    out_fileName_log,
    dir,
    numLoop,
    cap,
    videoFileName,
    imageFileName,
    imageExtension,
    fps_set,
    interval,
    tmpFolder,
    outFolder,
    accumFolder,
):
    #### 変数定義 ####
    ##### GPS関係のパラメータ設定（ここから） ####
    """
    carNumber = 'bus_D'
    freeWord = carNumber
    gps_device_name = "Prolific USB-to-Serial Comm Port"
    rate = 4800
    dataNum = 250
    """
    ##### GPS関係のパラメータ設定（ここまで） ####

    ##### CSV関係のパラメータ設定（ここから） ####
    today = datetime.date.today()
    date_forFile = today.strftime("%Y%m%d")
    # file_name = './upload_files/' + 'GPS_GPRMC'+ '_' + date_forFile + '_'
    """
    file_name = './upload_files/' + 'GPS_GPRMC'+ '_'
    ##### CSV関係のパラメータ設定（ここまで） ####
    
    ##### ファイルアップロード関係のパラメータ設定（ここから） ####
    host = 'stakahashi.ddns.net'
    #host = 'hokoudai.ddns.net'
    webdav_folder = '/webdav2021LAMTp8st/soyaBUS/'
    ##### ファイルアップロード関係のパラメータ設定（ここまで） ####
    """

    ##### GPSの初期化 ####
    # comport_name = gps.comport_search(gps_device_name)  # for Windows System
    ##comport = serial.Serial('COM3', baudrate=4800, parity=serial.PARITY_NONE)
    ##comport = serial.Serial(comport_name, rate)  #GPSは__GPS.pyで実施
    ##### GPSの初期化（ここまで） ####

    #### 10秒の計測開始
    print()
    print("-------  start  --------")
    start_time = time.time()

    ##### GPSの取得
    # csv_data, velocity = gps.getGPS(comport_name, dataNum, rate)  ## for Windows
    csv_data, velocity = gps.getGPS("/dev/ttyUSB0", dataNum, rate)
    # 出力ファイル名作成用のデータ整形
    csv_data_tmp = csv_data.replace("\n", ",")
    csv_data_tmp = csv_data_tmp.split(",")
    # print(csv_data_tmp)
    currentTime = "{:0=6}".format(int(csv_data_tmp[19]))
    currentDate = "{:0=6}".format(int(csv_data_tmp[26]))

    if (
        currentDate[0] == "0"
        or currentDate[0] == "1"
        or currentDate[0] == "2"
        or currentDate[0] == "3"
    ):
        currentDate = currentDate
    else:
        currentDate = date
        print("Date was corrected.")
    if currentDate[2] == "0" or currentDate[2] == "1":
        currentDate = currentDate
    else:
        currentDate = date
        print("Date was corrected.")
    if currentDate[4] != "2":
        currentDate = date
        print("Date was corrected.")

    csv_data_tmp = csv_data.split("\n")
    csv_data = csv_data_tmp[0] + "\n" + csv_data_tmp[1]
    csv_data_log0 = csv_data_tmp[0] + "\n"
    csv_data_log1 = csv_data_tmp[1]

    # 出力先の作成
    if (numLoop % 360) == 1:
        dir = tmpFolder + currentDate + "_" + currentTime + "/"
        if not os.path.exists(dir):
            os.mkdir(dir)
    # 出力ファイル名の設定
    videoFileName = dir + videoFileName + currentDate + "_" + currentTime + ".mp4"
    imageName = dir + imageFileName + currentDate + "_" + currentTime

    # CSV:出力ファイル名の設定
    out_fileName = (
        file_name + currentDate + "_" + currentTime + "_" + carNumber + ".csv"
    )
    flag_log = False
    if (numLoop % 60) == 1:  # Log files are newly created at each 10 min.
        print("Log CSV file name was created.")
        out_fileName_log = (
            dir + currentDate + "_" + currentTime + "_" + carNumber + "_log" + ".csv"
        )
        flag_log = True
    if out_fileName_log is None:
        print("Log CSV file name was created.")
        out_fileName_log = (
            dir + currentDate + "_" + currentTime + "_" + carNumber + "_log" + ".csv"
        )
        flag_log = True

    ############## 主処理
    numFrame = 0
    imageList = []

    # 初回はカメラ安定のため
    if numLoop == 1:
        ret, frame, rec = videoInitialization(cap, videoFileName, fps_set, numLoop)
        rec.release()
    # こちらが本番
    ret, frame, rec = videoInitialization(cap, videoFileName, fps_set, numLoop)

    while True:
        workFlag = 0

        frame_copy = frame.copy()
        # frame_copy2 = frame.copy()
        ## 分析領域を画像へ重畳表示(緑：路面判定、赤：WIPS) Edited by Sato at 2021.08.25 ##
        cv2.rectangle(
            frame_copy,
            (surface_area_Xright, surface_area_Ytop),
            (surface_area_Xleft, surface_area_Ybottom),
            (0, 255, 0),
            4,
        )
        cv2.rectangle(
            frame_copy,
            (WIPS_area_Xleft, WIPS_area_Ytop),
            (WIPS_area_Xright, WIPS_area_Ybottom),
            (0, 0, 255),
            4,
        )
        # frame_display = cv2.hconcat([frame, frame_copy, frame_copy2])

        cv2.imshow("Video", frame_copy)
        # cv2.imwrite('save_0827/'+str(numLoop)+".jpg", frame)
        rec.write(frame)
        """
        rec_end_time = time.time()
        rec_time = rec_end_time - start_time
        
        if (rec_time <= rec_interval):
            rec.write(frame)
        """

        ##### 静止画の取得およびWIPS計算（最小のWIPSの画像が決まり次第送信）
        thread_1 = threading.Thread(
            target=threading_WIPS_upload,
            args=(
                numFrame,
                fps_set,
                imageName,
                carNumber,
                imageExtension,
                imageList,
                frame,
                workFlag,
                flag_log,
                imageFileName,
                currentDate,
                currentTime,
                freeWord,
                csv_data,
                velocity,
                csv_data_log0,
                csv_data_log1,
                out_fileName,
                out_fileName_log,
                host,
                webdav_folder,
                outFolder,
                accumFolder,
            ),
        )
        thread_1.start()

        numFrame = numFrame + 1
        # ビデオ出力の続き
        key = cv2.waitKey(1)
        ret, frame = cap.read()

        # Edited by Yagi at 2021.08.30
        # frame = cv2.flip(frame,-1)

        ##### システムインターバル用の計算
        end_time = time.time()
        elapsed_time = end_time - start_time

        if elapsed_time >= interval:
            mes = "Proceed : " + currentTime
            print(mes)
            """
            print(elapsed_time)
            """
            break

    return currentDate, out_fileName_log, dir, rec