#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
# -*- coding: utf-8 -*-
__author__ = 'Administrator'
'''
@Time    : 2020/5/19 16:43
@Author  : Jason.Fan
@File    : structural_var.py
所有的结构体，变量定义在这里
'''
import os,sys
from enum import Enum   #声明枚举类型用


IsDebug=1
AdminPWD='lrbs7687'
Version = '4.1.2'
ScanSNFlag=0     #标记是否扫描了SN
NoticeMessageYes=0
CurrentTestItemRow=0    #每个DUT测试项目Index递增，用于加入QTableWidget中显示



#定义枚举类, Run从1开始
DUTStatusMode = Enum('DUTStatusMode', ('Run','Pass','Fail','StandBy','ReTest','WaitSFC','BootUp'))
ConnectType   = Enum('ConnectType',('TCPIP','GPIB','USB'))
TypeSN        = Enum('TypeSN',('PSN','CSN'))

# class ConnectType(Enum):
#     TCPIP=0
#     GPIB=1
#     USB=2



class TabParam:
    def __init__(self):
        self.Tab_stationList=[]
        self.Tab_chrCurrentPath=''
        self.Tab_chrTabPath=''
        self.Tab_chrTabProgramTitle=''
        self.Tab_chrPCName=''
        self.Tab_chrIPAddr1=''
        self.Tab_chrIPAddr2=''
        self.Tab_chrProductName=''
        self.Tab_chrStationNumber=''
        self.Tab_OpWorkID=''
        self.Tab_chrStationName=''
        self.Tab_DEVNAME1=''
        self.Tab_DEVNAME2=''
        self.Tab_IsSFISLocal=0

        self.Tab_IsDialogBeforeTest=0
        self.Tab_IsAutoFixture=0
        self.Tab_SNLength=16
        self.Tab_Pass=0
        self.Tab_Fail=0
        self.FPY_rate=0.00
        self.Tab_ConMAX=10000
        self.Tab_AntMAX=5000
        self.Tab_CountCon=0
        self.Tab_CountAnt=0
        self.FIXCOMPort=''
        self.DUTCOMPort=''

class TabDataBase:
    class ORACLEDB:
        def __init__(self):
            self.IsOracleDB=0
            self.OracleServerIP=''
            self.ServerPort=1234
            self.DBName=''
            self.UserName=''
            self.PassWord=''
class TabSaveLog:
    def __init__(self):
        self.Tab_IsLogOnLocal=1
        self.Tab_IsLogOnServer=0
        self.Tab_LocalLogPath=''
        self.Tab_ServerDrive=''
        self.Tab_UserName=''
        self.Tab_PassWord=''
        self.Tab_ServerAddress=''
        self.Tab_ServerLogPath=''
class TabMACRange:
    def __init__(self):
        self.Ismaclocal = 1
        self.MACbegin = '300ED5E95689'
        self.MACend = '300ED5E95750'
        self.MACcurrent = '8096CA16145E'

class TabIMEIRange:
    def __init__(self):
        self.Isimeilocal=1
        self.IMEIbegin='86281901006391'
        self.IMEIend='86281901006342'
        self.IMEIcurrent='86281901006163'
class TabDUTInfo:
    def __init__(self):
        self.HHSN=''   #扫描一枪的HongHai SN ， 针对L6/L10 赋值给下面
        self.PSN=''    #L6 SN
        self.CSN=''    #L10 SN
        self.WIFIMACID1=''
        self.WIFIMACID2=''
        self.BTMACID=''
        self.IMEI1=''
        self.IMEI2=''
        self.MEID=''
        self.IsRunStatus=0
        self.IsSFISOn=0
        self.IsSample=0
        self.iStartTime=0
        self.iEndTime=0
        self.chrErrorCode=''
        self.chrSFISErrorCode=''
        self.IsPassDCTResponse=''
        self.TestCycleTime=0
