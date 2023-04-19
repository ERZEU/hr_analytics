import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem

from design_v2 import Ui_MainWindow
from controller import Function
from parse_async import df


class Qui(QtWidgets.QMainWindow):
    """Класс интерфейса"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mas_vac = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.obj_fun = Function()  # экземпляр класса контроллера
        self.ui.pushButton_2.clicked.connect(self.finder)
        self.ui.pushButton_3.clicked.connect(self.graphic_zp)
        self.ui.pushButton_4.clicked.connect(self.graphic_requirement)
        self.ui.pushButton_5.clicked.connect(self.graph_zp_region)
        self.ui.pushButton_6.clicked.connect(self.save)
        self.ui.pushButton_7.clicked.connect(self.graph_region)

        self.ui.tableWidget.horizontalScrollBar().setStyleSheet("""QScrollBar:horizontal{
                                                                    background-color: #060212;
                                                                    border: 0px;
                                                                     }
                                                                    QScrollBar::handle:horizontal{
                                                                        background-color: #51B56D;  }
                                                                        """)
        self.ui.tableWidget.verticalScrollBar().setStyleSheet("""QScrollBar:vertical{
                                                                    background-color: #060212;
                                                                    border: 0px;
                                                                     }
                                                                 QScrollBar::handle:vertical{
                                                                    background-color: #51B56D;  }""")
        self.ui.tableWidget.horizontalHeader().setDefaultSectionSize(135)
        self.ui.tableWidget.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background: rgb(20, 20, 19); color: white; padding-left: 5px; padding-right: 5px; }")
        self.ui.tableWidget.verticalHeader().setStyleSheet("QHeaderView::section{background: rgb(20, 20, 19); color: white }")
        self.ui.tableWidget.setColumnCount(9)
        self.ui.tableWidget.setRowCount(2000)
        self.ui.tableWidget.setHorizontalHeaderLabels(
            ["Компания", "Название вакансии", "Ссылка", "Город", "Время публикации", "Зарплата от", "Зарплата до",
             "cur", "Требования"])

    def finder(self):
        name_vac = self.ui.lineEdit.text()
        name_area = self.ui.lineEdit_2.text()
        self.mas_vac = self.obj_fun.get_vac(name_vac, name_area)
        self.show_vac(self.mas_vac)

    def graphic_zp(self):
        self.obj_fun.graph_zp(self.mas_vac)

    def graph_zp_region(self):
        self.obj_fun.graph_zp_region(self.mas_vac)

    def graphic_requirement(self):
        self.obj_fun.graph_names(self.mas_vac)

    def graph_region(self):
        self.obj_fun.graph_region(self.mas_vac)

    def show_vac(self, mas_vac):

        # заполнение таблицы
        self.ui.tableWidget.setColumnCount(9)
        self.ui.tableWidget.setRowCount(len(mas_vac.index))
        self.ui.tableWidget.setHorizontalHeaderLabels(
            ["Компания", "Название вакансии", "Ссылка", "Город", "Время публикации", "Зарплата от", "Зарплата до",
             "cur", "Требования"])

        for i, row in mas_vac.iterrows():
            self.ui.tableWidget.setRowCount(self.ui.tableWidget.rowCount() + 1)

            for j in range(self.ui.tableWidget.columnCount()):
                self.ui.tableWidget.setItem(i, j, QTableWidgetItem(str(row[j])))

        # отображение количества вакансий
        # self.ui.lcdNumber.clear()
        self.ui.lcdNumber.display(len(mas_vac.index))



    def save(self):
        self.obj_fun.save(self.mas_vac)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Qui()
    win.show()
    sys.exit(app.exec_())
