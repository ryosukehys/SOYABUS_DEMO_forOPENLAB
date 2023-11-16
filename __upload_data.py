import os
import shutil
import time

import easywebdav


def upload_data(host_url, webdav_folder, uploadFolder, dstFolder):
    fileList = os.listdir(uploadFolder)

    # print(fileList)

    fileList_jpg = [s for s in fileList if s.endswith(".jpg")]
    fileList_csv = [s for s in fileList if s.endswith(".csv")]

    # print(fileList_jpg)
    # print(fileList_csv)

    flag = True
    # http://192.168.22.24/files/ <- VMのUbuntuに仮で立てたWebサーバ

    try:
        webdav = easywebdav.connect(
            host=host_url,
            # host='bswv.86s.jp',
            # host='bswv1.86s.jp',
            # host='bswv2.86s.jp',
            username="webdavLAMT",
            port=80,
            protocol="http",
            password="lamt2021LAMT"
            # timeout = 3
        )
    except:
        print("Webdav connection ERROR.")
        return False

    webdav.cd(webdav_folder)

    for i in range(len(fileList_jpg)):
        if i > 10:
            break
        moveFile = uploadFolder + fileList_jpg[i]
        dstFile_onServer = webdav_folder + fileList_jpg[i]

        #### ここにuploadの機能を実装
        # webdav.upload(moveFile, dstFile_onServer)
        if not webdav.exists(dstFile_onServer):
            flag = False

        ### uploadが成功した場合に下をやるように書きたい
        if flag:
            # moveFile = uploadFolder + fileList_jpg[i]
            #### uploadしたファイルを蓄積用のフォルダに移動
            dstFile = dstFolder + fileList_jpg[i]
            if not os.path.exists(uploadFolder):
                os.mkdir(uploadFolder)
            if os.path.exists(dstFile):
                os.remove(dstFile)  # 先に存在した良く判らないファイルを削除
            shutil.copy(moveFile, dstFile)  # All JPG files are moved.
            os.remove(moveFile)

    flag = True
    for i in range(len(fileList_csv)):
        if i > 10:
            break
        moveFile = uploadFolder + fileList_csv[i]
        dstFile_onServer = webdav_folder + fileList_csv[i]

        #### ここにuploadの機能を実装
        # webdav.upload(moveFile, dstFile_onServer)
        if not webdav.exists(dstFile_onServer):
            flag = False

        ### uploadが成功した場合に下をやるように書きたい
        if flag:
            # moveFile = uploadFolder + fileList_csv[i]
            #### uploadしたファイルを蓄積用のフォルダに移動
            dstFile = dstFolder + fileList_csv[i]
            if not os.path.exists(uploadFolder):
                os.mkdir(uploadFolder)
            if os.path.exists(dstFile):
                os.remove(dstFile)  # 先に存在した良く判らないファイルを削除
            # shutil.copy(moveFile, dstFile)  #CSV files are removed only.
            os.remove(moveFile)
            # os.remove(dstFile)
            # return True

    # return False
    return True
