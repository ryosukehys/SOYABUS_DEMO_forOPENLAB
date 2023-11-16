def parameter_main():

    ##### システム全体の基本設定 ####
    testLoop = -1    #テスト用の変数で繰り返し回数を示している．本番時には-1にして無限大にする．
    interval = 7 #7秒毎
    tmpFolder = './tmp_files/'
    outFolder = './upload_files/'
    accumFolder = './accum_files/'

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

    return testLoop, interval, tmpFolder, outFolder, accumFolder, videoFileName, imageFileName, imageExtension, camera_index, fps_set, width_set

def parameter_submain():
    ## WIPSが最小となる画像に対する路面状態判別
    #jpeg画像を読み込む(カラー画像)

    height = 480
    width = 640
    #--- 処理対象の領域を切り出す　-----
    surface_area_Ytop = 360 #260 # Edited by Sato at 2022.12.01
    surface_area_Ybottom = 480#460 # Edited by Sato at 2022.12.01
    surface_area_Xleft = 180#70
    surface_area_Xright = 480#570
    #image=frame[280:400, 170:470]
    surface_resize_width = 200
    surface_resize_height = 80
    #image = np.array(cv2.resize(image, (200, 80)))

    #2021/8/25_add_by_sato
    #路面判定の機械学習モデルを昼/夜で切り替える時間を定義
    noon_model_start = 6
    noon_model_end = 18

    #2021/12/1_add_by_sato
    #WIPS算出
    WIPS_area_Ytop = 72 # Edited by Sato at 2022.12.01
    WIPS_area_Ybottom = 328 # Edited by Sato at 2021.12.01
    WIPS_area_Xleft = 192
    WIPS_area_Xright = 448
    #### 変数定義 ####
    ##### GPS関係のパラメータ設定（ここから） ####
    #carNumber = 'car_99'
    carNumber = 'bus_H'# Edited by Yagi at 2021.08.30
    freeWord = carNumber
    gps_device_name = "Prolific USB-to-Serial Comm Port"
    rate = 4800
    dataNum = 250
    ##### GPS関係のパラメータ設定（ここまで） ####

    ##### CSV関係のパラメータ設定（ここから） ####
    """
    today = datetime.date.today()
    date_forFile = today.strftime('%Y%m%d')
    """
    #file_name = './upload_files/' + 'GPS_GPRMC'+ '_' + date_forFile + '_'
    file_name = './upload_files/' + 'GPS_GPRMC'+ '_'
    ##### CSV関係のパラメータ設定（ここまで） ####

    ##### ファイルアップロード関係のパラメータ設定（ここから） ####
    host = 'stakahashi.ddns.net'
    #host = 'hokoudai.ddns.net'
    webdav_folder = '/webdav2021LAMTp8st/soyaBUS/_tmp_bus_H/'
    ##### ファイルアップロード関係のパラメータ設定（ここまで） ####

    rec_interval = 8

    return height, width, surface_area_Ytop, surface_area_Ybottom, surface_area_Xleft, surface_area_Xright, surface_resize_width, surface_resize_height, noon_model_start, noon_model_end, WIPS_area_Ytop, WIPS_area_Ybottom, WIPS_area_Xleft, WIPS_area_Xright, carNumber, freeWord, gps_device_name, rate, dataNum, file_name, host, webdav_folder, rec_interval
