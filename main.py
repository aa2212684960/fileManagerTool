import os,shutil,time,winshell
from PySide2.QtCore import QDir,Qt,QModelIndex,QItemSelectionModel
from PySide2.QtWidgets import QApplication, QFileSystemModel,QTreeView,QFileDialog,QHeaderView,QMenu,QInputDialog,\
    QMessageBox,QShortcut,QMainWindow,QLineEdit,QVBoxLayout,QWidget
from PySide2.QtGui import QKeySequence


class fileManagerBase(QTreeView):
    def __init__(self,parent=None):
        super().__init__(parent);
        self.model = QFileSystemModel();
        self.curNodePath = QFileDialog.getExistingDirectory();
        self.delFilePath = '';
        self.curNodeName = '';
        self.model.setRootPath(QDir.rootPath());
        self.resize(1024, 512);

        self.setDragEnabled(True);
        self.setAcceptDrops(True);
        self.viewport().setAcceptDrops(True);
        self.setMouseTracking(True);

        self.setDragDropMode(QTreeView.InternalMove);#设置拖放模式为内部移动
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents);
        self.setContextMenuPolicy(Qt.CustomContextMenu);

        self.setModel(self.model);
        self.setRootIndex(self.model.index(self.curNodePath));

        self.customContextMenuRequested.connect(self.showContextMenu);
        self.doubleClicked.connect(self.openFile);
        self.clicked.connect(self.saveNodePath);

        self.setContextMenu();


    def setContextMenu(self):
        self.menu = QMenu()
        createFolder = self.menu.addAction('新建文件夹');
        delFolder = self.menu.addAction('删除文件');
        undelFolder = self.menu.addAction('删除回滚');

        createFolder.setShortcut('Ctrl+A');  # 设置快捷键
        delFolder.setShortcut('Ctrl+D');
        undelFolder.setShortcut('Ctrl+Z');

        createFolderShortcut = QShortcut(QKeySequence('Ctrl+A'), self);
        createFolderShortcut.activated.connect(self.createFolderAction);

        delFolderShortcut = QShortcut(QKeySequence('Ctrl+D'), self);
        delFolderShortcut.activated.connect(self.deleteAction);

        undelFolderShortcut = QShortcut(QKeySequence('Ctrl+Z'), self);
        undelFolderShortcut.activated.connect(self.undeleteAction);


        createFolder.triggered.connect(self.createFolderAction);
        delFolder.triggered.connect(self.deleteAction);
        undelFolder.triggered.connect(self.undeleteAction);


    def showContextMenu(self, pos):
        self.menu.exec_(self.mapToGlobal(pos));


    def createFolderAction(self):
        folderName ,ok = QInputDialog.getText(None,'请输入文件夹名称','',flags=Qt.WindowCloseButtonHint);
        if os.path.isdir(self.curNodePath):
            path = self.curNodePath + '/' + folderName;
        else:
            prePath = os.path.split(self.curNodePath)[0]
            path = prePath + '/' + folderName;

        os.mkdir(path);


    def deleteAction(self):
        selectedRows = self.selectionModel().selectedRows();
        if len(selectedRows) > 0:
            selectedRowIndex = selectedRows[0];
            selectedNodeName = selectedRowIndex.data();
            self.delFilePath = self.model.filePath(selectedRowIndex);

            reply = QMessageBox.question(self, '警告', f'即将删除 "{selectedNodeName}" ,请确认！', QMessageBox.Yes | QMessageBox.No);
            if reply == QMessageBox.Yes:
                try:
                    os.rmdir(self.delFilePath);
                except Exception as e:
                    winshell.delete_file(self.delFilePath,allow_undo=True);
                    print('deleteAction',e);

            #删除了文件就要把当前文件路径截断到上一层级,并且更新路径栏显示
            self.curNodePath = os.path.split(self.curNodePath)[0];
            self.updateFriendWidget();


    def undeleteAction(self):
        path = self.delFilePath.replace('/', '\\')
        winshell.recycle_bin().undelete(path);


    def openFile(self,index: QModelIndex):
        curNodePath = self.model.filePath(index);

        if os.path.isfile(curNodePath):
            os.startfile(curNodePath);


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction();


    def dragMoveEvent(self, event):
        index = self.indexAt(event.pos());
        self.selectionModel().select(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)


    def dropEvent(self, event):
        for url in event.mimeData().urls():
            srcPath = url.path()[1:];
            srcFileName = os.path.split(srcPath)[1].split('.')[0];#获取源文件名
            fileSuffix = srcPath.split('.')[-1];#获取源文件拓展名
            if os.path.isfile(srcPath):
                selectedRows = self.selectionModel().selectedRows();
                if len(selectedRows) != 0:#如果鼠标移动在文件夹或者文件上
                    selectedRowIndex = self.selectionModel().selectedRows()[0];
                    curNodeName = selectedRowIndex.data();
                    NotRepectFileName = curNodeName + str(time.time());
                    curNodePath = self.model.filePath(selectedRowIndex);

                    if os.path.isdir(curNodePath):#若鼠标移动到文件夹上,文件将以文件夹名称+时间戳命名并保存到对应文件夹中
                        savePath = curNodePath + '/' + NotRepectFileName + '.' + fileSuffix;
                    else:#鼠标移动到文件上,那么就以原来的文件名保存到当前路径
                        savePath = os.path.split(curNodePath)[0] + '/' + srcFileName + '.' + fileSuffix;
                else:
                    #鼠标移动到空白的位置,那么就以原来的文件名保存到当前路径
                    savePath = self.curNodePath  + '/' + srcFileName + '.' + fileSuffix;

                winshell.move_file(srcPath, savePath);#文件移动


    def mouseMoveEvent(self, event):
            index = self.indexAt(event.pos());#获取当前鼠标对应的QModelIndex
            self.selectionModel().select(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows);#清除其他行的选中状态,并且设置当前行所有列为选中状态


    def saveNodePath(self,index:QModelIndex):
        self.curNodePath = self.model.filePath(index);
        self.updateFriendWidget();

    def updateFriendWidget(self):
        pass


class fileMoveManager(fileManagerBase):
    def __init__(self,parent=None):
        super().__init__(parent);


    def updateFriendWidget(self):
        friend = self.parent().findChild(QLineEdit,'pathEdit');
        friend.setText(self.curNodePath);#更新路径信息


    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            index = self.indexAt(event.pos());
            self.selectionModel().select(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows);
            selectedRows = self.selectionModel().selectedRows();
            if len(selectedRows) > 0:  # 如果鼠标移动在文件夹或者文件上
                selectedRowIndex = self.selectionModel().selectedRows()[0];
                self.curNodePath = self.model.filePath(selectedRowIndex);
                print(self.curNodePath)

        elif event.button() == Qt.LeftButton:
            super(fileMoveManager, self).mousePressEvent(event)


class fileManagerTool(QWidget):
    def __init__(self):
        super().__init__();

        self.resize(1024,512);
        self.setWindowTitle('文件分类命名辅助工具');
        layout = QVBoxLayout();

        lineEdit = QLineEdit(self);
        lineEdit.setObjectName('pathEdit');#设置对象名称,方便后面在treeview中找到此对象
        lineEdit.setAlignment(Qt.AlignLeft);#设置文本对齐方式为左对齐

        treeView = fileMoveManager(self);
        lineEdit.setText(treeView.curNodePath);#设置首次显示的路径

        layout.addWidget(lineEdit);
        layout.addWidget(treeView);

        self.setLayout(layout);



app = QApplication([])
mainWindow = fileManagerTool();
mainWindow.show();
app.exec_()
