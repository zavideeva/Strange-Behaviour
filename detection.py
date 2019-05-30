import cv2


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


def run():
    while True:
        print('To quit press q')
        print('Do you want to connect to webcam? y/n')
        ans = input()
        if ans == 'y':
            cam = cv2.VideoCapture(0)
            for i in range(5):
                ok, frame = cam.read()
            break
        elif ans == 'n':
            print('Enter name of video')
            name = input()
            cam = cv2.VideoCapture(name)
            break
        elif ans == 'q':
            print('Finishing program')
            return 1
        else:
            print('Try again')

    if not cam.isOpened():
        print('Could not open video')
        return 0
    ok, frame = cam.read()
    if not ok:
        print('Could not read video file')
        return 0
    print("How many objects do you want to detect?")
    ans = input()
    if ans.isdecimal():
        ans = int(ans)
    else:
        ans = 0
    objects = []
    for i in range(ans):
        objects.append(choose_region_detection(frame))
    amount_objects = len(objects)
    all_trackers = []
    for i in range(amount_objects):
        all_trackers.append(track_object(objects[i][0], frame))
    while True and ans != 0:
        ready, frame = cam.read()
        if not ready:
            print("Video ends")
            break
        for i in range(amount_objects):
            upd, obj = all_trackers[i].update(frame)
            if upd:
                x1 = (int(obj[0]), int(obj[1]))
                x2 = (int(obj[0] + obj[2]), int(obj[1] + obj[3]))
                if (objects[i][1] != None) and (not is_object_inside(objects[i][1], x1+x2)):
                    print("WARNING: OBJECT IS OUTSIDE OF BORDERS")
                    print("Borders: ", objects[i][1])
                    print("Coord: ", x1 + x2)
                cv2.rectangle(frame, x1, x2, (255, 0, 0), 2, 1)
        cv2.imshow("Track object", frame)
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break
    print("Exit from program")
    cam.release()
    cv2.destroyAllWindows()
    return 1


def track_object(coord, image):
    object_ = tuple(coord)
	#choosed MIL
    cur_tracker = create_tracker(0)
    init = cur_tracker.init(image, object_)
    return cur_tracker


def choose_region_detection(image):
    coords = cv2.selectROI("Tracking", image)
    print("Do you want to select borders? y/n")
    ans = input()
    if ans == 'y':
        while True:
            print("Choose borders")
            borders = choose_border(image)

            if not is_object_inside(borders, coords):
                print("Object is out of borders")
            else:
                break
            break
        return [coords, borders]
    return [coords, None]


def choose_border(image):
    coord = cv2.selectROI("Borders", image)
    right_coord = (coord[0], coord[1], coord[0] + coord[2], coord[1] + coord[3])
    return right_coord


def is_object_inside(borders, obj):
    b_x1, b_y1, b_x2, b_y2 = borders
    x3, y3, x4, y4 = obj
    return (b_x1 < x3) and (b_y1 < y3) and (x4 < b_x2) and (y4 < b_y2)


if __name__ == '__main__':
    run()
