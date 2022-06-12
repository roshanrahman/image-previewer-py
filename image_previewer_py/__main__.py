import time
import sys
import glob
from PyQt5 import QtWidgets, QtGui, QtCore
from form import Ui_MainWindow


class ProcessWorker(QtCore.QObject):
    image_changed = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, image_list, framerate: int = 60) -> None:
        super().__init__()
        self.framerate = framerate
        self.image_list = image_list

    def do_work(self):
        while True:
            for f in self.image_list:
                image = QtGui.QImage(f)
                self.image_changed.emit(image)
                time.sleep(1 / self.framerate)


class MonitorFileChangeWorker(QtCore.QObject):
    file_changed = QtCore.pyqtSignal(list)

    def __init__(self, folder: str) -> None:
        super().__init__()
        self.folder = folder

    def do_work(self):
        while True:
            self.file_changed.emit(
                get_files_matching_pattern(self.folder + "/*"))
            time.sleep(2)


class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self, folder: str, framerate: int = 60):
        super(ApplicationWindow, self).__init__()
        if folder is None:
            folder = self.get_folder_from_browser()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("ᕦ( ˘ᴗ˘ )ᕤ Pweview images as a woop")
        self.ui.label.setText(
            f"Looping through images in {folder} at {framerate} fps")
        self.framerate = framerate
        self.files = get_files_matching_pattern(folder + "/*")
        self.scene = QtWidgets.QGraphicsScene()
        self.workerThread = QtCore.QThread()
        self.worker = ProcessWorker(self.files, framerate)
        self.worker.moveToThread(self.workerThread)
        self.worker.image_changed.connect(self.set_image)
        self.workerThread.started.connect(self.worker.do_work)
        self.workerThread.start()
        self.workerThread2 = QtCore.QThread()
        self.worker2 = MonitorFileChangeWorker(folder)
        self.worker2.moveToThread(self.workerThread2)
        self.worker2.file_changed.connect(self.update_files)
        self.workerThread2.started.connect(self.worker2.do_work)
        self.workerThread2.start()

    @QtCore.pyqtSlot(list)
    def update_files(self, images):
        self.files = images
        self.worker.image_list = self.files

    @QtCore.pyqtSlot(QtGui.QImage)
    def set_image(self, image: QtGui.QImage):
        self.scene.clear()
        self.scene.addPixmap(QtGui.QPixmap.fromImage(image))
        self.ui.graphicsView.setScene(self.scene)

    def get_folder_from_browser(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Folder")
        return folder


# Returns list of every file matching the regex pattern
def get_files_matching_pattern(path_pattern):
    result = glob.glob(path_pattern)
    print(result)
    return sorted(result)


def main():
    folder = None
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow(folder=folder)
    application.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
