import struct
import bpy
import time
import threading
import socket
import datetime
 
FREQ = 50
buf = [0x00] * 29
 
def get_seconds():
 
    datetime_object = datetime.datetime.now()
    now_timetuple = datetime_object.timetuple()
    now_second = time.mktime(now_timetuple)
    mow_millisecond = int(now_second * 1000 + datetime_object.microsecond / 1000)
    
    #print "timetuple-- "+ str(now_timetuple)
    #print "datimeobject-- " + str(datetime_object)
    #print "second-- " + str(now_second)
    #print("millisecond-- " + str(mow_millisecond))
    
    return mow_millisecond
 
def pack_be24(b, p, r):
    
    b[p + 2] = r & 0xff
    r >>= 8
    b[p + 1] = r & 0xff
    r >>= 8
    b[p] = r & 0xff
    
def pack_be24_15(b, p, d):
    #print(int(d * 32768.0))
    pack_be24(b, p, int(d * 32768.0))
    
def pack_be24_6(b, p, d):
    pack_be24(b, p, int(d * 64.0))
 
def to_freed_pack(id, loc, rot):
    
    buf[0] = 0xd1
    
    # id
    buf[1] = id & 0xff
    
    # rot
    pack_be24_15(buf, 2, rot.z * 180.0 / 3.1415926) # Pan
    pack_be24_15(buf, 5, rot.x * 180.0 / 3.1415926) # Tilt
    pack_be24_15(buf, 8, rot.y * 180.0 / 3.1415926) # Roll
    
    # loc
    pack_be24_6(buf, 11, loc.x)
    pack_be24_6(buf, 14, loc.y)
    pack_be24_6(buf, 17, loc.z)
    
    pack_be24(buf, 20, 0) # zoom
    pack_be24(buf, 23, 0) # focus
    
    buf[26] = 0
    buf[27] = 0
    
    # checksum
    cs = 0x40
    
    for i in range(0, 28):
        cs -= buf[i]
        
    buf[28] = cs % 256
 
    return buf
 
class FreedSender(threading.Thread):
    def __init__(self, obj):
        self.obj = obj
        threading.Thread.__init__(self)
    
    def run(self):
        last_send_time = get_seconds()
        
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        
        while True:
            curr_time = get_seconds()
            
            if curr_time - last_send_time >= 20 :
                loc, rot, scale = self.obj.matrix_world.decompose()
                last_send_time = curr_time
                
                #print(type(rot))
                
                right_rot = rot
                right_rot.w *= -1
                right_loc = loc
                right_loc.x *= -1
                right_loc.y *= -1
                euler = right_rot.to_euler('ZXY')
 
                #print(loc)
                #print(rot)
                
                
                
                b = to_freed_pack(0, right_loc * 1000.0, euler)
                #print(b)
                s.sendto(bytes(b), ("127.0.0.1", 8800))
                
                last_send_time = curr_time
                
            #time.sleep(0.002)
 
'''    
for collection in bpy.data.collections:
   print(collection.name)
   for obj in collection.all_objects:
      print("obj: ", obj.name)  
'''
 
#obj = bpy.context.object
obj = bpy.data.objects['Cube']
print(obj)
runner = FreedSender(obj)
runner.start()
