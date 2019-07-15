## Description
The main goal of our project is to detect strange behavior using a camera. The strange behaviour is determined by situation in which chosen objects go out of the borders or disappear from the camera view. Also our system can find some objects without selecting (the list of objects is presented in coco.names).
	
## Getting Started:
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

## Installing

Clone this Github repository
Open yolo_gui file

## Usage:

To start/stop a video press 'Play'.
[main menu](https://github.com/zavideeva/Strange-Behaviour/blob/master/screenshots/main_menu.jpg)

This is how it displayed:
[video started](https://github.com/zavideeva/Strange-Behaviour/blob/master/screenshots/video_started.jpg)

To run yolo to find objects press 'Search', later press 'Play'.
[search](https://github.com/zavideeva/Strange-Behaviour/blob/master/screenshots/search_objects.jpg)


To add new object to list of tracking items: 

	select boundaries for object. 
[select boundaries](https://github.com/zavideeva/Strange-Behaviour/blob/master/screenshots/set_border.jpg)

	select object itself. 
[select target](https://github.com/zavideeva/Strange-Behaviour/blob/master/screenshots/select_target.jpg)

	add name in text label and press 'Add'.
[add name](https://github.com/zavideeva/Strange-Behaviour/blob/master/screenshots/add_name.jpg)

Object tracking: targets rounded by a blue square
[target detected](https://github.com/zavideeva/Strange-Behaviour/blob/master/screenshots/target_detected.jpg)

To remove object from tracking items press item's name in object list, press 'Remove'
[remove target](https://github.com/zavideeva/Strange-Behaviour/blob/master/screenshots/remove_selected.jpg)

## Built With
PyQt5
OpenCV
Numpy
## Authors

* **Kazybek Askarbek** - *Graphical User Interface* - [QazyBi](https://github.com/QazyBi)
* **Alena Zavideeva** - *Object tracking* - [Zavideeva](https://github.com/zavideeva)
* **Leonid Tyurin** - *YOLO object detection* - [LyzeOfKiel](https://github.com/LyzeOfKiel)
* **Tagir** - *Action Recognition* - [tagirium](https://github.com/tagirium)


