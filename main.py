import sys
from PyQt5 import QtCore, QtWidgets, QtMultimedia

class ListDialog(QtWidgets.QDialog):
    def __init__(self, intervals, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Listas")
        self.rows_layout = QtWidgets.QVBoxLayout()
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(QtWidgets.QLabel("Sprendimas"))
        header_layout.addWidget(QtWidgets.QLabel("H"))
        header_layout.addWidget(QtWidgets.QLabel("Min"))
        header_layout.addWidget(QtWidgets.QLabel("S"))
        self.rows_layout.addLayout(header_layout)
        self.edits = []
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(self.rows_layout)

        for label, total_secs in intervals:
            h = total_secs // 3600
            r = total_secs % 3600
            m = r // 60
            s = r % 60
            row = QtWidgets.QHBoxLayout()
            lbl_edit = QtWidgets.QLineEdit(label)
            h_edit = QtWidgets.QLineEdit(str(h))
            m_edit = QtWidgets.QLineEdit(str(m))
            s_edit = QtWidgets.QLineEdit(str(s))
            row.addWidget(lbl_edit)
            row.addWidget(h_edit)
            row.addWidget(m_edit)
            row.addWidget(s_edit)
            self.edits.append((lbl_edit, h_edit, m_edit, s_edit))
            self.rows_layout.addLayout(row)

        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add")
        self.save_btn = QtWidgets.QPushButton("Save")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.add_row)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def add_row(self):
        row = QtWidgets.QHBoxLayout()
        lbl_edit = QtWidgets.QLineEdit("Naujas")
        h_edit = QtWidgets.QLineEdit("0")
        m_edit = QtWidgets.QLineEdit("0")
        s_edit = QtWidgets.QLineEdit("0")
        row.addWidget(lbl_edit)
        row.addWidget(h_edit)
        row.addWidget(m_edit)
        row.addWidget(s_edit)
        self.edits.append((lbl_edit, h_edit, m_edit, s_edit))
        self.rows_layout.addLayout(row)

    def get_data(self):
        data = []
        for lbl_edit, h_edit, m_edit, s_edit in self.edits:
            name = lbl_edit.text().strip()
            try:
                hh = int(h_edit.text().strip())
            except:
                hh = 0
            try:
                mm = int(m_edit.text().strip())
            except:
                mm = 0
            try:
                ss = int(s_edit.text().strip())
            except:
                ss = 0
            total = hh * 3600 + mm * 60 + ss
            data.append((name, total))
        return data

