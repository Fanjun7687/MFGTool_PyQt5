# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
# -*- coding: utf-8 -*-
__author__ = 'Administrator'
'''
@Time    : 2020/5/8 15:47
@Author  : Jason.Fan
@File    : Python_Demo.py

用上python的bytes和str两种类型转换的函数encode()、decode()即可！
(str---->bytes) 【编码过程】 str通过encode()方法可以编码为指定的bytes；
(bytes-->str) 【解码过程】 如果我们从网络或磁盘上读取了字节流，那么读到的数据就是bytes。要把bytes变为str，就需要用decode()方法；



'''
import os
import subprocess


class Adb(object):
    """ Provides some adb methods """

    @staticmethod      #静态方法可以直接引用类方法，如  Adb.get_adb_devices
    def get_adb_devices():   #获取挂载的设备device ID
        """
        Do adb devices
        :return The first connected device ID
        """
        cmd = "adb devices"
        bytes_line = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        #bytes_line是返回的内容是字节类型
        if bytes_line.find(bytes("List of devices attached",'utf-8')) < 0:  # adb is not working
            return None
        return bytes_line.decode('utf-8').split("\t")[0].split("\r\n")[-1]  # This line may have different format

    @staticmethod
    def pull_sd_dcim(device, target_dir='E:/files'):
        """ Pull DCIM files from device """
        print("Pulling files")
        des_path = os.path.join(target_dir, device)
        if not os.path.exists(des_path):
            os.makedirs(des_path)
        print(des_path)
        cmd = "adb pull /sdcard/DCIM/ " + des_path
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(result)
        print("Finish!")
        return des_path

    @staticmethod
    def some_adb_cmd():
        #some_adb_cmd方法执行一连串的命令。各个命令之间用&&连接
        p = subprocess.Popen('adb shell cd sdcard&&ls&&cd ../sys&&ls', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return_code = p.poll()
        while return_code is None:
            line = p.stdout.readline()
            return_code = p.poll()
            line = line.strip().decode('gbk')
            if line:
                print(line)
        print("Done")

if __name__ == '__main__':
    # adb_func=Adb()
    # print(adb_func.get_adb_devices())

    # print(Adb.get_adb_devices())
    Adb.some_adb_cmd()