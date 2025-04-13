from PyQt6 import QtCore, QtGui, QtWidgets
import os, shutil
from settings import MZ_AXIS
from average import AverageThread
from composite_spectrum import CompositeSpectrumThread
from time_trace import TimeTraceThread
from intensity_matrix import IntensityMatrixThread
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(940, 650)
        MainWindow.setFixedSize(QtCore.QSize(940, 650))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setStyleSheet('background-color: rgb(50,50,50);')
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.browseButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.browseButton.setGeometry(QtCore.QRect(650, 300, 102, 34))
        self.browseButton.setObjectName("browseButton")
        self.input_list = QtWidgets.QListWidget(parent=self.centralwidget)
        self.input_list.setGeometry(QtCore.QRect(20, 280, 611, 71))
        self.input_list.setObjectName("input_list")
        self.input_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.input_label.setGeometry(QtCore.QRect(20, 250, 451, 18))
        self.input_label.setObjectName("input_label")
        self.logo = QtWidgets.QLabel(parent=self.centralwidget)
        self.logo.setGeometry(QtCore.QRect(0, 0, 991, 231))
        self.logo.setObjectName("logo")
        self.progress_window = QtWidgets.QLabel(parent=self.centralwidget)
        self.progress_window.setGeometry(QtCore.QRect(20, 440, 900, 271))
        self.progress_window.setStyleSheet("background-color: rgb(255, 255, 255); color: rgb(0, 0, 0);")
        self.progress_window.setText("")
        self.progress_window.setObjectName("progress_window")
        self.progress_window.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea = QtWidgets.QScrollArea(parent=self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(20, 430, 900, 271))
        self.scrollArea.setWidget(self.progress_window)
        self.progress_bar = QtWidgets.QProgressBar(parent=self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(20, 430, 900, 20))
        self.progress_bar.setProperty("value", 0)
        self.start_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.start_button.setGeometry(QtCore.QRect(300, 370, 102, 50))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.browseButton.clicked.connect(self.browseButtonClicked)
        self.start_button.clicked.connect(self.startPreprocessing)

    def browseButtonClicked(self):
        # When the user clicks the button, open a file dialog that accepts only a single directory
        # Store the directory in a variable and show the filepath in the input list
        self.input_list.clear()
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Directory")
        self.input_list.addItem(directory)
        self.statusbar.showMessage(f"Input directory was set to: -- {directory}.", 5000)

    def startPreprocessing(self):
        self.statusbar.showMessage(f"Preprocessing on path {self.input_list.item(0).text()} in progress...")
        self.preprocess(self.input_list.item(0).text())
        self.start_button.setEnabled(False)
        self.browseButton.setEnabled(False)

    def update_progress_bar(self, text, progress):
        self.progress_bar.setValue(progress)
        self.progress_window.setText(self.progress_window.text() + text)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Preprocess.py"))
        self.browseButton.setText(_translate("MainWindow", "Browse"))
        self.input_label.setText(_translate("MainWindow", "Please input the directory path to mzML files:"))
        self.start_button.setText(_translate("MainWindow", "Start"))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "logo-preprocess.png")))


    def preprocess(self, path):
        path = Path(path)

        # If there are any files from previous analyses, delete them
        if os.path.exists(path / "average"):
            shutil.rmtree(path / "average")
        if os.path.exists(path / "time_traces"):
            shutil.rmtree(path / "time_traces")
        if os.path.exists(path / "composite_spectrum_pos.csv"):
            os.remove(path / "composite_spectrum_pos.csv")
        if os.path.exists(path / "composite_spectrum_neg.csv"):
            os.remove(path / "composite_spectrum_neg.csv")
        
        # Recreate
        os.mkdir(path / "average")
        os.mkdir(path / "time_traces")

        # Averaging spectra
        self.average = AverageThread(path / "average", MZ_AXIS)
        self.average.progress_signal.connect(self.update_progress_bar)
        self.average.start()
        # When AverageThread finishes, end the AverageThread safely and start the CompositeSpectrumThread
        self.average.finished.connect(self.average.deleteLater)
        self.composite = CompositeSpectrumThread(path, MZ_AXIS)
        self.composite.progress_signal.connect(self.update_progress_bar)
        self.average.finished.connect(self.composite.start)

        # When CompositeSpectrumThread finishes, end the CompositeSpectrumThread safely and start the TimeTraceThread
        self.composite.finished.connect(self.composite.deleteLater)
        self.time_trace = TimeTraceThread(path / "time_traces", MZ_AXIS)
        self.time_trace.progress_signal.connect(self.update_progress_bar)
        self.composite.finished.connect(self.time_trace.start)
        # When TimeTraceThread finishes, end the TimeTraceThread safely and start the IntensityMatrixThread
        self.time_trace.finished.connect(self.time_trace.deleteLater)
        
        self.intensity_matrix = IntensityMatrixThread(path)
        self.time_trace.finished.connect(self.intensity_matrix.start)
        self.intensity_matrix.finished.connect(self.intensity_matrix.deleteLater)
        
        self.intensity_matrix.finished.connect(self.finish_message)
        self.start_button.setEnabled(True) 

    def finish_message(self):
        self.statusbar.showMessage(f"Preprocessing complete! Results written to {self.input_list.item(0).text()}/intensity_matrix.csv.", 10000)