import numpy as np
import cv2
import sys
from os import walk


# wrapper for a functionality that finds the ROI for a face in an image
class FaceDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # detect the face in the given image
    # return ROI (cropped image) that defines the face region, as well as the rotation of the ROI
    # this ROI can be rotated to make the face appear more upright
    # if there are multiple faces in the image, return the first one
    def detect_face(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        angles = [0, 10, -10, 20, -20, 30, -30]
        for a in angles:
            img_rotated, _ = rotate_image(img, degreesCCW=a)
            gray_rotated, _ = rotate_image(gray, degreesCCW=a)
            faces = self.face_cascade.detectMultiScale(gray_rotated, 1.2, 5)
            if len(faces) > 0:
                area_largest = float("-inf")
                best = -1
                for i in range(len(faces)): # if multiple ROIs are detected pick the largest one
                    x, y, w, h = faces[i]
                    area = w * h
                    if area > area_largest:
                        area_largest = area
                        best = i
                x, y, w, h = faces[best]
                roi = img_rotated[int(y):int(y+h), int(x):int(x+w)]
                return roi, a
        sys.stderr.write("Warning: FaceDetector: no face detected\n")
        return None, 0


# a utility tool used to rotate images to detect angled faces
# returns the rotated image as numpy array and the affine transformation matrix
def rotate_image(img, scaleFactor=1, degreesCCW=30):
    # note: numpy uses (y,x) convention but most OpenCV functions use (x,y)
    (oldY, oldX) = img.shape[:2]
    # rotate about center of image
    M = cv2.getRotationMatrix2D(center=(oldX/2,oldY/2), angle=degreesCCW, scale=scaleFactor)
    # choose a new image size.
    newX, newY = oldX * scaleFactor, oldY * scaleFactor
    # include this if you want to prevent corners being cut off
    r = np.deg2rad(degreesCCW)
    newX, newY = (abs(np.sin(r)*newY) + abs(np.cos(r)*newX), abs(np.sin(r)*newX) + abs(np.cos(r)*newY))

    # the warpAffine function call, below, basically works like this:
    # 1. apply the M transformation on each pixel of the original image
    # 2. save everything that falls within the upper-left "dsize" portion of the resulting image.

    # So I will find the translation that moves the result to the center of that region.
    (tx,ty) = ((newX-oldX)/2,(newY-oldY)/2)
    M[0,2] += tx # third column of matrix holds translation, which takes effect after rotation.
    M[1,2] += ty

    rotatedImg = cv2.warpAffine(img, M, dsize=(int(newX),int(newY)))
    return rotatedImg, M


# if __name__ == "__main__":
#     fd = FaceDetector()
#     path = "./images/set1/"
#     _, _, filenames = next(walk(path))
#     filenames.sort()
#     for f in filenames:
#         img = cv2.imread(path + f)
#         face, _ = fd.detect_face(img)
#         if face is None:
#             continue
#         cv2.imshow("face", face)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()

