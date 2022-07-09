import sys
import cv2
from PyQt5 import uic
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QMdiArea, QAction, QFileDialog, QMessageBox, QLabel, QMdiSubWindow

class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        self.images = dict()
        self.active_window = None

        uic.loadUi("main.ui", self)

        self.mdi = self.findChild(QMdiArea, "mdiArea")
        self.setCentralWidget(self.mdi)
        self.mdi.subWindowActivated.connect(self.__active_window)

        #Deklarowanie glownego menu
        self.action_open = self.findChild(QAction, "actionOtworz")
        self.action_save = self.findChild(QAction, "actionZapisz")
        self.action_cascade = self.findChild(QAction, "actionKaskad")
        self.action_exit = self.findChild(QAction, "actionWyjscie")
        self.action_autor = self.findChild(QAction, "actionAutor")

        self.action_morf = self.findChild(QAction, "actionMorfologiczna_rekonstrukcja")

        self.action_open.triggered.connect(self.open_windows)
        self.action_save.triggered.connect(self.save)
        self.action_cascade.triggered.connect(self.mdi.cascadeSubWindows)
        self.action_exit.triggered.connect(self.close)

        self.action_autor.triggered.connect(self.autor)

        self.action_morf.triggered.connect(self.morf)
        self.show()

    def morf(self):
        if (self.check() == -1):
            return

        name = self.active_window.name
        img = self.active_window.data

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
        iterations = 10
        erosion = cv2.erode(img, kernel, iterations)
        dilation = cv2.dilate(erosion, kernel, iterations)
        mask = img
        marker = erosion
        result = self.imreconstruct(marker, mask, kernel)

        self.add_new_window("erosion " + name, erosion)
        self.add_new_window("Dylacja " + name, dilation)
        self.add_new_window("Morfologiczna rekonstrukcja " + name, result)

    def imreconstruct(self, marker: np.ndarray, mask: np.ndarray, kernel):
        while True:
            expanded = cv2.dilate(src=marker, kernel=kernel)
            cv2.bitwise_and(src1=expanded, src2=mask, dst=expanded)
            if (marker == expanded).all():
                return expanded
            marker = expanded

    def check(self):
        if self.active_window == None:
            QMessageBox.warning(self, "Brak aktywnego obrazu", "Otwórz najpierw obraz\n")
            return -1
        return 1

    def open_windows(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open file", "", "All Files (*);;"
                                                                            "BMP files(*.bmp);;"
                                                                            "JPEG files (*.jpeg *.jpg);;"
                                                                            "PNG(*.png);;"
                                                                            "TIFF files (*.tiff *.tif)")
        if not file_paths:
            return
        for file_path in file_paths:
            if file_path:
                self.add_new_window(file_path.split("/")[-1], cv2.imread(file_path, cv2.IMREAD_GRAYSCALE))

    def add_new_window(self, name, img):
        image = Image(name, img)
        self.images[name] = image
        self.mdi.addSubWindow(image.subwindow)
        image.subwindow.show()

    def __active_window(self, sub):
        if sub.name in self.images:
            self.active_window = self.images.get(sub.name)

    def save(self):
        if(self.check()==-1):
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save file", self.active_window.name,
                                                   "All Files (*);;"
                                                   "Bitmap (*.bmp *.dib);;"
                                                   "Image files (*.jpg *.png *.tif)")

        if not file_path:
            return
        cv2.imwrite(file_path, self.active_window.data)

    def autor(self):
        autor = """
                                    <p style="text-align: center">
                                        <b>APO projekt egzaminacyjny</b><br>
                                    </p>
                                    <table>
                                        <tr><td>Autor:</td>         <td>Edgar Ostrowski-Cobas</td></tr>
                                        <tr><td>  Numer  i Temat Projektu:</td>    <td>30: Implementacja operacji rekonstrukcji morfologicznej </td></tr>
                                        <tr><td>Grupa i Nr Albumu:</td>    <td>ID06IO2, 19225</td></tr>
                                    </table>
                                   """

        QMessageBox.information(self, "Informacja", autor)


class Image:
    def __init__(self, image_name, image_data):
        self.name = image_name
        self.data = image_data
        self.subwindow = SubWin(self.name, self.data)

class SubWin(QMdiSubWindow):
    def __init__(self, img_name, img_data):
        super().__init__()
        self.name = img_name
        self.data = img_data
        self.image_label = QLabel()
        self.setWidget(self.image_label)
        self.setWindowTitle(self.name)
        rgb_image = cv2.cvtColor(self.data, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        tempimage = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.pixmap = QPixmap(tempimage)
        self.image_label.setPixmap(self.pixmap.copy())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    UIWindow = GUI()
    app.exec_()