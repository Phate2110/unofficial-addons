################################################################################
#      This file is part of OpenELEC - http://www.openelec.tv
#      Copyright (C) 2009-2012 Stephan Raue (stephan@openelec.tv)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with OpenELEC.tv; see the file COPYING.  If not, write to
#  the Free Software Foundation, 51 Franklin Street, Suite 500, Boston, MA 02110, USA.
#  http://www.gnu.org/copyleft/gpl.html
################################################################################

import os
import sys
import time
import xbmcaddon
import subprocess
from xml.dom.minidom import parse

sys.path.append('/usr/share/kodi/addons/service.openelec.settings')

import oe

__addon__ = xbmcaddon.Addon();
__path__  = os.path.join(__addon__.getAddonInfo('path'), 'bin') + '/'

pauseXBMC = __addon__.getSetting("PAUSE_XBMC")

# widevine stuff
__url__   = 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'
__file__  = __url__.split('/')[-1]
__tar__   = 'data.tar.xz'
__tmp__   = '/tmp/widevine/'
__lib__   = 'opt/google/chrome/libwidevinecdm.so'

def widevine():
  try:
    if not os.path.isdir(__tmp__):
      os.mkdir(__tmp__)
    if not os.path.exists(__tmp__ + __file__):
      oe.download_file(__url__, __tmp__ + __file__)
    oe.notify('Chromium', 'Extracting libwidevinecdm.so')
    oe.execute('cd ' + __tmp__ + ' && ar -x ' + __file__)
    oe.execute('tar xf ' + __tmp__ + __tar__ + ' -C ' + __tmp__ + ' ./' + __lib__)
    oe.copy_file(__tmp__ + __lib__, __path__ + __lib__.split('/')[-1])
    oe.notify('Chromium', 'Installation of libwidevinecdm.so succeeded')
  except Exception, e:
    oe.notify('Chromium', 'Installation of libwidevinecdm.so failed')

def pauseXbmc():
  if pauseXBMC == "true":
    xbmc.executebuiltin("PlayerControl(Stop)")
    xbmc.audioSuspend()
    xbmc.enableNavSounds(False)

def resumeXbmc():
  if pauseXBMC == "true":
    xbmc.audioResume()
    xbmc.enableNavSounds(True)

def startChromium(args):
  oe.execute('chmod +x ' + __path__ + 'chromium')
  oe.execute('chmod +x ' + __path__ + 'chromium.bin')
  oe.execute('chmod 4755 ' + __path__ + 'chrome-sandbox')

  try:
    window_mode = {
        'maximized': '--start-maximized',
        'kiosk': '--kiosk',
        'none': '',
    }
    gpu_blacklist = ''
    if __addon__.getSetting('IGNORE_GPU_BLACKLIST') == 'true':
      gpu_blacklist = '--ignore-gpu-blacklist'
    if (__addon__.getSetting('USE_CUST_AUDIODEVICE') == 'true'):
      alsa_device = __addon__.getSetting('CUST_AUDIODEVICE_STR')
    else:
      alsa_device = getAudioDevice()
    alsa_param = ''
    if not alsa_device == None and not alsa_device == '':
      alsa_param = '--alsa-output-device=' + alsa_device
    chrome_params = window_mode.get(__addon__.getSetting('WINDOW_MODE')) + ' ' + gpu_blacklist + ' ' + alsa_param + ' ' + args + ' ' + __addon__.getSetting('HOMEPAGE')
    oe.execute(__path__ + 'chromium ' + chrome_params)
  except:
    pass

def isRuning(pname):
  tmp = os.popen("ps -Af").read()
  pcount = tmp.count(pname)
  if pcount > 0:
    return True
  return False

def getAudioDevice():
  try:
    dom = parse("/storage/.kodi/userdata/guisettings.xml")
    audiooutput=dom.getElementsByTagName('audiooutput')
    for node in audiooutput:
      dev = node.getElementsByTagName('audiodevice')[0].childNodes[0].nodeValue
    if dev.startswith("ALSA:"):
      dev = dev.split("ALSA:")[1]
      if dev == "@":
        return None
      if dev.startswith("@:"):
        dev = dev.split("@:")[1]
    else:
      # not ALSA
      return None
  except:
    return None
  if dev.startswith("CARD="):
    dev = "plughw:" + dev
  return dev

if (not __addon__.getSetting("firstrun")):
  __addon__.setSetting("firstrun", "1")
  __addon__.openSettings()

try:
  args = ' '.join(sys.argv[1:])
except:
  args = ""

oe.dbg_log('chromium', "'" + unicode(args) + "'")

if args == 'widevine':
    widevine()
else:
  if not isRuning('chromium.bin'):
    pauseXbmc()
    startChromium(args)
    while isRuning('chromium.bin'):
      time.sleep(1)
    resumeXbmc()

