from PySide2.QtWidgets import QProgressDialog
from PySide2.QtCore import Qt
import os

class ProgressDialogBase(QProgressDialog):
    def __init__(self):
        self.rejectCall = True;#防止QProgressDialog自动调用setVisible显示
        super().__init__();
        self.setProgressDialog();

    def setProgressDialog(self):
        self.setLabelText('正在处理...');
        self.setCancelButton(None);  # 去掉右下角Cancel按钮
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setModal(True);  # 设置为模态框
        self.setStyleSheet(
            "QProgressBar {width: 300px; height: 20px;color:black;font:20px;text-align:center; }QProgressBar::chunk {background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #21CBF3)}");

    def setVisible(self, visible: bool):#QProgressDialog子类必须重写setVisible,否则会自动调用父类的setVisible让进度条显示出来
        if self.rejectCall:
            super().setVisible(visible);
        self.rejectCall = False;

class ProgressDialogForFile(ProgressDialogBase):
    def __init__(self,rootPath=''):
        self.rootPath = rootPath;
        super().__init__();
        self.setProgressDialog();

    def setProgressDialog(self):
        if self.rootPath == '':
            return ;
        self.setLabelText('正在处理...');
        self.setRange(0, len([f for f in os.listdir(self.rootPath) if f.endswith('.txt')]));  # 获取.txt文件的个数并将其设置为进度条最大值
        self.setCancelButton(None);  # 去掉右下角Cancel按钮
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setModal(True);  # 设置为模态框
        self.setStyleSheet(
            "QProgressBar {width: 300px; height: 20px;color:black;font:20px;text-align:center; }QProgressBar::chunk {background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #21CBF3)}");


    def setVisible(self, visible:bool):#QProgressDialog子类必须重写setVisible,否则会自动调用父类的setVisible让进度条显示出来
        pass;

