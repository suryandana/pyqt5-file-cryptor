from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from pathlib import Path

class WindowStart(QWidget):
    def __init__(self):
        super().__init__()
        self.filenames = []

        self.layout = QFormLayout()
        
        self.btn_browse = QPushButton('Browse')
        self.line_browse = QLabel()

        self.radgroup_browse = QButtonGroup()
        self.rad_file = QRadioButton("Select File(s)")
        self.rad_folder = QRadioButton("Select Folder")
        self.radgroup_browse.addButton(self.rad_file)
        self.radgroup_browse.addButton(self.rad_folder)

        self.com_mode = QComboBox()
        self.line_key = QLineEdit()
        
        self.btn_exec = QPushButton('Execute')
        
        self.text_log = QTextEdit()
        self.btn_clear_log = QPushButton('Clear')

        self.btn_browse.clicked.connect(self.browse)
        self.btn_exec.clicked.connect(self.crypt)

        self.validate_btn_exec()

        self.rad_file.setChecked(True)

        self.radgroup_browse.buttonToggled.connect(self.empty_filenames)

        self.line_key.setEnabled(False)
        # self.text_log.setEnabled(False)
        self.text_log.setReadOnly(True)

        self.lb_result = QLabel()
        self.lb_result.setWordWrap(True)
        
        self.com_mode.addItems([
            "Invert the first 64 bytes",
            "Prepend keyword to the files",
            "Operate the first bytes and keyword with XOR"
        ])

        self.com_mode.currentIndexChanged.connect(self.toggle_mode)

        self.layout.addRow(self.btn_browse, self.line_browse)
        self.layout.addRow(self.rad_file, self.rad_folder)
        # self.layout.addRow(self.radgroup_browse)
        self.layout.addRow(self.com_mode)
        self.layout.addRow(self.line_key)
        self.layout.addRow(self.btn_exec)
        self.layout.addRow(self.text_log)
        self.layout.addRow(self.btn_clear_log)

        # self.layout.addRow(self.rad_file, self.com_mode)
        # self.layout.addRow(self.rad_folder, self.btn_exec)

        self.layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.layout.setLabelAlignment(Qt.AlignRight)
        self.setLayout(self.layout)

    def browse(self):
        browse = QFileDialog()
        if self.rad_file.isChecked():
            browse.setFileMode(QFileDialog.ExistingFiles)
        elif self.rad_folder.isChecked():
            browse.setFileMode(QFileDialog.Directory)

        
        if browse.exec_():
            self.filenames = browse.selectedFiles()
            if len(self.filenames) == 1:
                self.line_browse.setText(self.filenames[0])
            elif len(self.filenames) > 1:
                self.line_browse.setText("{} files selected".format(len(self.filenames)))
        self.validate_btn_exec()

    def toggle_mode(self):
        if self.com_mode.currentText() == "Invert the first 64 bytes":
            self.line_key.setEnabled(False)
        elif self.com_mode.currentText() == "Prepend keyword to the files":
            self.line_key.setEnabled(True)
        elif self.com_mode.currentText() == "Operate the first bytes and keyword with XOR":
            self.line_key.setEnabled(True)

    def crypt(self):
        if self.rad_file.isChecked():
            for filename in self.filenames:
                # print("if rad_file.isChecked():")
                with open(filename, 'rb+') as openfile:
                    openfile.seek(0)
                    filebytes = []
                    for i in range(64):
                        filebytes.append((int.from_bytes(openfile.read(1), "little") ^ 0xFF).to_bytes(1, byteorder='little'))

                    openfile.seek(0)
                    for filebyte in filebytes: openfile.write(filebyte)
                    self.text_log.append("Successfully changing the first 64-bit of \"{}\"".format(filename))
        elif self.rad_folder.isChecked():
            for filename in sorted(Path(self.filenames[0]).glob('**/*')):
                with open(filename, 'rb+') as openfile:
                    openfile.seek(0)
                    filebytes = []
                    for i in range(64):
                        filebytes.append((int.from_bytes(openfile.read(1), "little") ^ 0xFF).to_bytes(1, byteorder='little'))

                    openfile.seek(0)
                    for filebyte in filebytes: openfile.write(filebyte)
                    self.text_log.append("Successfully changing the first 64-bit of \"{}\"".format(filename))
        self.empty_filenames()
 
    def empty_filenames(self):
        self.filenames = []
        self.line_browse.setText("")
        self.validate_btn_exec()

    def validate_btn_exec(self):
        self.btn_exec.setEnabled(not len(self.filenames) == 0)

    def clear_log(self):
        self.text_log.setText("")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        width = 800
        height = 600
        self.number_of_questions = 30

        screen = app.primaryScreen()
        size = screen.size()
        self.setGeometry(
            int((size.width()-width)/2), #pos_x
            int((size.height()-height)/2), #pos_y
            width, #win_width
            height #win_height
        )
        self.setFixedSize(width, height)
        self.startWindowStart()

    def startWindowStart(self):
        self.Start = WindowStart()
        self.setWindowTitle("File Cryptor")
        self.setCentralWidget(self.Start)

        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    w = MainWindow()
    sys.exit(app.exec_())