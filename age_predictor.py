import numpy as np
import cv2
from face_detector import FaceDetector
from os import walk


# wrapper for a utility that returns the apparent age of a still face image
class AgePredictor:
    def __init__(self):
        # age model
        # model structure: https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/static/age.prototxt
        # pre-trained weights: https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/static/dex_chalearn_iccv2015.caffemodel
        self.age_model = cv2.dnn.readNetFromCaffe("data/age.prototxt", "data/dex_chalearn_iccv2015.caffemodel")
        self.fd = FaceDetector()

    # given an image
    # extract roi using face detector and predict the age using the age model
    # 3 return values:
    ## apparent_age is the model predicted age of the face
    ## roi is the region of the image that contains the face
    ## angle is the rotation angle (in CCW) for the roi
    def predict_age(self, img):
        # extract roi and resize it to the desired dimensions for the age model
        roi, angle = self.fd.detect_face(img)
        if roi is None:
            return -1, None, 0
        roi_resized = cv2.resize(roi, (224, 224))
        img_blob = cv2.dnn.blobFromImage(roi_resized)
        # run it through the model and return predicted age
        self.age_model.setInput(img_blob)
        age_dist = self.age_model.forward()[0]
        output_indexes = np.array([i for i in range(0, 101)])
        apparent_age = round(np.sum(age_dist * output_indexes), 2)
        return apparent_age, roi, angle


# if __name__ == "__main__":
#     ap = AgePredictor()
#     path = "./images/set1/"
#     _, _, filenames = next(walk(path))
#     filenames.sort()
#     for f in filenames:
#         img = cv2.imread(path + f)
#         age, _, _ = ap.predict_age(img)
#         print(f + ": " + str(age))
