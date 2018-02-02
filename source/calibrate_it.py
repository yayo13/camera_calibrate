#!/usr/bin/env python
# -*- coding:utf-8 -*-

from calibrate_camera import calibrate

basePath = 'C:/Users/yayo/Desktop/calibrate'
chessImgDir = basePath + '/sqare/'
describeFile = basePath + '/describe.json'
infoFile = basePath + '/sqare_caminfo.json'

cal = calibrate(chessImgDir, describeFile, infoFile)
cal.loadDescribeFile()
cal.loadImageFile()
cal.calibrate_it()