#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
#-*-coding:utf-8 -*-

#先安装如下
#pip3 install wmi pypiwin32


import sys
from wmi import WMI
import io,time,socket,json
import platform
import uuid
import serial                   #pip install serial
import serial.tools.list_ports    #pip install pyserial

class HardWareInfo(object):

    def __init__(self):
        self.c=WMI()
        pass
    def __del__(self):
        pass
#CPU信息
    def get_CPU(self):
        cpumsg=[]
        for cpu in self.c.Win32_Processor():
            tmpmsg={}
            tmpmsg['name']=cpu.Name
            tmpmsg['systemName']=cpu.SystemName
            tmpmsg['cpuClock']=cpu.MaxClockSpeed
            tmpmsg['cpuDataWidth']=cpu.DataWidth
            tmpmsg['serial number']=cpu.ProcessorID.strip()
            tmpmsg['coreNum']=cpu.NumberOfCores
            tmpmsg['numofLogicalProcessors']=cpu.NumberOfLogicalProcessors
            tmpmsg['cpuPercent']=cpu.loadPercentage
            tmpmsg['timestamp']= time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
            tmpmsg['Manufacturer']=cpu.Manufacturer  #处理器的制造商
            cpumsg.append(tmpmsg)
        print(cpumsg)
        return cpumsg
        pass

#Memory信息
    def get_Memory(self):
        memmsg=[]
        for mem in self.c.Win32_PhysicalMemory():
            tmpmsg = {}
            tmpmsg['Tag唯一标识符的物理存储器'] = mem.Tag
            tmpmsg['Capacity'] = str(int(mem.Capacity)/1024/1024/1024)+'GB'
            tmpmsg['SerialNumber编号'] = mem.SerialNumber.strip()  #编号
            tmpmsg['UUID'] = mem.qualifiers['UUID'][1:-1]
            tmpmsg['Manufacturer内存生产商']=mem.Manufacturer.strip()  #内存生产商
            tmpmsg['Name']=mem.Name   #物理内存
            tmpmsg['PartNumber零件编号']=mem.PartNumber  #零件编号
            tmpmsg['Speed速率']=str(mem.Speed)+'Mhz'     #运行频率
            memmsg.append(tmpmsg)
        print(memmsg)
        return memmsg

#Graphic信息
    def get_Graphic(self):
        grapicmsg=[]
        for v in self.c.Win32_VideoController():
            tmpmsg={}
            tmpmsg['caption描述']=v.Caption
            # tmpmsg['AdapterRAM显存容量']=str.format('%.2f GB'%((v.AdapterRAM)/(1024**3)))
            tmpmsg['AdapterRAM显存容量']=str(round(((v.AdapterRAM)/(1024**3)),3))+'GB'
            tmpmsg['Resolution分辨率']=str(v.CurrentHorizontalResolution)+'*'+str(v.CurrentVerticalResolution)
            tmpmsg['DriverVersion驱动版本号']=v.DriverVersion
            grapicmsg.append(tmpmsg)
        print(grapicmsg)
        return grapicmsg

#网络信息
    def get_Netware(self):
        netmsg=[]
        for n in self.c.Win32_NetworkAdapter():
            mactmp = n.MACAddress
            if mactmp and len(mactmp.strip()) > 5:   #mactmp不等于None
                tmpmsg = {}
                tmpmsg['ProductName'] = n.ProductName  #网络适配器的产品名称
                tmpmsg['NetConnectionID'] = n.NetConnectionID   #网络连接的名称出现在网络连接控制面板程序
                tmpmsg['NetConnectionStatus']= n.NetConnectionStatus #网络适配器连接至网络的状态     2 : Connected
                tmpmsg['MACAddress'] = n.MACAddress
                tmpmsg['Speed速率']=(n.Speed)     #-估计当前带宽比特每秒
                tmpmsg['AdapterType']=n.AdapterType
                netmsg.append(tmpmsg)
        print(netmsg)
        return netmsg

    def get_network_info(self):
      network = []
      for nw in self.c.Win32_NetworkAdapterConfiguration (IPEnabled=1):
       network.append(
        {
         "MAC": nw.MACAddress,
         "ip": nw.IPAddress
        }
       )
      print("Network info:", json.dumps(network, sort_keys=True,indent=4))   #调整输出的JSON格式
      return network

    def get_mac_address(self):
        self.mac=uuid.UUID(int = uuid.getnode()).hex[-12:]   #Get the hardware address as a 48-bit positive integer
        # return ":".join([mac[e:e+2] for e in range(0,11,2)]).upper()
        return "".join([self.mac[e:e+2] for e in range(0,11,2)]).upper()


#电池信息
    def get_Battery(self):
        bIsHaveBattery=False
        for b in self.c.Win32_Battery():
            bIsHaveBattery=True
        print('Battery Is ',bIsHaveBattery)
        return bIsHaveBattery

#主板信息
    def get_MotherBoard(self):
        boards = []
        for board_id in self.c.Win32_BaseBoard():
            tmpmsg = {}
            tmpmsg['UUID'] = board_id.qualifiers['UUID'][1:-1]   #主板UUID,有的主板这部分信息取到为空值，ffffff-ffffff这样的
            tmpmsg['SerialNumber'] = board_id.SerialNumber                #主板序列号
            tmpmsg['Manufacturer'] = board_id.Manufacturer       #主板生产品牌厂家
            tmpmsg['Product'] = board_id.Product                 #主板型号
            tmpmsg['Description'] = board_id.Description                 #-对象的描述（底板）
            boards.append(tmpmsg)
        print(boards)
        return boards

