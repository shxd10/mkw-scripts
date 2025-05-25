import sys
import os
import struct
import csv
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import QTimer, QSettings
import external_utils as ex

# This constant determines how the buttons are arranged.
# Ex: BUTTON_LAYOUT[section_index][row_index][column_index]
BUTTON_LAYOUT = [
    [
        ["Load from Player", "Load from Ghost"],
        ["Save to RKG", "Load from RKG"],
        ["Open in Editor", "Load from CSV"],
    ],
    [
        ["Load from Player", "Load from Ghost"],
        ["Save to RKG", "Load from RKG"],
        ["Open in Editor", "Load from CSV"],
    ],
]

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        try:
            self.shm_activate = ex.SharedMemoryBlock.connect(name="editor_activate")
            self.shm_buttons = ex.SharedMemoryBlock.connect(name="editor_buttons")
            self.shm_player_csv = ex.SharedMemoryReader(name="editor_player_csv")
            self.shm_ghost_csv = ex.SharedMemoryReader(name="editor_ghost_csv")
            self.shm_close_event = ex.SharedMemoryBlock.connect(name="editor_window_closed")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Shared memory buffer '{e.filename}' not found. Make sure the `editor` script is enabled.")
        
        self.setWindowTitle("TAS Toolkit GUI")
        self.setGeometry(100, 100, 500, 250)
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)  # For topmost equivalent
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        root_layout = QHBoxLayout(central_widget)
        
        self.activate_state = [False, False]
        self.toggle_editor = True
        
        self.player_csv_text = f"File : {os.path.basename(self.shm_player_csv.read_text())}"
        self.ghost_csv_text = f"File : {os.path.basename(self.shm_ghost_csv.read_text())}"
        self.player_label = None
        self.ghost_label = None
        
        for section_index, section_title in enumerate(["Player Inputs", "Ghost Inputs"]):
            self.create_section(root_layout, section_index, section_title)
                    
        self.shm_close_event.write_text("0")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loop_actions)
        self.timer.start(10)
        
        self.create_menubar()
    
    def on_checkbox_change(self, state, index):
        self.activate_state[index] = bool(state)
        self.shm_activate.write(struct.pack('>??', *self.activate_state))
    
    def on_button_click(self, section_index, row_index, col_index):
        button_data = struct.pack('>?BBB', True, section_index, row_index, col_index)
        self.shm_buttons.write(button_data)
        
    def create_menubar(self):
        menubar = self.menuBar()
        type_menu = menubar.addMenu("View")
        
        editor_action = QAction("View CSV Editor", self, checkable=True, checked=True, triggered=lambda: self.view_editor(editor_action.isChecked()))
        
        type_menu.addAction(editor_action)
        
    def create_section(self, root_layout, section_index, section_title):
        section_frame = QGroupBox(section_title)
        section_layout = QVBoxLayout(section_frame)
        
        # Add to parent layout
        root_layout.addWidget(section_frame)
        
        # Create checkbox
        checkbox = QCheckBox("Activate")
        checkbox.setChecked(self.activate_state[section_index])
        checkbox.stateChanged.connect(lambda state, idx=section_index: self.on_checkbox_change(state, idx))
        section_layout.addWidget(checkbox)
        
        # Create label for file display
        label = QLabel(self.player_csv_text if section_index == 0 else self.ghost_csv_text)
        section_layout.addWidget(label)
        
        # Store reference to label for updates
        if section_index == 0:
            self.player_label = label
        else:
            self.ghost_label = label
        
        # Create button rows
        for row_index, row in enumerate(BUTTON_LAYOUT[section_index]):
            btn_row_frame = QFrame()
            btn_row_layout = QHBoxLayout(btn_row_frame)
            section_layout.addWidget(btn_row_frame)
            
            for col_index, btn_text in enumerate(row):
                button = QPushButton(btn_text)
                
                # i need this or else it'll just return the last value of the button layout
                def on_button_click(s_idx, r_idx, c_idx):
                    return lambda: self.on_button_click(s_idx, r_idx, c_idx)
                
                button.clicked.connect(on_button_click(section_index, row_index, col_index))
                btn_row_layout.addWidget(button)
        
    def view_editor(self, condition):
        if self.toggle_editor:
            print("a")
    
    def loop_actions(self):
        new_text = self.shm_player_csv.read_text()
        if new_text:
            self.player_csv_text = f"File : {os.path.basename(os.path.dirname(new_text))}"
            if self.player_label:
                self.player_label.setText(self.player_csv_text)
        
        new_text = self.shm_ghost_csv.read_text()
        if new_text:
            self.ghost_csv_text = f"File : {os.path.basename(os.path.dirname(new_text))}"
            if self.ghost_label:
                self.ghost_label.setText(self.ghost_csv_text)
    
    def closeEvent(self, event):
        #This part of the code is only accessed when the window has been closed
        #self.shm_close_event.write_text("1")
        super().closeEvent(event)
        
        
