#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import cv2
import json
import math
import numpy as np
from mouse_click import mouse

class calibrate(object):
    def __init__(self, chessImages, describe, saveFile):
        self._chess_folder = chessImages
        self._describe = describe
        self._infoFile = saveFile

        self._pattern_size = 0
        self._sub_pix_size = 0
        self._criteria = 0
        self._file_list = 0

        self._object_point = 0
        self._object_list = 0
        self._image_list = 0

        self._cameraMatrix = 0
        self._distCoeffs = 0
        self._pixel2mm = 0

    def loadDescribeFile(self):
        print "loading describe params from %s..."%self._describe
        with open(self._describe, 'r') as f:
            jsData = json.load(f)

            self._pattern_size = (jsData['patternSize']['points_per_row'], \
                                  jsData['patternSize']['points_per_col'])
            self._sub_pix_size = (jsData['subPixWinSize'], jsData['subPixWinSize'])
            self._criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, \
                              jsData['criteria']['max_iter'], \
                              jsData['criteria']['eps'])
            object_distance = jsData['objectDistance']

        self._object_point = np.zeros((self._pattern_size[0]*self._pattern_size[1], 3), \
                                      dtype=np.float32)
        # is related to error from cv2.calibrateCamera
        for row in range(self._pattern_size[1]):
            for col in range(self._pattern_size[0]):
                self._object_point[row*self._pattern_size[0]+col][0] = col*object_distance
                self._object_point[row*self._pattern_size[0]+col][1] = row*object_distance
        '''
        self._object_point = np.zeros((self._pattern_size[0]*self._pattern_size[1],3), np.float32)
        self._object_point[:,:2] = np.mgrid[0:self._pattern_size[0],0:self._pattern_size[1]].T.reshape(-1,2)
        '''


    def loadImageFile(self):
        self._file_list = list()
        print "loading chessboard image from %s..."%self._chess_folder
        files = os.listdir(self._chess_folder)
        for file in files:
            self._file_list.append(self._chess_folder + file)
        print '    got %d images'%len(self._file_list)


    def calibrate_it(self):
        print 'calibrating...'
        self._image_list = list()
        self._object_list = list()

        im_size = 0
        for image in self._file_list:
            imgBGR = cv2.imread(image)
            if isinstance(imgBGR, np.ndarray):
                imgGray = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2GRAY)
                im_size = imgGray.shape
                ret, corners = cv2.findChessboardCorners(imgGray, self._pattern_size, \
                                                         flags=cv2.CALIB_CB_ADAPTIVE_THRESH + \
                                                               cv2.CALIB_CB_NORMALIZE_IMAGE + \
                                                               cv2.CALIB_CB_FAST_CHECK)
                if ret:
                    # pattern found
                    cv2.cornerSubPix(imgGray, corners, self._sub_pix_size, (-1,-1), self._criteria)
                    self._image_list.append(corners)
                    self._object_list.append(self._object_point)
                cv2.drawChessboardCorners(imgBGR, self._pattern_size, corners, ret)
                cv2.imshow('chess', imgBGR)
                cv2.waitKey(10)

        err, self._cameraMatrix, self._distCoeffs, rves, tvecs = cv2.calibrateCamera(self._object_list, self._image_list, \
                                                          im_size[::-1], None, None)
        print '    error: %.4f'%err
        self.calc_rate()
        print 'saving camera info...'
        self.save_camera_info(self._cameraMatrix, self._distCoeffs[0])
        cv2.destroyAllWindows()
        return True


    def calc_rate(self):
        '''
        calculate rate of image point -> object point
        '''
        # undistort image
        cv2.destroyAllWindows()
        src_img = cv2.imread(self._file_list[0])
        remaped = cv2.undistort(src_img, self._cameraMatrix, self._distCoeffs)

        # choose two points
        print 'choose two points by mouse'
        win_name = "click_to_choose_2_points"
        cv2.namedWindow(win_name)
        cv2.imshow(win_name, remaped)
        cv2.waitKey(1)

        mo = mouse(win_name)
        mo.update_message(remaped, 1, (0,0))
        mo.activate_mouse()
        while mo._active_mouse:
            cv2.waitKey(1)

        # input geometry distance
        real_dist = float(raw_input('input the real distance of two points (mm): '))
        image_dist = math.sqrt(math.pow(mo._position[0][0]-mo._position[1][0],2) + \
                               math.pow(mo._position[0][1]-mo._position[1][1],2))
        self._pixel2mm = real_dist / image_dist
        print 'distance in image: %.2f'%image_dist
        print 'distance in real world: %.2f'%real_dist
        print 'pixel to world: %.2f'%self._pixel2mm


    def save_camera_info(self, matrix, dist):
        '''
        cameraMatrix
            f_x 0  c_x
            0  f_y c_y
            0   0   1

        distCoeffs
            k1, k2, p1, p2, k3
        '''
        mtx = {"f_x":matrix[0][0], "c_x":matrix[0][2], "f_y":matrix[1][1], "c_y":matrix[1][2]}
        distCf = {"k1":dist[0], "k2":dist[1], "k3":dist[4], "p1":dist[2], "p2":dist[3]}
        rate = {"pixel2mm":self._pixel2mm}

        with open(self._infoFile, 'w') as jsFile:
            json.dump([mtx, distCf, rate], jsFile)

        print 'camera info saved to %s'%self._infoFile

'''
def main():
    basePath = 'C:/Users/yayo/Desktop/calibrate'
    chessImgDir = basePath + '/sqare/'
    describeFile = basePath + '/describe.json'
    infoFile = basePath + '/sqare_caminfo.json'

    cal = calibrate(chessImgDir, describeFile, infoFile)
    cal.loadDescribeFile()
    cal.loadImageFile()
    cal.calibrate_it()


if __name__ == '__main__':
    main()
'''