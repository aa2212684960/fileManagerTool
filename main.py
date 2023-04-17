import os,time,winshell
from PySide2.QtCore import QDir,Qt,QModelIndex,QItemSelectionModel
from PySide2.QtWidgets import QApplication, QFileSystemModel,QTreeView,QFileDialog,QHeaderView,QMenu,QInputDialog,\
    QMessageBox,QShortcut,QLineEdit,QVBoxLayout,QWidget
from PySide2.QtGui import QKeySequence
from  ProgressDialog.ProgressDialog import *

class fileManagerBase(QTreeView):
    def __init__(self,parent=None):
        super().__init__(parent);
        self.model = QFileSystemModel();
        self.rootPath = QFileDialog.getExistingDirectory();
        self.curNodePath = self.rootPath;
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
        pass;



    def showContextMenu(self, pos):
        self.menu.exec_(self.mapToGlobal(pos));


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

    def updateFriendWidget(self):#更新QlineEdit控件所显示的路径
        pass


class fileMoveManager(fileManagerBase):
    def __init__(self,parent=None):
        super().__init__(parent);
        self.progressDialog = ProgressDialogForFile(self.rootPath);

    def setContextMenu(self):
        self.menu = QMenu()
        createFolder = self.menu.addAction('新建文件夹');
        delFolder = self.menu.addAction('删除文件');
        undelFolder = self.menu.addAction('删除回滚');
        addTag = self.menu.addAction('追加标签');

        createFolder.setShortcut('Ctrl+A');  # 设置快捷键
        delFolder.setShortcut('Ctrl+D');
        undelFolder.setShortcut('Ctrl+Z');

        #快捷键按下时触发对应函数
        createFolderShortcut = QShortcut(QKeySequence('Ctrl+A'), self);
        createFolderShortcut.activated.connect(self.createFolderAction);

        delFolderShortcut = QShortcut(QKeySequence('Ctrl+D'), self);
        delFolderShortcut.activated.connect(self.deleteAction);

        undelFolderShortcut = QShortcut(QKeySequence('Ctrl+Z'), self);
        undelFolderShortcut.activated.connect(self.undeleteAction);

        #按下触发对应函数
        createFolder.triggered.connect(self.createFolderAction);
        delFolder.triggered.connect(self.deleteAction);
        undelFolder.triggered.connect(self.undeleteAction);
        addTag.triggered.connect(self.apendTagToAllTxt);

    def createFolderAction(self):
        folderName ,ok = QInputDialog.getText(None,'请输入文件夹名称','',flags=Qt.WindowCloseButtonHint);#弹出输入框对话框
        if os.path.isdir(self.curNodePath):#判断是否是文件夹路径
            path = os.path.normpath(os.path.join(self.curNodePath, folderName));  # 组合路径然后根据所处平台路径规则设置正反斜杠
        else:#如果是文件目录
            prePath = os.path.split(self.curNodePath)[0];#获取上级目录
            path = os.path.normpath(os.path.join(prePath, folderName));  # 组合路径然后根据所处平台路径规则设置正反斜杠

        try:#若创建文件夹失败抛出异常则捕获异常之后输出此函数名
            os.mkdir(path);
        except Exception as e:
            print('createFolderAction:',e);


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

    def apendTagToAllTxt(self):
        tag, ok = QInputDialog.getText(None, '请输入本次新增的Tag', '', flags=Qt.WindowCloseButtonHint);#弹出输入框对话框,返回输入的文本和状态信息

        if tag == '':#如果没有输入任何信息则不进行任何操作
            return ;
        else:
            tag = f',{tag}';

        reply = QMessageBox.question(self, '警告', f'即将往所选文件夹中所有Tag文本中插入新Tag "{tag}" ,请确认！',
                                     QMessageBox.Yes | QMessageBox.No);#弹出警告框防止误操作

        if reply == QMessageBox.No:#若选择No则不进行任何操作
            return ;

        self.progressDialog.setVisible(True);
        for subdir, dirs, files in os.walk(self.curNodePath):  # 将路径分割成父路径,子目录数组,文件数组
            for file in files:
                filepath = os.path.normpath(os.path.join(subdir, file));  # 组合路径然后根据所处平台路径规则设置正反斜杠
                if filepath.endswith('.txt'):#检测文件是否为.txt文件
                    with open(filepath, 'a') as f:
                        f.write(tag)
                        self.progressDialog.setValue(self.progressDialog.value() + 1);#让进度条往前走一步

        self.progressDialog.setValue(self.progressDialog.value() + 1);#结尾再走一步到100%


    def undeleteAction(self):
        path = self.delFilePath.replace('/', '\\')
        winshell.recycle_bin().undelete(path);

    def updateFriendWidget(self):#
        friend = self.parent().findChild(QLineEdit,'pathEdit');
        friend.setText(self.curNodePath);#更新路径信息

    def mousePressEvent(self, event):#重写此事件,在按下鼠标右键呼出右键菜单的时做出响应
        if event.button() == Qt.RightButton:
            index = self.indexAt(event.pos());#获取当前鼠标位置所对应的QTreeview节点索引
            if index.isValid():#索引有效则说明鼠标右键在子文件夹或者文件上按下
                self.selectionModel().select(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows);#通过节点索引找到对应的行并设置整行为选中状态
                self.curNodePath = self.model.filePath(index);#更新当前文件或文件夹路径
            else:#鼠标在空白处按下
                self.curNodePath = self.rootPath;#修改当前节点路径为根节点

        elif event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos());  # 获取当前鼠标位置所对应的QTreeview节点索引
            if not index.isValid():#索引无效说明,当前鼠标点击在空处
                self.curNodePath = self.rootPath;#所以修改当前节点路径为根节点
                self.updateFriendWidget();#更新路径显示
        
        super().mousePressEvent(event);#调用父类的事件处理函数










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




if __name__ == '__main__':
    app = QApplication([])
    mainWindow = fileManagerTool();
    mainWindow.show();
    app.exec_()
