import cv2
from src.pipert2.core.base.routine import Routine


class OpenCVCaptureFrame(Routine):
    def __init__(self, stream_address, fps=30., *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_stream_address(stream_address)
        self.stream = None
        self.fps = fps

    def _set_stream_address(self, stream_address):
        try:
            self.stream_address = int(stream_address)
        except ValueError:
            self.stream_address = stream_address

        self.stream_address = stream_address
        self.isFile = str(self.stream_address).endswith("mp4")

    def begin_capture(self):
        self.stream = cv2.VideoCapture(self.stream_address)
        if self.isFile:
            self.fps = self.stream.get(cv2.CAP_PROP_FPS)
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self._logger.info(f"Starting video capture on {self.stream_address}")

    @Routine.events("ChangeStream")
    def change_stream(self, stream_address):
        self._logger.info(f"Changing source stream address to {stream_address}")
        self.begin_capture()

    def grab_frame(self):
        if self.stream.isOpened():
            grabbed, frame = self.stream.read()
            if grabbed:
                return frame
            else:
                self._logger.info("Failed to capture frame")
        else:
            self._logger.info("Failed to open stream")
            self._logger.info("Retrying...")
            self.begin_capture()

        return None

    def main_logic(self, data):
        return {"frame": self.grab_frame()}

    def setup(self):
        self.begin_capture()

    def cleanup(self):
        self.stream.release()