import math
import numpy as np
import cv2

class Config_Cam():
    """
    Build trackbar from list of attributes names for configuration.
    Parameters 3 lists:
        names: names of attributes of cam.
        values: current value of attribute
        counts: max values of attributes
    """

    def __init__(self,**dict):
        def nothing(x):
            pass
        #Get list of names of attributes to config
        self.names=dict['names']
        #Get list of values of attributes to config
        self.values=dict['values']
        #Get list of counts of attributes to config
        self.counts=dict['counts']
        #Predefine window name
        cv2.namedWindow('image')
        for i in range(len(self.names)):
            #Create trackbars from all the names each one is called with a
            #name from the list params(nameOfTrackbar,windowName,currentValue,countValue,callBackName)
            cv2.createTrackbar(self.names[i], 'image', self.values[i],self.counts[i],nothing)

    def on_track(self,x):
        pass

    def main(self):
        cap = cv2.VideoCapture(0)
        #Define a dictionary that will hold the variables of the exact value
        #of the configed parameter
        myDic={}
        while True:
            self.ret,self.img =cap.read()
            #Wait to show the image
            k = cv2.waitKey(10) & 0xFF
            #Escape breaks the program
            if k == 27:
                break
            #Iterate names
            for n in (self.names):
                #Set value of dictionary to value of slider parameters name of bar, name of window
                myDic[n]=cv2.getTrackbarPos(n,'image')
                #Set the name of attribute in a way that opencv understand
                #for example:cv2.CAP_PROP_CONTRAST
                attr='cv2.CAP_PROP_'+n.upper()
                #Set the desired value to the camera, ranges of these attributes are 0:1
                #and the sliders values are 0:100 so we scale it by 1/100
                # the eval method change from string to object.
                cap.set(eval(attr),myDic[n])
            #Show video with configed cam on the predefined window parameters winName,frame
            cv2.imshow('image',self.img)

class DetectColor():
    """
    Dynamic tracking system. The user chooses with the left button of the mouse which
    color to track.
    Parameters: None.
    Return: None.
    """
    def __init__(self):
        cv2.namedWindow('img')
        cv2.setMouseCallback('img',self.get_color)
        #Variable that enable the tracking only after the first click.
        self.firstClick=False

    def get_color(self,event,x,y,flags,param):
        #if left mouse was clicked
        if event == cv2.EVENT_LBUTTONDOWN:
            self.x=x
            self.y=y
            self.firstClick=True
            #Variable that enable the computation of the color to track only once
            #after each click
            self.notClickedYet = True

    def main(self):
        #Enable video
        cap = cv2.VideoCapture(0)
        while True:
            #Read from camera
            _, frame = cap.read()
            #Show stream on 'img' window
            cv2.imshow('img', frame)
            #Wait to show stream
            k = cv2.waitKey(10) & 0xFF
            #Escape breaks the code
            if k == 27:
                break
            if self.firstClick:
                #Convert image to hsv format.
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                if self.notClickedYet:
                    #Lower bound is determined by taking the h value and subtracting 10
                    #and s and v values are fixed to 50
                    lower=np.array([max(0, hsv[self.y, self.x][0]-10), 50, 50])
                    #Upper bound is determined by taking the h value and adding 10
                    #and s and v values are fixed to 255
                    upper=np.array([min(180, hsv[self.y, self.x][0])+10, 255, 255])
                    self.notClickedYet=False
                #Mask of 0 and 1 of the pixels within the range between lower and upper
                mask = cv2.inRange(hsv, lower, upper)
                #Apply the mask to the original pic
                res = cv2.bitwise_and(frame,frame, mask= mask)
                #Show the mask
                cv2.imshow('mask', mask)
                #Show the tracked color
                cv2.imshow('res', res)
        cv2.destroyAllWindows()

