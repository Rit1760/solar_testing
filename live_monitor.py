
# import sys
# import datetime
# import inspect
# from PyQt6.QtWidgets import (
#     QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
#     QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
#     QScrollArea, QAbstractItemView, QMenu,
#     QApplication, QSpinBox
# )
# from PyQt6.QtCore import QTimer, Qt
# from PyQt6.QtGui import QShortcut, QKeySequence

# try:
#     from pymodbus.client import ModbusTcpClient
# except Exception:
#     from pymodbus.client.sync import ModbusTcpClient


# class LiveMonitorWidget(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)

#         self.setWindowTitle("Live Monitor — Configurable Strings")

#         self.node_count = 96
#         self.header_registers = 10
#         self.string_current_count = 24

#         self.client = None
#         self.connected = False
#         self._mb_kw = {"unit": 1}

#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_data)

#         self.table = None
#         self.scroll_area = None
#         self.str_spin = None

#         self._init_ui()

#     def _init_ui(self):
#         layout = QVBoxLayout(self)

#         conn_layout = QHBoxLayout()

#         self.ip_input = QLineEdit("192.168.1.20")
#         self.ip_input.setFixedWidth(130)

#         self.port_input = QLineEdit("502")
#         self.port_input.setFixedWidth(60)

#         conn_layout.addWidget(QLabel("IP:"))
#         conn_layout.addWidget(self.ip_input)
#         conn_layout.addWidget(QLabel("Port:"))
#         conn_layout.addWidget(self.port_input)

#         self.str_spin = QSpinBox()
#         self.str_spin.setRange(1, 24)
#         self.str_spin.setValue(self.string_current_count)

#         apply_btn = QPushButton("Apply")
#         apply_btn.clicked.connect(self._apply_string_columns)

#         clear_btn = QPushButton("Clear")
#         clear_btn.clicked.connect(self.clear_table_data)

#         conn_layout.addWidget(QLabel("Strings:"))
#         conn_layout.addWidget(self.str_spin)
#         conn_layout.addWidget(apply_btn)
#         conn_layout.addWidget(clear_btn)

#         # ================= LIVE CLOCK + RX STATUS =================
#         self.date_time_label = QLabel()
#         self.rx_status_label = QLabel("Rx: ---")
#         self.node_status_label = QLabel("Nodes: 0/96")
#         conn_layout.addWidget(self.node_status_label)

#         def update_clock():
#             now = datetime.datetime.now()
#             self.date_time_label.setText(now.strftime("%Y-%m-%d | %H:%M:%S"))

#         self.clock_timer = QTimer(self)
#         self.clock_timer.timeout.connect(update_clock)
#         self.clock_timer.start(1000)
#         update_clock()

#         conn_layout.addWidget(self.date_time_label)
#         conn_layout.addWidget(self.rx_status_label)

#         # ================= CONNECT BUTTON (LAST RIGHT) =================
#         self.connect_button = QPushButton("Connect")
#         self.connect_button.clicked.connect(self.toggle_connection)
#         self.set_button_disconnected_style()
#         conn_layout.addWidget(self.connect_button)

#         layout.addLayout(conn_layout)

#         # ================= TABLE =================
#         self.scroll_area = QScrollArea()
#         self.scroll_area.setWidgetResizable(True)
#         layout.addWidget(self.scroll_area)

#         self.status_label = QLabel("Status: Idle")
#         layout.addWidget(self.status_label)

#         self._rebuild_table(self.string_current_count)




#     def _apply_string_columns(self):
#         new_count = int(self.str_spin.value())
#         if new_count != self.string_current_count:
#             self._rebuild_table(new_count)
#             self.status_label.setText(f"Applied {new_count} String Columns")

#     def clear_table_data(self):
#         if not self.table:
#             return

#         for i in range(self.node_count):
#             for j in range(1, self.table.columnCount()):
#                 self.table.setItem(i, j, QTableWidgetItem(""))

#         self.status_label.setText("Data Cleared")

#     def set_button_connected_style(self):
#         self.connect_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #2e7d32;
#                 color: white;
#                 padding: 6px 12px;
#                 border-radius: 6px;
#             }
#         """)

#     def set_button_disconnected_style(self):
#         self.connect_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #d32f2f;
#                 color: white;
#                 padding: 6px 12px;
#                 border-radius: 6px;
#             }
#         """)

#     def _rebuild_table(self, string_count):
#         total_columns = 13 + string_count

#         headers = [
#             "ID", "Reading Time", "Rx Node", "SMB Node ID", "Comm Status",
#             "SPD Status", "DC Switch", "Temp", "Board Temp",
#             "Bus Voltage", "Output Current", "Power MSB", "Power LSB"
#         ] + [f"String {i+1}" for i in range(string_count)]

