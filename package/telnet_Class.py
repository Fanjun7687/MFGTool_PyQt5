# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
# -*- coding: utf-8 -*-
__author__ = 'Administrator'
'''
@Time    : 2020/5/8 15:47
@Author  : Jason.Fan
@File    : Python_Demo.py




'''
import os, sys, time
import telnetlib

class Telnet(object):
    def __init__(self,username,password):
        self.username=username
        self.password=password
    @staticmethod
    def telnet_login(self,ip):
        tn=telnetlib.Telnet(ip,port=23,timeout=50)  ## 连接Telnet服务器
        tn.read_until('Username')
        tn.write(self.username+'\n')
        tn.read_until('Password')
        tn.write(self.password+'\n')
        time.sleep(1)
        tn.write('system' + '\n')  # 输入命令
        tn.write('domain paoa' + '\n')
        tn.write('****' + '\n')
        tn.write('****' + '\n')
        time.sleep(50)
        result1 = tn.read_very_eager()  # 获得结果
        print ('result1')
        # 命令执行完毕后，终止Telnet连接（或输入exit退出）
        tn.close()  # tn.write('exit\n')




if __name__ == '__main__':
    Telnet.telnet_login('192.168.1.200')

