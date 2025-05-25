from PySide6.QtWidgets import *
from PySide6.QtGui import QAction, QColor
from PySide6.QtCore import Qt, QTimer, QSettings
import csv
import external_utils as ex
import os
import sys

class CSVEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Editor")
        self.setGeometry(100, 100, 600, 600)
    
        self.shm_frame_of_input = ex.SharedMemoryReader('editor_frame_of_input')
        self.shm_player_csv = ex.SharedMemoryReader(name="editor_player_csv")
        self.shm_ghost_csv = ex.SharedMemoryReader(name="editor_ghost_csv")
        
        self.csv_loaded = False
        self.last_highlighted_row = None
        
        #best way i could find to highlight every frame, i cant just put the function on the @on_frameadvance event :(
        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self.check_frame_change)
        self.frame_timer.start(10) #10ms
        
        self.track_timer = QTimer(self)
        self.track_timer.timeout.connect(self.check_track_change)
        self.track_timer.start(1000)
        
        self.see_checkboxes = True
        self.checkboxes_columns = [0, 2]
        self.checkbox_flags = Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
        self.box_checked = Qt.CheckState.Checked
        self.box_unchecked = Qt.CheckState.Unchecked
        
        self.autosave = True
        self.loaded_type = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)
        
        self.label_layout = QHBoxLayout()
        self.layout.addLayout(self.label_layout)
        
        self.track_label = QLabel(f"Current Track: {os.path.basename(os.path.dirname(self.shm_player_csv.read_text()))}", self)
        #self.track_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.label_layout.addWidget(self.track_label)
        self.label_layout.addStretch(0)
        
        self.range_label = QLabel(str(), self)
        #self.range_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        self.range_label.setStyleSheet("color: red;")
        self.label_layout.addWidget(self.range_label)
        
        self.table_widget.itemChanged.connect(self.on_item_change)
        
        self.load_settings()
        
        self.create_menubar()

    def create_menubar(self):
        menubar = self.menuBar()
        type_menu = menubar.addMenu("Load TTK Type")
        type_manual_submenu = QMenu("Manual", self)
        
        file_menu = menubar.addMenu("File")
        option_menu = menubar.addMenu("Options")
        print(self.shm_player_csv.read_text())
        player_action = QAction("Player", self, triggered=lambda: self.load_csv(self.shm_player_csv.read_text()))
        ghost_action = QAction("Ghost", self, triggered=lambda: self.load_csv(self.shm_ghost_csv.read_text()))
        csv_action = QAction("CSV", self, triggered=self.ask_csv)
        rkg_action = QAction("RKG", self, triggered=self.ask_rkg)
        save_action = QAction("Save", self, shortcut="Ctrl+S", triggered=lambda: self.save_csv(self.shm_player_csv.read_text()))
        checkbox_action = QAction("Toggle Checkboxes", self, checkable=True, checked=True, triggered=lambda: self.toggle_checkboxes(checkbox_action.isChecked()))
        autosave_action = QAction("Auto-Save", self, checkable=True, checked=True, triggered=lambda: self.toggle_autosave(autosave_action.isChecked()))
        
        type_menu.addAction(player_action)
        type_menu.addAction(ghost_action)
        type_menu.addSeparator()
        type_menu.addMenu(type_manual_submenu)
        type_manual_submenu.addAction(csv_action)
        type_manual_submenu.addAction(rkg_action)
        file_menu.addAction(save_action)
        option_menu.addAction(checkbox_action)
        option_menu.addAction(autosave_action)
        

    def load_csv(self, csv_path):
        self.csv_loaded = False
        column_names = ["A", "B", "Item", "X", "Y", "Dpad", "Drift"]
        placeholder_row = ["0"] * 6 + ["-1"]
        
        if not os.path.exists(csv_path):
            QMessageBox.warning(self, "Warning", f"The {os.path.basename(os.path.dirname(self.shm_player_csv.read_text()))}/{os.path.basename(csv_path)} file does not exists.\nCreated a new file with a placeholder row.")
            with open(csv_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(placeholder_row)
            data = [placeholder_row]
            
        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                data = list(reader)

                if not data:
                    QMessageBox.warning(self, "Warning", f"The {os.path.basename(os.path.dirname(self.shm_player_csv.read_text()))}/{os.path.basename(csv_path)} file is empty.\nCreated a placeholder row.")
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
            QMessageBox.critical(self, "Error", f"Failed to load {os.path.basename(os.path.dirname(self.shm_player_csv.read_text()))}/{os.path.basename(csv_path)}.\n{e}")
            return
                        
    def save_csv(self, csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as file:
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
    
    # i know theres `ex.open_dialog_box` but just figured i'd use the built-in pyside dialog
    def ask_csv(self):
        csv_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if csv_path:
            self.load_csv(csv_path)
            
    def ask_rkg(self):
        rkg_path, _ = QFileDialog.getOpenFileName(self, "Select RKG File", "", "RKG Files (*.rkg)")
        if rkg_path:
            pass
        
    def check_track_change(self):
        new_text = self.shm_player_csv.read_text()
        if new_text:
            self.track_label.setText(f"Current Track: {os.path.basename(os.path.dirname(new_text))}")
        
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
        new_frame_of_input = ex.SharedMemoryReader('editor_frame_of_input').read_text()

        if new_frame_of_input != self.shm_frame_of_input.read_text():
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
        self.save_csv(self.shm_player_csv.read_text())
        
    def closeEvent(self, event):
        settings = QSettings("ttk", "csv_editor")
        settings.setValue("position", self.pos())
        settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def load_settings(self):
        settings = QSettings("ttk", "csv_editor")
        self.move(settings.value("position"))
        self.restoreGeometry(settings.value("geometry"))
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVEditor()
    window.show()
    sys.exit(app.exec())
    