class TabInstrument:
    class CMW500:
        def __init__(self):
            self.iIsOnCMW500=0
            self.dPathLoss698=0
            self.dPathLoss850=0
            self.dPathLoss900=0
            self.dPathLoss1750=0
            self.dPathLoss1850=0
            self.dPathLoss1900=0
            self.dPathLoss1950=0
            self.dPathLoss2150=0
            self.dPathLoss2500=0
            self.dPathLoss2550=0
            self.dPathLoss2650=0
            self.dPathLoss2700=0
# //此处默认都是RF1 COM Port的路由线路
# //conductive connect  RF1 com
            self.dPathLoss_WIFI_2GL=0    #2412Mhz
            self.dPathLoss_WIFI_2GM=0    #2442Mhz
            self.dPathLoss_WIFI_2GH=0    #2472Mhz
            self.dPathLoss_WIFI_5GL=0    #5180Mhz
            self.dPathLoss_WIFI_5GM=0    #5500Mhz
            self.dPathLoss_WIFI_5GH=0    #5805Mhz
            self.dPathLoss_BT_2GL=0    #2402Mhz  0 channel
            self.dPathLoss_BT_2GM=0    #2441Mhz   39 channel
            self.dPathLoss_BT_2GH=0    #2480Mhz   78 channel            
# //OTA connect         RF1 com
            self.dAntLoss_WIFI_2GL=0
            self.dAntLoss_WIFI_2GM=0
            self.dAntLoss_WIFI_2GH=0
            self.dAntLoss_WIFI_5GL=0
            self.dAntLoss_WIFI_5GM=0
            self.dAntLoss_WIFI_5GH=0
            self.dAntLoss_BT_2GL=0    #2402Mhz  0 channel
            self.dAntLoss_BT_2GM=0    #2441Mhz   39 channel
            self.dAntLoss_BT_2GH=0    #2480Mhz   78 channel
    class IQ2011:
        def __init__(self):
            self.iIsOnIQ2011=0
            self.iIsConnected=0
# //for Conductive RF
            self.dPathLoss_2G=0   #单天线
            self.dPathLoss_2GL=0
            self.dPathLoss_2GH=0
            self.dPathLoss_5G=0
            self.dPathLoss_5GL=0
            self.dPathLoss_5GH=0
# #for OTA RF
            self.dPathLoss_2G_CHAN1=0     #双天线    2442
            self.dPathLoss_2GL_CHAN1=0     #双天线   2412
            self.dPathLoss_2GH_CHAN1=0     #双天线   2472
            self.dPathLoss_2G_CHAN2=0
            self.dPathLoss_2GL_CHAN2=0     #双天线
            self.dPathLoss_2GH_CHAN2=0     #双天线
            self.dPathLoss_5G_CHAN1=0      #5500
            self.dPathLoss_5GL_CHAN1=0     #5180
            self.dPathLoss_5GH_CHAN1=0     #5785
            self.dPathLoss_5G_CHAN2=0
            self.dPathLoss_5GL_CHAN2=0
            self.dPathLoss_5GH_CHAN2=0
# #for OTA BT
            self.dPathLoss_2G_BTCHAN1=0     #   2402
            self.dPathLoss_2GL_BTCHAN1=0     #   2442
            self.dPathLoss_2GH_BTCHAN1=0     #   2480
    class IQxel:
        def __init__(self):
            self.iIsOnIQxel=0
            self.IQxelTestFlag=0
            self.dPathLoss_2G=0
            self.dPathLoss_5G=0
            self.dPathLoss_5GAC_CHAN1=0
            self.dPathLoss_5GAC_CHAN2=0
    class GSS6100:
        def __init__(self):
            self.GSS6100TestFlag=0
            self.CN_LowLimit=0
            self.CN_HighLimit=0
            self.PRN_ID=32     # satelliteid 1--32
            self.d_CNoValue=0.01   #CN value  //for qualcommm way test
    class Keithley2303A:
        def __init__(self):
            self.iIsOn2303A=0
            self.iGPIBAddress=5

class RFResult:
    def __init__(self):
        self.dWifiPower=0.1
        self.dWifiEVM=0.1
        self.dWifiFreqErr=0.1
        self.dWifiPer=0.1
        self.dBTPower=0.1
        self.dBTBer=0.1


if __name__ == '__main__':
    print(DUTTestStatus.Run.value)