#BIOS信息
    def get_BiosInfo(self):
        biosmsg=[]
        for b in self.c.Win32_Bios():
            tmpmsg={}
            # tmpmsg['BiosCharacteristics']=b.BiosCharacteristics #BIOS特征码
            tmpmsg['Version']=b.Version  #BIOS版本
            tmpmsg['Manufacturer'] =b.Manufacturer.strip()                 #BIOS固件生产厂家
            # tmpmsg['ReleaseDate'] = b.ReleaseDate                   #BIOS释放日期
            tmpmsg['SMBIOSBIOSVersion'] = b.SMBIOSBIOSVersion       #系统管理规范版本
            tmpmsg['BIOSVersion'] = b.BIOSVersion       #系统管理规范版本
            tmpmsg['Caption'] = b.Caption       #系统管理规范版本
            biosmsg.append(tmpmsg)
        print(biosmsg)
        return biosmsg

#HardDisk信息
    def get_HDDInfo(self):
        HDDmsg=[]
        for h in self.c.Win32_DiskDrive():
            tmpmsg={}
            tmpmsg['SerialNumber'] = h.SerialNumber.strip()   #由制造商分配的号,硬盘序列号    #同 print(self.c.Win32_PhysicalMedia()[0].SerialNumber.lstrip().rstrip())
            tmpmsg['DeviceID'] = h.DeviceID  #磁盘驱动器与系统中的其他设备的唯一标识符
            tmpmsg['Caption'] = h.Caption #对象的序列号
            tmpmsg['Size'] = str(round(int(h.Size)/(1024**3),2))+'GB'   #磁盘大小
            tmpmsg['UUID'] = h.qualifiers['UUID'][1:-1]
            tmpmsg['Description']=h.Description
            tmpmsg['TotalCylinders柱面总数']=h.TotalCylinders   #物理磁盘驱动器上柱面总数
            tmpmsg['TotalHeads磁头总数']=h.TotalHeads   #磁盘驱动器上磁头总数
            tmpmsg['TotalSectors扇区总数']=h.TotalSectors   #物理磁盘驱动器上的扇区总数
            tmpmsg['Manufacturer']=h.Manufacturer
            HDDmsg.append(tmpmsg)
        print(HDDmsg)
        return HDDmsg

#Keyboard& mouse
    def get_KeyBoardInfo(self):
        KBmsg=[]
        for kb in self.c.Win32_Keyboard():
            tmpmsg={}
            tmpmsg['caption描述']=kb.Caption
            tmpmsg['CreationClassName']=kb.CreationClassName
            tmpmsg['Description']=kb.Description
            tmpmsg['ErrorDescription']=kb.ErrorDescription
            tmpmsg['Status']=kb.Status
            KBmsg.append(tmpmsg)
        print(KBmsg)
        return KBmsg

    def get_MouseInfo(self):   #当插入USB鼠标后，会有两个鼠标设备dict
        mmsg=[]
        for kb in self.c.Win32_PointingDevice():
            tmpmsg={}
            tmpmsg['caption描述']=kb.Caption
            tmpmsg['CreationClassName']=kb.CreationClassName
            tmpmsg['Description']=kb.Description
            tmpmsg['Name']=kb.Name
            tmpmsg['Manufacturer']=kb.Manufacturer
            tmpmsg['Status']=kb.Status
            mmsg.append(tmpmsg)
        print(mmsg)
        return mmsg

#打印机信息
    def get_PrinterInfo(self):
        pmsg=[]
        for p in self.c.Win32_Printer():
            tmpmsg={}
            tmpmsg['caption描述']=p.Caption
            tmpmsg['Comment']=p.Comment
            tmpmsg['CurrentPaperType']=p.CurrentPaperType
            tmpmsg['PortName']=p.PortName  # LPT1:, LPT2:, LPT3:  or IPAddress
            tmpmsg['DriverName']=p.DriverName
            tmpmsg['Name']=p.Name
            pmsg.append(tmpmsg)
        print(pmsg)
        return pmsg


#当前进程信息
    def get_RunningProcess(self):
        process=[]
        for p in self.c.Win32_Process():
            process.append({p.Name:p.ProcessId})    #list加入json类型字典
        print(process)
        print('Total Process Numbers Is :',len(process))
        for ss in process:
            print(ss.keys())  #只获取字典的keys   对应值ss.values()
        return process


    def get_SerialComPort(self):
        comList=[]
        comport_list=list(serial.tools.list_ports.comports())
        if(len(comport_list)<=0):
            print('no Serial Com Port be found')
        else:
            for i in comport_list:
                # print(i[0])
                comList.append(i[0])
        return comList



if __name__ == '__main__':
    # sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
    print(u'系统操作名称:'+platform.platform()[:-len(platform.version())+1])
    print(u'操作系统版本号:'+platform.version())
    print(u'操作系统的位数:'+platform.architecture()[0])
    print(u'HostName:'+socket.getfqdn(socket.gethostname()))
    print('IPAddress:'+socket.gethostbyname(socket.getfqdn(socket.gethostname())))


    mHW=HardWareInfo()
    print(mHW.get_SerialComPort())

    # print('本机物理地址:'+mHW.get_mac_address())
    # print('CPU Type:',mHW.get_CPU()[0]['name'])
    # print('CPU Freq:',mHW.get_CPU()[0]['cpuClock'],'Mhz')

    # mHW.get_CPU()
    # mHW.get_Memory()
    # mHW.get_Graphic()
    # mHW.get_Netware()
    # mHW.get_network_info()
    # mHW.get_Battery()
    # mHW.get_MotherBoard()
    # mHW.get_BiosInfo()
    # mHW.get_HDDInfo()
    # print(mHW.get_HDDInfo()[0]['SerialNumber'])
    # mHW.get_RunningProcess()

    # mHW.get_KeyBoardInfo()
    # mHW.get_MouseInfo()
    # mHW.get_PrinterInfo()






