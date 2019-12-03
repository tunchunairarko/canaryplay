import time
import board
import busio
import adafruit_adxl34x
import numpy
import smbus
import datetime
import sonify
import plotly.plotly as py# plotly library
from plotly.graph_objs import Scatter, Layout, Figure # plotly graph objects
import json
import requests
import os

def main():        
    username = 'messay'
    api_key = 'aGWxBNUA1wgFnC8xkY66'
    stream_token = '8g0wx06s37'
    
    py.sign_in(username, api_key)

    trace1 = Scatter(
        x=[],
        y=[],
        stream=dict(
            token=stream_token,
            maxpoints=200
        )
    )

    layout = Layout(
        title='Canary Patient Motion Monitor'
    )

    fig = Figure(data=[trace1], layout=layout)
    print (py.plot(fig, filename='Canary Patient Motion Monitor Values'))

    stream = py.Stream(stream_token)
    stream.open()
    
    Sonifier=sonify.Sonifier(audioDeviceId=2)
    i2c = busio.I2C(board.SCL, board.SDA)
    bus = smbus.SMBus(1)
    control_url="https://canaryplay.isensetune.com/app/param.json"
    accelerometer = adafruit_adxl34x.ADXL345(i2c)
    while True:
        r=requests.get(control_url)
        d=json.loads(r.content)
        bus.write_byte_data(0x60, 0x26, 0x39)
        time.sleep(1)
        data = bus.read_i2c_block_data(0x60, 0x00, 4)
        # Convert the data to 20-bits
        pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
        pressure = (pres / 4.0) / 1000.0
        #print ("Pressure : %.2f kPa" %pressure)
        time.sleep(0.2)
        a=accelerometer.acceleration
        b=numpy.sqrt(numpy.square(a[0])+numpy.square(a[1])+numpy.square(a[2]))
        #print("Acceleration : %f" %b)
        
        key,baroSd=Sonifier.mapDataToMidiRange(b,pressure)
        stream.write({'x': datetime.datetime.now(), 'y': b})
        Sonifier.playAudio(key,int(d['volume']),baroSd+int(d['pitch']),d['instrument'])
        

if __name__=='__main__':
    main()
