#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import RPi.GPIO as GPIO
import os
import sys
import time
import logging
import spidev as SPI
sys.path.append("..")
from lib import LCD_1inch54
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime
import socket
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# Raspberry Pi pin configuration:
tft = 21
RST = 27
DC = 25
BL = 18
bus = 0
device = 0
logging.basicConfig(level=logging.DEBUG)
GPIO.setup(tft,GPIO.OUT)
GPIO.output(tft,1)
try:
    import psutil
except ImportError:
    print("The psutil library was not found. Run 'sudo -H pip install psutil' to install it.")
    sys.exit()
def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return "%sB" % n
def cpu_usage():
    # load average, uptime
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    av1, av2, av3 = os.getloadavg()
    return "Ld:%.1f %.1f %.1f Up: %s" \
        % (av1, av2, av3, str(uptime).split('.')[0])


def mem_usage():
    usage = psutil.virtual_memory()
    return "Mem: %s %.0f%%" \
        % (bytes2human(usage.used), 100 - usage.percent)


def disk_usage(dir):
    usage = psutil.disk_usage(dir)
    return "SD:  %s %.0f%%" \
        % (bytes2human(usage.used), usage.percent)


def network(iface):
    stat = psutil.net_io_counters(pernic=True)[iface]
    return "%s: Tx%s, Rx%s" % \
           (iface, bytes2human(stat.bytes_sent), bytes2human(stat.bytes_recv))
def get_ip_addresses(family):
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == family:
                yield (interface, snic.address)
#ipv4s = list(get_ip_addresses(socket.AF_INET))
disp = LCD_1inch54.LCD_1inch54()
disp.Init()
try:
 while True:
    # display with hardware SPI:
    ''' Warning!!!Don't  creation of multiple displayer objects!!! '''
    #disp = LCD_1inch54.LCD_1inch54(spi=SPI.SpiDev(bus, device),spi_freq=10000000,rst=RST,dc=DC,bl=BL)
#    disp = LCD_1inch54.LCD_1inch54()
    # Initialize library.
#    disp.Init()
    # Clear display.
    ipv4s = list(get_ip_addresses(socket.AF_INET))
    ips = ipv4s[1]
    ip = ips[1]
    now = datetime.now()
    time1 = now.strftime("%y/%m/%d")
    time2 = now.strftime("%H:%M:%S")
    disp.clear()
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    logging.info("draw text")
    Font1 = ImageFont.truetype("../Font/Font01.ttf",25)
    Font2 = ImageFont.truetype("../Font/Font01.ttf",20)
    Font3 = ImageFont.truetype("../Font/Font00.ttf",15)
    Font4 = ImageFont.truetype("../Font/Font00.ttf",28)
    Font5 = ImageFont.truetype("../Font/Font00.ttf",32)
    Font5 = ImageFont.truetype("../Font/Font00.ttf",32)
    draw.rectangle([(0,0),(240,30)],fill = "VIOLET")
    draw.text((50, 0), 'Olive and Iris', fill = "WHITE",font=Font1)
    draw.rectangle([(0,30),(240,120)],fill = "YELLOW")
    draw.text((5, 30),cpu_usage() , fill = "BLACK",font=Font3)
    draw.text((5, 45),disk_usage('/') , fill = "BLACK",font=Font3)
    draw.text((5, 60),network('wlan0') , fill = "BLACK",font=Font3)
    draw.text((5, 75),mem_usage() , fill = "BLACK",font=Font3)
    draw.text((5, 90),'Wlan : '+ip , fill = "BLACK",font=Font3)
    draw.rectangle([(0,120),(120,180)],fill = "AQUA")
    draw.rectangle([(120,180),(240,180)],fill = "WHITE")
    draw.text((25, 130),'28 C' , fill = "BLACK",font=Font5)
    draw.text((145,130 ),'68 %' , fill = "BLACK",font=Font5)
    draw.rectangle([(0,180),(240,240)],fill = "BLACK")
    draw.text((85, 180),"TIME" , fill = "GREY",font=Font4)
    draw.text((50, 210),time1 , fill = "WHITE",font=Font4)
#    draw.rectangle([(0,115),(190,160)],fill = "RED")
#    draw.text((5, 118), 'WaveShare', fill = "WHITE",font=Font2)
    im_r=image1.rotate(270)
    disp.ShowImage(im_r)
    time.sleep(60)
#    disp.module_exit()
#    logging.info("quit:")
except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    disp.module_exit()
    GPIO.output(tft,0)
    GPIO.cleanup()
    logging.info("quit:")
    exit()