#         new_table = QTableWidget(self.node_count, total_columns, self)
#         new_table.setHorizontalHeaderLabels(headers)

#         new_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
#         new_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

#         new_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
#         new_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
#         new_table.verticalHeader().setVisible(False)

#         QShortcut(QKeySequence.StandardKey.Copy, new_table,
#                   activated=self.copy_selected_cells)

#         new_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
#         new_table.customContextMenuRequested.connect(self.show_table_context_menu)

#         for i in range(self.node_count):
#             new_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

#         self.scroll_area.setWidget(new_table)
#         self.table = new_table
#         self.string_current_count = string_count

#     def copy_selected_cells(self):
#         if not self.table:
#             return

#         selected = self.table.selectedIndexes()
#         if not selected:
#             return

#         selected = sorted(selected, key=lambda x: (x.row(), x.column()))

#         rows = {}
#         for index in selected:
#             row = index.row()
#             col = index.column()
#             if row not in rows:
#                 rows[row] = {}
#             item = self.table.item(row, col)
#             rows[row][col] = "" if item is None else item.text()

#         output = []
#         for r in sorted(rows.keys()):
#             cols = rows[r]
#             line = [cols.get(c, "") for c in range(min(cols), max(cols)+1)]
#             output.append("\t".join(line))

#         QApplication.clipboard().setText("\n".join(output))

#     def show_table_context_menu(self, pos):
#         menu = QMenu(self)
#         copy_action = menu.addAction("Copy")
#         if menu.exec(self.table.viewport().mapToGlobal(pos)) == copy_action:
#             self.copy_selected_cells()

#     def toggle_connection(self):
#         if not self.connected:
#             self.connect_to_gateway()
#         else:
#             self.disconnect_from_gateway()

#     def connect_to_gateway(self):
#         try:
#             ip = self.ip_input.text().strip()
#             port = int(self.port_input.text().strip())

#             self.client = ModbusTcpClient(ip, port=port, timeout=3)

#             if not self.client.connect():
#                 raise Exception("Connection failed")

#             params = inspect.signature(self.client.read_holding_registers).parameters
#             self._mb_kw = {"slave": 1} if "slave" in params else {"unit": 1}

#             self.connected = True
#             self.connect_button.setText("Disconnect")
#             self.set_button_connected_style()
#             self.status_label.setText("Connected")

#             self.timer.start(2000)

#         except Exception as e:
#             self.status_label.setText(f"Error: {e}")

#     def disconnect_from_gateway(self):
#         self.connected = False
#         self.timer.stop()

#         if self.client:
#             self.client.close()

#         self.client = None
#         self.connect_button.setText("Connect")
#         self.set_button_disconnected_style()
#         self.status_label.setText("Disconnected")

#     def update_data(self):
#         if not self.client:
#             return

#         try:
#             now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#             self.table.setUpdatesEnabled(False)

#             for i in range(self.node_count):
#                 base = 10 + i * 40
#                 result = self.client.read_holding_registers(base, 40, **self._mb_kw)

#                 if not result or result.isError():
#                     continue

#                 regs = result.registers

#                 def safe(idx, default=0):
#                     return regs[idx] if idx < len(regs) else default

#                 rx_node = safe(39)
#                 smb_id = safe(0)
#                 temp = safe(7)

#                 self.table.setItem(i, 1, QTableWidgetItem(now))
#                 self.table.setItem(i, 2, QTableWidgetItem(str(rx_node)))
#                 self.table.setItem(i, 3, QTableWidgetItem(str(smb_id)))
#                 self.table.setItem(i, 7, QTableWidgetItem(str(temp)))

#             self.table.setUpdatesEnabled(True)

#             # RX STATUS UPDATE
#             ok = sum(1 for i in range(self.node_count)
#                      if self.table.item(i, 2)
#                      and self.table.item(i, 2).text().isdigit()
#                      and int(self.table.item(i, 2).text()) != 0)

#             self.rx_status_label.setText(f"Rx: OK={ok} FAIL={self.node_count-ok}")

#         except Exception as e:
#             self.status_label.setText(f"Polling Error: {e}")
#             self.disconnect_from_gateway()


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w = LiveMonitorWidget()
#     w.resize(1400, 800)
#     w.show()
#     sys.exit(app.exec())


































# import sys
# import datetime
# import inspect
# from PyQt6.QtWidgets import (
#     QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
#     QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
#     QScrollArea, QAbstractItemView, QMenu,
#     QApplication, QSpinBox
# )
# from PyQt6.QtCore import QTimer, Qt
# from PyQt6.QtGui import QShortcut, QKeySequence

