#!/usr/bin/env python
# -*- coding:utf-8 -*-

import cv2
from camera_measure import measure

baseDir = 'C:/Users/yayo/Desktop/calibrate'
caminfo = baseDir + '/sqare_caminfo.json'

# test
imageFile = baseDir + '/sqare/25.jpg'
image = cv2.imread(imageFile)

remap_size = (image.shape[1]*2, image.shape[0]*2)
me = measure(caminfo)
me.loadCamInfo()
me.generateMap(remap_size)
remaped = me.remapImage(image)

dist = me.measure_line((310,272), (526,207))
print 'distance: %.4f mm'%dist

cv2.imshow('source', image)
cv2.imshow('remaped', remaped)
cv2.waitKey(0)