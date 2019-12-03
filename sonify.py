
from scipy.interpolate import interp1d
import io
from time import sleep
import pygame.midi
import pygame
from constants import *
from sensors import *
import math
import time
import random
class RunningStats:
    """
    Here is a literal pure Python translation of the Welford's algorithm implementation from 
    http://www.johndcook.com/standard_deviation.html:
    https://github.com/liyanage/python-modules/blob/master/running_stats.py
    """    
    def __init__(self):
        self.n = 0
        self.old_m = 0
        self.new_m = 0
        self.old_s = 0
        self.new_s = 0

    def clear(self):
        self.n = 0

    def push(self, x):
        self.n += 1

        if self.n == 1:
            self.old_m = self.new_m = x
            self.old_s = 0
        else:
            self.new_m = self.old_m + (x - self.old_m) / self.n
            self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)

            self.old_m = self.new_m
            self.old_s = self.new_s

    def mean(self):
        return self.new_m if self.n else 0.0

    def variance(self):
        return self.new_s / (self.n - 1) if self.n > 1 else 0.0

    def standard_deviation(self):
        return math.sqrt(self.variance())


class Sonifier:
    def __init__(self,sensors=['Accelerometer'],
                 instrument='electric guitar (clean)',
                 audioDeviceId=0,delay=0.7):
        self.prevAcceleroVal=0
        self.prevBaroVal=0
        self.sensors=sensors
        # self.n = 0
        # self.old_m = 0
        # self.new_m = 0
        # self.old_s = 0
        # self.new_s = 0
        self.acceleroDeviator=RunningStats()
        self.baroDeviator=RunningStats()
        self.instrument = INSTRUMENTS[instrument]
        self.volume=127
        self.prevKey=0
        self.audioDeviceID=audioDeviceId
        self.delay=delay
        self.pitch=0
        self.player=''
    def deletePlayer(self):
        pygame.midi.init()
        del self.player
        pygame.midi.quit()
    def changeInstrument(self,instrument):
        pygame.midi.init()
        
        self.instrument = INSTRUMENTS[instrument]
        self.player.set_instrument(self.instrument)
        pygame.midi.quit()
    def changePitch(self,val):
        pygame.midi.init()
        self.player=pygame.midi.Output(self.audioDeviceID)
        self.player.set_instrument(self.instrument)
        self.player.pitch_bend(val)
        del self.player
        pygame.midi.quit()    
    def playAudio(self,key,volume,pitch,instrument):
        pygame.midi.init()
        print(pygame.midi.get_count())
        self.player=pygame.midi.Output(self.audioDeviceID)
        self.instrument=instrument
        self.player.set_instrument(INSTRUMENTS[self.instrument])
        self.player.pitch_bend(pitch,self.audioDeviceID)
        self.player.note_on(key, volume)
        self.delay=random.uniform(0.5,0.8)
        time.sleep(self.delay)
        self.player.note_off(key, volume)
        del self.player
        pygame.midi.quit()
    
    def soothingSound(self,dataPoint):
        if(self.prevAcceleroVal==0):
            self.prevAcceleroVal=dataPoint
        
        self.acceleroDeviator.push(dataPoint)
        self.acceleroDeviator.mean()        
        sd=self.acceleroDeviator.standard_deviation()
        
        if(dataPoint<self.prevAcceleroVal) and not (dataPoint-sd<ADXL345['2G'][0]):
            dataPoint=dataPoint-sd
        elif(dataPoint>self.prevAcceleroVal) and not (dataPoint+sd>ADXL345['2G'][1]):
            dataPoint=dataPoint+sd
        
        dataPoint = ADXL345['2G'][0] if dataPoint < ADXL345['2G'][0] else ADXL345['2G'][1] if dataPoint > ADXL345['2G'][1] else dataPoint
        return dataPoint
    
    def soothingPitch(self,dataPoint):
        if(self.prevBaroVal==0):
            self.prevBaroVal=dataPoint
        
        self.baroDeviator.push(dataPoint)
        self.baroDeviator.mean()        
        sd=self.baroDeviator.standard_deviation()
        
        # if(dataPoint<self.prevBaroVal) and not (dataPoint-sd<BMP180[0]):
        #     dataPoint=dataPoint-sd
        # elif(dataPoint>self.prevBaroVal) and not (dataPoint+sd>BMP180[1]):
        #     dataPoint=dataPoint+sd
        
        # dataPoint = BMP180[0] if dataPoint < BMP180[0] else BMP180[1] if dataPoint > BMP180[1] else dataPoint
        #return dataPoint
        return sd
    
    
    def mapDataToMidiRange(self,accDataPoint,baroDataPoint):
        """
        midi notes have a range of 0 - 127. Make sure the data is in that range
        data: list of tuples of x, y coordinates for pitch and timing
        min: min data value, defaults to 0
        max: max data value, defaults to 127
        return: data, but y normalized to the range specified by min and max
        """
        accDataPoint=self.soothingSound(accDataPoint)    
        baroSd=int(self.soothingPitch(baroDataPoint))*10
        
        m=interp1d([ADXL345['2G'][0],ADXL345['2G'][1]],[MIDI_RANGE_LOW,MIDI_RANGE_HIGH])
        key=m(accDataPoint)
        key=int(key)
        
        if(self.acceleroDeviator.n==20):
            self.acceleroDeviator.clear()
        self.prevAcceleroVal=accDataPoint
        return key,baroSd
    
    
    ############DATA FORMATTER##############
    def clear(self):
        self.n = 0

    def push(self, x):
        self.n += 1
        
        if self.n == 1:
            self.old_m = self.new_m = x
            self.old_s = 0
        else:
            self.new_m = self.old_m + (x - self.old_m) / self.n
            self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)

            self.old_m = self.new_m
            self.old_s = self.new_s

    def mean(self):
        return self.new_m if self.n else 0.0

    def variance(self):
        return self.new_s / (self.n - 1) if self.n > 1 else 0.0

    def standard_deviation(self):
        return math.sqrt(self.variance())        

    ######################################
    