class FetureMatch:
    """
    Use Orb, Brisk, Kaze, Akaze methods to detect a predefined object.
    Parameters:
        modes: list of methods
        img2Find: A croped image we have 2 find
        img2Search: An image contains few objects includes the croped one.
    Methods:
        compute: Computes the center of mass of the predefined object
        show: Show the img2Search with box around the img2Find
        getCm: Returns dictionary key=methodName value=centerOfMass,#goodPoints
    """

    def __init__(self, modes, img2Find, img2Search):
        self.MIN_MATCH_COUNT = 8
        self.img1 = cv2.imread(img2Find)  # queryImage
        self.img2 = cv2.imread(img2Search)  # trainImage
        self.modes = modes
        # Dictinary for center of masses key=mode val=cm
        self.cms = {}

    def compute(self, flage=None):
        # Convert images to gray scale  cv2.cvtColor
        gray1 = cv2.cvtColor(self.img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(self.img2, cv2.COLOR_BGR2GRAY)
        # Dictinary for center of masses key=mode val=cm
        myDic = {}
        # Declare distance type 4 the matcher to orb and brisk.
        distanceType = cv2.NORM_HAMMING
        for mode in self.modes:
            # All modes have same signature cv2.mode_create() mode is defined in big letters.
            # Parameters: orb:nfeatures=10000, brisk:thresh=10, kaze and akaze:distanceType:cv2.DIST_L2
            # ToDo declare all detectors
            if mode == 'orb':
                detector = cv2.ORB_create(nfeatures=1000)
            elif mode == 'brisk':
                detector = cv2.BRISK_create(thresh=10)
            elif mode == 'kaze':
                detector = cv2.KAZE_create()
                distanceType = cv2.DIST_L2
            elif mode == 'akaze':
                detector = cv2.AKAZE_create()
            # Declare matcher
            matcher = cv2.BFMatcher(distanceType)
            # kp pos of keyPoints, des descriptors interesting points.
            kp1, des1 = detector.detectAndCompute(gray1, None)
            kp2, des2 = detector.detectAndCompute(gray2, None)
            matches = matcher.knnMatch(des1, des2, k=2)
            good = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good.append(m)
            if len(good) > self.MIN_MATCH_COUNT:
                src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                h, w = gray1.shape
                pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)
                # Flatten the points of the object to a list.
                rvl = dst.ravel()
                cmx = cmy = nPts = 0
                # Calculate the center of mass
                # Traverse the Flatten list of points
                cmx = np.mean(dst[:, 0, 0])
                cmy = np.mean(dst[:, 0, 1])
                # Convert center of mass to integers (pixels)
                self.cm = (int(cmx), int(cmy))
                # Update dictionary cms with the cm position and the number of
                # good points in every method.
                self.cms[mode] = ((cmx, cmy), len(good))
                # Draw green poligon around the searched object on the original picture
                self.img2 = cv2.polylines(self.img2, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA)
                # Draw blue circle of the C.M on the original image
                # circle(img,pos,radius,color,thikness
                self.img2 = cv2.circle(self.img2, self.cm, 5, (255, 0, 0), 5)
            else:
                print("mode=%s ,Not enough matches are found - %d/%d" % (mode, len(good), self.MIN_MATCH_COUNT))

    def show(self):
        """
        Shows the boxed colored detected object in the searched image
        :return:
        """
        self.compute()
        cv2.imshow('Colored Detected Object', self.img2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def getCm(self):
        """

        :return: dictionary with the method as key, center of mass and #good matches
        as a tuple value
        """
        return self.cms


class Crop:
    """
    Draws rect with mouse, crop image
    according to the rect.
    Operate: instance.main(pathRead, pathWrite)
    parameters:
    pathRead: raw image
    pathWrite: cropped image
    left button draws rectangle
    right button crop
    """
    def __init__(self, path, n):
        self.path = path
        self.n = n
        self.startY=0
        self.startX=0

    def draw_rect(self, event, x, y, flags, param):
        # Left mouse press: start drawing
        if event == cv2.EVENT_LBUTTONDOWN:
            self.startX, self.startY = x, y
            self.drawing = True  # Start dynamic drawing
            #print(f"startX{self.startX},startY:{self.startY}")
        # Mouse move: update rectangle while dragging
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            temp_img = self.img.copy()
            cv2.rectangle(temp_img, (self.startX, self.startY), (x, y), (0, 255, 0), 1)
            cv2.imshow('image', temp_img)

        # Left mouse release: stop drawing
        elif event == cv2.EVENT_LBUTTONUP:
            self.x, self.y = x, y
            self.drawing = False
            # Draw the final rectangle
            cv2.rectangle(self.img, (self.startX, self.startY), (self.x, self.y), (0, 255, 0), 1)
            cv2.imshow('image', self.img)

        # Right double-click: reset image
        elif event == cv2.EVENT_RBUTTONDBLCLK:
            self.img = self.original_img.copy()
            cv2.imshow('image', self.img)

        # Right mouse button: crop and save the image
        elif event == cv2.EVENT_RBUTTONDOWN:
            if not (self.startX and self.startY and self.x and self.y):
                print("No valid region selected for cropping.")
                return

            # Ensure coordinates are sorted correctly
            sortx = sorted([self.startX, self.x])
            sorty = sorted([self.startY, self.y])

            # Crop from the original (unmodified) image
            cropped_img = self.original_img[max(sorty[0], 0):min(sorty[1], self.original_img.shape[0]),
                          max(sortx[0], 0):min(sortx[1], self.original_img.shape[1])]

            if cropped_img.size == 0:
                print("No valid region to crop.")
            else:
                cv2.imwrite(self.path, cropped_img)
                print(f"Cropped image saved at: {self.path}")



    """
    Computes center of mass of n objects
    parameters:
        path: path to pic
        n: Number of objects
    """

    def compute(self):
        """
        Computes the center of mass for the n largest contours using moments.
        """
        im = cv2.imread(self.path)
        imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(imgray, 127, 255, cv2.THRESH_BINARY_INV)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        mmuyan = sorted(contours, key=lambda c: cv2.arcLength(c, True), reverse=True)

        self.cms = []
        self.angles = []

        for i in range(min(self.n, len(mmuyan))):
            rect = cv2.minAreaRect(mmuyan[i])
            box = cv2.boxPoints(rect)
            box = np.int64(box)  # Fix applied here

            angle = self.comp_angle(box)

            self.pic = cv2.drawContours(im, [box], 0, (0, 0, 255), 2)
            M = cv2.moments(mmuyan[i])
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                cx_original = cx + self.startX
                cy_original = cy + self.startY
                print(cx_original,cx,self.startX)
                self.pic = cv2.circle(self.pic, (cx, cy), 3, (0, 255, 0), 2)
                cv2.putText(self.pic, str(round(angle, 2)), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 2)
                self.cms.append((cx_original, cy_original))
                self.angles.append(angle)

    def show(self):
        """
        Shows the image with contours and centroids.
        """
        self.compute()
        cv2.imshow('pic', self.pic)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_cm(self):
        """
        Returns the list of centers of mass of n objects.
        """
        self.compute()
        return self.cms

    def comp_angle(self, box):
        """
        Computes the angle of the object.
        :param box: Contour bounding box
        :return: Angle of the narrow side of the object
        """
        dist1 = np.linalg.norm(box[1] - box[0])
        dist2 = np.linalg.norm(box[3] - box[0])
        if dist1 < dist2:
            cos = np.dot((box[1] - box[0]), (10, 0)) / (dist1 * 10)
            return np.degrees(np.arccos(cos))
        cos = np.dot((box[3] - box[0]), (10, 0)) / (dist2 * 10)
        return np.degrees(np.arccos(cos))

    def get_angles(self):
        """
        Returns the list of angles of n objects.
        """
        self.compute()
        return self.angles

    def main(self, pathRead, pathWrite):
        self.img = cv2.imread(pathRead)
        self.original_img = self.img.copy()  # Keep an unmodified version
        self.path = pathWrite
        self.drawing = False  # Initialize drawing state
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.draw_rect, param=pathRead)
        while True:
            cv2.imshow('image', self.img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:  # ESC to exit
                break
        cv2.destroyAllWindows()








def savePic(path='img1.jpg', flag=None):
    """
    Show stream; press 's' to save an image, 'q' to quit.
    Parameters:
        path: Path to save the image
        flag: Optional flag for image conversion (not used here)
    """
    cap = cv2.VideoCapture(0)  # Open the default camera
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    while True:
        # Capture a frame from the camera
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame from the camera.")
            break

        # Display the video feed
        cv2.imshow('Video Feed', frame)

        # Wait for key press
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):  # Save the frame when 's' is pressed
            if frame is not None:
                try:
                    cv2.imwrite(path, frame)
                    print(f"Image saved at: {path}")
                except Exception as e:
                    print(f"Error saving image: {e}")
            else:
                print("No frame to save!")
        elif key == ord('q'):  # Quit the program when 'q' is pressed
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