# try:
#     from pymodbus.client import ModbusTcpClient
# except Exception:
#     from pymodbus.client.sync import ModbusTcpClient


# class LiveMonitorWidget(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)

#         self.setWindowTitle("Live Monitor — Configurable Strings")

#         self.node_count = 96
#         self.header_registers = 10
#         self.string_current_count = 24

#         self.client = None
#         self.connected = False
#         self._mb_kw = {"unit": 1}

#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_data)

#         self.reconnect_attempts = 0
#         self.max_reconnect_attempts = 5

#         self.table = None
#         self.scroll_area = None
#         self.str_spin = None

#         self._init_ui()

#     def _init_ui(self):
#         layout = QVBoxLayout(self)

#         conn_layout = QHBoxLayout()

#         self.ip_input = QLineEdit("192.168.1.20")
#         self.ip_input.setFixedWidth(230)

#         self.port_input = QLineEdit("502")
#         self.port_input.setFixedWidth(150)

#         conn_layout.addWidget(QLabel("IP:"))
#         conn_layout.addWidget(self.ip_input)
#         conn_layout.addWidget(QLabel("Port:"))
#         conn_layout.addWidget(self.port_input)

#         self.str_spin = QSpinBox()
#         self.str_spin.setRange(1, 24)
#         self.str_spin.setValue(self.string_current_count)

#         apply_btn = QPushButton("Apply")
#         apply_btn.clicked.connect(self._apply_string_columns)

#         clear_btn = QPushButton("Clear")
#         clear_btn.clicked.connect(self.clear_table_data)

#         conn_layout.addWidget(QLabel("Strings:"))
#         conn_layout.addWidget(self.str_spin)
#         conn_layout.addWidget(apply_btn)
#         conn_layout.addWidget(clear_btn)

#         self.date_time_label = QLabel()
#         self.rx_status_label = QLabel("TX: ---")

#         self.node_status_label = QLabel("Nodes: 0")
#         self.gateway_status_label = QLabel("Gateway Sr No: 0")

#         def update_clock():
#             now = datetime.datetime.now()
#             self.date_time_label.setText(now.strftime("%Y-%m-%d | %H:%M:%S"))

#         self.clock_timer = QTimer(self)
#         self.clock_timer.timeout.connect(update_clock)
#         self.clock_timer.start(1000)
#         update_clock()

#         conn_layout.addWidget(self.date_time_label)
#         conn_layout.addWidget(self.rx_status_label)
#         conn_layout.addWidget(self.gateway_status_label)

#         conn_layout.addWidget(self.node_status_label)

#         self.connect_button = QPushButton("Connect")
#         self.connect_button.clicked.connect(self.toggle_connection)
#         self.set_button_disconnected_style()
#         conn_layout.addWidget(self.connect_button)

#         layout.addLayout(conn_layout)

#         self.scroll_area = QScrollArea()
#         self.scroll_area.setWidgetResizable(True)
#         layout.addWidget(self.scroll_area)

#         self.status_label = QLabel("Status: Idle")
#         layout.addWidget(self.status_label)

#         self._rebuild_table(self.string_current_count)

#     def _apply_string_columns(self):
#         new_count = int(self.str_spin.value())
#         if new_count != self.string_current_count:
#             self._rebuild_table(new_count)
#             self.status_label.setText(f"Applied {new_count} String Columns")

#     def clear_table_data(self):
#         if not self.table:
#             return

#         for i in range(self.node_count):
#             for j in range(1, self.table.columnCount()):
#                 self.table.setItem(i, j, QTableWidgetItem(""))

#         self.status_label.setText("Data Cleared")

#     def set_button_connected_style(self):
#         self.connect_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #2e7d32;
#                 color: white;
#                 padding: 6px 12px;
#                 border-radius: 6px;
#             }
#         """)

#     def set_button_disconnected_style(self):
#         self.connect_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #d32f2f;
#                 color: white;
#                 padding: 6px 12px;
#                 border-radius: 6px;
#             }
#         """)

#     def _rebuild_table(self, string_count):
#         total_columns = 13 + string_count

#         headers = [
#             "ID", "Reading Time", "Rx Node", "SMB Node ID", "Comm Status",
#             "SPD Status", "DC Switch", "Temp", "Board Temp",
#             "Bus Voltage", "Output Current", "Power MSB", "Power LSB"
#         ] + [f"String {i+1}" for i in range(string_count)]

#         new_table = QTableWidget(self.node_count, total_columns, self)
#         new_table.setHorizontalHeaderLabels(headers)

#         new_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
#         new_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

#         new_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
#         new_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
#         new_table.verticalHeader().setVisible(False)

