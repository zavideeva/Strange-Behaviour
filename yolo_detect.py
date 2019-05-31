import numpy as np
import argparse
import cv2
import os

MIN_PROB = 0.4
OVERLAP_THRESHHOLD = 0.2


def find_electric_objects(img_path, yolo_directory_path, min_prob, overlap_threshhold):
    '''
    Returns map of detected objects
    key   - object name
    value - list of coordinates
    :param img_path:
    :param yolo_directory_path:
    :param min_prob:
    :param overlap_threshhold:
    :return:
    '''
    labelsPath = os.path.sep.join([yolo_directory_path, "coco.names"])
    LABELS = open(labelsPath).read().strip().split("\n")

    weightsPath = os.path.sep.join([yolo_directory_path, "yolov3.weights"])
    configPath = os.path.sep.join([yolo_directory_path, "yolov3.cfg"])

    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
    image = cv2.imread(img_path)
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
            if LABELS[classID] in electric_things and confidence > MIN_PROB:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, min_prob, overlap_threshhold)

    names_and_coords = {}
    if len(idxs) > 0:
        for i in idxs.flatten():
            x, y = boxes[i][0], boxes[i][1]
            w, h = boxes[i][2], boxes[i][3]
            names_and_coords[LABELS[classIDs[i]]] = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]

    return names_and_coords



if __name__ == '__main__':
    img_path = 'images/camera_view.jpg'
    print(find_electric_objects(img_path, 'yolo-coco', MIN_PROB, OVERLAP_THRESHHOLD))