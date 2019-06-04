import cv2


class TrackableObject:
    tracker = None
    borders = None
    cam_borders = None
    object_not_found = 0

    def __init__(self, coords, name='Object'):
        self.name = name
        self.coords = tuple(coords)

    def init_tracker(self, image):
        self.tracker = create_tracker(4)
        init_track = self.tracker.init(image, self.coords)

    def is_object_inside_borders(self):
        b_x1, b_y1, b_x2, b_y2 = self.borders
        x1, y1, x2, y2 = self.coords
        return (b_x1 < x1) and (b_y1 < y1) and (x2 < b_x2) and (y2 < b_y2)

    def is_object_inside_cam_borders(self):
        b_x1, b_y1, b_x2, b_y2 = self.cam_borders
        x1, y1, x2, y2 = self.coords
        return (b_x1 < x1) and (b_y1 < y1) and (x2 < b_x2) and (y2 < b_y2)

    def detect_obj(self, ans):
        if not ans:
            self.object_not_found += 1
        else:
            self.object_not_found = 0
        if self.object_not_found > 20:
            print("WARNING:{} IS NOT FOUND!!!".format(self.name))

    def set_borders(self, coords):
        self.borders = coords

    def set_cam_borders(self, camera):
        width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.cam_borders = (0, 0, width, height)


def create_tracker(index):
    # types of trackers
    tracker_types = ("MIL", "KCF", "Boosting", "CSRT", "MedianFlow", "MOSSE")
    # set type of tracker
    cur_type = tracker_types[index]

    if cur_type == "MIL":
        return cv2.TrackerMIL_create()
    elif cur_type == "KCF":
        # faster FPS throughput, but handles slightly lower
        # object tracking accuracy
        return cv2.TrackerKCF_create()
    elif cur_type == "Boosting":
        return cv2.TrackerBoosting_create()
    elif cur_type == "CSRT":
        # higher object tracking accuracy, low FPS throughput
        return cv2.TrackerCSRT_create()
    elif cur_type == "MedianFlow":
        return cv2.TrackerMedianFlow_create()
    elif cur_type == 'MOSSE':
        # perfect for pure speed
        return cv2.TrackerMOSSE_create()
    else:
        return cv2.TrackerMIL_create()


def init_obj_detection(objects_map, img):
    objects = []
    for key in objects_map:
        obj = TrackableObject(objects_map[key], key)
        obj.init_tracker(img)
        objects.append(obj)
    return objects


def get_first_point(coords):
    return coords[0], coords[1]


def get_second_point(coords):
    return coords[2], coords[3]


def tracking(camera, objects):
    while True:
        ready, img = camera.read()
        if not ready:
            print("Video ends")
            break
        for i in range(len(objects)):
            upd, obj = objects[i].tracker.update(img)
            if upd:
                objects[i].detect_obj(True)
                x1 = (int(obj[0]), int(obj[1]))
                x2 = (int(obj[0] + obj[2]), int(obj[1] + obj[3]))
                objects[i].coords = x1 + x2
                if objects[i].borders and not objects[i].is_object_inside_borders():
                    print("WARNING: OBJECT IS OUTSIDE OF BORDERS")
                cv2.rectangle(img, x1, x2, (255, 0, 0), 2, 1)
                cv2.putText(img, objects[i].name, get_first_point(objects[i].coords), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255))
                if objects[i].borders:
                    cv2.rectangle(img, get_first_point(objects[i].borders), get_second_point(objects[i].borders), (0, 255, 0), 2, 1)
                if not objects[i].is_object_inside_cam_borders():
                    print("WARNING: OBJECT IS OUTSIDE THE CAMERA VIEW")
            else:
                objects[i].detect_obj(False)
        cv2.imshow("Track object", img)
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break


def detect(object_map, camera, img):
    objs = init_obj_detection(object_map, img)
    tracking(camera, objs)


if __name__ == '__main__':
    # Testing
    cam = cv2.VideoCapture("video.mp4")
    # cam = cv2.VideoCapture("http://192.168.0.158:4747/video")
    for i in range(5):
        ok, frame = cam.read()

    r = cv2.selectROI("Tracking object", frame)
    r1 = (int(r[0]), int(r[1]))
    r2 = (int(r[0] + r[2]), int(r[1] + r[3]))
    obj1 = TrackableObject(r, "Human")
    obj1.init_tracker(frame)
    cv2.rectangle(frame, r1, r2, (0, 255, 0), 2, 1)
    b = cv2.selectROI("Borders", frame)
    b1 = (int(b[0]), int(b[1]))
    b2 = (int(b[0] + b[2]), int(b[1] + b[3]))
    obj1.set_borders(b1+b2)
    obj1.set_cam_borders(cam)
    tracking(cam, [obj1])
    cam.release()
    cv2.destroyAllWindows()
