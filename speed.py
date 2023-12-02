import random

import cv2
import numpy as np
import argparse

argParser = argparse.ArgumentParser()
argParser.add_argument("-f", "--file", help="enter file path", default=0)
argParser.add_argument("-c", "--constant", help="enter constant", default=7.8)
args = argParser.parse_args()
constant = float(args.constant)
file_name = args.file
try:
    cap = cv2.VideoCapture(file_name)
except AttributeError:
    raise AttributeError("Please enter a valid file path")
points = []
ret, prev_frame = cap.read()
og = prev_frame.copy()
cap.release()


def mouse_callback(event, x, y, flags, param):
    global prev_frame

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        if len(points) % 4 == 0:
            # Create a polygon
            polygon = np.array(points[-4:], np.int32)
            polygon = polygon.reshape((-1, 1, 2))

            # Fill the polygon on a separate blank image
            polygon_image = np.zeros_like(prev_frame)
            cv2.fillPoly(polygon_image, [polygon],
                         (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

            prev_frame = cv2.addWeighted(prev_frame, 1, polygon_image, 0.6, 0.3)
            # Display the image with the blended polygon
            cv2.imshow('Image with Polygon', prev_frame)


def get_polygon_points():
    cv2.namedWindow('Image with Polygon')
    cv2.setMouseCallback('Image with Polygon', mouse_callback)
    cv2.imshow('Image with Polygon', prev_frame)
    cv2.waitKey(0)
    cv2.destroyWindow('Image with Polygon')
    return points


def masks(points_poly, frame=og):
    h = []
    copy_frame = np.zeros_like(frame)
    for point_ in points_poly:
        mask = np.zeros_like(frame)
        mask = cv2.fillPoly(mask, [np.array(point_, np.int32)], (255, 255, 255))
        mask = cv2.bitwise_and(frame, mask)
        h.append(mask)
    # for i in h:
    #     cv2.add(copy_frame, i, copy_frame)
    return h


if __name__ == '__main__':
    pts = get_polygon_points()
    # GROUPING THE POINTS INTO 4
    set_poly = []
    for i in range(0, len(pts), 4):
        set_poly.append(pts[i:i + 4])
    cap = cv2.VideoCapture(file_name)
    ret, frame1 = cap.read()
    prvs = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    prvs = masks(set_poly, prvs)
    hsv = np.zeros_like(frame1)
    hsv[..., 1] = 255
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        next = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        next = masks(set_poly, next)
        motion_sum = [0 for i in range(len(next))]
        all_optic = []
        for i in range(len(next)):
            flow = cv2.calcOpticalFlowFarneback(prvs[i], next[i], None, 0.5, 3, 3, 2, 5, 1.2, 2)
            mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            hsv[..., 0] = ang * 180 / np.pi / 2
            hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
            rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            all_optic.append(rgb)
            motion_sum[i] = np.sum(mag)
        f = np.zeros_like(frame)
        for i in all_optic:
            cv2.add(f, i, f)
        # cv2.imshow('frame', f)
        # show the motion sum on the frame
        for i in range(len(motion_sum)):
            speed = round(constant * motion_sum[i] / abs((set_poly[i][2][0] - set_poly[i][0][0]) * (set_poly[
                                                                                                   i][2][
                                                                                                   1] -
                                                                                               set_poly[i][0][1])), 2)
            if speed <= 15:
                color = (255, 255, 255)
                speed = 0
            elif 80 > speed >= 15:
                color = (0, 255, 255)
            elif 120 > speed >= 80:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
            cv2.putText(frame, str(speed),
                        set_poly[i][0],
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        color, 2)
        # add the polygon to the frame
        for i in range(len(set_poly)):
            cv2.polylines(frame, [np.array(set_poly[i], np.int32)], True, (0, 255, 0), 2)
        # cv2.add(frame, f, frame)
        cv2.addWeighted(frame, 1, f, 4, 0, frame)
        cv2.imshow('frame', frame)
        prvs = next
        # flow = cv2.calcOpticalFlowFarneback(prvs, next, None, 0.5, 10, 15, 3, 5, 1.2, 0)
        # mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        # rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        # cv2.imshow('frame', rgb)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
