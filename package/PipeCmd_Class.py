# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
# -*- coding: utf-8 -*-
__author__ = 'Administrator'
'''
@Time    : 2020/5/8 15:47
@Author  : Jason.Fan
@File    : Python_Demo.py


'''
import os, sys, time
import subprocess


# import win32api
# import win32process, win32event
class PipeCMD(object):
    @staticmethod  ## 静态方法无需实例化
    def CreatePipeAndRun(szCmd):
        p = subprocess.Popen(szCmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        while p.poll() is None:  # Popen.poll() 检查子进程是否已结束
            line = p.stdout.readline().strip()
            if line:  # 不为空
                print('Pipe output: [{}]'.format(line.decode('gbk')))
        if p.returncode == 0:
            print('Pipe success')
        else:
            print('Pipe failed')

    @staticmethod
    def Get_ADBDevice():
        c_line = \
        subprocess.Popen('adb devices', shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE).communicate()[0]
        str_line = c_line.decode('utf-8')
        if str_line.find('List of devices attached') < 0:
            return None
        # print(str_line)
        return str_line.split("\t")[0].split("\r\n")[-1]  # -1是指list的最后一个元素

    @staticmethod
    # 执行strSend指令,期望获取指定字符strExpRec
    def Pipe_SendCmdExpectStr(strSend, strExpRec,iTimeOver):
        bRet = False
        beginTime=int(time.time())
        p = subprocess.Popen(strSend, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        while p.poll() is None :  # Popen.poll() 检查子进程是否已结束
            endTime=int(time.time())
            if (endTime-beginTime)>=iTimeOver:
                p.terminate()
                break
            line = p.stdout.readline().strip().decode('gbk')
            if line:  # 不为空
                # print('Pipe output: [{}]'.format(line))
                print('{}'.format(line))
                if strExpRec in line: bRet = True
        print(bRet)
        print('Pipe success') if p.returncode == 0 else print('Pipe failed')
        return bRet and p.returncode==0


if __name__ == '__main__':
    # PipeCMD.CreatePipeAndRun('ping 192.168.1.92')
    # PipeCMD.CreatePipeAndRun('adb devices')
    # print(PipeCMD.demo('adb devices'))



    ret = PipeCMD.Pipe_SendCmdExpectStr('ping 192.168.1.92', '0%',2)
    print(ret)
    # print('ok') if ret == True else print('ng')
