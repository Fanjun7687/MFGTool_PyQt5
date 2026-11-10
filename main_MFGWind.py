# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
# -*-coding:utf-8 -*-

'''
ctrl+shift+(1,2,3,4,5,....) 创建代码标签
ctrl+(1,2,3....) 快速定位标签位置

程序打包exe:  pyinstall -F -w ***.py , 在同级目录下生成dist目录，记得将依赖的其他文件copy过去

'''

import sys, time, os
from threading import Thread
import threading
import subprocess
import win32api, win32gui, win32con, win32process
import configparser, socket
import random
import pygame
import keyboard, mouse
from enum import Enum

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from myUI import *

from package import structural_var as SVAR  # 从package目录导入模块
from package import hardwareInfo as HWI
from package import windowHandlerCtrl as WHC
from package.SerialCom_Class import ComBasic
from package.errorCode import ErrorCode


class MFGWindow(QMainWindow, Ui_MainWindow):   #Ui_MainWindow直接指向myUI的主类
    # 定义各种信号
    signal_updateStation = pyqtSignal(str)  # 更新站位信息面板的信号
    signal_addtestLog = pyqtSignal(str)  # 追加测试日志信息到pTE_TestLog控件
    signal_sfcRouterChk = pyqtSignal(str)   #SFC Routing Check SN
    signal_popNotice = pyqtSignal(str)   #弹出提示窗口
    signal_testResultInsert= pyqtSignal(list)   #QTableWidget的TestResult项目追加
    signal_testResultClear=pyqtSignal()   #清空QTableWidget的所有测试项目记录
    signal_showStatus=pyqtSignal(Enum)   #更改DUT测试状态

    def __init__(self, parent=None):
        super(MFGWindow, self).__init__(parent)
        self.setupUi(self)
        self.Var_Defined()  # 变量定义
        self.SetPCInfo()
        self.SetDUTInfo()
        self.InitTableWidget()    #初始化TestResult 的元件格式
        self.SignalBind()  # 绑定所有信号和槽
        self.keyboardGrabber()  # 键盘监听

        # self.CheckConnCounter()
        # print(SVAR.DUTStatusMode.StandBy,SVAR.DUTStatusMode.StandBy.name,SVAR.DUTStatusMode.StandBy.value)
        # self.lcd_TestTime.setSegmentStyle(QLCDNumber.Flat)
        # self.lcd_TestTime.setMode(QLCDNumber.Oct)
        # self.lcd_TestTime.setDigitCount(8)
        self.lcd_TestTime.display('00:00:59')

        lst_TestResult=[SVAR.CurrentTestItemRow,'Test Item1',245.6,125.3,700.3,'PASS']
        self.signal_testResultInsert.emit(lst_TestResult)
        self.signal_testResultInsert.emit([SVAR.CurrentTestItemRow,'Test Item1',245.6,125.3,700.3,'PASS'])
        self.signal_testResultInsert.emit([SVAR.CurrentTestItemRow,'Test Item1',245.6,125.3,700.3,'PASS'])
        self.signal_testResultInsert.emit([SVAR.CurrentTestItemRow,'Test Item1',863.2,125.3,700.3,'FAIL'])
        self.signal_testResultInsert.emit([SVAR.CurrentTestItemRow,'Test Item1',245.6,125.3,700.3,'PASS'])
        self.signal_testResultInsert.emit([SVAR.CurrentTestItemRow,'Test Item1',245.6,125.3,700.3,'PASS'])
        self.signal_testResultInsert.emit([SVAR.CurrentTestItemRow,'Test Item1',245.6,125.3,700.3,'PASS'])
        self.signal_testResultInsert.emit([SVAR.CurrentTestItemRow,'Test Item1',245.6,125.3,700.3,'FAIL'])

        print(type(SVAR.DUTStatusMode.Run))

        self.sTabDUTInfo.chrErrorCode='[{0}] {1}'.format(ErrorCode.SNLEN0.get_code(),ErrorCode.SNLEN0.get_msg())
        print(self.sTabDUTInfo.chrErrorCode)

        self.sTabDUTInfo.PSN='F123456789012345'
        print(self.sTabParam.Tab_SNLength)
        print(len(self.sTabDUTInfo.PSN))
        # self.PTTest_SBB115()



    def __del__(self):
        pass

    def closeEvent(self, event):  # 重写closeEvent方法，实现dialog窗体关闭时执行一些代码  ,event: close()触发的事件
        if (SVAR.IsDebug == 1):
            event.accept
            pass
        else:
            reply = QMessageBox.question(self,
                                         '本程序',
                                         "是否要退出程序？",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def keyPressEvent(self, QKeyEvent):  # 监听键盘输入或者扫描枪输入，以回车作为终结标记，相当于Hook钩子
        if QKeyEvent.key() == Qt.Key_Return or QKeyEvent.key() == Qt.Key_Enter:  # Key_Return 大键盘回车  Key_Enter:小键盘回车
            print(self.sTabDUTInfo.HHSN)
            if len(self.sTabDUTInfo.HHSN) != self.sTabParam.Tab_SNLength:
                self.DbSFCErrInfoAdd('Input Number Is :[ %s ]' % self.sTabDUTInfo.HHSN)
                self.DbSFCErrInfoAdd('Length Is: %d' % len(self.sTabDUTInfo.HHSN))
                self.sTabDUTInfo.HHSN = ''
                return
            else:
                self.Slot_AddTestLog('Input DUT SN :%s' % self.sTabDUTInfo.HHSN)
                if SVAR.ScanSNFlag == 0: SVAR.ScanSNFlag = 1
                print('DUTInfo TableView Max Rows :', self.tv_DUTInfo.model().rowCount())
                self.UpdateDUTInfo('HHSN', self.sTabDUTInfo.HHSN)
                self.Slot_AddTestLog('Current Station Name : {0}'.format(self.sTabParam.Tab_chrStationName))
                self.UpdateDUTInfo('PSN',
                                   self.sTabDUTInfo.HHSN) if self.sTabParam.Tab_chrStationName == 'PT' else self.UpdateDUTInfo(
                    'CSN', self.sTabDUTInfo.HHSN)
                if not self.sTabDUTInfo.IsSFISOn and not SVAR.ScanSNFlag:    #测试状态中，如扫描SN不处理
                    self.pb_Run.setEnabled(False)
                    return
                self.pTE_TestLog.setPlainText('')    #Test Memo Log Clear
                if self.sTabDUTInfo.IsSFISOn:
                    result=self.signal_sfcRouterChk.emit(self.sTabDUTInfo.HHSN)
                    if not result: return
                self.begin_Test()
                self.sTabDUTInfo.HHSN=''
                return
        else:
            self.sTabDUTInfo.HHSN += QKeyEvent.text()
            # print(QKeyEvent.text(),end='')

        pass

    def SetPCInfo(self):
        self.modePCInfo = QStandardItemModel(0, 2)
        self.modePCInfo.setHorizontalHeaderLabels(['Parameter', 'Value'])
        # self.modePCInfo.setItem(0,0,QStandardItem('%s'%('ComputerName')))
        # self.modePCInfo.setItem(0,1,QStandardItem('%s'%('JASONPC')))
        self.modePCInfo.appendRow(
            [QStandardItem('%s' % ('ComputerName')), QStandardItem('%s' % (self.sTabParam.Tab_chrPCName))])
        self.modePCInfo.appendRow(
            [QStandardItem('%s' % ('IP Address1')), QStandardItem('%s' % (self.sTabParam.Tab_chrIPAddr1))])
        self.modePCInfo.appendRow([QStandardItem('%s' % ('IP Address2')), QStandardItem('%s' % ('xxx.xxx.xxx.xxx'))])
        self.modePCInfo.appendRow([QStandardItem('%s' % ('Total PASS Qty')), QStandardItem('%d' % (self.sTabParam.Tab_Pass))])
        self.modePCInfo.appendRow([QStandardItem('%s' % ('Total FAIL Qty')), QStandardItem('%d' % (self.sTabParam.Tab_Fail))])

        if ((self.sTabParam.Tab_Pass + self.sTabParam.Tab_Fail) > 0):
            self.sTabParam.FPY_rate = "{:.2f} %".format(
                self.sTabParam.Tab_Pass * 100.00 / (self.sTabParam.Tab_Pass + self.sTabParam.Tab_Fail))
        else:
            self.sTabParam.FPY_rate = '0.00 %'
        self.modePCInfo.appendRow([QStandardItem('%s' % ('F.P.Y')), QStandardItem('%s' % (self.sTabParam.FPY_rate))])
        self.modePCInfo.appendRow(
            [QStandardItem('%s' % ('Test Cycle Time')), QStandardItem('%s' % (self.sTabDUTInfo.TestCycleTime))])
        self.modePCInfo.appendRow(
            [QStandardItem('%s' % ('RF  Probe Count')), QStandardItem('%s' % (self.sTabParam.Tab_CountAnt))])
        self.modePCInfo.appendRow(
            [QStandardItem('%s' % ('Connector Count')), QStandardItem('%s' % (self.sTabParam.Tab_CountCon))])
        self.modePCInfo.appendRow([QStandardItem('%s' % ('FIX COM'))])
        self.modePCInfo.appendRow([QStandardItem('%s' % ('DUT COM'))])

        self.tv_PCInfo.setModel(self.modePCInfo)
        self.tv_PCInfo.horizontalHeader().setStretchLastSection(True)  ##水平方向标签拓展剩下的窗口部分，填满表格
        self.tv_PCInfo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 水平方向，表格大小拓展到适当的尺寸
        # self.tv_PCInfo.setEnabled(False)
        self.tv_PCInfo.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        self.tv_PCInfo.setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选择
        self.tv_PCInfo.verticalHeader().setVisible(False)  # 设置第一栏序号不显示
        # load com port info in cbb_FIXCOM & cbb_DUTCOM
        self.cbb_FIXCOM.addItems(self.mHW.get_SerialComPort());
        self.cbb_FIXCOM.setCurrentIndex(-1)
        self.cbb_DUTCOM.addItems(self.mHW.get_SerialComPort());
        self.cbb_DUTCOM.setCurrentIndex(-1)
        pass

    def SetDUTInfo(self):
        self.modeDUTInfo = QStandardItemModel(0, 2)
        self.modeDUTInfo.setHorizontalHeaderLabels(['TrackingNumb', 'Value'])
        # self.modeDUTInfo.setItem(0,0,QStandardItem('%s'%('ComputerName')))
        # self.modeDUTInfo.setItem(0,1,QStandardItem('%s'%('JASONPC')))
        self.modeDUTInfo.appendRow([QStandardItem('%s' % ('HHSN')), QStandardItem('%s' % (self.sTabDUTInfo.HHSN))])
        self.modeDUTInfo.appendRow([QStandardItem('%s' % ('PSN')), QStandardItem('%s' % (self.sTabDUTInfo.PSN))])
        self.modeDUTInfo.appendRow([QStandardItem('%s' % ('CSN')), QStandardItem('%s' % (self.sTabDUTInfo.CSN))])
        self.modeDUTInfo.appendRow([QStandardItem('%s' % ('WIFIMACID1')), QStandardItem('%s' % (self.sTabDUTInfo.WIFIMACID1))])
        self.modeDUTInfo.appendRow([QStandardItem('%s' % ('WIFIMACID2')), QStandardItem('%s' % (self.sTabDUTInfo.WIFIMACID2))])
        self.modeDUTInfo.appendRow([QStandardItem('%s' % ('BTMACID')), QStandardItem('%s' % (self.sTabDUTInfo.BTMACID))])
        self.modeDUTInfo.appendRow([QStandardItem('%s' % ('IMEI1')), QStandardItem('%s' % (self.sTabDUTInfo.IMEI1))])
        self.modeDUTInfo.appendRow([QStandardItem('%s' % ('IMEI2')), QStandardItem('%s' % (self.sTabDUTInfo.IMEI2))])
        self.modeDUTInfo.appendRow([QStandardItem('%s' % ('MEID')), QStandardItem('%s' % (self.sTabDUTInfo.MEID))])

        self.tv_DUTInfo.setModel(self.modeDUTInfo)  # 绑定数据源
        self.tv_DUTInfo.horizontalHeader().setStretchLastSection(True)  ##水平方向标签拓展剩下的窗口部分，填满表格
        self.tv_DUTInfo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 水平方向，表格大小拓展到适当的尺寸
        # self.tv_PCInfo.setEnabled(False)
        self.tv_DUTInfo.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        self.tv_DUTInfo.setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选择
        self.tv_DUTInfo.verticalHeader().setVisible(False)  # 设置第一栏序号不显示
        pass

    def UpdateDUTInfo(self, strKey, value):  # 更新指定strkey的内容
        for index in range(self.tv_DUTInfo.model().rowCount()):  # 遍历所有row的index
            if self.tv_DUTInfo.model().item(index, 0).text() == strKey:
                self.modeDUTInfo.setItem(index, 1, QStandardItem('%s' % (value)))
                self.tv_DUTInfo.setModel(self.modeDUTInfo)
                break

    def UpdatePCInfo(self, strKey, value):
        for index in range(self.tv_PCInfo.model().rowCount()):  # 遍历所有row的index
            if self.tv_PCInfo.model().item(index, 0).text() == strKey:
                self.modePCInfo.setItem(index, 1, QStandardItem('%s' % (value)))
                self.tv_PCInfo.setModel(self.modePCInfo)
                break

    def Var_Defined(self):
        self.sTabParam = SVAR.TabParam()
        self.sTabDataBase = SVAR.TabDataBase()
        self.sTabDUTInfo = SVAR.TabDUTInfo()
        self.sTabMACRange = SVAR.TabMACRange()
        self.sTabIMEIRange = SVAR.TabIMEIRange()
        self.sTabInstrument = SVAR.TabInstrument()
        self.sTabSaveLog = SVAR.TabSaveLog()

        self.mHW = HWI.HardWareInfo()
        self.sTabParam.Tab_chrPCName = socket.gethostname()
        try:
            self.sTabParam.Tab_chrIPAddr1 = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
        except socket.gaierror:  # 主机名无法解析时(如无DNS/离线环境)回环地址兜底
            self.sTabParam.Tab_chrIPAddr1 = '127.0.0.1'
        print(self.sTabParam.FPY_rate)

        if not os.path.exists('./cfg.tab'):
            QMessageBox.warning(self, '警告提示', '没有找到cfg.tab文件', QMessageBox.Yes | QMessageBox.Yes)
            exit()
            self.close()
        else:
            self.getCfgSetting()


#some variable init 需要的变量初始化定义在这
        self.sTabDUTInfo.IsRunStatus=0


    def InitTableWidget(self):
        Headers=['Index','Test Item','Test Value','Low Spec','High Spec','Test Result']
        font = QFont('Times New Roman', 10)
        font.setBold(True)  #设置字体加粗
        self.tw_TestResult.horizontalHeader().setFont(font)  #设置表头字体
        self.tw_TestResult.horizontalHeader().setStyleSheet('QHeaderView::section{background:#99CCFF};color:blue;') #设置表头的背景色为
        # self.tw_TestResult.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        # self.tw_TestResult.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        # self.tw_TestResult.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch)
        # self.tw_TestResult.horizontalHeader().setSectionResizeMode(3,QHeaderView.Stretch)
        # self.tw_TestResult.horizontalHeader().setSectionResizeMode(4,QHeaderView.Stretch)
        self.tw_TestResult.horizontalHeader().setSectionResizeMode(5,QHeaderView.Stretch)

        self.tw_TestResult.setEditTriggers(QAbstractItemView.NoEditTriggers) #设置表格不可更改
        self.tw_TestResult.setSortingEnabled(True)#设置表头可以自动排序
        # self.tw_TestResult.horizontalHeader().resizeSection(0,60)
        self.tw_TestResult.setFrameShape(QFrame.Box) #设置外框
        self.tw_TestResult.setSelectionMode(QAbstractItemView.SingleSelection) #设置只可以单选，设置选取方式为单个选取,可以使用ExtendedSelection进行多选
        self.tw_TestResult.setSelectionBehavior(QAbstractItemView.SelectRows) #设置 不可选择单个单元格，只可选择一行。设置表格的选取方式是行选取
        self.tw_TestResult.setColumnCount(6)
        self.tw_TestResult.setRowCount(0)
        self.tw_TestResult.setHorizontalHeaderLabels(Headers)  #使用使用setHorizontalHeaderLabels和setVerticalHeaderLabels，设置标题方便，推荐
        # self.tw_TestResult.setVerticalHeaderLabels(('1', '2','3','4','5','6'))
        self.tw_TestResult.verticalHeader().setVisible(False)#隐藏列表头
        # setStretchLastSection(true); //均分各列
        self.tw_TestResult.setColumnWidth(0,58) # 设置table表格第4列的宽度，130为宽度
        self.tw_TestResult.setColumnWidth(1,211) # 设置table表格第4列的宽度，130为宽度
        self.tw_TestResult.setColumnWidth(2,211) # 设置table表格第4列的宽度，130为宽度
        self.tw_TestResult.setColumnWidth(3,211) # 设置table表格第4列的宽度，130为宽度
        self.tw_TestResult.setColumnWidth(4,211) # 设置table表格第4列的宽度，130为宽度
        # self.tw_TestResult.setColumnWidth(5,100) # 设置table表格第4列的宽度，130为宽度
        #以下两行是颜色背景交替
        self.tw_TestResult.setAlternatingRowColors(True)
        self.tw_TestResult.setStyleSheet('alternate-background-color:#FFE0FFFF;background:white;color:#000000;')



        # row=self.tw_TestResult.rowCount()
        # print(row)
        # self.tw_TestResult.insertRow(row) #插入到第一行
        # self.tw_TestResult.setItem(row, 0, QTableWidgetItem('8'))# 位置为第0行，第0列，后面为QTableWidgetItem对象，可以为str类型，int类型
        # self.tw_TestResult.setItem(row, 1, QTableWidgetItem('板载温度'))# 调用setTextAlignment()方法，设置文本居中显示
        # self.tw_TestResult.setItem(row, 2, QTableWidgetItem('4'))


        # item_id=QTableWidgetItem('1')
        # item_id.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # 设置物件的状态为只可被选择（未设置可编辑）
        # item_name = QTableWidgetItem("door") #我们要求它可以修改，所以使用默认的状态即可
        # item_pos = QTableWidgetItem("(1,2)")
        # item_pos.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # 设置物件的状态为只可被选择
        # self.tw_TestResult.setItem(row, 0, item_id)
        # self.tw_TestResult.setItem(row, 1, item_name)
        # self.tw_TestResult.setItem(row, 2, item_pos)

        #设置所有单元格内容居中对齐
        # for i in range(1):     #row index
        #      for j in range(3):   #column index
        #                self.tw_TestResult.item(i,j).setTextAlignment(Qt.AlignCenter)



    def getCfgSetting(self):
        self.cfgtab = configparser.ConfigParser()
        self.cfgtab.read("./cfg.tab")
        print('========================Get Cfg.tab Param===================')
        self.sTabParam.Tab_stationList = self.cfgtab.get('General', 'stationlist').split(',')
        # print(self.sTabParam.Tab_stationList)
        self.sTabParam.Tab_chrProductName = self.cfgtab.get("General", "productname");
        self.sTabParam.Tab_chrStationName = self.cfgtab.get('General', 'stationname');
        self.lb_ProjectName.setText(self.sTabParam.Tab_chrProductName + ' [' + self.sTabParam.Tab_chrStationName + "]")
        self.sTabParam.Tab_StationNumber = self.cfgtab.get('General', 'stationnumber')
        self.sTabParam.Tab_OpWorkID = self.cfgtab.get('General', 'opworkid')
        self.sTabParam.Tab_IsSFISLocal = self.cfgtab.get('General', 'issfclocal')
        self.sTabParam.Tab_IsDialogBeforeTest = self.cfgtab.get('General', 'isdialogbeforetest')
        self.sTabParam.Tab_IsAutoFixture = self.cfgtab.get('General', 'isautofixture')
        self.sTabParam.Tab_SNLength = (int)(self.cfgtab.get('General', 'snlength'))
        self.sTabParam.Tab_Pass = (int)(self.cfgtab.get('Result', 'pass'))
        self.sTabParam.Tab_Fail = (int)(self.cfgtab.get('Result', 'fail'))
        self.sTabParam.Tab_ConMAX = (int)(self.cfgtab.get('Cable', 'conmax'))
        self.sTabParam.Tab_AntMAX = (int)(self.cfgtab.get('Cable', 'antmax'))
        self.sTabParam.Tab_CountCon = (int)(self.cfgtab.get('Cable', 'concounter'))
        self.sTabParam.Tab_CountAnt = (int)(self.cfgtab.get('Cable', 'antcounter'))

        self.sTabParam.Tab_DEVNAME1 = self.cfgtab.get('DEVLIST', 'devname1');
        print(self.sTabParam.Tab_DEVNAME1)
        self.sTabParam.Tab_DEVNAME2 = self.cfgtab.get('DEVLIST', 'devname2');
        print(self.sTabParam.Tab_DEVNAME2)
        self.Slot_AddTestLog(self.sTabParam.Tab_DEVNAME2)
        self.sTabParam.Ismaclocal = self.cfgtab.get('MACRange', 'ismaclocal')
        self.sTabParam.MACbegin = self.cfgtab.get('MACRange', 'macbegin')
        self.sTabParam.MACend = self.cfgtab.get('MACRange', 'macend')
        self.sTabParam.MACcurrent = self.cfgtab.get('MACRange', 'maccurrent')
        self.sTabParam.Isimeilocal = self.cfgtab.get('IMEIRange', 'isimeilocal')
        self.sTabParam.IMEIbegin = self.cfgtab.get('IMEIRange', 'imeibegin')
        self.sTabParam.IMEIend = self.cfgtab.get('IMEIRange', 'imeiend')
        self.sTabParam.IMEIcurrent = self.cfgtab.get('IMEIRange', 'imeicurrent')

        self.sTabDataBase.ORACLEDB.IsOracleDB = self.cfgtab.get('DataBase', 'isoracledb')
        self.sTabDataBase.ORACLEDB.OracleServerIP = self.cfgtab.get('DataBase', 'serverip')
        self.sTabDataBase.ORACLEDB.ServerPort = self.cfgtab.get('DataBase', 'serverport')
        self.sTabDataBase.ORACLEDB.DBName = self.cfgtab.get('DataBase', 'dbname')
        self.sTabDataBase.ORACLEDB.UserName = self.cfgtab.get('DataBase', 'username')
        self.sTabDataBase.ORACLEDB.PassWord = self.cfgtab.get('DataBase', 'password')

        self.sTabSaveLog.Tab_IsLogOnLocal = self.cfgtab.get('SAVELOG', 'islogonlocal')
        self.sTabSaveLog.Tab_IsLogOnServer = self.cfgtab.get('SAVELOG', 'islogonserver')
        self.sTabSaveLog.Tab_LocalLogPath = self.cfgtab.get('SAVELOG', 'locallogpath')
        self.sTabSaveLog.Tab_ServerDrive = self.cfgtab.get('SAVELOG', 'serverdrive')
        self.sTabSaveLog.Tab_UserName = self.cfgtab.get('SAVELOG', 'username')
        self.sTabSaveLog.Tab_PassWord = self.cfgtab.get('SAVELOG', 'password')
        self.sTabSaveLog.Tab_ServerAddress = self.cfgtab.get('SAVELOG', 'serveraddress')
        self.sTabSaveLog.Tab_ServerLogPath = self.cfgtab.get('SAVELOG', 'serverlogpath')

        self.sTabInstrument.IQ2011.iIsOnIQ2011 = self.cfgtab.get('IQ2011', 'isoniq2011')
        self.sTabInstrument.IQ2011.dPathLoss_2G = self.cfgtab.get('IQ2011', 'pathloss_2g')
        self.sTabInstrument.IQ2011.dPathLoss_2GL = self.cfgtab.get('IQ2011', 'pathloss_2gl')
        self.sTabInstrument.IQ2011.dPathLoss_2GH = self.cfgtab.get('IQ2011', 'pathloss_2gh')
        self.sTabInstrument.IQ2011.dPathLoss_5G = self.cfgtab.get('IQ2011', 'pathloss_5g')
        self.sTabInstrument.IQ2011.dPathLoss_5GL = self.cfgtab.get('IQ2011', 'pathloss_5gl')
        self.sTabInstrument.IQ2011.dPathLoss_5GH = self.cfgtab.get('IQ2011', 'pathloss_5gh')
        self.sTabInstrument.IQ2011.dPathLoss_2G_CHAN1 = self.cfgtab.get('IQ2011', 'pathloss_2g_chan1')
        self.sTabInstrument.IQ2011.dPathLoss_2GL_CHAN1 = self.cfgtab.get('IQ2011', 'pathloss_2gl_chan1')
        self.sTabInstrument.IQ2011.dPathLoss_2GH_CHAN1 = self.cfgtab.get('IQ2011', 'pathloss_2gh_chan1')
        self.sTabInstrument.IQ2011.dPathLoss_2G_CHAN2 = self.cfgtab.get('IQ2011', 'pathloss_2g_chan2')
        self.sTabInstrument.IQ2011.dPathLoss_2GL_CHAN2 = self.cfgtab.get('IQ2011', 'pathloss_2gl_chan2')
        self.sTabInstrument.IQ2011.dPathLoss_2GH_CHAN2 = self.cfgtab.get('IQ2011', 'pathloss_2gh_chan2')
        self.sTabInstrument.IQ2011.dPathLoss_5G_CHAN1 = self.cfgtab.get('IQ2011', 'pathloss_5g_chan1')
        self.sTabInstrument.IQ2011.dPathLoss_5GL_CHAN1 = self.cfgtab.get('IQ2011', 'pathloss_5gl_chan1')
        self.sTabInstrument.IQ2011.dPathLoss_5GH_CHAN1 = self.cfgtab.get('IQ2011', 'pathloss_5gh_chan1')
        self.sTabInstrument.IQ2011.dPathLoss_5G_CHAN2 = self.cfgtab.get('IQ2011', 'pathloss_5g_chan2')
        self.sTabInstrument.IQ2011.dPathLoss_5GL_CHAN2 = self.cfgtab.get('IQ2011', 'pathloss_5gl_chan2')
        self.sTabInstrument.IQ2011.dPathLoss_5GH_CHAN2 = self.cfgtab.get('IQ2011', 'pathloss_5gh_chan2')
        self.sTabInstrument.IQ2011.dPathLoss_2G_BTCHAN1 = self.cfgtab.get('IQ2011', 'pathloss_2g_btchan1')
        self.sTabInstrument.IQ2011.dPathLoss_2GL_BTCHAN1 = self.cfgtab.get('IQ2011', 'pathloss_2gl_btchan1')
        self.sTabInstrument.IQ2011.dPathLoss_2GH_BTCHAN1 = self.cfgtab.get('IQ2011', 'pathloss_2gh_btchan1')
        self.sTabInstrument.IQ2011.iIsConnected = 0

        # you could add parameters as you need here from cfg.tab
        pass

    def DbSFCErrInfoAdd(self, strErr):
        self.pte_SFISLog.appendPlainText(strErr)

    def DbSFCInfoAdd(self, strMsg):
        self.pTE_SFCLog.appendPlainText(strMsg)
        pass

    def SetTestPanelTop(self):
        self.tabWidget_2.setCurrentIndex(1)

    def SetTestMessageTop(self):
        self.tabWidget_2.setCurrentIndex(0)

    def Zero_Ant(self):
        pwd, okPressed = QInputDialog.getText(self, 'Notice', 'Input Password', QLineEdit.Normal, '')
        if okPressed and pwd == SVAR.AdminPWD:
            self.sTabParam.Tab_CountAnt = 0
            self.cfgtab.set('Cable', 'antcounter', str(self.sTabParam.Tab_CountAnt))
            with open("cfg.tab", 'w+') as f:
                self.cfgtab.write(f)
        else:
            QMessageBox.critical(self, 'Warning', 'Error Input Password', QMessageBox.Yes | QMessageBox.Yes)

    def Zero_Con(self):
        pwd, okPressed = QInputDialog.getText(self, 'Notice', 'Input Password', QLineEdit.Normal, '')
        if okPressed and pwd == SVAR.AdminPWD:
            self.sTabParam.Tab_CountCon = 0
            self.cfgtab.set('Cable', 'concounter', str(self.sTabParam.Tab_CountCon))
            with open("cfg.tab", 'w+') as f:
                self.cfgtab.write(f)
        else:
            QMessageBox.critical(self, 'Warning', 'Error Input Password', QMessageBox.Yes | QMessageBox.Yes)
        pass

    def Zero_Pass(self):
        pwd, okPressed = QInputDialog.getText(self, 'Notice', 'Input Password', QLineEdit.Normal, '')
        if okPressed and pwd == SVAR.AdminPWD:
            self.sTabParam.Tab_Pass = 0
            self.cfgtab.set('Result', 'pass', str(self.sTabParam.Tab_Pass))
            with open("cfg.tab", 'w+') as f:
                self.cfgtab.write(f)
        else:
            QMessageBox.critical(self, 'Warning', 'Error Input Password', QMessageBox.Yes | QMessageBox.Yes)
        pass

    def Zero_Fail(self):
        pwd, okPressed = QInputDialog.getText(self, 'Notice', 'Input Password', QLineEdit.Normal, '')
        if okPressed and pwd == SVAR.AdminPWD:
            self.sTabParam.Tab_Fail = 0
            self.cfgtab.set('Result', 'fail', str(self.sTabParam.Tab_Fail))
            with open("cfg.tab", 'w+') as f:
                self.cfgtab.write(f)
        else:
            QMessageBox.critical(self, 'Warning', 'Error Input Password', QMessageBox.Yes | QMessageBox.Yes)
        pass

    def DevelopAbout(self):
        QMessageBox.about(self, "About", 'Developed By: JASON.FAN \r\n Ver: {}'.format(SVAR.Version))
        pass

    def SetIsSample(self):
        self.sTabDUTInfo.IsSample=1;SVAR.IsDebug=1
        self.sTabDUTInfo.IsSFISOn=0
        print(self.sTabDUTInfo.IsSFISOn,self.sTabDUTInfo.IsSample)

    def SetIsSFISON(self):
        self.sTabDUTInfo.IsSFISOn=1
        self.sTabDUTInfo.IsSample=0;SVAR.IsDebug=0
        print(self.sTabDUTInfo.IsSFISOn,self.sTabDUTInfo.IsSample)

    def SetIsSFISOFF(self):
        self.sTabDUTInfo.IsSFISOn=0
        self.sTabDUTInfo.IsSample=0;SVAR.IsDebug=0
        print(self.sTabDUTInfo.IsSFISOn,self.sTabDUTInfo.IsSample)


    # ***********************************************************************************************************************
    # ====================================================Signal & Event Bind Slot===========================================
    # ***********************************************************************************************************************
    def SignalBind(self):
        # Menu item event bind
        self.actionLoad_Setting_File.triggered.connect(self.LoadCfgTab)
        self.actionExit.triggered.connect(self.close)
        self.actionTest_Panel.triggered.connect(self.SetTestPanelTop)
        self.actionTest_Message.triggered.connect(self.SetTestMessageTop)

        self.actionZero_Ant.triggered.connect(self.Zero_Ant)
        self.actionZero_Con.triggered.connect(self.Zero_Con)
        self.actionZero_Pass.triggered.connect(self.Zero_Pass)
        self.actionZero_Fail.triggered.connect(self.Zero_Fail)

        self.action_About.triggered.connect(self.DevelopAbout)

        #SFIS Status Change event bind
        self.rb_SAMPLE.toggled.connect(self.SetIsSample)
        self.rb_SFISON.toggled.connect(self.SetIsSFISON)
        self.rb_SFISOFF.toggled.connect(self.SetIsSFISOFF)

        # Short Icon button event bind
        self.pb_Openfile.clicked.connect(self.LoadCfgTab)
        self.pb_Remote.clicked.connect(self.remote_Control)
        self.pb_Register.clicked.connect(self.local_Register)
        self.pb_Command.clicked.connect(self.dos_Window)
        self.pb_Devicemgr.clicked.connect(self.device_Manager)
        self.pb_Keyboard.clicked.connect(self.soft_KeyBoard)
        self.pb_PingTest.clicked.connect(self.ping_Detect)
        self.pb_Run.clicked.connect(self.begin_Test)
        # COM Port select bind event
        self.cbb_FIXCOM.currentIndexChanged.connect(self.FIXCOMSelectChanged)
        self.cbb_DUTCOM.currentIndexChanged.connect(self.DUTCOMSelectChanged)

        # Project Name Panel setup rightclick menu
        self.lb_ProjectName.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lb_ProjectName.customContextMenuRequested.connect(self.RightMenu)  ##开放右键策略

        # bind signal connect slot here!!
        self.signal_updateStation.connect(self.Slot_UpdateStationName)  # 33!!通过connect方法连接信号与槽函数或者可调用对象。
        self.signal_addtestLog.connect(self.Slot_AddTestLog)
        self.signal_sfcRouterChk.connect(self.Slot_SFCRoutingCheck)
        self.signal_popNotice.connect(self.Slot_PopNotice)
        self.signal_testResultInsert.connect(self.Slot_TestResult_Insert)
        self.signal_testResultClear.connect(self.Slot_TestResult_Clear)
        self.signal_showStatus.connect(self.Slot_ShowStatus)

    def RightMenu(self, position):
        menu = QMenu(self)
        for station in self.sTabParam.Tab_stationList:
            menu.addAction(station)
        menu.triggered.connect(self.RightMenuSlot)  # 菜单选择Item时触发
        menu.exec_(self.lb_ProjectName.mapToGlobal(position))  # Qcursor.pos()  也可以
        # action = menu.exec_(self.lb_ProjectName.mapToGlobal(position))
        # quitAciton=menu.addAction("Quit")
        # if action==quitAciton:
        #     qApp.quit()

    def RightMenuSlot(self, act):
        self.sTabParam.Tab_chrStationName = act.text()
        self.signal_updateStation.emit(self.sTabParam.Tab_chrStationName)  # 44!!通过emit()方法发射信号。
        # self.lb_ProjectName.setText(self.sTabParam.Tab_chrProductName+' ['+self.sTabParam.Tab_chrStationName+"]")

    # 22！！定义槽函数，它有多个不同的输入参数。槽函数就是普通类中的函数或方法。
    def Slot_UpdateStationName(self, var):
        self.lb_ProjectName.setText(self.sTabParam.Tab_chrProductName + ' [' + var + "]")
        self.sTabParam.Tab_chrStationName = var
        self.cfgtab.set('General', 'stationname', str(self.sTabParam.Tab_chrStationName))
        with open("cfg.tab", 'w+') as f:
            self.cfgtab.write(f)

    def Slot_AddTestLog(self, strMsg):
        self.pTE_TestLog.appendPlainText(strMsg)
        # print(self.pTE_TestLog.toPlainText())    #获取plaintext控件内容
        pass

    def Slot_SFCRoutingCheck(self,SN):
        #need add sfc check code here!!!
        rez=0
        return rez
        pass

    def Slot_PopNotice(self,strMsg):
        QMessageBox.information(self,'Notice',strMsg,QMessageBox.Yes)
        SVAR.NoticeMessageYes = 1

    def FIXCOMSelectChanged(self):
        isInitOK = 0
        self.sTabParam.FIXCOMPort = (self.cbb_FIXCOM.currentText()).strip()
        print(self.sTabParam.FIXCOMPort)

        # init com port showed in cbb_FIXCOM
        try:
            self.FIXCOM = ComBasic(self.sTabParam.FIXCOMPort, 115200)
            isInitOK = 1
            self.FIXCOM.com_stop()
            self.FIXCOM.com_start()
            # self.FIXCOM.com_send('hello\r\n')
        except Exception as e:
            if isInitOK:
                self.FIXCOM.com_stop()
            QMessageBox.critical(self, 'warning', 'Error Open FIXTURE COM', QMessageBox.Yes | QMessageBox.Yes)
            self.cbb_FIXCOM.setStyleSheet('background-color:red;color:white')
            return
        QMessageBox.information(self, 'Notice', 'Init Fixture Com port OK~~')
        self.cbb_FIXCOM.setEnabled(False)
        self.cbb_FIXCOM.setStyleSheet('background-color:green;color:white')

    def DUTCOMSelectChanged(self):
        isInitOK = 0
        self.sTabParam.DUTCOMPort = (self.cbb_DUTCOM.currentText()).strip()
        print(self.sTabParam.DUTCOMPort)

        # init com port showed in cbb_DUTCOM
        try:
            self.DUTCOM = ComBasic(self.sTabParam.DUTCOMPort, 115200)
            isInitOK = 1
            self.DUTCOM.com_stop()
            self.DUTCOM.com_start()
            # self.DUTCOM.com_send('hello\r\n')
        except Exception as e:
            if isInitOK:
                self.DUTCOM.com_stop()
            QMessageBox.critical(self, 'warning', 'Error Open DUT COM', QMessageBox.Yes | QMessageBox.Yes)
            self.cbb_DUTCOM.setStyleSheet('background-color:red;color:white')
            return
        QMessageBox.information(self, 'Notice', 'Init DUT Com port OK~~')
        self.cbb_DUTCOM.setEnabled(False)
        self.cbb_DUTCOM.setStyleSheet('background-color:green;color:white')
        pass


    def Slot_TestResult_Insert(self,lst_TestResult):     #消息槽，单条测试项目的信息(list)，追加到QTableWiget中
        SVAR.CurrentTestItemRow=self.tw_TestResult.rowCount()
        # print(SVAR.CurrentTestItemRow,self.tw_TestResult.rowCount())
        self.tw_TestResult.insertRow(SVAR.CurrentTestItemRow)
        for i in range(len(lst_TestResult)):
            if i==0 :
                item=QTableWidgetItem(str(lst_TestResult[i]+1))   #只是为了好看，序号从1开始，(默认从0开始)
            else:
                item=QTableWidgetItem(str(lst_TestResult[i]))
            # if lst_TestResult[5] == 'FAIL':
            #     item.setBackground(QColor(255,0,0))      #红FAIL
            # else:
            #     item.setBackground(QColor(152,251,152))  #绿PASS
            item.setBackground(QColor(255,0,0) if lst_TestResult[5] == 'FAIL' else QColor(202,251,202))
            self.tw_TestResult.setItem(SVAR.CurrentTestItemRow,i,item)
        SVAR.CurrentTestItemRow=self.tw_TestResult.rowCount()   #再计算一次总行数
        #设置所有单元格内容居中对齐
        for i in range(SVAR.CurrentTestItemRow):     #row index 行数序号
             for j in range(6):   #column index列数序号
                       self.tw_TestResult.item(i,j).setTextAlignment(Qt.AlignCenter)
        pass

    def Slot_TestResult_Clear(self):
        #清除所有TestResult的记录
        rowTestResult=self.tw_TestResult.rowCount()
        for rp in range(0,rowTestResult)[::-1]:
            self.tw_TestResult.removeRow(rp)
        SVAR.CurrentTestItemRow=0
        #clear other PlainTextEdit
        self.pte_SFISLog.setPlainText('')
        self.pte_DUTLog.setPlainText('')
        self.pTE_SFCLog.setPlainText('')
        self.pTE_TestLog.setPlainText('')

    def Slot_ShowStatus(self,enumValue):
        if enumValue==SVAR.DUTStatusMode.Run:
            self.lb_ErrorCode.setText('ErrorCode:')
            self.sTabDUTInfo.IsRunStatus=1
            self.sTabDUTInfo.iStartTime=int(time.time())    #取当前时间戳的整数
            print('start time : %d '%self.sTabDUTInfo.iStartTime)
            self.sTabDUTInfo.chrErrorCode=''
            self.lcd_TestTime.display('00:00:00')
            self.lb_TestStatus.setStyleSheet('background-color: rgb(255, 255, 0)')
            self.lb_TestStatus.setText('Running...')
            self.signal_testResultClear.emit()
            self.lb_ProjectName.customContextMenuRequested.disconnect(self.RightMenu)  ##关闭右键策略
            self.pb_Run.clicked.disconnect(self.begin_Test)   #关闭点击开始事件
            return
        if enumValue==SVAR.DUTStatusMode.Pass:
            self.lb_ErrorCode.setText('ErrorCode:')
            self.sTabDUTInfo.IsRunStatus=0
            self.sTabDUTInfo.iEndTime=int(time.time())    #取当前时间戳的整数
            print('end time : %d '%self.sTabDUTInfo.iEndTime)
            self.UpdatePCInfo('Test Cycle Time','{0} s'.format(self.sTabDUTInfo.iEndTime-self.sTabDUTInfo.iStartTime))
            self.signal_addtestLog.emit("====> Total Test Time: %d s"%(self.sTabDUTInfo.iEndTime-self.sTabDUTInfo.iStartTime))
            self.sTabDUTInfo.IsSFISOn=0
            if self.sTabDUTInfo.IsSFISOn:
                if self.sTabDUTInfo.IsPassDCTResponse==1:
                    self.lb_TestStatus.setStyleSheet('background-color: rgb(0, 255, 0)')
                    self.lb_TestStatus.setText('Pass')
                else:
                    self.lb_TestStatus.setStyleSheet('background-color: rgb(255, 105, 180)')
                    self.lb_TestStatus.setText('SFC REPLY NG')
            else:
                self.lb_TestStatus.setStyleSheet('background-color: rgb(0, 255, 0)')
                self.lb_TestStatus.setText('Pass')
            self.UpdatePassRate()
            self.sTabDUTInfo.chrErrorCode=''
            self.lcd_TestTime.display('00:00:57')
            self.lb_ProjectName.customContextMenuRequested.connect(self.RightMenu)  ##恢复右键策略
            self.pb_Run.clicked.connect(self.begin_Test)   #恢复点击开始事件
            return
        if enumValue==SVAR.DUTStatusMode.Fail:
            self.lb_ErrorCode.setText('ErrorCode:%s'%self.sTabDUTInfo.chrErrorCode)
            self.sTabDUTInfo.IsRunStatus=0
            self.sTabDUTInfo.iEndTime=int(time.time())    #取当前时间戳的整数
            print('end time : %d '%self.sTabDUTInfo.iEndTime)
            self.UpdatePCInfo('Test Cycle Time','{0} s'.format(self.sTabDUTInfo.iEndTime-self.sTabDUTInfo.iStartTime))
            self.signal_addtestLog.emit("====> Total Test Time: %d s"%(self.sTabDUTInfo.iEndTime-self.sTabDUTInfo.iStartTime))
            self.sTabDUTInfo.IsSFISOn=0
            if self.sTabDUTInfo.IsSFISOn:
                if self.sTabDUTInfo.IsPassDCTResponse==1:
                    self.lb_TestStatus.setStyleSheet('background-color: rgb(0, 255, 0)')
                    self.lb_TestStatus.setText('Pass')
                else:
                    self.lb_TestStatus.setStyleSheet('background-color: rgb(255, 105, 180)')
                    self.lb_TestStatus.setText('SFC REPLY NG')
            else:
                self.lb_TestStatus.setStyleSheet('background-color: rgb(255, 0, 0)')
                self.lb_TestStatus.setText('Fail')
            self.UpdateFailRate()
            self.sTabDUTInfo.chrErrorCode=''
            self.lcd_TestTime.display('00:00:36')
            self.lb_ProjectName.customContextMenuRequested.connect(self.RightMenu)  ##恢复右键策略
            self.pb_Run.clicked.connect(self.begin_Test)   #恢复点击开始事件
            return
        if enumValue==SVAR.DUTStatusMode.StandBy:
            self.lb_ErrorCode.setText('ErrorCode:')
            self.sTabDUTInfo.IsRunStatus=0
            self.sTabDUTInfo.iStartTime=0
            self.sTabDUTInfo.iEndTime=0    #取当前时间戳的整数
            self.lcd_TestTime.display('00:00:00')
            self.lb_TestStatus.setStyleSheet('background-color: #40E0D0')
            self.lb_TestStatus.setText('StandBy')
            self.lb_ProjectName.customContextMenuRequested.connect(self.RightMenu)  ##恢复右键策略
            self.pb_Run.clicked.connect(self.begin_Test)   #恢复点击开始事件
            return
        if enumValue==SVAR.DUTStatusMode.ReTest:
            self.lb_ErrorCode.setText('ErrorCode:')
            self.sTabDUTInfo.IsRunStatus=1
            self.sTabDUTInfo.iStartTime=0
            self.sTabDUTInfo.iEndTime=0    #取当前时间戳的整数
            self.lcd_TestTime.display('00:00:00')
            self.lb_TestStatus.setStyleSheet('background-color: #9932CC')
            self.lb_TestStatus.setText('ReTest')
            self.lb_ProjectName.customContextMenuRequested.connect(self.RightMenu)  ##恢复右键策略
            self.pb_Run.clicked.connect(self.begin_Test)   #恢复点击开始事件
            return
        if enumValue==SVAR.DUTStatusMode.WaitSFC:
            self.lb_ErrorCode.setText('ErrorCode:')
            self.sTabDUTInfo.IsRunStatus=0
            self.sTabDUTInfo.iStartTime=0
            self.sTabDUTInfo.iEndTime=0    #取当前时间戳的整数
            self.lcd_TestTime.display('00:00:00')
            self.lb_TestStatus.setStyleSheet('background-color: #4682B4')
            self.lb_TestStatus.setText('WaitSFC')
            self.lb_ProjectName.customContextMenuRequested.connect(self.RightMenu)  ##恢复右键策略
            self.pb_Run.clicked.connect(self.begin_Test)   #恢复点击开始事件
            return
        if enumValue==SVAR.DUTStatusMode.BootUp:
            self.lb_ErrorCode.setText('ErrorCode:')
            self.sTabDUTInfo.IsRunStatus=1
            self.sTabDUTInfo.iStartTime=0
            self.sTabDUTInfo.iEndTime=0    #取当前时间戳的整数
            self.lcd_TestTime.display('00:00:00')
            self.lb_TestStatus.setStyleSheet('background-color: #48D1CC')
            self.lb_TestStatus.setText('BootUp......')
            self.lb_ProjectName.customContextMenuRequested.connect(self.RightMenu)  ##恢复右键策略
            self.pb_Run.clicked.connect(self.begin_Test)   #恢复点击开始事件
            return



    # ***********************************************************************************************************************
    # ====================================================功能性函数     =====================================================
    # ***********************************************************************************************************************
    # 非租塞延迟(毫秒级)
    def delay_run(self, ms):
        ms = ms / 2  #不知道为什么必须除以 2 ，才能和设置的毫秒数相符
        while (ms > 0):
            pygame.time.wait(1)
            QApplication.processEvents()
            ms -= 1

    def LoadCfgTab(self):
        fileSelect, fileType = QFileDialog.getOpenFileName(self, '选取配置文件', os.getcwd(), 'Tab File(*.tab)')
        if fileSelect == '':
            return
        else:
            self.getCfgSetting()
        pass

    def SetCfgTabValue(self,strSection,strKey,value):   #更改cfgtab文件中键值
        self.cfgtab.set(strSection, strKey, str(value))
        with open("cfg.tab", 'w+') as f:
             self.cfgtab.write(f)


    def CheckConnCounter(self):
        div_con=divmod(self.sTabParam.Tab_CountCon,self.sTabParam.Tab_ConMAX)
        if div_con[0]>=1 and div_con[1]>=0:
            QMessageBox.warning(self, 'Warning', 'Please replace Connector', QMessageBox.Yes | QMessageBox.Yes)
            return False
        div_ant=divmod(self.sTabParam.Tab_CountAnt,self.sTabParam.Tab_AntMAX)
        if div_ant[0]>=1 and div_ant[1]>=0:
            QMessageBox.warning(self, 'Warning', 'Please replace Anternna', QMessageBox.Yes | QMessageBox.Yes)
            return False
        self.sTabParam.Tab_CountAnt+=1;self.SetCfgTabValue('Cable','antcounter',self.sTabParam.Tab_CountAnt);self.UpdatePCInfo('RF  Probe Count',self.sTabParam.Tab_CountAnt)
        self.sTabParam.Tab_CountCon+=1;self.SetCfgTabValue('Cable','concounter',self.sTabParam.Tab_CountCon);self.UpdatePCInfo('Connector Count',self.sTabParam.Tab_CountCon)
        return True

    def UpdatePassRate(self):
        self.sTabParam.Tab_Pass+=1
        self.cfgtab.set('Result', 'pass', str(self.sTabParam.Tab_Pass))
        with open("cfg.tab", 'w+') as f:
             self.cfgtab.write(f)
        self.UpdatePCInfo('Total PASS Qty',self.sTabParam.Tab_Pass)
        self.UpdatePCInfo('F.P.Y',"{:.2f} %".format(self.sTabParam.Tab_Pass * 100.00 / (self.sTabParam.Tab_Pass + self.sTabParam.Tab_Fail)))
        pass

    def UpdateFailRate(self):
        self.sTabParam.Tab_Fail+=1
        self.cfgtab.set('Result', 'fail', str(self.sTabParam.Tab_Fail))
        with open("cfg.tab", 'w+') as f:
             self.cfgtab.write(f)
        self.UpdatePCInfo('Total FAIL Qty',self.sTabParam.Tab_Fail)
        self.UpdatePCInfo('F.P.Y',"{:.2f} %".format(self.sTabParam.Tab_Pass * 100.00 / (self.sTabParam.Tab_Pass + self.sTabParam.Tab_Fail)))
        pass


    def OnPass(self):
        pass

    def OnFail(self):
        pass

    def CheckSNRule(self,enumValue):
        if enumValue==SVAR.TypeSN.PSN:
            if len(self.sTabDUTInfo.PSN)!=self.sTabParam.Tab_SNLength:
                self.sTabDUTInfo.chrErrorCode='[{0}] {1}'.format(ErrorCode.SNLEN0.get_code(),ErrorCode.SNLEN0.get_msg())
                return False
        elif enumValue==SVAR.TypeSN.CSN:
            if len(self.sTabDUTInfo.CSN)!=self.sTabParam.Tab_SNLength:
                self.sTabDUTInfo.chrErrorCode='[{0}] {1}'.format(ErrorCode.SNLEN0.get_code(),ErrorCode.SNLEN0.get_msg())
                return False
        return True

    def CheckMACRule(self,strMAC):
        if len(strMAC)!=12:
            self.sTabDUTInfo.chrErrorCode='[{0}] {1}'.format(ErrorCode.MACREE.get_code(),ErrorCode.MACREE.get_msg())
            return False
        for i in range(12):
            if strMAC[i]<'0' or strMAC[i]>'F':
                self.sTabDUTInfo.chrErrorCode='[{0}] {1}'.format(ErrorCode.MACREE.get_code(),ErrorCode.MACREE.get_msg())
                return False
        return True

    def CheckIMEIRule(self,strIMEI):
        if len(strIMEI)!=15:
            self.sTabDUTInfo.chrErrorCode='[{0}] {1}'.format(ErrorCode.IMEIEE.get_code(),ErrorCode.IMEIEE.get_msg())
            return False
        for i in range(15):
            if strMAC[i]<'0' or strMAC[i]>'9':
                self.sTabDUTInfo.chrErrorCode='[{0}] {1}'.format(ErrorCode.IMEIEE.get_code(),ErrorCode.IMEIEE.get_msg())
                return False
        return True

    def CheckMEIDRule(self,strMEID):
        if len(strMEID)!=14:
            self.sTabDUTInfo.chrErrorCode='[{0}] {1}'.format(ErrorCode.MEIDEE.get_code(),ErrorCode.MEIDEE.get_msg())
            return False
        for i in range(14):
            if strMAC[i]<'0' or strMAC[i]>'F':
                self.sTabDUTInfo.chrErrorCode='[{0}] {1}'.format(ErrorCode.MEIDEE.get_code(),ErrorCode.MEIDEE.get_msg())
                return False
        return True


    #指定时间内发送strSend,期望获取到strExpRec，返回值是True/False
    def Pipe_SendCmdExpectStr(self,strSend,strExpRec,iTimeOver):
        bRet = False
        beginTime=int(time.time())
        p = subprocess.Popen(strSend, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        while p.poll() is None :  # Popen.poll() 检查子进程是否已结束
            endTime=int(time.time())
            if (endTime-beginTime)>=iTimeOver:
                p.terminate()
                self.sTabDUTInfo.chrErrorCode='[{0}] {1}'.format(ErrorCode.CMDTIM.get_code(),ErrorCode.CMDTIM.get_msg())
                break
            line = p.stdout.readline().strip().decode('gbk')
            if line:  # 不为空
                # print('{}'.format(line))    # print('Pipe output: [{}]'.format(line))
                self.signal_addtestLog.emit('{}'.format(line))
                if strExpRec in line: bRet = True
        print(bRet)
        print('Pipe success') if p.returncode == 0 else print('Pipe failed')
        return bRet and p.returncode==0

    #指定时间内发送strSend,返回值是内容List
    def Pipe_SendCmdGetRetStr(self,strSend,iTimeOver=3):
        sRet=[]
        beginTime=int(time.time())
        try:
            p = subprocess.Popen(strSend, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #注意此时Shell的值如果True,就不能正常显示结果在GUI
        except (FileNotFoundError, OSError) as e:   #命令不存在(如adb未装/不在PATH)时, 写入测试日志而不是抛线程异常
            self.signal_addtestLog.emit('[CMD ERROR] %s: %s' % (e, strSend))
            print('[CMD ERROR]', e, strSend)
            return sRet
        while p.poll() is None :  # Popen.poll() 检查子进程是否已结束
            endTime=int(time.time())
            if (endTime-beginTime)>=iTimeOver:
                p.terminate()
                self.sTabDUTInfo.chrErrorCode='[{0}] {1}'.format(ErrorCode.CMDTIM.get_code(),ErrorCode.CMDTIM.get_msg())
                break
            line = p.stdout.readline().strip().decode('gbk')
            if line:  # 不为空
                print('{}'.format(line))    # print('Pipe output: [{}]'.format(line))
                self.signal_addtestLog.emit('{}'.format(line))
                sRet.append(line)
        # print(sRet)
        return sRet


    # ***********************************************************************************************************************
    # ====================================================Project 测试调用=====================================================
    # ***********************************************************************************************************************
    def PTTest_ProjectName(self):
        if not self.CheckSNRule(SVAR.TypeSN.PSN):
            self.signal_testResultInsert.emit([SVAR.CurrentTestItemRow,'CheckSNRule',self.sTabDUTInfo.PSN,'','','FAIL'])
            return False
        else:
            self.signal_testResultInsert.emit([SVAR.CurrentTestItemRow,'CheckSNRule',self.sTabDUTInfo.PSN,'','','PASS'])





    def FTTest_ProjectName(self):
        return True

    def RunInTest_ProjectName(self):
        return True

    # ***********************************************************************************************************************
    # ====================================================Threading 调用=====================================================
    # ***********************************************************************************************************************

    def beginTestThread(self):
        # if int(self.sTabParam.Tab_IsDialogBeforeTest):
        #     self.signal_popNotice.emit('Please plug in device!')
        #     while (not SVAR.NoticeMessageYes):
        #         QApplication.processEvents()
        #         print('waiting your select--------------')
        #         self.delay_run(500)
        #     SVAR.NoticeMessageYes=0

        print('==============Only Thread Func Test Here~============')
        self.pTE_TestLog.setPlainText('')
        self.signal_showStatus.emit(SVAR.DUTStatusMode.Run)
        if not SVAR.IsDebug:
            if self.sTabParam.Tab_chrProductName=='SBB-115':
                if self.sTabParam.Tab_chrStationName=='PT' and not self.PTTest_ProjectName():
                    self.OnFail()
                    self.signal_showStatus.emit(SVAR.DUTStatusMode.Fail)
                    return
                if self.sTabParam.Tab_chrStationName=='FT' and not self.FTTest_ProjectName5():
                    self.OnFail()
                    self.signal_showStatus.emit(SVAR.DUTStatusMode.Fail)
                    return
                if self.sTabParam.Tab_chrStationName=='RunIn' and not self.RunInTest_ProjectName():
                    self.OnFail()
                    self.signal_showStatus.emit(SVAR.DUTStatusMode.Fail)
                    return
            #Add new project test here~~
            elif self.sTabParam.Tab_chrProductName=='XXXXXX':
                pass
            elif self.sTabParam.Tab_chrProductName=='YYYYYY':
                pass
            else:
                QMessageBox.critical(self, 'Warning', 'Others Project SKU ~~~Cancel', QMessageBox.Yes | QMessageBox.Yes)
                return
        else:
            self.delay_run(2000)
            # self.Pipe_SendCmdExpectStr('ping 192.168.1.92','0%',6)
            self.Pipe_SendCmdGetRetStr('adb shell cd sdcard&&ls&&cd ../sys&&ls',6)
            self.Pipe_SendCmdGetRetStr('adb devices',6)
            # self.OnPass()
            self.signal_showStatus.emit(SVAR.DUTStatusMode.Pass)




    def begin_Test(self):
        print('==============Begin Test============')
        #评估版本可打开下面代码
        # if self.sTabParam.Tab_Pass >= 300:
        #     QMessageBox.about(self,'Notice','Evaluation version!Please user Release Version\n')
        #     QApplication.closeAllWindows()
        #     exit(1)   #非正常退出
        if self.sTabDUTInfo.IsRunStatus:
           self.DbSFCErrInfoAdd('Test Program is running...')
           return
        if int(self.sTabParam.Tab_IsDialogBeforeTest):
            reply=QMessageBox.information(self,'Notice','Please Insert DUT And Power On~',QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
            if reply!=QMessageBox.Yes:
                self.signal_showStatus.emit(SVAR.DUTStatusMode.StandBy)
                return
            else:
                if not self.CheckConnCounter(): return   #有对话窗体不能放到Thread中运行

        bThread=Thread(target=self.beginTestThread,daemon=True)
        bThread.start()
        # bThread.join()

    class pingDetectTaskHandler(Thread):
        def run(self):
            # 使用ShellExecute函数，就相当于在资源管理器中双击文件图标一样，系统会打开相应的应用程序执行操作
            win32api.ShellExecute(0, 'open', 'ping.exe', '192.168.1.1', '-t', 3)  # 0表示不显示，1表示正常显示，2表示最小化，3表示最大化

    def ping_Detect(self):
        self.pingDetectTaskHandler(daemon=True).start()

    class softKeyBoardTaskHandler(Thread):
        def run(self):
            kb_hwnd = WHC.findWindowHandler('屏幕键盘')
            if (kb_hwnd == None):
                # print(os.getenv("windir"))
                os.system('osk.exe')
            else:
                WHC.setWindowStatus(kb_hwnd)

    def soft_KeyBoard(self):
        self.softKeyBoardTaskHandler(daemon=True).start()

    class dosWindowTaskHandler(Thread):
        def run(self):
            win32api.ShellExecute(0, 'open', 'cmd.exe', '', '', 1)

    def dos_Window(self):
        self.dosWindowTaskHandler(
            daemon=True).start()  # 如果需要等待线程执行使用join，这样主线程会阻塞  .setDaemon(True)在start前设置，可以保证在主线程终止时，子线程也终止

    class deviceManagerTaskHandler(Thread):
        def run(self):
            dev_hwnd = WHC.findWindowHandler('设备管理器')
            if (dev_hwnd == None):
                os.system('devmgmt.msc')
            else:
                WHC.setWindowStatus(dev_hwnd)

    def device_Manager(self):
        self.deviceManagerTaskHandler(daemon=True).start()

    class remoteControlTaskHandler(Thread):
        def run(self):
            # subprocess.getstatusoutput('mstsc.exe')  #方法一：保存可执行程序中的打印值和主函数的返回值，但不会将执行过程中要打印的内容打印出来
            mstsc_hwnd = WHC.findWindowHandler('远程桌面连接')
            if (mstsc_hwnd == None):
                os.system('mstsc.exe')  # 方法二：
            else:
                WHC.setWindowStatus(mstsc_hwnd)
                # tkinter.messagebox.showinfo('提示', '远程控制窗体开启')

    def remote_Control(self):
        # self.pb_Remote.setStyleSheet("QPushButton{background:transparent}")
        self.remoteControlTaskHandler(daemon=True).start()

    class localRegisterTaskHandler(Thread):
        def run(self):
            reg_hwnd = WHC.findWindowHandler('注册表编辑器')
            if (reg_hwnd == None):
                subprocess.getstatusoutput(
                    os.getenv("windir") + '\\regedit.exe')  # os.getenv('windir') 获取本系统中windows目录绝对路径
            else:
                WHC.setWindowStatus(reg_hwnd)

    def local_Register(self):
        self.localRegisterTaskHandler(daemon=True).start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MFGWindow()
    myWin.show()
    sys.exit(app.exec_())
