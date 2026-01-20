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
WINDOW_SIZE = 200  # Number of data points to show on the graph at once

class RealTimePlotter:
    def __init__(self):
        # 1. Initialize Serial Connection
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        except Exception as e:
            print(f"Error connecting to {SERIAL_PORT}: {e}")
            sys.exit()

        # 2. Set up CSV Logging
        os.makedirs('logs', exist_ok=True)  # Create logs folder if it doesn't exist
        self.csv_file = open(CSV_FILENAME, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Time', 'AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ'])

        # 3. Set up PyQtGraph Layout
        self.app = QtWidgets.QApplication([])
        self.win = pg.GraphicsLayoutWidget(show=True, title="Black Box 2.0 Real-Time Dashboard")
        self.win.resize(1000, 800)

        # Create 6 plot areas (3 rows, 2 columns)
        self.plots = []
        self.curves = []
        titles = ['Acc X', 'Acc Y', 'Acc Z', 'Gyro X', 'Gyro Y', 'Gyro Z']
        
        for i in range(6):
            p = self.win.addPlot(title=titles[i])
            # Wrap to new row after every 2 plots
            if i % 2 == 1: self.win.nextRow()
            curve = p.plot(pen='y') # Yellow line
            self.plots.append(p)
            self.curves.append(curve)

        # Data buffers
        self.data_buffers = [np.zeros(WINDOW_SIZE) for _ in range(6)]
        self.start_time = time.time()

        # 4. Timer for GUI Updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10) # Update every 10ms

    def update(self):
        while self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if not line: continue
                
                # Parsing the space-separated format: %f %f %f %f %f %f
                values = [float(val) for val in line.split()]
                
                if len(values) == 6:
                    current_time = time.time() - self.start_time
                    # Log to CSV
                    self.csv_writer.writerow([current_time] + values)
                    
                    # Update internal buffers for plotting
                    for i in range(6):
                        self.data_buffers[i] = np.roll(self.data_buffers[i], -1)
                        self.data_buffers[i][-1] = values[i]
                        self.curves[i].setData(self.data_buffers[i])
                        
            except Exception as e:
                print(f"Parse error: {e}")

    def run(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtWidgets.QApplication.instance().exec()
        self.csv_file.close()
        self.ser.close()

if __name__ == "__main__":
    plotter = RealTimePlotter()
    plotter.run()