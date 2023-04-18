from PySide2.QtCore import QObject,Signal
import os

class Worker(QObject):
    def __init__(self):
        super().__init__()
        pass;

    def process(self):
        pass;


    def run(self):
        pass;


class AddTagWorker(Worker):
    progressValue = Signal(int);
    def __init__(self,path='',tag=''):
        super().__init__();
        self.path = path;
        self.tag = tag;
        self.i = 0;

    def process(self):
        if self.path == '' or self.tag == '':
            return ;
        for subdir, dirs, files in os.walk(self.path):  # 将路径分割成父路径,子目录数组,文件数组
            for file in files:
                filepath = os.path.normpath(os.path.join(subdir, file));  # 组合路径然后根据所处平台路径规则设置正反斜杠
                if filepath.endswith('.txt'):  # 检测文件是否为.txt文件
                    with open(filepath, 'a') as f:
                        f.write(self.tag)
                        self.run();

    def run(self):
        self.i += 1;
        self.progressValue.emit(self.i);