#         QShortcut(QKeySequence.StandardKey.Copy, new_table,
#                   activated=self.copy_selected_cells)

#         new_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
#         new_table.customContextMenuRequested.connect(self.show_table_context_menu)

#         for i in range(self.node_count):
#             new_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

#         self.scroll_area.setWidget(new_table)
#         self.table = new_table
#         self.string_current_count = string_count

#     def copy_selected_cells(self):
#         if not self.table:
#             return

#         selected = self.table.selectedIndexes()
#         if not selected:
#             return

#         selected = sorted(selected, key=lambda x: (x.row(), x.column()))

#         rows = {}
#         for index in selected:
#             row = index.row()
#             col = index.column()
#             if row not in rows:
#                 rows[row] = {}
#             item = self.table.item(row, col)
#             rows[row][col] = "" if item is None else item.text()

#         output = []
#         for r in sorted(rows.keys()):
#             cols = rows[r]
#             line = [cols.get(c, "") for c in range(min(cols), max(cols)+1)]
#             output.append("\t".join(line))

#         QApplication.clipboard().setText("\n".join(output))

#     def show_table_context_menu(self, pos):
#         menu = QMenu(self)
#         copy_action = menu.addAction("Copy")
#         if menu.exec(self.table.viewport().mapToGlobal(pos)) == copy_action:
#             self.copy_selected_cells()

#     def toggle_connection(self):
#         if not self.connected:
#             self.connect_to_gateway()
#         else:
#             self.disconnect_from_gateway()

#     def connect_to_gateway(self):
#         try:
#             ip = self.ip_input.text().strip()
#             port = int(self.port_input.text().strip())

#             self.client = ModbusTcpClient(ip, port=port, timeout=3)

#             if not self.client.connect():
#                 raise Exception("Connection failed")

#             params = inspect.signature(self.client.read_holding_registers).parameters
#             self._mb_kw = {"slave": 1} if "slave" in params else {"unit": 1}

#             self.connected = True
#             self.reconnect_attempts = 0 
#             self.connect_button.setText("Disconnect")
#             self.set_button_connected_style()
#             self.status_label.setText("Connected")

#             self.timer.start(2000)

#         except Exception as e:
#             self.status_label.setText(f"Error: {e}")

#     def disconnect_from_gateway(self):
#         self.connected = False
#         self.timer.stop()

#         if self.client:
#             self.client.close()

#         self.client = None
#         self.connect_button.setText("Connect")
#         self.set_button_disconnected_style()
#         self.status_label.setText("Disconnected")


#     def try_reconnect(self):
#         if self.reconnect_attempts >= self.max_reconnect_attempts:
#             self.status_label.setText("Reconnect Failed ")
#             return

#         self.reconnect_attempts += 1
#         delay = 3000 * self.reconnect_attempts

#         self.status_label.setText(
#               f"Reconnecting... Attempt {self.reconnect_attempts} (in {delay//1000}s)"
#             )

#         QTimer.singleShot(delay, self.connect_to_gateway)


#     def update_data(self):
#         if not self.client:
#             return

#         try:
#             now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#             self.table.setUpdatesEnabled(False)

#             for i in range(self.node_count):
#                 base = 10 + i * 40
#                 result = self.client.read_holding_registers(base, 40, **self._mb_kw)

#                 if not result or result.isError():
#                     continue

#                 regs = result.registers

#                 def safe(idx, default=0):
#                     return regs[idx] if idx < len(regs) else default


#                 rx_node = safe(39)
#                 smb_id = safe(0)
#                 comm_status = safe(1)
#                 spd_status = safe(2)
#                 dc_switch = safe(3)
#                 temp = safe(7)
#                 board_temp = safe(8)
#                 bus_voltage = safe(9)
#                 output_current = safe(10)
#                 power_msb = safe(11)
#                 power_lsb = safe(12)

#                 self.table.setItem(i, 1, QTableWidgetItem(now))
#                 self.table.setItem(i, 2, QTableWidgetItem(str(rx_node)))
#                 self.table.setItem(i, 3, QTableWidgetItem(str(smb_id)))
#                 self.table.setItem(i, 4, QTableWidgetItem(str(comm_status)))
#                 self.table.setItem(i, 5, QTableWidgetItem(str(spd_status)))
#                 self.table.setItem(i, 6, QTableWidgetItem(str(dc_switch)))
#                 self.table.setItem(i, 7, QTableWidgetItem(str(temp)))
#                 self.table.setItem(i, 8, QTableWidgetItem(str(board_temp)))
#                 self.table.setItem(i, 9, QTableWidgetItem(str(bus_voltage)))
#                 self.table.setItem(i, 10, QTableWidgetItem(str(output_current)))
#                 self.table.setItem(i, 11, QTableWidgetItem(str(power_msb)))
#                 self.table.setItem(i, 12, QTableWidgetItem(str(power_lsb)))

                

