import cv2
import numpy as np
from age_predictor import AgePredictor
from os import walk


class Sorter:
    # path specifies a directory that contains all the face images to be sorted
    # only accepts JPEG files!!
    # these images will be read as numpy arrays and stored in a list
    def __init__(self, path):
        # each item in the list in an entry for an image:
        ## [path+filename, color_image, predicted_age, face_roi, face_roi_angle]
        ## path+filename: this is the unique path that identifies where the image is
        ## color_image: the result of cv2.imread(path+filename)
        ## predicted_age: a number that is returned by the age model
        ## face_roi: a rectangular region of the image that contains the face
        ## face_roi_angle: face_roi rectangle might not be upright, so a rotation angle must be specified
        self.images = list()
        # age predictor
        self.ap = AgePredictor()
        # walk the given path directory and read the images
        # store all the images in the list
        _, _, filenames = next(walk(path))
        filenames.sort()
        for f in filenames:
            if f[-5:] != ".jpeg": continue
            self.images.append([path + f, cv2.imread(path + f), -1, None, 0])


    # sorts the set of images based on age
    # this function assumes that the ages haven't been computed yet
    # should only call this function ONCE per Sorter!
    def sort(self):
        for image in self.images:
            image[2], image[3], image[4] = self.ap.predict_age(image[1])
        self.images.sort(key=lambda image: image[2])


    # list all entries, everything
    def list_all(self):
        return self.images

    # list only the images (numpy arrays)
    def list_all_images(self):
        return list(map(lambda image: image[1], self.images))


# if __name__ == "__main__":
#     sorter = Sorter("./images/set3/")
#     sorter.sort()
#     images_sorted = sorter.list_all()
#     for i in images_sorted:
#         winname = i[0] + ": " + str(i[2]) + " years old"
#         h, w, _ = i[1].shape
#         sf = 400 / h
#         dsize = (int(w * sf), 400)
#         cv2.namedWindow(winname)
#         cv2.moveWindow(winname, 40,30)
#         cv2.imshow(winname, cv2.resize(i[1], dsize))
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()
