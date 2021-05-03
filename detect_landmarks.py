import numpy as np
import dlib
import cv2
# import matplotlib.pyplot as plt


class FaceLandmarkDetector:
    """Detect face landmarks using dlib"""
    PREDICTOR_PATH = './data/shape_predictor_68_face_landmarks.dat'

    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.PREDICTOR_PATH)

    # @staticmethod
    # def plot_landmarks(img, landmarks, show_plot=True):
    #     # convert from BGR (opencv) to RGB (matplotlib)
    #     img = img[..., ::-1]

    #     # display face image
    #     plt.imshow(img)

    #     # plot landmarks
    #     plt.scatter(x=landmarks[:, 0], y=landmarks[:, 1], c='r', s=20, edgecolors='k')

    #     if show_plot:
    #         plt.show()

    def predict(self, img):
        # find how many faces there are and the bounding box for each
        # if there are multiple faces, use the first face
        faces = self.detector(img, 1)
        if len(faces) == 0:
            return np.empty((0, 2), dtype="int")
        landmarks = self.predictor(img, faces[0]).parts()
        # landmarks is a dlib.points object, convert it to np array
        landmarks_np = np.empty((len(landmarks), 2), dtype="int")
        for i in range(len(landmarks)):
            landmarks_np[i] = (landmarks[i].x, landmarks[i].y)
        return landmarks_np


# if __name__ == '__main__':
#     face_filename = './data/head1.jpg'
#     face = cv2.imread(face_filename)

#     d = FaceLandmarkDetector()
#     landmarks = d.predict(face)

#     d.plot_landmarks(face, landmarks)