#                 for s in range(self.string_current_count):
#                     value = safe(13 + s)
#                     self.table.setItem(i, 13 + s, QTableWidgetItem(str(value)))

#             self.table.setUpdatesEnabled(True)

#             ok = sum(1 for i in range(self.node_count)
#                      if self.table.item(i, 2)
#                      and self.table.item(i, 2).text().isdigit()
#                      and int(self.table.item(i, 2).text()) != 0)

#             self.rx_status_label.setText(f"TX: OK={ok} FAIL={self.node_count-ok}")

#             self.node_status_label.setText(f"Nodes: {ok}/{self.node_count}")

#         except Exception as e:
#             self.status_label.setText(f"Polling Error: {e}")
#             self.disconnect_from_gateway()

#             QTimer.singleShot(3000, self.try_reconnect)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w = LiveMonitorWidget()
#     w.resize(1400, 800)
#     w.show()
#     sys.exit(app.exec())












# ALL DATA IN THIS CODE 











import sys
import datetime
import inspect
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QAbstractItemView, QMenu,
    QApplication, QSpinBox
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QShortcut, QKeySequence

try:
    from pymodbus.client import ModbusTcpClient
except Exception:
    from pymodbus.client.sync import ModbusTcpClient


class LiveMonitorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Live Monitor — Configurable Strings")

        self.node_count = 96
        self.header_registers = 10
        self.string_current_count = 24

        self.client = None
        self.connected = False
        self._mb_kw = {"unit": 1}

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)

        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

        self.table = None
        self.scroll_area = None
        self.str_spin = None

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        conn_layout = QHBoxLayout()

        self.ip_input = QLineEdit("192.168.1.20")
        self.ip_input.setFixedWidth(230)

        self.port_input = QLineEdit("502")
        self.port_input.setFixedWidth(150)

        conn_layout.addWidget(QLabel("IP:"))
        conn_layout.addWidget(self.ip_input)
        conn_layout.addWidget(QLabel("Port:"))
        conn_layout.addWidget(self.port_input)

        self.str_spin = QSpinBox()
        self.str_spin.setRange(1, 24)
        self.str_spin.setValue(self.string_current_count)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_string_columns)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_table_data)

        conn_layout.addWidget(QLabel("Strings:"))
        conn_layout.addWidget(self.str_spin)
        conn_layout.addWidget(apply_btn)
        conn_layout.addWidget(clear_btn)

        self.date_time_label = QLabel()
        self.rx_status_label = QLabel("TX: ---")
        self.node_status_label = QLabel("Nodes: 0")
        self.gateway_status_label = QLabel("Gateway Sr No: 0")

        def update_clock():
            now = datetime.datetime.now()
            self.date_time_label.setText(now.strftime("%Y-%m-%d | %H:%M:%S"))

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(update_clock)
        self.clock_timer.start(1000)
        update_clock()

        conn_layout.addWidget(self.date_time_label)
        conn_layout.addWidget(self.rx_status_label)
        conn_layout.addWidget(self.gateway_status_label)
        conn_layout.addWidget(self.node_status_label)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        self.set_button_disconnected_style()
        conn_layout.addWidget(self.connect_button)

        layout.addLayout(conn_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        self._rebuild_table(self.string_current_count)

    def _apply_string_columns(self):
        new_count = int(self.str_spin.value())
        if new_count != self.string_current_count:
            self._rebuild_table(new_count)
            self.status_label.setText(f"Applied {new_count} String Columns")

    def clear_table_data(self):
        if not self.table:
            return

        for i in range(self.node_count):
            for j in range(1, self.table.columnCount()):
                self.table.setItem(i, j, QTableWidgetItem(""))

        self.status_label.setText("Data Cleared")

    def set_button_connected_style(self):
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
        """)

    def set_button_disconnected_style(self):
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
        """)

    def _rebuild_table(self, string_count):
        total_columns = 13 + string_count

        headers = [
            "ID", "Reading Time", "Rx Node", "SMB Node ID", "Comm Status",
            "SPD Status", "DC Switch", "Temp", "Board Temp",
            "Bus Voltage", "Output Current", "Power MSB", "Power LSB"
        ] + [f"String {i+1}" for i in range(string_count)]

        new_table = QTableWidget(self.node_count, total_columns, self)
        new_table.setHorizontalHeaderLabels(headers)

        new_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        new_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

        new_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        new_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        new_table.verticalHeader().setVisible(False)

        QShortcut(QKeySequence.StandardKey.Copy, new_table,
                  activated=self.copy_selected_cells)

        new_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        new_table.customContextMenuRequested.connect(self.show_table_context_menu)

        for i in range(self.node_count):
            new_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

        self.scroll_area.setWidget(new_table)
        self.table = new_table
        self.string_current_count = string_count

    def copy_selected_cells(self):
        if not self.table:
            return

        selected = self.table.selectedIndexes()
        if not selected:
            return

        selected = sorted(selected, key=lambda x: (x.row(), x.column()))

        rows = {}
        for index in selected:
            row = index.row()
            col = index.column()
            if row not in rows:
                rows[row] = {}
            item = self.table.item(row, col)
            rows[row][col] = "" if item is None else item.text()

        output = []
        for r in sorted(rows.keys()):
            cols = rows[r]
            line = [cols.get(c, "") for c in range(min(cols), max(cols)+1)]
            output.append("\t".join(line))

        QApplication.clipboard().setText("\n".join(output))

    def show_table_context_menu(self, pos):
        menu = QMenu(self)
        copy_action = menu.addAction("Copy")
        if menu.exec(self.table.viewport().mapToGlobal(pos)) == copy_action:
            self.copy_selected_cells()

    def toggle_connection(self):
        if not self.connected:
            self.connect_to_gateway()
        else:
            self.disconnect_from_gateway()

    def connect_to_gateway(self):
        try:
            ip = self.ip_input.text().strip()
            port = int(self.port_input.text().strip())

            self.client = ModbusTcpClient(ip, port=port, timeout=3)

            if not self.client.connect():
                raise Exception("Connection failed")

            params = inspect.signature(self.client.read_holding_registers).parameters
            self._mb_kw = {"slave": 1} if "slave" in params else {"unit": 1}

            self.connected = True
            self.reconnect_attempts = 0
            self.connect_button.setText("Disconnect")
            self.set_button_connected_style()
            self.status_label.setText("Connected")

            self.timer.start(2000)

        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def disconnect_from_gateway(self):
        self.connected = False
        self.timer.stop()

        if self.client:
            self.client.close()

        self.client = None
        self.connect_button.setText("Connect")
        self.set_button_disconnected_style()
        self.status_label.setText("Disconnected")

    def try_reconnect(self):
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.status_label.setText("Reconnect Failed ")
            return

        self.reconnect_attempts += 1
        delay = 3000 * self.reconnect_attempts

        self.status_label.setText(
            f"Reconnecting... Attempt {self.reconnect_attempts} (in {delay//1000}s)"
        )

        QTimer.singleShot(delay, self.connect_to_gateway)

    def update_data(self):



        if not self.client:
            return

        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.table.setUpdatesEnabled(False)

            for i in range(self.node_count):
                base = 10 + i * 40
                result = self.client.read_holding_registers(base, 40, **self._mb_kw)

                if not result or result.isError():
                    continue

                regs = result.registers

                def safe(idx, default=0):
                    return regs[idx] if idx < len(regs) else default

                rx_node = safe(39)
                smb_id = safe(0)
                smb_status = safe(6)

                temp = safe(7)
                board_temp = safe(8)
                bus_voltage = safe(9)
                output_current = safe(10) / 10.0
                power_msb = safe(11)
                power_lsb = safe(12)

                if smb_status & 0b10:
                    comm_status = "SMB RF Fail"
                elif smb_status & 0b1:
                    comm_status = "SMB RS485 Fail"
                else:
                    comm_status = "OK"

                spd_status = "Fail" if (smb_status & 0b100000) else "OK"
                dc_switch = "OFF" if (smb_status & 0b10000) else "ON"

                if rx_node == 0:
                    for col in range(4, 13 + self.string_current_count):
                        self.table.setItem(i, col, QTableWidgetItem("---"))
                    continue

                self.table.setItem(i, 1, QTableWidgetItem(now))
                self.table.setItem(i, 2, QTableWidgetItem(str(rx_node)))
                self.table.setItem(i, 3, QTableWidgetItem(str(smb_id)))
                self.table.setItem(i, 4, QTableWidgetItem(comm_status))
                self.table.setItem(i, 5, QTableWidgetItem(spd_status))
                self.table.setItem(i, 6, QTableWidgetItem(dc_switch))
                self.table.setItem(i, 7, QTableWidgetItem(str(temp)))
                self.table.setItem(i, 8, QTableWidgetItem(str(board_temp)))
                self.table.setItem(i, 9, QTableWidgetItem(str(bus_voltage)))
                self.table.setItem(i, 10, QTableWidgetItem(str(output_current)))
                self.table.setItem(i, 11, QTableWidgetItem(str(power_msb)))
                self.table.setItem(i, 12, QTableWidgetItem(str(power_lsb)))

                for s in range(self.string_current_count):
                    value = safe(13 + s) / 1000.0
                    self.table.setItem(i, 13 + s, QTableWidgetItem(str(value)))

            self.table.setUpdatesEnabled(True)

            ok = sum(1 for i in range(self.node_count)
                     if self.table.item(i, 2)
                     and self.table.item(i, 2).text().isdigit()
                     and int(self.table.item(i, 2).text()) != 0)

            self.rx_status_label.setText(f"TX: OK={ok} FAIL={self.node_count-ok}")
            self.node_status_label.setText(f"Nodes: {ok}/{self.node_count}")

        except Exception as e:
            self.status_label.setText(f"Polling Error: {e}")
            self.disconnect_from_gateway()
            QTimer.singleShot(3000, self.try_reconnect)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LiveMonitorWidget()
    w.resize(1400, 800)
    w.show()
    sys.exit(app.exec())














