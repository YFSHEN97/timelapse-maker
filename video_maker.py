import numpy as np
import cv2
import math
from sorter import Sorter
from detect_landmarks import FaceLandmarkDetector
from warp_image import ImageWarper
from face_detector import rotate_image
import extrapolate_vector_field as evf


# given a list of face images already sorted according to age 
# return a new list of these faces, where each has been transformed, plus new landmarks
# the transformation performs the following steps in order:
### rotation, so that eyes in each image is horizontal
### scaling warp, so that the two eyes have the same distance in each face
### translation, so that the eyes are aligned in all images
## mode "eye" uses eye alignment all the way
## mode "lse" uses least square alignment for all images except the first
def align_faces(faces, mode="eye"):
    results = []
    landmarks = []
    d = FaceLandmarkDetector()
    if mode == "eye":
        for img in faces:
            img_aligned, new_landmarks = eye_alignment(img, d)
            if img_aligned is None or new_landmarks.shape == (0, 2):
                continue
            results.append(img_aligned)
            landmarks.append(new_landmarks)
    elif mode == "lse":
        prev_landmarks = None
        for img in faces:
            if prev_landmarks is None:
                img_aligned, new_landmarks = eye_alignment(img, d)
            else:
                img_aligned, new_landmarks = least_square_alignment(prev_landmarks, img, d)
            if img_aligned is None or new_landmarks.shape == (0, 2):
                continue
            prev_landmarks = new_landmarks
            results.append(img_aligned)
            landmarks.append(new_landmarks)
    return results, landmarks


# given a single face IMG, do transformations on it
# according to the eye alignment heuristic
# the transformation performs the following steps in order:
### rotation, so that eyes in IMG is horizontal
### scaling warp, so that the two eyes have a certain fixed distance
### translation, so that the eyes are aligned at a certain location
# arguments:
### d: reference to a face landmark detector object
### ed: the desired eye distance (in px) after scaling (default to 150)
### el: the left margin (in px) after translation (default to 400)
### et: the top margin (in px) after translation (default to 260)
def eye_alignment(img, d, ed=150, el=400, et=260):
    cc = img.shape[2] # number of channels
    # step 1: rotate the image (without downsizing it) to make the eyes horizontal
    landmarks = d.predict(img)
    if landmarks.shape == (0, 2):
        return None, None # landmarks not detected in this face, skip it
    eye1 = landmarks[36]
    eye2 = landmarks[45]
    angle = np.arctan((eye1[1]-eye2[1]) / (eye1[0]-eye2[0]))
    img_r, _ = rotate_image(img, scaleFactor=1, degreesCCW=angle * 180 / np.pi)
    # step 2: scale the image so that the two eyes' distance is the target distance
    eye_dist = np.linalg.norm(eye1 - eye2)
    sf = ed / eye_dist
    img_rs = cv2.resize(img_r, None, fx=sf, fy=sf)
    # step 3: crop out/pad a 800*600 region with the eyes at the center
    oldY, oldX = img.shape[:2]
    newY, newX = img_r.shape[:2]
    Mr = cv2.getRotationMatrix2D(center=(oldX/2, oldY/2), angle=angle * 180 / np.pi, scale=1)
    Mt = np.float32([[1, 0, 0.5*(newX-oldX)], [0, 1, 0.5*(newY-oldY)]])
    eye1rs = np.matmul(Mt, np.append(np.matmul(Mr, np.append(eye1, 1)), 1)) * sf
    eye2rs = np.matmul(Mt, np.append(np.matmul(Mr, np.append(eye2, 1)), 1)) * sf
    eye_center = 0.5 * (eye1rs + eye2rs)
    ex = int(eye_center[0])
    ey = int(eye_center[1])
    minx = ex - el
    maxx = minx + 800
    miny = ey - et
    maxy = miny + 600
    dy, dx = img_rs.shape[:2]
    hh = min(maxy, dy) - max(miny, 0)
    ww = min(maxx, dx) - max(minx, 0)
    hs = max(-miny, 0)
    ws = max(-minx, 0)
    result = np.full((600, 800, cc), (0,0,0), dtype=np.uint8)
    result[hs:hs+hh, ws:ws+ww] = img_rs[max(miny, 0):min(maxy, dy), max(minx, 0):min(maxx, dx)]
    landmarks = d.predict(result)
    return result, landmarks


