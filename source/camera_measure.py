#!/usr/bin/env python
# -*- coding:utf-8 -*-

import cv2
import json
import math
import numpy as np

class measure(object):
    def __init__(self, caminfo):
        self._camera_info_file = caminfo

        self._cameraMatrix = 0
        self._cameraDist = 0
        self._pixel2mm = 0
        self._mapX = 0
        self._mapY = 0


    def loadCamInfo(self):
        '''
        cameraMatrix
            f_x 0  c_x
            0  f_y c_y
            0   0   1

        distCoeffs
            k1, k2, p1, p2, k3

        rate
        '''
        print 'loading camera info from %s...'%self._camera_info_file
        self._cameraMatrix = np.zeros((3,3), dtype=np.float64)
        self._cameraDist = np.zeros((1,5), dtype=np.float64)
        with open(self._camera_info_file, 'r') as f:
            jsData = json.load(f)
            self._cameraMatrix[0][0] = jsData[0]['f_x']
            self._cameraMatrix[0][2] = jsData[0]['c_x']
            self._cameraMatrix[1][1] = jsData[0]['f_y']
            self._cameraMatrix[1][2] = jsData[0]['c_y']
            self._cameraMatrix[2][2] = 1.0

            self._cameraDist[0][0] = jsData[1]['k1']
            self._cameraDist[0][1] = jsData[1]['k2']
            self._cameraDist[0][2] = jsData[1]['p1']
            self._cameraDist[0][3] = jsData[1]['p2']
            self._cameraDist[0][4] = jsData[1]['k3']

            self._pixel2mm = jsData[2]['pixel2mm']
        print '    done!'


    def generateMap(self, remap_size):
        self._mapX, self._mapY = cv2.initUndistortRectifyMap(self._cameraMatrix, \
                                                             self._cameraDist, \
                                                             None, \
                                                             None, \
                                                             remap_size, \
                                                             cv2.CV_32FC1)


    def remapImage(self, image):
        remapedImage = cv2.remap(image, self._mapX, self._mapY, cv2.INTER_LINEAR)
        return remapedImage


    def measure_line(self, p1, p2):
        npPoints = np.zeros((2,1,2), dtype=np.float32)
        remapedPoints = np.zeros((2,1,2), dtype=np.float32)
        npPoints[0][0] = p1
        npPoints[1][0] = p2
        # remap points
        cv2.cv.UndistortPoints(cv2.cv.fromarray(npPoints), \
                               cv2.cv.fromarray(remapedPoints), \
                               cv2.cv.fromarray(self._cameraMatrix), \
                               cv2.cv.fromarray(self._cameraDist), \
                               P=cv2.cv.fromarray(self._cameraMatrix))
        distance = math.sqrt(math.pow(remapedPoints[0][0][0]-remapedPoints[1][0][0],2) + \
                             math.pow(remapedPoints[0][0][1]-remapedPoints[1][0][1],2))
        return distance*self._pixel2mm

'''
def main():
    baseDir = 'C:/Users/yayo/Desktop/calibrate'
    caminfo = baseDir + '/sqare_caminfo.json'

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


if __name__ == '__main__':
    main()
'''