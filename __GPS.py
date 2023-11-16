import serial
import binascii

from serial.tools import list_ports


##### GPSの処理 ####　#チェックサムの検証を本来はしないとダメ
def comport_search(gps_device_name):
    ports = list_ports.comports()
    # device = [info for info in ports if gps_device_name in info.serial_number]
    device = [info for info in ports]
    device_name = str(device[0])
    if gps_device_name in device_name:
        return device[0].device
    else:
        print("計測器が接続されていません")
        # exit()


def getGPS(comport_name, dataNum, rate):
    print("getGPS")
    comport = serial.Serial(comport_name, rate)

    GPRMC = -1
    # 安全のための処理
    while GPRMC == -1:
        flag = True
        while flag:
            try:
                tmp = comport.read(dataNum)
                flag = False
            except:
                flag = True

        tmp_string = tmp.decode("utf-8", errors="ignore")
        tmp_string = (
            "$GPRMC,022313.00,A,4305.7218591,N,14120.4855501,E,0.0,,130723,9.7,W,D*0A"
        )
        tmp_string = tmp_string.replace("\r", ",")
        tmp_string = tmp_string.replace("\n", "")
        tmp2 = tmp_string.split(",")

        try:
            for i in range(len(tmp2)):
                if tmp2[i] == "$GPRMC":
                    GPRMC = i
                    break
            if "*" in tmp2[GPRMC + 12]:
                print("Correct GPS data.  " + str(tmp2[GPRMC + 12]))
            else:
                GPRMC = -1
                print("Reload GPS data.  " + str(tmp2[GPRMC + 12]))
                GPRMC = -1
        except:
            pass

        if not GPRMC == -1:
            try:
                try:
                    if float(tmp2[GPRMC + 1]) >= 150000:
                        time_jst = (
                            float(tmp2[GPRMC + 1]) - 150000
                        )  # UTC time is transrated to JST
                    else:
                        time_jst = 90000 + float(
                            tmp2[GPRMC + 1]
                        )  # UTC time is transrated to JST
                        # 24を超える時間になることがあるので要調整
                except ValueError as ev:
                    print("vaule Error:", ev)
                    time_jst = 999999

                # print(tmp2[GPRMC+9])
                if (float(time_jst) / 10000) <= 9:
                    currentDate = float(tmp2[GPRMC + 9])
                    if currentDate == 301122:
                        currentDate = str("011222")
                    elif currentDate == 311222:
                        currentDate = str("010123")
                    elif currentDate == 310123:
                        currentDate = str("010223")
                    elif currentDate == 280223:
                        currentDate = str("010323")
                    elif currentDate == 310323:
                        currentDate = str("010423")
                    elif currentDate == 300423:
                        currentDate = str("010523")
                    elif currentDate == 310523:
                        currentDate = str("010623")
                    elif currentDate == 300623:
                        currentDate = str("010723")
                    elif currentDate == 310723:
                        currentDate = str("010823")
                    elif currentDate == 310823:
                        currentDate = str("010923")
                    elif currentDate == 300923:
                        currentDate = str("011023")
                    elif currentDate == 311023:
                        currentDate = str("011123")
                    elif currentDate == 301123:
                        currentDate = str("011223")
                    elif currentDate == 311223:
                        currentDate = str("010124")
                    else:
                        currentDate = (
                            currentDate + 10000
                        )  # difference of date due to time zone is transrated to JST
                else:
                    currentDate = float(tmp2[GPRMC + 9])
                # print(currentDate)
                # Edited by HAYASHI at 2023.6.28

                csv_data = "date_time_JST,status(A is OK),latitude,north-south,longitude,east-west,deg,date,WIPS,image_name,velocity,roadSurface,dry,semi-wet,wet,slush,ice,fresh,freeWord\n"
                csv_data = (
                    csv_data
                    + "{:0=6}".format(int(time_jst))
                    + ","
                    + tmp2[GPRMC + 2]
                    + ","
                    + tmp2[GPRMC + 3]
                    + ","
                    + tmp2[GPRMC + 4]
                )
                csv_data = (
                    csv_data + "," + tmp2[GPRMC + 5] + "," + tmp2[GPRMC + 6] + ","
                )
                csv_data = (
                    csv_data
                    + tmp2[GPRMC + 8]
                    + ","
                    + "{:0=6}".format(int(currentDate))
                    + ","
                )
                if tmp2[GPRMC + 7] == "":
                    velocity = "0"
                else:
                    velocity = str(float(tmp2[GPRMC + 7]) * 1.852)
            except IndexError as e:
                # print('catch IndexError:', e)
                GPRMC = -1

    # GPRMCのみ処理
    if tmp2[GPRMC] == "$GPRMC":
        comport.close()
        return csv_data, velocity

    print("ERROR: Func_getGPS_CLOSE")
