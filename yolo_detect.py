import numpy as np
import argparse
import cv2
import os
import detect_object
import time

MIN_PROB = 0.1
OVERLAP_THRESHHOLD = 0.2

"""
All weights and mappings can be found at https://pjreddie.com/darknet/yolo/
"""


class CocoObject:
    def __init__(self, name, coords):
        self.name = name
        self.coords = coords


def find_electric_objects(yolo_directory_path, min_prob, overlap_threshhold, image):
    """
    :param yolo_directory_path:
    :param min_prob:
    :param overlap_threshhold:
    :param image: np array
    :return: list of detected CocoObjects, where
                key   - object name
                value - list of coordinates
    """
    labelsPath = os.path.sep.join([yolo_directory_path, "coco.names"])
    LABELS = open(labelsPath).read().strip().split("\n")

    weightsPath = os.path.sep.join([yolo_directory_path, "yolov3.weights"])
    configPath = os.path.sep.join([yolo_directory_path, "yolov3.cfg"])


    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
    (H, W) = image.shape[:2]

    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    boxes = []
    confidences = []
    classIDs = []
    electric_things = ['tvmonitor', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone']

    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > MIN_PROB and LABELS[classID] in electric_things:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, min_prob, overlap_threshhold)

    names_and_coords = []
    if len(idxs) > 0:
        for i in idxs.flatten():
            x, y = boxes[i][0], boxes[i][1]
            w, h = boxes[i][2], boxes[i][3]
            names_and_coords.append(CocoObject(LABELS[classIDs[i]], (x,y,w,h)))

    return names_and_coords


if __name__ == '__main__':
    img_path = 'videos/walk360.mp4'
    cam = cv2.VideoCapture(img_path)
    ok, image = cam.read()

    start = time.time()
    coco_objects = find_electric_objects('yolo-coco', MIN_PROB, OVERLAP_THRESHHOLD, image)
    end = time.time()
    print("[INFO] YOLO took {:.6f} seconds".format(end - start))
    print(coco_objects)
    print(len(coco_objects))
    for coco_object in coco_objects:
        coords = coco_object.coords
        cv2.rectangle(image, (coords[0], coords[1]), (coords[0] + coords[2], coords[1] + coords[3]), (0, 255, 0))
    detect_object.detect(coco_objects, cam, image)