class StudyTimerApp(QtWidgets.QWidget):
    def __init__(self, fullscreen=False):
        super().__init__()
        self.setWindowTitle("Study Timer")
        if fullscreen:
            self.showFullScreen()

        self.intervals = [
            ("Work #1", 2 * 60 * 60),
            ("Break #1", 20 * 60),
            ("Work #2", 2 * 60 * 60),
            ("Break #2", 30 * 60),
            ("Work #3", 90 * 60),
            ("Break #3", 30 * 60),
            ("Work #4", 2 * 60 * 60)
        ]

        self.current_index = 0
        self.remaining_time = self.intervals[self.current_index][1]
        self.is_running = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.countdown)

        layout_main = QtWidgets.QVBoxLayout(self)

        self.phase_label = QtWidgets.QLabel(self.intervals[self.current_index][0], self)
        self.phase_label.setAlignment(QtCore.Qt.AlignCenter)
        self.phase_label.setStyleSheet("font-weight: bold; font-size: 16pt;")
        layout_main.addWidget(self.phase_label)

        self.time_label = QtWidgets.QLabel("00:00:00", self)
        self.time_label.setAlignment(QtCore.Qt.AlignCenter)
        layout_main.addWidget(self.time_label)

        # ------------------------------------------------------
        # New: Label that shows total remaining WORK time
        # ------------------------------------------------------
        self.total_work_label = QtWidgets.QLabel("Work Left: 00:00:00", self)
        self.total_work_label.setAlignment(QtCore.Qt.AlignCenter)
        layout_main.addWidget(self.total_work_label)
        # Calculate total work time at the start
        self.total_work_time_left = 0
        self.calculate_total_work_time_left()

        self.progress_bar_interval = QtWidgets.QProgressBar(self)
        self.progress_bar_total = QtWidgets.QProgressBar(self)
        self.progress_bar_interval.setRange(0, self.remaining_time)
        self.progress_bar_interval.setValue(self.remaining_time)
        total_seconds = sum(d for _, d in self.intervals)
        self.progress_bar_total.setRange(0, total_seconds)
        self.progress_bar_total.setValue(total_seconds)
        layout_main.addWidget(self.progress_bar_interval)
        layout_main.addWidget(self.progress_bar_total)

        btn_layout = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton("Startas")
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.resume_button = QtWidgets.QPushButton("Resume")
        self.reset_button = QtWidgets.QPushButton("Reset")
        self.skip_break_button = QtWidgets.QPushButton("Skip Break")
        self.list_button = QtWidgets.QPushButton("Listas")

        self.start_button.clicked.connect(self.start_timer)
        self.stop_button.clicked.connect(self.stop_timer)
        self.resume_button.clicked.connect(self.resume_timer)
        self.reset_button.clicked.connect(self.reset_timer)
        self.skip_break_button.clicked.connect(self.skip_break)
        self.list_button.clicked.connect(self.open_list_dialog)

        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)
        btn_layout.addWidget(self.resume_button)
        btn_layout.addWidget(self.reset_button)
        btn_layout.addWidget(self.skip_break_button)
        btn_layout.addWidget(self.list_button)

        layout_main.addLayout(btn_layout)

        self.update_time_label()

    def calculate_total_work_time_left(self):
        self.total_work_time_left = sum(
            d for lbl, d in self.intervals if "Work" in lbl
        )

    def update_total_work_label(self):
        h = self.total_work_time_left // 3600
        r = self.total_work_time_left % 3600
        m = r // 60
        s = r % 60
        self.total_work_label.setText(f"Work Left: {h:02}:{m:02}:{s:02}")

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.timer.start(1000)

    def stop_timer(self):
        self.is_running = False
        self.timer.stop()

    def resume_timer(self):
        if not self.is_running:
            self.is_running = True
            self.timer.start(1000)

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.current_index = 0
        self.remaining_time = self.intervals[self.current_index][1]
        self.phase_label.setText(self.intervals[self.current_index][0])
        self.update_progress_bars()
        self.update_time_label()
        self.calculate_total_work_time_left()
        self.update_total_work_label()

    def skip_break(self):
        if "Break" in self.intervals[self.current_index][0]:
            self.remaining_time = 0
            self.countdown()

    def open_list_dialog(self):
        dlg = ListDialog(self.intervals, self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            new_data = dlg.get_data()
            self.intervals = new_data
            self.reset_timer()

    def countdown(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            # If the current interval is "Work", decrement total work time left
            if "Work" in self.intervals[self.current_index][0]:
                self.total_work_time_left -= 1
            self.update_time_label()
            self.update_total_work_label()
        else:
            self.current_index += 1
            if self.current_index < len(self.intervals):
                self.remaining_time = self.intervals[self.current_index][1]
                self.phase_label.setText(self.intervals[self.current_index][0])
                self.update_progress_bars()
                self.update_time_label()
            else:
                self.timer.stop()
                self.is_running = False
                self.phase_label.setText("Done")
                self.time_label.setText("00:00:00")
                QtMultimedia.QSound.play("alarm.wav")

    def update_time_label(self):
        h = self.remaining_time // 3600
        m = (self.remaining_time % 3600) // 60
        s = self.remaining_time % 60
        self.time_label.setText(f"{h:02}:{m:02}:{s:02}")
        self.progress_bar_interval.setValue(self.progress_bar_interval.maximum() - self.remaining_time)
        total_elapsed = sum(d for _, d in self.intervals[:self.current_index]) + (
            self.intervals[self.current_index][1] - self.remaining_time
        )
        self.progress_bar_total.setValue(total_elapsed)

    def update_progress_bars(self):
        self.progress_bar_interval.setRange(0, self.remaining_time)
        self.progress_bar_interval.setValue(0)
        t = sum(d for _, d in self.intervals)
        self.progress_bar_total.setRange(0, t)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.width()
        h = self.height()
        sf = min(w, h) // 15
        f = self.time_label.font()
        f.setPointSize(max(sf, 10))
        self.time_label.setFont(f)
        p = self.phase_label.font()
        p.setPointSize(max(sf // 2, 8))
        self.phase_label.setFont(p)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = StudyTimerApp(fullscreen=False)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
