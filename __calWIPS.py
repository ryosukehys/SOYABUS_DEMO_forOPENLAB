import cv2
import sys
import numpy as np

from parameter import parameter_submain
height, width, surface_area_Ytop, surface_area_Ybottom, surface_area_Xleft, surface_area_Xright, surface_resize_width, surface_resize_height, noon_model_start, noon_model_end, WIPS_area_Ytop, WIPS_area_Ybottom, WIPS_area_Xleft, WIPS_area_Xright, carNumber, freeWord, gps_device_name, rate, dataNum, file_name, host, webdav_folder, rec_interval = parameter_submain()

def calWIPS(imageList):
    WIPS = 8.0
    tmpWIPS = [0.0, 0.0, 0.0]
    for i in range(len(imageList)):
        #(1) jpeg画像を読み込む(グレースケール)
        img = cv2.imread(imageList[i],0)
        #height, width = img.shape
        height = 480
        width = 640
        #print("Tst")
        img = img / 255
        #(2) グレースケール変換(0.0 <-> 1.0)
        #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #(3) 指定位置を繰りぬく(256px * 256px) <-とりあえず、ど真ん中
        grayPart = img[int(WIPS_area_Ytop):int(WIPS_area_Ybottom), int(WIPS_area_Xleft):int(WIPS_area_Xright)]
        #(4) フーリエ変換
        fimg = np.fft.fft2(grayPart)
        fimg =  np.fft.fftshift(fimg)
        #(5) パワースペクトルを計算  -->  wips
        mag = 20*np.log(np.abs(fimg)) / 32
        magSpec_Part = mag[97:161, 97:161]
        magSpec_Part[int(64/2)-20:int(64/2)+20, int(64/2)-20:int(64/2)+20] = 0
        tmpWIPS[i] = np.log(np.sum(magSpec_Part))
    
    WIPS = min(tmpWIPS)
    minIndex = tmpWIPS.index(WIPS)
    
    return WIPS, minIndex
