#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
#-*-coding:utf-8 -*-

# 我把通信定义分为三层：base底层、application应用层、user_api客户层
# 下面打包了serial的类，属于ttl_base底层的类，其他应用直接继承此类即可

import time
import queue
import serial
import threading


def hex_show(data):
    lin = ['%02X' % i for i in data]
    return (" ".join(lin))
    pass

class ComBasic:
    def __init__(self, port='COM1', band_rate=115200):
        self.my_serial = serial.Serial(port=port, baudrate=band_rate, timeout=0.5)
        self.com_stop()

        # 线程相关设置
        self._alive = False
        self._waitEnd = None
        self._stop = False
        self.thread_read, self.thread_send = None, None

        # 数据变量
        self._com_read_buf, self._com_read_len = None, None
        self._send_queue = queue.Queue()

    # 定义串口等待的函数
    def __waiting(self):
        if self._waitEnd:
            self._waitEnd.wait()

    # 关闭串口
    def com_stop(self):
        self._alive = False
        self.my_serial.close()
        if self.my_serial.isOpen():
            self._alive = False
            self.my_serial.close()

    def com_start(self, thread_mode=True):
        """
        启动串口的函数(可选择用线程 或者 不用线程)
        :param thread_mode: True 启动线程读写 False 单独读写
        :return: 是否打开端口成功
        """
        try:
            self.my_serial.open()
        except serial.SerialException:
            print(serial.SerialException)
        if self.my_serial.isOpen():
            if thread_mode:
                self._waitEnd = threading.Event()
                self._alive = True
                self.thread_read = threading.Thread(target=self.com_reader)
                self.thread_read.setDaemon(True)
                # self.thread_send = threading.Thread(target=self.com_sender)
                # self.thread_send.setDaemon(True)
                self.thread_read.start()
            return True
        else:
            return False

    def com_send(self, send_data_):
        self._send_queue.put(send_data_)

    def com_sender(self, data_=None, thread_mode=False):
        """
        串口发送函数
        单独发送则传递数据列表  线程发送则给 self._send_queue 队列赋值
        :param thread_mode: True 启动线程发送 False 单独发送
        :param data_: 单独发送则传递数据列表  线程发送则不需要次参数
        :return: None
        """
        if thread_mode:
            try:
                while self._alive:
                    try:
                        data_ = self._send_queue.get(timeout=0.1)
                    except queue.Empty:
                        pass
                    else:
                        self.__send_base(data_)
            finally:
                self._waitEnd.set()
                self._alive = False
        else:
            self.__send_base(data_)



    def __send_base(self, data_):
        """
        发送的硬件操作 十六进制发送和字符串发送
        :param data_: 发送的数据 列表
        :return:
        """
        try:  # 如果输入不是十六进制数据--
            str_input = hex_show(data_)
            # print(str_input)
            self.my_serial.write(bytes.fromhex(str_input))
        except serial.SerialTimeoutException:  # --则将其作为字符串输出
            self.my_serial.write(bytes(data_, encoding='utf-8'))
        finally:
            self.my_serial.flush()

    def com_reader(self, thread_mode=True):
        """
        串口接收函数
        单独接收则返回数据列表  线程发送则给 _com_read_buf 赋值
        :param thread_mode: True 启动线程接收 False 单独接收
        :return: 单独接收则返回数据列表
        """
        if not thread_mode:
            return self.__read_base()
        else:
            try:
                while self._alive:
                    try:
                        self.__read_base()
                    except Exception as ex:
                        print(ex)
            finally:
                self._waitEnd.set()
                self._alive = False

    def __read_base(self):
        """
        读取的硬件操作  先调用inWaiting和sleep配合接收，、
        然后再判断一次，把结果赋值给self._com_read_buf, self._com_read_len
        :return: 数据列表 和 数据长度 ，如果没有数据则返回None
        """
        init_data = ''
        init_data = init_data.encode('utf-8')  # 由于串口使用的是字节，故而要进行转码，否则串口会不识
        time.sleep(0.02)
        init_n = self.my_serial.inWaiting()  # 获取接收到的数据长度
        # print("init_n=", init_n)
        if init_n:
            init_data = init_data + self.my_serial.read(init_n)
        n = self.my_serial.inWaiting()
        if len(init_data) > 0 and n == 0:
            self._com_read_len, self._com_read_buf = init_n, init_data
            # print(time.strftime("%Y-%m-%d %X"), 'data:', hex_show(self._com_read_buf), 'len:', self._com_read_len)
        else:
            self._com_read_buf, self._com_read_len = None, None
        self.my_serial.flushInput()
        return self._com_read_buf, self._com_read_len

    # 获取接收数据
    def com_return(self, thread_flag=True):
        if not thread_flag:
            self.com_reader(thread_flag)
        return self._com_read_len, self._com_read_buf

    @classmethod
    def change_read_data(cls, com_data):
        """
        读取的数据字符串处理 python串口都是byte类型字符串，需要转为数字列表
        :param com_data: 原始接收的数据 byte类型字符串
        :return: 数字列表
        """
        try:
            # 转十六进制显示
            result = hex_show(com_data)
            # 将数据按换行分割并输出
            string = result.split(' ')
            data = string[:len(com_data)]
            # 字符串转数字列表
            data = [int(x, base=16) for x in data]
            return data
        except Exception as ex:
            print("格式错误，请重试！", ex)


if __name__ == '__main__':
    ser = ComBasic('COM1', 115200)
    ser.com_start()
    ser.com_sender(data_=[1, 2, 3, 4, 5, 6])
