import numpy as np
import cv2



def measure_position_center_normalized(show=False) -> tuple:

    # Capture the video frame
    # by frame
    #vid.release()
    vid = cv2.VideoCapture(-1)
    vid.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
    ret, frame = vid.read()
    vid.release()
    bilateral_filtered_image = cv2.bilateralFilter(frame, 100, 175, 175)
    #bilateral_filtered_image = cv2.GaussianBlur(bilateral_filtered_image, (5, 5), 0)
    hsv = cv2.cvtColor(bilateral_filtered_image, cv2.COLOR_BGR2HSV)
    h,s,v= cv2.split(hsv)
    ret_h, th_h = cv2.threshold(h,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    ret_s, th_s = cv2.threshold(s,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    ret_v, th_v = cv2.threshold(s,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    th=cv2.bitwise_or(th_h,th_s)
    #Ajouts de bord à l'image
    bordersize=0
    th=cv2.copyMakeBorder(th, top=bordersize, bottom=bordersize, left=bordersize, right=bordersize, borderType= cv2.BORDER_CONSTANT, value=[0,0,0] )
    #Remplissage des contours
    im_floodfill = th.copy()
    h, w = th.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(im_floodfill, mask, (0,0), 255)
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)
    th = th | im_floodfill_inv
    #Enlèvement des bord de l'image
    th=th[bordersize: len(th)-bordersize,bordersize: len(th[0])-bordersize]
    resultat=cv2.bitwise_and(frame,frame,mask=th)

    #edge_detected_image = cv2.Canny(bilateral_filtered_image, 50, 100)
    #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    #thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    if show:
        cv2.imshow('Edge', im_floodfill_inv)
        cv2.imshow('Bilateral', bilateral_filtered_image)
    contours,_= cv2.findContours(im_floodfill_inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour_list = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour,0.02*cv2.arcLength(contour,True),True)
        area = cv2.contourArea(contour)
        if ( area > 20000 ):
            M = cv2.moments(contour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            print(f"YES {len(approx)} and area={area}")
        else:
            print(f"{len(approx)} and area={area}")
            continue
        contour_list.append(contour)
        if show:
            cv2.circle(frame, (cX, cY), 1, (0, 0, 255), 3)
        break  # ne prendre que le premier
    if show:
        cv2.drawContours(frame, contour,  -1, (255,0,0), 2)
        cv2.imshow('Objects Detected',frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    rY,rX = im_floodfill_inv.shape
    return None if not contour_list else (2*(cX/rX-0.5),2*(cY/rY-0.5))

if __name__ == "__main__":
    while True:
        cXY = measure_position_center_normalized(True)
    pass