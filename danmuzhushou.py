import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.welcome import PandaTv


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = PandaTv()
    current_path = os.path.dirname(__file__)
    w.setWindowIcon(QIcon(os.path.join(current_path, 'sources/images/favicon.ico')))
    w.show()
    sys.exit(app.exec_())


