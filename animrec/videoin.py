#! /usr/bin/env python
#
# Controlled media recording library for the Rasperry-Pi
# Copyright (c) 2019 Jolle Jolles <j.w.jolles@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from threading import Thread
import os
import cv2
import time
import animlab.utils as alu
import animlab.imutils as alimu
import animlab.mathutils as almau

class VideoIn:
    def __init__(self, system="auto", vidsize=0.3, framerate=32, roi=False):

        """ Opens a video stream from native camera, webcam or rpi camera """

        if system == "auto":
            self.cam = "rpi" if alu.is_rpi() else 0
        elif system in ["rpi",0,1,2]:
            self.cam = system
        else:
            self.cam = 0

        self.roi = roi

        if self.cam == "rpi":
            from picamera.array import PiRGBArray
            from picamera import PiCamera
            self.maxres = (2592,1944)
            self.res = (self.maxres[0]*vidsize,self.maxres[1]*vidsize)
            self.res = alimu.picamconv(self.res)
            self.camera = PiCamera()
            self.camera.resolution = self.res
            self.camera.framerate = framerate
            self.rawCapture = PiRGBArray(self.camera, size=self.resolution)
            self.stream = self.camera.capture_continuous(self.rawCapture,
                          format="bgr", use_video_port=True)

        else:
            self.stream = cv2.VideoCapture(self.cam)
            self.stream.set(3, 4000)
            self.stream.set(4, 4000)
            self.maxresolution = (int(self.stream.get(3)), int(self.stream.get(4)))
            self.stream.set(3, resolution[0])
            self.stream.set(4, resolution[1])
            self.resolution = (int(self.stream.get(3)), int(self.stream.get(4)))

        self.stopped = False


    def start(self):
        Thread(target=self.update, args=()).start()
        time.sleep(2)
        return self


    def update(self):
        if self.cam == "rpi":
            for f in self.stream:
                self.frame = f.array
                self.rawCapture.truncate(0)
                if self.stopped:
                    self.stream.close()
                    self.rawCapture.close()
                    self.camera.close()
                    return
        else:
            while True:
                _, self.frame) = self.stream.read()
                if self.stopped:
                    self.stream.release()
                    return


    def read(self):
        if self.roi:
            self.frame = alimu.crop(self.frame, self.roi[0], self.roi[1])
        return self.frame


    def img(self):
        w,h = self.maxresolution
        if self.cam == "rpi":
            self.image = np.empty((h * w * 3,), dtype=np.uint8)
            camera.capture(self.image, 'bgr')
            self.image = self.image.reshape((h, w, 3))
            self.stream.close()
            self.rawCapture.close()
            self.camera.close()
        else:
            self.stream.set(3, w)
            self.stream.set(4, h)
            _, self.image = self.stream.read()
            self.stop()

        if self.roi:
            zoom = alimu.roi_to_zoom(self.roi, self.resolution)
            newroi = alimu.zoom_to_roi(zoom, self.maxresolution)
            self.image = alimu.crop(self.image, newroi[0], newroi[1])

        return self.image


    def stop(self):
        self.stopped = True
