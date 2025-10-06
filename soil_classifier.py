import cv2

def classify_soil(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img,(100,100))
    hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    avg_color = hsv.mean(axis=0).mean(axis=0)
    h,s,v = avg_color

    if h<20 and s<50 and v<50:
        return "clay"
    elif h>20 and h<50 and s>50 and v>50:
        return "sandy"
    elif h>20 and h<50 and s>50 and v<50:
        return "loamy"
    else:
        return "silty"
    
    