# import sys
# import datetime
# import inspect
# from PyQt6.QtWidgets import (
#     QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
#     QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
#     QScrollArea, QAbstractItemView, QMenu,
#     QApplication, QSpinBox
# )
# from PyQt6.QtCore import QTimer, Qt
# from PyQt6.QtGui import QShortcut, QKeySequence

# try:
#     from pymodbus.client import ModbusTcpClient
# except Exception:
#     from pymodbus.client.sync import ModbusTcpClient


# class LiveMonitorWidget(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)

#         self.setWindowTitle("Live Monitor — Configurable Strings")

#         self.node_count = 96
#         self.header_registers = 10
#         self.string_current_count = 24

#         self.client = None
#         self.connected = False
#         self._mb_kw = {"unit": 1}

#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_data)

#         self.reconnect_attempts = 0
#         self.max_reconnect_attempts = 5

#         self.table = None
#         self.scroll_area = None
#         self.str_spin = None

#         self._init_ui()

#     def _init_ui(self):
#         layout = QVBoxLayout(self)
#         conn_layout = QHBoxLayout()

#         self.ip_input = QLineEdit("192.168.1.20")
#         self.port_input = QLineEdit("502")

#         conn_layout.addWidget(QLabel("IP:"))
#         conn_layout.addWidget(self.ip_input)
#         conn_layout.addWidget(QLabel("Port:"))
#         conn_layout.addWidget(self.port_input)