# given the transformed version of the previous face in the sequence
# compute and return the transformed img and landmarks of the current face
# the transformation performs the following steps in order:
### scaling warp, so that the two eyes have a certain fixed distance
### rotation + translation, so that the two sets of landmarks have least-square error
# arguments:
### prev_landmarks: landmarks of the previous face in the sequence
### img: face IMG of the current face
### d: reference to a face landmark detector object
### ed: the desired eye distance (in px) for the purpose of scaling (default to 150)
def least_square_alignment(prev_landmarks, img, d, ed=150):
    cc = img.shape[2] # number of channels
    # step 1: detect eyes, and scale the image so that the eyes have desired distance
    landmarks = d.predict(img).astype(np.float32)
    if landmarks.shape == (0, 2):
        return None, None # landmarks not detected in this face, skip it
    eye1 = landmarks[36]
    eye2 = landmarks[45]
    eye_dist = np.linalg.norm(eye1 - eye2)
    sf = ed / eye_dist
    img_s = cv2.resize(img, None, fx=sf, fy=sf)
    landmarks *= sf
    # step 2: compute optimal rotation/translation using Kabsch's Algorithm
    A_centroid = np.mean(landmarks, axis=0)
    B_centroid = np.mean(prev_landmarks, axis=0)
    H = np.matmul((landmarks - A_centroid).T, (prev_landmarks - B_centroid))
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0:
        Vt[1,:] *= -1
        R = Vt.T @ U.T
    theta = -math.asin(R[1, 0]) # minus sign due to inverted y-axis for images
    # step 3: rotate the image and compute where centroid A ends up at after the rotation
    # the rotation here must NOT crop the image in any way!
    (oldY, oldX) = img_s.shape[:2]
    img_sr, M = rotate_image(img_s, scaleFactor=1, degreesCCW=theta * 180 / np.pi)
    A_centroid = np.matmul(M, np.append(A_centroid, 1))
    # step 5: crop out 800*600 region in the roto-scaled image
    # must make sure that after cropping A_centroid overlaps with B_centroid!!
    minx = int(A_centroid[0] - B_centroid[0])
    maxx = minx + 800
    miny = int(A_centroid[1] - B_centroid[1])
    maxy = miny + 600
    dy, dx = img_sr.shape[:2]
    hh = min(maxy, dy) - max(miny, 0)
    ww = min(maxx, dx) - max(minx, 0)
    hs = max(-miny, 0)
    ws = max(-minx, 0)
    result = np.full((600, 800, cc), (0,0,0), dtype=np.uint8)
    result[hs:hs+hh, ws:ws+ww] = img_sr[max(miny, 0):min(maxy, dy), max(minx, 0):min(maxx, dx)]
    landmarks = d.predict(result)
    return result, landmarks


# given a list of transformed faces
# generate a timelapse video out of it
# the previous face is morphed into the next
# interval is the time (in seconds) between each successive face
# pause is the time (in seconds) that we dwell on each face
# fps is the frame rate of the video
def make_video(faces, landmarks, out_filename, interval=1, pause=0.5, fps=30):
    assert len(faces) > 1
    e = evf.Extrapolator()
    w = ImageWarper()
    out = cv2.VideoWriter(out_filename, cv2.VideoWriter_fourcc(*'mp4v'), fps, (800,600))
    for i in range(len(faces) - 1):
        face1 = faces[i]
        face2 = faces[i+1]
        landmarks1 = landmarks[i]
        landmarks2 = landmarks[i+1]
        # compute the warping field face1 -> face2
        face1_x = landmarks2[:, 0]
        face1_y = landmarks2[:, 1]
        face1_dx = landmarks1[:, 0] - landmarks2[:, 0]
        face1_dy = landmarks1[:, 1] - landmarks2[:, 1]
        face1_fx, face1_fy = e.extrapolate(face1_x, face1_y, face1_dx, face1_dy, (600,800))
        # compute the warping field face2 -> face1
        face2_x = landmarks1[:, 0]
        face2_y = landmarks1[:, 1]
        face2_dx = landmarks2[:, 0] - landmarks1[:, 0]
        face2_dy = landmarks2[:, 1] - landmarks1[:, 1]
        face2_fx, face2_fy = e.extrapolate(face2_x, face2_y, face2_dx, face2_dy, (600,800))
        # first put original face1 into the video for duration "pause"
        for j in range(int(pause * fps)):
            out.write(face1)
        # then produce the warped sequence
        warp_amounts = np.linspace(0., 1., int(interval * fps))
        for j, warp_amount in enumerate(warp_amounts):
            face1_warped = w.warp(face1, face1_fx, face1_fy, warp_amount)
            face2_warped = w.warp(face2, face2_fx, face2_fy, 1 - warp_amount)
            # We alpha blend the original images
            face_out = (1 - warp_amount) * face1_warped + warp_amount * face2_warped
            # write video frame
            out.write(face_out.astype(np.uint8))
    # put the last face into the video for duration "pause"
    for i in range(int(pause * fps)):
        out.write(faces[-1])
    out.release()


# a much simpler version of the video maker that doesn't perform the morphing operations
def make_video_nomorph(faces, out_filename, pause=1, fps=30):
    out = cv2.VideoWriter(out_filename, cv2.VideoWriter_fourcc(*'mp4v'), fps, (800,600))
    for i in range(len(faces)):
        for j in range(int(pause * fps)):
            out.write(faces[i])
    out.release()


# if __name__ == "__main__":
#     path = "./images/set3/"
#     sorter = Sorter(path)
#     sorter.sort()
#     facelist = list(map(lambda f: f[1], sorter.list_all()))
#     facelist = align_faces(facelist)
#     VM = VideoMaker()
#     VM.make_video(facelist, "./data/out.mp4")
#     VM.make_video_nomorph(facelist, "./data/out_nomorph.mp4")

