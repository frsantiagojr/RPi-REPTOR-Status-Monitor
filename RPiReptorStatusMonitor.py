#!/usr/bin/python
# -*- coding: utf-8 -*-
# Dependencies:
## pip3 install psutil
## pip3 install uptime
#
# Serial port needs to be released from console after boot
# cd /etc/systemd/system
# systemctl mask serial-getty@ttyS0.service
# sync
# reboot

import time
import sys
import psutil
import socket
import fcntl
import struct
import os
import platform
import re
import uuid
from rpi_mates.controller import RPiMatesController as MatesController
from mates.constants import *

ALL_DATA = -1
CPU_USE  = 0
CPU_TEMP = 1
GPU_TEMP = 2
RAM_USE  = 3
HDD_USE  = 4
RAM_USE_CONT = 5
CPU_USE_CONT = 6

def getSSID():
    ssid = os.popen("iwconfig wlan0 \
                | grep 'ESSID' \
                | awk '{print $4}' \
                | awk -F\\\" '{print $2}'").read()
    return ssid

def getSystemInfo():
    mates.updateTextArea(13, "Total number of Cores: " + str(psutil.cpu_count(logical=True),), True)
    mates.updateTextArea(14, platform.release(), True)
    mates.updateTextArea(15, str(platform.version()), True)
    mates.updateTextArea(12, str(platform.machine()), True)
    mates.updateTextArea(16, "Total RAM: "+ str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB", True)
    hdd = psutil.disk_usage('/')
    mates.updateTextArea(17, "Total HDD Capacity: %d GB" % (hdd.total / (2**30)), True)

def getNetworkInfo():
    mates.updateTextArea(18, getSSID(), True)
    mates.updateTextArea(19, socket.gethostname(), True)
    mates.updateTextArea(20, get_interface_ipaddress('wlan0'), True)
    mates.updateTextArea(21, ':'.join(re.findall('..', '%012x' % uuid.getnode())), True)
    iostat = psutil.net_io_counters(pernic=False)
    mates.updateTextArea(22, str(iostat[1]) + " bytes", True)
    mates.updateTextArea(23, str(iostat[0]) + " bytes")

def up():
    t = int(time.clock_gettime(time.CLOCK_BOOTTIME))
    days = 0
    hours = 0
    min = 0
    out = ''
    days = int(t / 86400)
    t = t - (days * 86400)
    hours = int(t / 3600)
    t = t - (hours * 3600)
    min = int(t / 60)
    out += str(days) + 'd '
    out += str(hours) + 'h '
    out += str(min) + 'm'
    return out


def get_interface_ipaddress(network):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,
                                struct.pack('256s',
                                network[:15].encode('utf-8')))[20:24])  # SIOCGIFADDR
    except OSError:
        return '0.0.0.0'
    
def get_temp(sensor: str):
    cpu_temp = psutil.sensors_temperatures()
    cpu_temp = psutil.sensors_temperatures()[sensor]
    cpu_temp = psutil.sensors_temperatures()[sensor][0]
    return int(cpu_temp.current)

def increment(val1: int, val2: int):
    respi = 1
    respi = val2 - val1
    if abs(respi) < 10:
        if respi > 0:
            respi = 1
        else:
            respi = -1
    else:
        respi = respi / 10
    return int(respi)

def get_hdd():
    hdd = psutil.disk_partitions(0)
    drive = psutil.disk_usage('/')
    percent = drive.percent
    return percent

def set_Page(newPage: int):
    mates.setPage(newPage, 3000)
    currPage = newPage
    
def set_GaugeLedDigitPercent(num: int, val: int):
    mates.setLedDigitsShortValue(num, val)
    mates.setWidgetValueByIndex(MatesWidget.MATES_MEDIA_GAUGE_B, num, val)
    
def set_GaugeLedDigitTemp(num: int, val: int):
    mates.setLedDigitsShortValue(num, val)
    mates.setWidgetValueByIndex(MatesWidget.MATES_MEDIA_GAUGE_B, num, int(val / 10))
    
