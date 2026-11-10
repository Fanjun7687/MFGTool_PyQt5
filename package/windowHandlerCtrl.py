#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
# -*- coding: utf-8 -*-
__author__ = 'Administrator'
'''
@Time    : 2020/5/18 10:02
@Author  : Jason.Fan
@File    : windowHandlerCtrl.py
python和pywin32实现窗口查找、遍历和点击
'''
import win32gui,win32api,win32con

#根据窗口类名和标题查找窗口句柄，获取窗口位置和大小
def getWinRect(classname,titlename):  #return tuple()
    hwnd=win32gui.FindWindow(classname,titlename)
    print(hwnd);print('%x'%hwnd)
    rect=left,top,right,bottom = win32gui.GetWindowRect(hwnd)
    print(rect)
    return rect

#根据标题描述查找窗口句柄，获取窗口位置和大小
def getWinRect(titlename):  #return tuple()
    hwnd=findWindowHandler(titlename)
    print(hwnd)
    rect=left,top,right,bottom = win32gui.GetWindowRect(hwnd)
    print(rect)
    return rect

#查找标题描述的窗口Handler, #return hwnd  if exist ,else return None
def findWindowHandler(titlename):
    hwnd_title = dict()
    def get_all_hwnd(hwnd,mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            hwnd_title.update({hwnd:win32gui.GetWindowText(hwnd)})
    win32gui.EnumWindows(get_all_hwnd, 0)
    for h,title_window in hwnd_title.items():
        if title_window == titlename:
            print(h, title_window)     #title_window.decode('***')  如果显示不正常，需要解码
            return h

def enumWindowHandler():  #遍历目前所有窗口
    hwnd_title = dict()
    def get_all_hwnd(hwnd,mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            hwnd_title.update({hwnd:win32gui.GetWindowText(hwnd)})
    win32gui.EnumWindows(get_all_hwnd, 0)
    for h,title_window in hwnd_title.items():
        if title_window != '':
            print(h, title_window)     #title_window.decode('***')  如果显示不正常，需要解码
    pass

#通过父句柄获取子句柄
#获得parent的所有子窗口句柄,返回子窗口句柄列表
def get_ChildWindows(parent):
    if not parent:
        return
    hwndChildList = []
    win32gui.EnumChildWindows(parent, lambda hwnd, param: param.append(hwnd),  hwndChildList)
    return hwndChildList

#根据某个句柄获取类名和标题
def get_Title_ClsName(hwnd):
    title = win32gui.GetWindowText(hwnd)
    clsname = win32gui.GetClassName(hwnd)
    return title,clsname

# #获取父句柄hwnd类名为clsname的子句柄
# 父窗口句柄 若不为0，则按照z-index的顺序从hwndChildAfter向后开始搜索子窗体，否则从第一个子窗体开始搜索。 子窗口类名 子窗口标题
# FindWindowEx(hwndParent=0, hwndChildAfter=0, lpszClass=None, lpszWindow=None)
# subHandle = win32gui.FindWindowEx(hwnd, None, clsname, None)
# subHandle = win32gui.FindWindowEx(hwnd, 0, 'EDIT', None)


def closeWindow(hwnd):
    win32gui.PostMessage(hwnd,win32con.WM_CLOSE,0,0)

def setWindowStatus(hwnd):
    if (win32gui.IsIconic(hwnd)):
        win32gui.ShowWindow(hwnd,win32con.SW_SHOWNORMAL)
# SW_HIDE：隐藏窗口并激活其他窗口。nCmdShow=0。
# SW_MAXIMIZE：最大化指定的窗口。nCmdShow=3。
# SW_MINIMIZE：最小化指定的窗口并且激活在Z序中的下一个顶层窗口。nCmdShow=6。
# SW_RESTORE：激活并显示窗口。如果窗口最小化或最大化，则系统将窗口恢复到原来的尺寸和位置。在恢复最小化窗口时，应用程序应该指定这个标志。nCmdShow=9。
# SW_SHOW：在窗口原来的位置以原来的尺寸激活和显示窗口。nCmdShow=5。
# SW_SHOWDEFAULT：依据在STARTUPINFO结构中指定的SW_FLAG标志设定显示状态，STARTUPINFO 结构是由启动应用程序的程序传递给CreateProcess函数的。nCmdShow=10。
# SW_SHOWMAXIMIZED：激活窗口并将其最大化。nCmdShow=3。
# SW_SHOWMINIMIZED：激活窗口并将其最小化。nCmdShow=2。
# SW_SHOWMINNOACTIVE：窗口最小化，激活窗口仍然维持激活状态。nCmdShow=7。
# SW_SHOWNA：以窗口原来的状态显示窗口。激活窗口仍然维持激活状态。nCmdShow=8。
# SW_SHOWNOACTIVATE：以窗口最近一次的大小和状态显示窗口。激活窗口仍然维持激活状态。nCmdShow=4。
# SW_SHOWNORMAL：激活并显示一个窗口。如果窗口被最小化或最大化，系统将其恢复到原来的尺寸和大小。应用程序在第一次显示窗口的时候应该指定此标志。nCmdShow=1。



def main():
    enumWindowHandler()
    getHwnd=findWindowHandler('Reflow Sensor RawData Record System (RSRRS) Version--T1210_V1.03')
    getWinRect('无标题 - 记事本')
    print(get_ChildWindows(getHwnd))
    pass


if __name__ == '__main__':
    main()
    pass