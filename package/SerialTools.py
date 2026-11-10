#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
#-*-coding:utf-8 -*-

#!/usr/bin/python
from serial import Serial  # 讀串口的模塊
from time import sleep
import os
import datetime


class otSerial(Serial):
    """Extended Serial Class with new functions to simplify scripting communication"""

    def send_expect(self, send_string, expect_string, timeout):  # 發送指令，期望在時間內獲取的字符串
        """Sends the input and continues to read until the output string is found
        if the output is not found within the timeout period than the function throws
        a StandardError exception"""
        self.received_string = ""  # 接受到的字符串，清除buffer
        self.write(send_string)  # 發送的字符串
        if len(expect_string) == 0:
            return "";
        self.received_string = ""
        start_time = datetime.datetime.now()  # 格式為 2013-12-19 14:28:00.562000
        current_time = datetime.datetime.now()
        time_delta = current_time - start_time
        while self.received_string.find(
                expect_string) == -1 and time_delta.total_seconds() <= timeout:  # buffer中沒有指定字符串，並且小於指定時間   #total_seconds()是所有秒數總和
            self.timeout = 1
            # print "Reading in Loop... time_delta.total_seconds =" + str(time_delta.total_seconds())
            self.received_string += self.read(1)  # 一位一位的讀取追加
            current_time = datetime.datetime.now()
            time_delta = current_time - start_time
        # OK, we either exceeeded or timeout or found our string...
        loc = self.received_string.find(expect_string)
        if (loc == -1):
            return ("Expect String [" + expect_string + "] was not found within [" + str(timeout) + "] Seconds")
        else:
            return self.received_string
        pass

    def send_wait(self, send_string, timeout_sec):  # 發送指令，等待指定時間
        """This function sends the given string, waits the specified time, and returns
        the entire receive buffer"""
        self.write(send_string)
        sleep(timeout_sec)
        return self.read(self.inWaiting())  # 監聽返回字符串的長度，一次性讀取返回值

    @staticmethod
    def reset_linux_serial_device_permissions(device_name, root_password):  # 重置許可
        """This static method will reset the permissions on a linux serial port for access"""
        print("Resetting Permissions")
        command = "echo google | sudo -S chmod 777 " + device_name  # 755代表用戶對文件有讀，寫，執行的權限    777代表，user,group,others都有讀寫和可執行權限
        os.system(command)  # 執行一條指令
        pass

    def send_expect_throttled(self, send_string, expect_string, timeout, millisecond_delay):
        """Same function as send_expect but throttles the write speed for slower devices that can't handle long strings"""
        self.received_string = ""
        delay = millisecond_delay / 1000.0
        self.flushInput()  # 測試用，清除串口輸入數據
        for i in range(0, len(send_string)):
            self.write(send_string[i])  # 一個一個字符寫入
            sleep(delay)
            output = self.read(1)
        if len(expect_string) == 0:
            return ""
        self.received_string = ""
        buffer = self.read(1000)  # 讀取1000字符
        # OK, the first thing we do is automatically throw away anything
        # we wrote out since the commands are being echo'd back
        start_time = datetime.datetime.now()
        current_time = datetime.datetime.now()
        time_delta = current_time - start_time
        while self.received_string.find(expect_string) == -1 and time_delta.total_seconds() <= timeout:
            self.timeout = 1
            # print "Reading in Loop... time_delta.total_seconds =" + str(time_delta.total_seconds())
            self.received_string += self.read(1)
            current_time = datetime.datetime.now()
            time_delta = current_time - start_time
        # OK, we either exceeeded or timeout or found our string...
        loc = self.received_string.find(expect_string)
        if (loc == -1):
            return ("Expect String [" + expect_string + "] was not found within [" + str(timeout) + "] Seconds")
        else:
            return self.received_string
        pass


if __name__ == "__main__":

    try:
        # myserial = otSerial(port='/dev/ttyUSB0', baudrate=115200, timeout=5)
        myserial = otSerial(port='COM1', baudrate=115200, timeout=5)
        received = myserial.send_expect("hello\r\n".decode('utf-8'), "zap-on-reset", 3)  # 在3秒之內發送'ls\r',期望獲得"zap-on-reset"
        myserial.close()
        print(received)

    except Exception as e:
        print(str(e))
        pass
