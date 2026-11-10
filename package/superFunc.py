# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
# -*- coding: utf-8 -*-
__author__ = 'Administrator'
'''
@Time    : 2020/5/12 14:00
@Author  : Jason.Fan
@File    : superFunc.py
'''
import os, sys, time, random

def mapNetDriver(strSrvdrive,strSrvAddrs,user,pwd):
    pass


#生成指定长度的验证码
def generate_code(code_len=4):
    """
    :param code_len: 验证码的长度(默认4个字符)
    :return: 由大小写英文字母和数字构成的随机验证码
    """
    all_chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    last_pos = len(all_chars) - 1
    code = ''
    for _ in range(code_len):
        index = random.randint(0, last_pos)
        code += all_chars[index]
    return code.upper()


def main():
    # getCode = generate_code(10)
    # print(getCode)

    return
    # data = [7, 20, 3, 15, 11]
    # result = [pow(num, 3) for num in data if num > 10]
    # print(result)
    #
    #
    # keys = ['1001', '1002', '1003']
    # values = ['骆昊', '王大锤', '白元芳']
    # d = dict(zip(keys, values))
    # print(d)
    #
    # S1='abcdefg12345678'
    # print(S1[::-1].upper())
    # print(S1.find('g12'))
    # print(S1.find('JASON'))
    # print(S1.index('g12'))
    # print('g12' in S1)
    # print(S1.center(50, '*'))
    # print(S1.rjust(50,' '))
    # print(S1.ljust(50,'='))
    # print(S1.isalnum())
    # f = [x + y for x in 'ABCDE' for y in '1234567']
    # print(f)
    # # 用列表的生成表达式语法创建列表容器
    # # 用这种语法创建列表之后元素已经准备就绪所以需要耗费较多的内存空间
    # f = [x ** 2 for x in range(1, 1000)]
    # print(sys.getsizeof(f))  # 查看对象占用内存的字节数
    # print(f)
    # f=[x for x in range(1,101)]
    # print(sys.getsizeof(f))
    # print(f)
    # f=(x for x in range(1,101))
    # print(sys.getsizeof(f))
    # print(tuple(f))





if __name__ == '__main__':
    main()
    pass