#         self.str_spin = QSpinBox()
#         self.str_spin.setRange(1, 24)
#         self.str_spin.setValue(self.string_current_count)

#         apply_btn = QPushButton("Apply")
#         apply_btn.clicked.connect(self._apply_string_columns)

#         clear_btn = QPushButton("Clear")
#         clear_btn.clicked.connect(self.clear_table_data)

#         conn_layout.addWidget(QLabel("Strings:"))
#         conn_layout.addWidget(self.str_spin)
#         conn_layout.addWidget(apply_btn)
#         conn_layout.addWidget(clear_btn)

#         self.date_time_label = QLabel()
#         self.rx_status_label = QLabel("TX: ---")
#         self.node_status_label = QLabel("Nodes: 0")
#         self.gateway_status_label = QLabel("Gateway Sr No: 0")

#         def update_clock():
#             now = datetime.datetime.now()
#             self.date_time_label.setText(now.strftime("%Y-%m-%d | %H:%M:%S"))

#         self.clock_timer = QTimer(self)
#         self.clock_timer.timeout.connect(update_clock)
#         self.clock_timer.start(1000)
#         update_clock()

#         conn_layout.addWidget(self.date_time_label)
#         conn_layout.addWidget(self.rx_status_label)
#         conn_layout.addWidget(self.gateway_status_label)
#         conn_layout.addWidget(self.node_status_label)

#         self.connect_button = QPushButton("Connect")
#         self.connect_button.clicked.connect(self.toggle_connection)
#         conn_layout.addWidget(self.connect_button)

#         layout.addLayout(conn_layout)

#         self.scroll_area = QScrollArea()
#         self.scroll_area.setWidgetResizable(True)
#         layout.addWidget(self.scroll_area)

#         self.status_label = QLabel("Status: Idle")
#         layout.addWidget(self.status_label)

#         self._rebuild_table(self.string_current_count)

#     def _apply_string_columns(self):
#         new_count = int(self.str_spin.value())
#         if new_count != self.string_current_count:
#             self._rebuild_table(new_count)

#     def clear_table_data(self):
#         if not self.table:
#             return
#         for i in range(self.node_count):
#             for j in range(1, self.table.columnCount()):
#                 self.table.setItem(i, j, QTableWidgetItem(""))

