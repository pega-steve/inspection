
import numpy as np
import cv2
from Queue import Queue
from threading import Thread, Lock, Condition
import time
import sys
from pubsub import pub

class ImageSource:

    def read(self):
        #time.sleep(1)
        return int(time.time())


class PcbDetection:
    pass
    def __init__(self):

        self.image_src = ImageSource()
        self.__subscribers = list()
        self.stopped = False
        self._frame_queue = Queue()
        self.fetch_thread = Thread(target=self.fetch)
        #self.fetch_thread.daemon=True
        self.fetch_thread.start()

    def attach(self, subscriber):
        self.__subscribers.append(subscriber)
        pass

    def notifySubscribers(self, image):
        for sub in self.__subscribers:
            sub.update(image)

    def fetch(self):
        while not self.stopped:
            if self.stopped:
                return
            time.sleep(2)
            img = self.image_src.read()
            if img:
                self.notifySubscribers(img)

    def stop(self):
        self.stopped = True
        self.fetch_thread.join()

class AOI:
    def __init__(self):
        self.__subscribers = list()
        self._predict_queue = Queue()
        self._result_queue = Queue()
        self.stopped = False
        self._thread = Thread(target=self.predict_thread)
        #self._thread.daemon=True
        self._thread.start()

    def attach(self, subscriber):
        self.__subscribers.append(subscriber)
        pass

    def notifySubscribers(self, result):
        for sub in self.__subscribers:
            sub.update_result(result)

    def update(self, frame):
        self._predict_queue.put(frame)

    def predict_thread(self):
        while not self.stopped:
            #print('predict_thread...')
            if self.stopped:
                return
            time.sleep(1)
            if not self._predict_queue.empty():
               # print('do predictd...', self._predict_queue.qsize())
                frame = self._predict_queue.get()
                result = self.predict(frame)
                if result is None:
                    print('predict None')
                    continue
                self.notifySubscribers(result)

    def predict(self, frame):
        time.sleep(1)
        if frame%5 == 0:
            return None 
        return str(frame)

    def stop(self):
        self.stopped = True
        self._thread.join()


class LogSaver:

    def update_result(self, frame):
        print('log_saver', frame)

class Viewer:

    def update_result(self, frame):
        print('viewer', frame)

class Inspection:

    def __init__(self, log_saver=None, viewer=None):
        self.__subscribers = list()
        self.pcb_detect = PcbDetection()
        self.aoi = AOI()
        self.pcb_detect.attach(self.aoi)
        
        self.aoi.attach(self)
        self.aoi.attach(log_saver)
        self.aoi.attach(viewer)

    def update_result(self, result):
        print('Inspection get result', result)
        return result

    def stop(self):
        self.aoi.stop()
        self.pcb_detect.stop()

    """
    def attach(self, subscriber):
        self.__subscribers.append(subscriber)
        pass


    def fetech_thread(self):
        pass

    def notifySubscripers(self):
        for sub in self.__subscribers:
            sub.update()
    """



if __name__ == '__main__':

    log_saver = LogSaver()
    viewer = Viewer()

    try:
        inspection = Inspection(log_saver=log_saver, viewer=viewer)
        while True:
            pass
            time.sleep(0.2)
        
    except KeyboardInterrupt:
        print('main KeyboardInterrupt')
        if inspection:
            inspection.stop()
            exit()

        
