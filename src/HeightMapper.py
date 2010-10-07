'''
Created on Oct 7, 2010

@author: jcobb
'''

from PIL import Image, ImageDraw
from ImprovedNoise import noise
import math


class HeightMapper(object):
    '''
    will create random heightmaps
    '''


    def __init__(self, w, h):
        '''
        Constructor
        '''
        self.w = w
        self.h = h
        self.heightfield = {}
    
    def generate(self):
        
        for x in range(self.w):
            for y in range (self.h):
                X = x*4 + math.sin(x)
                Y = y*4 + math.sin(y)
                rand = ((noise(float(X), float(Y), 0)+1)/2)*255
                self.heightfield[(x/4,y/4)] = rand
                

                
    def output(self, fname):
        print 'in output'
        img = Image.new("L",(self.w,self.h))
        draw = ImageDraw.Draw(img)
        print 'before for loop'
        print self.heightfield
        for i in self.heightfield.keys():
            print i, self.heightfield[i]
            draw.point(i,fill=self.heightfield[i])
        print "after for loop"
        img.save(fname)        
        
                
            
HM = HeightMapper(100,100)
HM.generate()
HM.output("c:/hm.bmp")