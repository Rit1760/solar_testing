# from PyQt6.QtWidgets import QApplication, QTabWidget, QMainWindow
# from live_monitor import LiveMonitorWidget
# import sys

# class GatewayApp(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Gateway Control Application")
#         self.resize(1000, 700)

#         tabs = QTabWidget()
#         tabs.addTab(LiveMonitorWidget(), "Live Monitor")
#         self.setCentralWidget(tabs)

# def main():
#     app = QApplication(sys.argv)
#     window = GatewayApp()
#     window.show()
#     sys.exit(app.exec())

# if __name__ == "__main__":
#     main()





from PyQt6.QtWidgets import QApplication, QTabWidget, QMainWindow
from live_monitor import LiveMonitorWidget
import sys

class GatewayApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gateway Control Application")
        self.resize(1000, 700)

        tabs = QTabWidget()
        tabs.addTab(LiveMonitorWidget(), "Live Monitor")
        self.setCentralWidget(tabs)

def main():
    app = QApplication(sys.argv)
    window = GatewayApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()