class CSVEditor(QWidget):
    def __init__(self, csv_path):
        super().__init__()
        
        self.csv_path = csv_path
        self.shm_frame_of_input = ex.SharedMemoryReader(name='editor_frame_of_input')
        
        self.csv_loaded = False
        self.last_highlighted_row = None
        self.loaded_type = None
        
        #best way i could find to highlight every frame, i cant just put the function on the @on_frameadvance event :(
        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self.check_frame_change)
        self.frame_timer.start(10) #10ms
        
        self.see_checkboxes = True
        self.checkboxes_columns = [0, 2]
        self.checkbox_flags = Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
        self.box_checked = Qt.CheckState.Checked
        self.box_unchecked = Qt.CheckState.Unchecked

        self.layout = QVBoxLayout(self)

        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)
        
        self.range_label = QLabel(str(), self)
        #self.range_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        self.range_label.setStyleSheet("color: red;")
        self.label_layout.addWidget(self.range_label)
        
        self.table_widget.itemChanged.connect(self.on_item_change)

    def load_csv(self, csv_path):
        self.csv_loaded = False
        column_names = ["A", "B", "Item", "X", "Y", "Dpad", "Drift"]
        placeholder_row = ["0"] * 6 + ["-1"]
        
        if not os.path.exists(csv_path):
            QMessageBox.warning(self, "Warning", f"The {os.path.basename(os.path.dirname(self.csv_path))}/{os.path.basename(csv_path)} file does not exists.\nCreated a new file with a placeholder row.")
            with open(csv_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(placeholder_row)
            data = [placeholder_row]
            
        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                data = list(reader)

                if not data:
                    QMessageBox.warning(self, "Warning", f"The {os.path.basename(os.path.dirname(self.csv_path))}/{os.path.basename(csv_path)} file is empty.\nCreated a placeholder row.")
                    data.append(placeholder_row)

            self.table_widget.setColumnCount(len(column_names))
            self.table_widget.setHorizontalHeaderLabels(column_names)

            header = self.table_widget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch) #i thought making it responsive would be hard lol
            self.table_widget.setRowCount(len(data))

            for row_idx, row in enumerate(data):
                for col_idx in range(len(row)):
                    # make col a checkbox if in checkboxes_columns
                    if self.see_checkboxes:
                        if col_idx in self.checkboxes_columns:
                            checkbox = QTableWidgetItem()
                            checkbox.setFlags(self.checkbox_flags)
                            checkbox.setCheckState(self.box_unchecked if row[col_idx] == "0" else self.box_checked) # 0 = unchecked
                            self.table_widget.setItem(row_idx, col_idx, checkbox)
                    else:
                        self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(row[col_idx]))
                        
            self.csv_loaded = True
            self.loaded_type = csv_path
                        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load {os.path.basename(os.path.dirname(self.csv_path))}/{os.path.basename(csv_path)}.\n{e}")
            return
                        
    def save_csv(self):
        with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for row_idx in range(self.table_widget.rowCount()):
                row_data = []
                for col_idx in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row_idx, col_idx)
                    if item.flags() == self.checkbox_flags: #transform checkbox value to binary text
                        match item.checkState():
                            case self.box_checked:
                                checkbox_value = "1"
                            case self.box_unchecked:
                                checkbox_value = "0"
                        row_data.append(checkbox_value)
                    else:
                        row_data.append(item.text())
                writer.writerow(row_data)
                
        print("saved")
        
    def highlight_row(self, row_idx):
        color = QColor(255, 255, 0, 50)
        highlighted_row = row_idx - 1

        # un-highlight the previous highlighted row
        if self.last_highlighted_row is not None and self.last_highlighted_row != highlighted_row:
            for col_idx in range(self.table_widget.columnCount()):
                prev_item = self.table_widget.item(self.last_highlighted_row, col_idx)
                if prev_item:
                    prev_item.setBackground(self.table_widget.palette().base().color()) # the base color

        # highlight current row
        for col_idx in range(self.table_widget.columnCount()):
            item = self.table_widget.item(highlighted_row, col_idx)
            if item:
                item.setBackground(color)
                
        self.last_highlighted_row = highlighted_row
        # auto-scroll
        self.table_widget.scrollToItem(self.table_widget.item(row_idx, 0), QAbstractItemView.ScrollHint.PositionAtCenter)
            
    def check_frame_change(self):
        if not self.csv_loaded:
            return
        new_frame_of_input = ex.SharedMemoryReader('editor_frame_of_input')

        if new_frame_of_input.read_text() != self.shm_frame_of_input.read_text():
            self.shm_frame_of_input = new_frame_of_input
            row_idx = int(new_frame_of_input)
            if 0 <= row_idx < self.table_widget.rowCount():
                self.range_label.setText(str())
                self.table_widget.blockSignals(True) # temprarily block signals to avoid tracking the change of the background in on_item_change()
                self.highlight_row(row_idx)
                self.table_widget.blockSignals(False)
            else:
                self.range_label.setText(f"Frame {row_idx} out of range.")
                
    def toggle_checkboxes(self, is_checked):
        self.table_widget.blockSignals(True)
        self.see_checkboxes = is_checked
        for row_idx in range(self.table_widget.rowCount()):
            for col_idx in range(self.table_widget.columnCount()):
                if col_idx in self.checkboxes_columns:
                    item = self.table_widget.item(row_idx, col_idx)
                    cell_value = str()
                    
                    if item:
                        if item.flags() == self.checkbox_flags:
                            state = item.checkState()
                            cell_value = "1" if state == self.box_checked else "0"
                        else:
                            cell_value = item.text()

                    if is_checked:
                        checkbox = QTableWidgetItem()
                        checkbox.setFlags(self.checkbox_flags)
                        checkbox.setCheckState(self.box_checked if cell_value == "1" else self.box_unchecked)
                        self.table_widget.setItem(row_idx, col_idx, checkbox)
                    else:
                        item = QTableWidgetItem(cell_value)
                        self.table_widget.setItem(row_idx, col_idx, item)
        self.table_widget.blockSignals(False)
                        
    def toggle_autosave(self, is_checked):
        self.autosave = is_checked
                        
    def on_item_change(self, changed_item):
        if not self.csv_loaded: return
        
        modifiers = QApplication.keyboardModifiers()
        selected_cells = self.table_widget.selectedIndexes()
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            value = changed_item.text()
            selected_cells = self.table_widget.selectedIndexes()
            for index in selected_cells:
                if index.row() == changed_item.row() and index.column() == changed_item.column():
                    continue
                item = self.table_widget.item(index.row(), index.column())
                if not item:
                    item = QTableWidgetItem()
                    self.table_widget.setItem(index.row(), index.column(), item)
                item.setText(value)
        
        if not self.autosave: return
        print(self.loaded_type)
        self.save_csv()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())