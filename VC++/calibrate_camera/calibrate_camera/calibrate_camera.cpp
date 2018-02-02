// calibrate_camera.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include "cstring"
#include "io.h"
#include "math.h"

#include "cxcore.h"
#include "cv.h"
#include "highgui.h"

#include "iostream"
#include "fstream"
using namespace std;
using namespace cv;


bool loadImageFile(const char* chess_folder, vector<string>& file_list){
	char dir[256];
	strcpy(dir, chess_folder);
	strcat(dir, "\\*.*");
	
	intptr_t handle;
	_finddata_t findData;

	handle = _findfirst(dir, &findData);
	if(handle == -1){
		cout << "Failed to find file!" << endl;
		return false;
	}

	do{
		if(findData.attrib & _A_SUBDIR){
			// 子目录
			if(strcmp(findData.name, ".") == 0 || strcmp(findData.name, "..") == 0)
				continue;

			strcpy(dir, chess_folder);
			strcat(dir, "\\");
			strcat(dir, findData.name);

			loadImageFile(dir, file_list);
		}
		else{
			string wholePath = chess_folder;
			file_list.push_back(wholePath + "\\" + findData.name);
		}
	}while(_findnext(handle, &findData) == 0);
	_findclose(handle);
	return true;
}

void createObjectPoints(vector<Point3f>& objects, Size board_size, Size square_size){
	objects.clear();
	for(int i=0; i<board_size.height; i++){
		for(int j=0; j<board_size.width; j++){
			Point3f realPoint;
			realPoint.x = j*square_size.width;
			realPoint.y = i*square_size.height;
			realPoint.z = 0;
			objects.push_back(realPoint);
		}
	}
}

bool saveCameraInfo(string filePath, Mat& cameraMatrix, Mat& distCoeff){
	cout << "saving camera info..." << endl;
	ofstream fout(filePath);
	
	cout << "camera matrix" << endl;
	fout << "camera matrix" << endl;
	cout << cameraMatrix << endl;
	fout << cameraMatrix << endl;

	cout << "dist coeffs" << endl;
	fout << "dist coeffs" << endl;
	cout << distCoeff << endl;
	fout << distCoeff << endl;

	return true;
}

bool calibrate(const char* chess_folder, Mat& cameraMatrix, Mat& distCoeff){
	vector<string> file_list;
	if(!loadImageFile(chess_folder, file_list))
		return false;

	vector<Point2f> image_points;
	vector<Point3f> object_points;
	vector<vector<Point2f>> image_points_vec;
	vector<vector<Point3f>> object_points_vec;

	createObjectPoints(object_points, Size(9, 6), Size(30, 30));

	Mat img_bgr, img_gray;
	Size image_size;

	cout << "calibrating..." << endl;
	for(int i=0; i<file_list.size(); i++){
		img_bgr = imread(file_list[i]);
		cvtColor(img_bgr, img_gray, CV_BGR2GRAY);
		image_size = Size(img_gray.cols,img_gray.rows);

		image_points.clear();
		bool ret = findChessboardCorners(img_gray, Size(9, 6), 
			image_points, CV_CALIB_CB_ADAPTIVE_THRESH | CV_CALIB_CB_NORMALIZE_IMAGE);
		
		if(ret){
			// pattern found
			cornerSubPix(img_gray, image_points, Size(5,5), Size(-1,-1), 
				TermCriteria(CV_TERMCRIT_ITER + CV_TERMCRIT_EPS, 30, 0.01));
			image_points_vec.push_back(image_points);
			object_points_vec.push_back(object_points);
		}
		drawChessboardCorners(img_bgr, Size(9, 6), image_points, ret);
		imshow("chess", img_bgr);
		waitKey(10);
	}

	destroyAllWindows();
	if(image_points_vec.size() < 1)
		return false;

	vector<Mat> rvecs, tvecs;
	double err = calibrateCamera(object_points_vec, image_points_vec, image_size, 
		cameraMatrix, distCoeff, rvecs, tvecs);
	cout << "calibrating finished with error "<< err << endl;

	return true;
}


float measure_distance(Mat& cameraMatrix, Mat& distCoeff, Point p1, Point p2){
	vector<Point2f> points, remapedPoints;
	points.push_back(p1);
	points.push_back(p2);

	undistortPoints(points, remapedPoints, cameraMatrix, distCoeff, noArray(), cameraMatrix);
	float distance = sqrt(pow(remapedPoints[0].x - remapedPoints[1].x, 2) + 
		             pow(remapedPoints[0].y - remapedPoints[1].y, 2));

	return distance;
}


void main(){
	char chessImagesPath[] = "C:\\Users\\yayo\\Desktop\\calibrate\\sqare";
	string savePath = "C:\\Users\\yayo\\Desktop\\calibrate\\sqare_caminfo.txt";
	Mat cameraMatrix = Mat(3,3,CV_32FC1, Scalar::all(0));
	Mat distCoeff = Mat(1,5,CV_32FC1, Scalar::all(0));

	if(!calibrate(chessImagesPath, cameraMatrix, distCoeff))
		return;

	saveCameraInfo(savePath, cameraMatrix, distCoeff);

	Mat remaped;
	Mat mapX, mapY;
	Mat image = imread("C:\\Users\\yayo\\Desktop\\calibrate\\sqare\\15.jpg");
	Size im_size = Size(image.cols*2, image.rows*2);
	initUndistortRectifyMap(cameraMatrix, distCoeff, Mat(), Mat(), im_size, CV_32FC1, mapX, mapY);
	remap(image, remaped, mapX, mapY, INTER_LINEAR);

	imshow("source", image);
	imshow("remaped", remaped);

	float rate = 0.682079;   // mm per pixel
	Point p1(222,219), p2(387,294);
	float distance = measure_distance(cameraMatrix, distCoeff, p1, p2);
	cout << "distance: "<<distance*rate<< " mm" <<endl;

	waitKey(0);
}