def update_Page(page: int, data: int):
    if page == 1:
        if data == ALL_DATA or data == CPU_USE: set_GaugeLedDigitPercent(1, lastCpuUse)
        if data == ALL_DATA or data == CPU_TEMP: set_GaugeLedDigitTemp(0, lastlTemp)
        if data == ALL_DATA or data == RAM_USE: set_GaugeLedDigitPercent(2, lastRamUse)
    if page == 2:
        if data == ALL_DATA or data == CPU_USE: set_GaugeLedDigitPercent(4, lastCpuUse)
        if data == ALL_DATA or data == CPU_TEMP: set_GaugeLedDigitTemp(3, lastlTemp)
        if data == ALL_DATA or data == GPU_TEMP: set_GaugeLedDigitTemp(6, lastlTempG)
        if data == ALL_DATA or data == RAM_USE: set_GaugeLedDigitPercent(5, lastRamUse)
    if page == 3:
        if data == ALL_DATA or data == CPU_USE: set_GaugeLedDigitPercent(7, lastCpuUse)
        if data == ALL_DATA or data == CPU_TEMP: set_GaugeLedDigitTemp(9, lastlTemp)
        if data == ALL_DATA or data == RAM_USE: set_GaugeLedDigitPercent(8, lastRamUse)
    if page == 4:
        if data == ALL_DATA or data == CPU_USE: set_GaugeLedDigitPercent(10, lastCpuUse)
        if data == ALL_DATA or data == CPU_TEMP: set_GaugeLedDigitTemp(12, lastlTemp)
        if data == ALL_DATA or data == HDD_USE: set_GaugeLedDigitPercent(13, lastHDD)
        if data == ALL_DATA or data == RAM_USE: set_GaugeLedDigitPercent(11, lastRamUse)
    if page == 5:
        if data == ALL_DATA or data == CPU_USE: set_GaugeLedDigitPercent(14, lastCpuUse)
        if data == ALL_DATA or data == CPU_TEMP:
            mates.setWidgetValueByIndex(MatesWidget.MATES_MEDIA_THERMOMETER, 0, int(lastlTemp / 10))
            mates.setLedDigitsShortValue(16, lastlTemp)
        if data == ALL_DATA or data == RAM_USE: set_GaugeLedDigitPercent(15, lastRamUse)
    if page == 6:
        if data == ALL_DATA or data == CPU_USE: mates.setLedDigitsShortValue(18, lastCpuUse)
        if data == CPU_USE_CONT: mates.setWidgetValueByIndex(MatesWidget.MATES_SCOPE, 0, int(lastCpuUse*29/5/10))
        if data == ALL_DATA or data == CPU_TEMP:
            mates.setWidgetValueByIndex(MatesWidget.MATES_MEDIA_THERMOMETER, 1, int(lastlTemp / 10))
            mates.setLedDigitsShortValue(17, lastlTemp)
        if data == ALL_DATA or data == RAM_USE: mates.setLedDigitsShortValue(19, lastRamUse)
        if data == RAM_USE_CONT: mates.setWidgetValueByIndex(MatesWidget.MATES_SCOPE, 1, int(lastRamUse*29/5/10))
#
def set_PageReady(page: int):
    if page < 7: update_Page(currPage, ALL_DATA)
    if page == 7: getSystemInfo()
    if page == 8: getNetworkInfo()

def get_rpi_model():
    model = "Unknown Raspberry Pi Model"
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Model"):
                    model = line.split(":")[1].strip()
                    break
    except FileNotFoundError:
        model="Could not determine Raspberry Pi model (no /proc/cpuinfo found)"
    except Exception as e:
        model = f"An error occured: (e)"

    return model 

