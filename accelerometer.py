import time
import board
import busio
import adafruit_adxl34x
import numpy
import smbus
import datetime

import plotly.plotly as py# plotly library
from plotly.graph_objs import Scatter, Layout, Figure # plotly graph objects

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
    title='Raspberry Pi Streaming Sensor Data'
)

fig = Figure(data=[trace1], layout=layout)

print (py.plot(fig, filename='Raspberry Pi Streaming Example Values'))

stream = py.Stream(stream_token)
stream.open()


i2c = busio.I2C(board.SCL, board.SDA)
bus = smbus.SMBus(1)
 
# For ADXL343
#accelerometer = adafruit_adxl34x.ADXL343(i2c)
# For ADXL345
accelerometer = adafruit_adxl34x.ADXL345(i2c)
 
while True:
    bus.write_byte_data(0x60, 0x26, 0x39)
    time.sleep(1)
    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 4 bytes
    # status, pres MSB1, pres MSB, pres LSB
    data = bus.read_i2c_block_data(0x60, 0x00, 4)
    # Convert the data to 20-bits
    pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    pressure = (pres / 4.0) / 1000.0
    # Output data to screen
    print ("Pressure : %.2f kPa" %pressure)
    
    #print("%f %f %f" % accelerometer.acceleration)
    accelerometer_raw=accelerometer.acceleration
    accelerometer_magnitude=numpy.sqrt(numpy.square(accelerometer_raw[0])+numpy.square(accelerometer_raw[1])+numpy.square(accelerometer_raw[2]))
    print("Acceleration : %f" %accelerometer_magnitude)
    #time.sleep(0.1)
    
    
    
    stream.write({'x': datetime.datetime.now(), 'y': accelerometer_magnitude})
    
    
    time.sleep(0.25) # delay between stream posts
