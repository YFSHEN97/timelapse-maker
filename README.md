# timelapse-maker

### Dependencies

This project depends on `npm`, Vue.js, OpenCV, FFmpeg, and NumPy. Make sure you have these installed.

In addition, to run the machine learning models directly, you need to have the data files downloaded and put into a directory called `data` at the root of the repository once you clone it (the models are not provided here because of GitHub's file size restrictions). You can get the data files here: [age predictor model structure](https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/static/age.prototxt), [age predictor model weights](https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/static/dex_chalearn_iccv2015.caffemodel), [dlib facial pose estimator with 68 landmarks](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2).

### How to build and run

Clone this repository, `cd` into the directory and run the following command:
```
$ npm install
```
This should automatically install all the dependencies for the frontend user interface. To be able to run the backend (the Python scripts), you need to have OpenCV, FFmpeg, and NumPy. In addition, you need to make a folder called `data` at the root level of the repository and put the required machine learning model files in there. After all the required dependencies are correctly installed/downloaded, you can run
```
$ npm run serve
```
to launch the frontend, and
```
$ python3 server.py
```
to run the Python server. To access the application, open your browser and go to `localhost:8080`.

### Questions

If you have any questions, please email yifei.shen@yale.edu.
