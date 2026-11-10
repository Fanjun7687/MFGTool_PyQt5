# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
# -*- coding: utf-8 -*-
__author__ = 'Administrator'
'''
@Time    : 2020/5/8 15:47
@Author  : Jason.Fan
@File    : Python_Demo.py

ErrorCode to be defined here!!

'''

# -*- coding: utf-8 -*
"""状态码枚举类

author: Jill

usage：
    结构为：错误枚举名-错误码code-错误说明message
    # 打印状态码信息
    code = Status.OK.get_code()
    print("code:", code)
    # 打印状态码说明信息
    msg = Status.OK.get_msg()
    print("msg:", msg)
"""
from enum import Enum, unique

@unique
class ErrorCode(Enum):
    TMOVER = {"TMOVER": "Test Time Over!!"}
    UNDEFI = {"UNDEFI": "Un-defined Error Code"}
    SRPE00 = {"SRPE00": "SFIS Receive Product Error"}
    SRSE00 = {"SRSE00": "SFIS Receive Status Error"}
    SFIS01 = {"SFIS01": "Upload File To SFIS LOGIN_PG Folder Error"}
    SFIS02 = {"SFIS02": "Upload File To SFIS RESULT Folder Error"}
    SFIS03 = {"SFIS03": "Read File From SFIS LOGIN_PG Folder Error"}
    SFIS04 = {"SFIS04": "Read File From SFIS RESULT Folder Error"}
    SFIS05 = {"SFIS05": "SFIS Response ERROR Info, Please Call IT....."}
    SFIS06 = {"SFIS06": "SFIS Responed Data TimeOut"}

    SNLEN0 = {"SNLEN0": "SCAN SN Length Error"}
    SRSR00 = {"SRSR00": "SFIS Receive PSN Rule Error"}
    SRIR00 = {"SRIR00": "SFIS Receive IMEI Rule Error"}
    SRMAC1 = {"SRMAC1": "SFIS Receive MAC1 Rule Error"}
    SRMAC2 = {"SRMAC2": "SFIS Receive MAC2 Rule Error"}
    SRCSN0 = {"SRCSN0": "SFIS Receive CSN Rule Error"}

    SDWL00 = {"SDWL00": "SFIS Define Wan Lan MAC Error"}
    SRWM00 = {"SRWM00": "SFIS Receive Wan MAC Rule Error"}
    SRLM00 = {"SRLM00": "SFIS Receive Lan MAC Rule Error"}
    SRW5M0 = {"SRW5M0": "SFIS Receive WLan 5G MAC Rule Error"}
    SRW2M0 = {"SRW2M0": "SFIS Receive WLan 2G MAC Rule Error"}
    SRWPK0 = {"SRWPK0": "SFIS Receive Wpakey Rule Error"}
    C5MF00 = {"C5MF00": "Check 5GWLan MAC Error"}
    C2MF00 = {"C2MF00": "Check 2GWLan MAC Error"}

    MACREE = {"MACREE": "MACAddress Format Error"}

    IMEIEE = {'IMEIEE': "IMEI Format Error"}
    MEIDEE = {'MEIDEE': "MEID Format Error"}

    CMDTIM = {'CMDTIM': "Dut Execute Command Time Out"}



    def get_code(self):
        """
        根据枚举名称取状态码code
        :return: 状态码code
        """
        return list(self.value.keys())[0]

    def get_msg(self):
        """
        根据枚举名称取状态说明message
        :return: 状态说明message
        """
        return list(self.value.values())[0]


if __name__ == '__main__':
    # 打印状态码信息
    code = ErrorCode.C5MF00.get_code()
    print("code:", code)
    # 打印状态码说明信息
    msg = ErrorCode.C5MF00.get_msg()
    print("msg:", msg)

    print()

    # 遍历枚举
    for errcode in ErrorCode:
        print(errcode.name, ":", errcode.value)
