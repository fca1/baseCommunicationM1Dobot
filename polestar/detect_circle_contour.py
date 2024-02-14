import numpy as np
import cv2


def measure_position_center_normalized(show=False) -> tuple:
    vid = cv2.VideoCapture(-1)

    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    bilateral_filtered_image = cv2.bilateralFilter(frame, 5, 175, 175)
    cv2.imshow('Bilateral', bilateral_filtered_image)
    edge_detected_image = cv2.Canny(bilateral_filtered_image, 50, 200)
    #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    #thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    if show:
        cv2.imshow('Edge', edge_detected_image)
    contours,_= cv2.findContours(edge_detected_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour_list = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True)
        area = cv2.contourArea(contour)
        if ((8<len(approx) ) & (area > 1000) ):
            M = cv2.moments(contour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            continue
        print(f"{len(approx)} and area={area}")
        contour_list.append(contour)
        if show:
            cv2.circle(frame, (cX, cY), 1, (0, 0, 255), 3)
        break  # ne prendre que le premier
    if show:
        cv2.drawContours(frame, contour_list,  -1, (255,0,0), 2)
        cv2.imshow('Objects Detected',frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    rY,rX = edge_detected_image.shape
    return None if not contour_list else (cX/rX,cY/rY)

if __name__ == "__main__":
    cXY = measure_position_center_normalized(True)
    pass