if __name__ == '__main__':

    rpi_model = get_rpi_model()

    if "Pi 5" in rpi_model:
        mates = MatesController('/dev/ttyAMA0')
    else:
        mates = MatesController('/dev/serial0')

    mates.begin(115200)

    print("==========================================")
    print(rpi_model,": REPTOR-250 Advanced Status Monitor")
    print("Press CTRL + C to exit.")
 
    gtime = up()
    lastCpuUse = 0
    lastTemp = 0
    lastTempG = 0
    lastlTemp = 0
    lastlTempG = 0
    lastRamUse = 0
    lastHDD = 0
    lastWIPaddr = '0.0.0.0'
    lastEIPaddr = '0.0.0.0'
    lastPage = -1
    currPage = 0
    lastbytesRX = 0
    lastbytesTX = 0
    MaxPage = 8
    RefreshVal = 0
    
    showLogo = 1

    lgpu = 50.5
    
    mates.updateTextArea(3, get_interface_ipaddress('wlan0'))
    mates.updateTextArea(9, get_interface_ipaddress('wlan0'))
    
    mates.updateTextArea(5, gtime, True)
    mates.updateTextArea(11, gtime, True)
    
    IPinterval = 0
    
    lcpu = int(get_temp("cpu_thermal") * 10)
    lgpu = int(get_temp("cpu_thermal") * 10)
    #lgpu = int(get_temp("gpu_thermal") * 10)

    IPinterval = 0
    
    
    while True:

        currPage = mates.getPage()
        if lastPage != currPage:
            if currPage == 0 and showLogo == 1:
                for n in range(0, 74):
                    mates.setWidgetValueByIndex(MatesWidget.MATES_ANIMATION, 0, n)
                time.sleep(3.000)
                for n in range(74, 120):
                    mates.setWidgetValueByIndex(MatesWidget.MATES_ANIMATION, 0, n)
                time.sleep(2.000)
                set_Page(1)
                showLogo = 0
            if lastPage != -1: RefreshVal = 1
            lastPage = currPage
        
        swiped = mates.getSwipeEventCount()
        if swiped > 0:
            swipe = mates.getNextSwipeEvent()
            if swipe == MatesSwipeConsts.MATES_SWIPE_WEST:
                currPage = currPage + 1
                if currPage > MaxPage: currPage = 1
                set_PageReady(currPage)
                set_Page(currPage)
            if swipe == MatesSwipeConsts.MATES_SWIPE_EAST:
                currPage = currPage - 1
                if currPage < 1: currPage = MaxPage
                set_PageReady(currPage)
                set_Page(currPage)
            
        lcpu = int(get_temp("cpu_thermal") * 10)
        lgpu = int(get_temp("cpu_thermal") * 10)
        #lgpu = int(get_temp("gpu_thermal") * 10)
        
        cpuuse = int(psutil.cpu_percent())
        ramuse = int(psutil.virtual_memory().percent)
        hdd = get_hdd()

        if currPage == 8:
            iostat = psutil.net_io_counters(pernic=False)
            if lastbytesRX != iostat[1]:
                lastbytesRX = iostat[1]
                mates.updateTextArea(22, str(iostat[1]) + " bytes", True)
            if lastbytesTX != iostat[0]:
                lastbytesTX = iostat[0]
                mates.updateTextArea(23, str(iostat[0]) + " bytes", True)
        
        if currPage == 6:
            update_Page(currPage, CPU_USE_CONT)
            update_Page(currPage, RAM_USE_CONT)
        
        if cpuuse != lastCpuUse:
            lastCpuUse = lastCpuUse - increment(cpuuse, lastCpuUse)
            update_Page(currPage, CPU_USE)
    
        if lcpu != lastlTemp:
            lastlTemp = lastlTemp - increment(lcpu, lastlTemp)
            update_Page(currPage, CPU_TEMP)
        
        if lgpu != lastlTempG:
            lastlTempG = lastlTempG - increment(lgpu, lastlTempG)
            update_Page(currPage, GPU_TEMP)

        if ramuse != lastRamUse:
            lastRamUse = lastRamUse - increment(ramuse, lastRamUse)
            update_Page(currPage, RAM_USE)
        
        if hdd != lastHDD:
            lastHDD = lastHDD - increment(hdd, lastHDD)
            update_Page(currPage, HDD_USE)
        
        if IPinterval > 20 or RefreshVal == 1:
            tempIPaddr = get_interface_ipaddress('eth0')
            if tempIPaddr != lastEIPaddr or RefreshVal == 1:
                if currPage == 1: mates.updateTextArea(1, tempIPaddr)
                if currPage == 3: mates.updateTextArea(7, tempIPaddr)
                lastEIPaddr = tempIPaddr
                if RefreshVal != 1: getNetworkInfo()
            tempIPaddr = get_interface_ipaddress('wlan0')
            if tempIPaddr != lastWIPaddr or RefreshVal == 1:
                if currPage == 1: mates.updateTextArea(3, tempIPaddr)
                if currPage == 3: mates.updateTextArea(9, tempIPaddr)
                lastWIPaddr = tempIPaddr
                if RefreshVal != 1: getNetworkInfo()
            IPinterval = 0

        IPinterval = IPinterval + 1
        time.sleep(0.040)

        tempTime = up()
        if tempTime != gtime or RefreshVal == 1:
            if currPage == 1: mates.updateTextArea(5, gtime, True)
            if currPage == 3: mates.updateTextArea(11, gtime, True)
            gtime = tempTime
        
        RefreshVal = 0
        
        time.sleep(0.020)