#     def _rebuild_table(self, string_count):
#         total_columns = 13 + string_count

#         headers = [
#             "ID", "Reading Time", "Rx Node", "SMB Node ID", "Comm Status",
#             "SPD Status", "DC Switch", "Temp", "Board Temp",
#             "Bus Voltage", "Output Current", "Power MSB", "Power LSB"
#         ] + [f"String {i+1}" for i in range(string_count)]

#         table = QTableWidget(self.node_count, total_columns)
#         table.setHorizontalHeaderLabels(headers)

#         for i in range(self.node_count):
#             table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

#         self.scroll_area.setWidget(table)
#         self.table = table
#         self.string_current_count = string_count

#     def toggle_connection(self):
#         if not self.connected:
#             self.connect_to_gateway()
#         else:
#             self.disconnect_from_gateway()

#     def connect_to_gateway(self):
#         try:
#             ip = self.ip_input.text()
#             port = int(self.port_input.text())

#             self.client = ModbusTcpClient(ip, port=port)
#             if not self.client.connect():
#                 raise Exception("Connection failed")

#             params = inspect.signature(self.client.read_holding_registers).parameters
#             self._mb_kw = {"slave": 1} if "slave" in params else {"unit": 1}

#             self.connected = True
#             self.connect_button.setText("Disconnect")
#             self.timer.start(2000)

#         except Exception as e:
#             self.status_label.setText(str(e))

#     def disconnect_from_gateway(self):
#         self.connected = False
#         self.timer.stop()
#         if self.client:
#             self.client.close()
#         self.connect_button.setText("Connect")

#     def update_data(self):
#         if not self.client:
#             return

#         try:
#             now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#             header = self.client.read_holding_registers(0, 10, **self._mb_kw)
#             if header and not header.isError():
#                 hregs = header.registers
#                 if len(hregs) >= 2:
#                     gateway_sr = (hregs[0] << 16) | hregs[1]
#                     self.gateway_status_label.setText(f"Gateway Sr No: {gateway_sr}")

#             self.table.setUpdatesEnabled(False)

#             for i in range(self.node_count):
#                 base = 10 + i * 40
#                 result = self.client.read_holding_registers(base, 40, **self._mb_kw)

#                 if not result or result.isError():
#                     continue

#                 regs = result.registers

#                 def safe(idx):
#                     return regs[idx] if idx < len(regs) else 0

#                 rx_node = safe(39)
#                 smb_id = safe(0)
#                 smb_status = safe(6)

#                 temp = safe(7)
#                 board_temp = safe(8)
#                 bus_voltage = safe(9)
#                 output_current = safe(10) / 10.0
#                 power_msb = safe(11)
#                 power_lsb = safe(12)

#                 if smb_status & 0b10:
#                     comm_status = "RF Fail"
#                 elif smb_status & 0b1:
#                     comm_status = "RS485 Fail"
#                 else:
#                     comm_status = "OK"

#                 spd_status = "Fail" if (smb_status & 0b100000) else "OK"
#                 dc_switch = "OFF" if (smb_status & 0b10000) else "ON"

#                 if rx_node == 0:
#                     continue

#                 self.table.setItem(i, 1, QTableWidgetItem(now))
#                 self.table.setItem(i, 2, QTableWidgetItem(str(rx_node)))
#                 self.table.setItem(i, 3, QTableWidgetItem(str(smb_id)))
#                 self.table.setItem(i, 4, QTableWidgetItem(comm_status))
#                 self.table.setItem(i, 5, QTableWidgetItem(spd_status))
#                 self.table.setItem(i, 6, QTableWidgetItem(dc_switch))
#                 self.table.setItem(i, 7, QTableWidgetItem(str(temp)))
#                 self.table.setItem(i, 8, QTableWidgetItem(str(board_temp)))
#                 self.table.setItem(i, 9, QTableWidgetItem(str(bus_voltage)))
#                 self.table.setItem(i, 10, QTableWidgetItem(str(output_current)))
#                 self.table.setItem(i, 11, QTableWidgetItem(str(power_msb)))
#                 self.table.setItem(i, 12, QTableWidgetItem(str(power_lsb)))

#                 for s in range(self.string_current_count):
#                     val = safe(13 + s) / 1000.0
#                     self.table.setItem(i, 13 + s, QTableWidgetItem(str(val)))

#             self.table.setUpdatesEnabled(True)

#         except Exception as e:
#             self.status_label.setText(f"Error: {e}")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w = LiveMonitorWidget()
#     w.resize(1400, 800)
#     w.show()
#     sys.exit(app.exec())