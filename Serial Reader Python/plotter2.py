import sys
import serial
import csv
import time
import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

# --- CONFIGURATION ---
SERIAL_PORT = 'COM4'
BAUD_RATE = 115200
CSV_FILENAME = f"logs/blackbox_log_{int(time.time())}.csv"
DEFAULT_WINDOW_SIZE = 50 

class RealTimePlotter:
    def __init__(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        except Exception as e:
            print(f"Error connecting: {e}"); sys.exit()

        os.makedirs('logs', exist_ok=True)
        self.csv_file = open(CSV_FILENAME, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Time', 'AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'AccMag', 'GyroMag'])

        self.app = QtWidgets.QApplication([])
        self.main_layout = QtWidgets.QHBoxLayout()
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.main_layout)
        
        self.win = pg.GraphicsLayoutWidget(title="Black Box 2.0 Real-Time Dashboard")
        self.main_layout.addWidget(self.win, stretch=4)

        self.sidebar_scroll = QtWidgets.QScrollArea()
        self.sidebar_widget = QtWidgets.QWidget()
        self.sidebar = QtWidgets.QVBoxLayout(self.sidebar_widget)
        self.sidebar_scroll.setWidget(self.sidebar_widget)
        self.sidebar_scroll.setWidgetResizable(True)
        self.main_layout.addWidget(self.sidebar_scroll, stretch=1)
        
        self.setup_sidebar()

        self.graph_window = 200 
        self.stats_window = DEFAULT_WINDOW_SIZE
        self.data_buffers = [np.zeros(self.graph_window) for _ in range(6)]
        # Extra buffers for Magnitudes to calculate their Variance/StdDev
        self.acc_mag_buffer = np.zeros(self.graph_window)
        self.gyro_mag_buffer = np.zeros(self.graph_window)
        
        self.curves = []
        titles = ['Acc X', 'Acc Y', 'Acc Z', 'Gyro X', 'Gyro Y', 'Gyro Z']
        for i in range(6):
            p = self.win.addPlot(title=titles[i])
            if i % 2 == 1: self.win.nextRow()
            self.curves.append(p.plot(pen='y'))

        self.start_time = time.time()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)

    def setup_sidebar(self):
        self.sidebar.addWidget(QtWidgets.QLabel("<b>Research Controls</b>"))
        self.window_input = QtWidgets.QLineEdit(str(DEFAULT_WINDOW_SIZE))
        self.window_btn = QtWidgets.QPushButton("Update Math Window")
        self.window_btn.clicked.connect(self.update_window_size)
        self.sidebar.addWidget(QtWidgets.QLabel("Stats Window (Samples):"))
        self.sidebar.addWidget(self.window_input)
        self.sidebar.addWidget(self.window_btn)
        
        # --- VECTOR MAGNITUDE SECTION ---
        self.sidebar.addSpacing(20)
        self.sidebar.addWidget(QtWidgets.QLabel("<span style='color: #00FF00;'><b>VECTOR MAGNITUDES (Orientation Independent)</b></span>"))
        
        self.mag_labels = {}
        for name in ['Acc Mag', 'Gyro Mag']:
            group = QtWidgets.QGroupBox(name)
            vbox = QtWidgets.QVBoxLayout()
            val = QtWidgets.QLabel("Value: 0.00"); var = QtWidgets.QLabel("Var: 0.00"); std = QtWidgets.QLabel("Std: 0.00")
            vbox.addWidget(val); vbox.addWidget(var); vbox.addWidget(std)
            group.setLayout(vbox); self.sidebar.addWidget(group)
            self.mag_labels[name] = {'val': val, 'var': var, 'std': std}

        # --- INDIVIDUAL AXES SECTION ---
        self.sidebar.addSpacing(20)
        self.sidebar.addWidget(QtWidgets.QLabel("<b>Individual Axis Stats</b>"))
        self.stat_labels = []
        names = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ']
        for name in names:
            group = QtWidgets.QGroupBox(name)
            vbox = QtWidgets.QVBoxLayout()
            val = QtWidgets.QLabel("Value: 0.00"); var = QtWidgets.QLabel("Var: 0.00"); std = QtWidgets.QLabel("Std: 0.00")
            vbox.addWidget(val); vbox.addWidget(var); vbox.addWidget(std)
            group.setLayout(vbox); self.sidebar.addWidget(group)
            self.stat_labels.append({'val': val, 'var': var, 'std': std})
        self.sidebar.addStretch()

    def update_window_size(self):
        try:
            val = int(self.window_input.text())
            if 1 < val <= self.graph_window: self.stats_window = val
        except: pass

    def update(self):
        while self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if not line: continue
                v = [float(val) for val in line.split()]
                if len(v) != 6: continue

                # 1. Vector Magnitude Calculations
                acc_mag = np.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
                gyro_mag = np.sqrt(v[3]**2 + v[4]**2 + v[5]**2)
                
                # 2. Update Buffers
                self.acc_mag_buffer = np.roll(self.acc_mag_buffer, -1); self.acc_mag_buffer[-1] = acc_mag
                self.gyro_mag_buffer = np.roll(self.gyro_mag_buffer, -1); self.gyro_mag_buffer[-1] = gyro_mag

                # 3. Stats for Magnitudes
                for name, buf, cur_val in [('Acc Mag', self.acc_mag_buffer, acc_mag), ('Gyro Mag', self.gyro_mag_buffer, gyro_mag)]:
                    rel = buf[-self.stats_window:]
                    self.mag_labels[name]['val'].setText(f"Value: {cur_val:.3f}")
                    self.mag_labels[name]['var'].setText(f"Var: {np.var(rel):.5f}")
                    self.mag_labels[name]['std'].setText(f"Std: {np.std(rel):.5f}")

                # 4. Individual Axes Logging & UI
                curr_t = time.time() - self.start_time
                self.csv_writer.writerow([curr_t] + v + [acc_mag, gyro_mag])
                
                for i in range(6):
                    self.data_buffers[i] = np.roll(self.data_buffers[i], -1); self.data_buffers[i][-1] = v[i]
                    self.curves[i].setData(self.data_buffers[i])
                    rel = self.data_buffers[i][-self.stats_window:]
                    self.stat_labels[i]['val'].setText(f"Value: {v[i]:.3f}")
                    self.stat_labels[i]['var'].setText(f"Var: {np.var(rel):.5f}")
                    self.stat_labels[i]['std'].setText(f"Std: {np.std(rel):.5f}")
            except: pass

    def run(self):
        self.central_widget.show(); self.app.exec()
        self.csv_file.close(); self.ser.close()

if __name__ == "__main__":
    RealTimePlotter().run()