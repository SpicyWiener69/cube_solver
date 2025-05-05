import cv2
import numpy as np
import threading
import time


class VideoStream:
    def __init__(self, debug=False, video_address="https://10.42.0.99:8080/video"):
        self.video_address = video_address
        self.cap = cv2.VideoCapture(self.video_address)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        self.thread = threading.Thread(target=self._update, daemon=True, args=())
        self.thread.start()
        time.sleep(1)
        return self

    #@timeit
    def _update(self):
        try:
            while not self.stopped:
                if not self.cap.isOpened():
                    self.stopped = True
                    
                    return
                # Do the SLOW read OUTSIDE the lock
                ret, new_frame = self.cap.read()
            
                # Use a short lock for the assignment
                with self.lock:
                    self.ret = ret
                    self.frame = new_frame
        finally:
            self.cap.release()
 
    def _read_frame(self):
        with self.lock:
            return self.ret, self.frame.copy()

    def read_resized_frame(self, scale_percent=50) -> np.array:
        '''
        custom resizeing for current computer display;
        adjust values if needed
        '''
        _, frame = self._read_frame()
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        frame = cv2.resize(frame,(width, height))  
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        #if ret:
            #return frame
        return frame
    
    def stop(self):
        print('stopping thread')
        self.stopped = True
        # if self.cap.isOpened():
        #     self.cap.release()
        if hasattr(self, 'thread') and self.thread.is_alive():
            try:
                self.thread.join(timeout=1.0)  # Wait up to 1 second
            except Exception as e:
                print(f"Error joining thread: {e}")

if __name__ == "__main__":
    stream = VideoStream().start()
    cv2.namedWindow('display')
    timeout_start = time.time()
    timeout = 15
    while time.time() < timeout_start + timeout:
        time.sleep(0)
        #_,frame = stream._read_frame()
        frame = stream.read_resized_frame()
        cv2.imshow('display',frame)
        cv2.waitKey(1)
    stream.stop()
    print('still runing')
    print('asdfasfd')