import cv2
import numpy as np
import threading
import time

class VideoStream:
    def __init__(self, debug=False, video_address="https://10.42.0.99:8080/video"):
        self.video_address = video_address
        self.cap = cv2.VideoCapture(self.video_address)
        self.debug = debug
        self.stopped = False
        self.display = False 
        self.ret = None
        self.frame = None
        self.resized_frame = None
        self.lock = threading.Lock()
        #self.window = cv2.namedWindow("video frame")
    def start(self):
        threading.Thread(target=self._update, daemon=True).start()
        return self

    # def display_frame(self, display_flag):
    #     self.display = display_flag


    @staticmethod
    def resize_frame(frame, scale_percent=50) -> np.ndarray:
        '''
        Custom resizing for current computer display; adjust values if needed.
        '''

        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        frame = cv2.resize(frame, (width, height))  
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        return frame

    def stop(self):
        self.stopped = True

    def _update(self):
        while not self.stopped:
            if not self.cap.isOpened():
                self.stop()
                return
            
            self.ret, self.frame = self.cap.read()
            if not self.ret:
                continue  # Skip if frame is not read properly

            self.resized_frame = self.resize_frame(self.frame)

            # if self.display:
            #     cv2.imshow("video frame", self.resized_frame)
            #     if cv2.waitKey(1) & 0xFF == ord('q'):  
            #         self.stop()
        
        self.cap.release()
        cv2.destroyAllWindows()

    def read_frame(self):
        return self.ret, self.frame

if __name__ == "__main__":
    stream = VideoStream().start()
    #stream.display_frame()
    while True:
        _, frame = stream.read_frame()
        img = cv2.imshow('frame',frame)
        cv2.waitKey(1)


    # try:
    #     while True:
    #         cmd = input("Press [Enter] to toggle display, type 'q' to quit: ").strip()
    #         if cmd == 'q':
    #             stream.stop()
    #             break
    #         stream.toggle_display_frame()
    #         time.sleep(0.1)
    # except KeyboardInterrupt:
    #     stream.stop()
