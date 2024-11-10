import sys
import serial
import numpy as np
import matplotlib.pyplot as plt
from PyQt6 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Configure serial connection for Arduino (update port for your system)
ser = serial.Serial('COM6', 9600, timeout=1)  # Check your Arduino COM port

# Main window class
class AudiogramApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.left_ear = []
        self.right_ear = []
        self.frequencies = [125, 250, 500, 1000, 2000, 4000, 8000]
        self.freq_labels = ["125", "250", "500", "1000", "2000", "4000", "8000"]

        # Set up a timer to update the audiogram data
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_audiogram)
        self.timer.start(1000)

    def initUI(self):
        # Set up the main window
        self.setWindowTitle("Audiogram Interface")
        self.setGeometry(100, 100, 800, 600)

        # Create a matplotlib figure for the audiogram
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.fig)
        self.setCentralWidget(self.canvas)

    def parse_results(self, line):
        try:
            left_ear = []
            right_ear = []

            if "Left Ear:" in line:
                left_ear = [float(x.split("Hz,")[1].replace(" db", "")) for x in line.split(" | ")]
            elif "Right Ear:" in line:
                right_ear = [float(x.split("Hz,")[1].replace(" db", "")) for x in line.split(" | ")]

            return left_ear, right_ear
        except Exception as e:
            print(f"Error parsing data: {e}")
            return [], []

    def update_audiogram(self):
        # Check if there is data in the serial buffer
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            if "Audiogram Results:" in line:
                self.left_ear, self.right_ear = [], []
            else:
                left, right = self.parse_results(line)
                self.left_ear.extend(left)
                self.right_ear.extend(right)
                if len(self.left_ear) == 7 and len(self.right_ear) == 7:
                    self.plot_audiogram(self.left_ear, self.right_ear)

    def plot_audiogram(self, left_ear, right_ear):
        # Plot the audiogram
        self.ax.clear()
        self.ax.plot(self.frequencies, left_ear, marker='o', color='red', label='Left Ear')
        self.ax.plot(self.frequencies, right_ear, marker='x', color='blue', label='Right Ear')
        self.ax.invert_yaxis()
        self.ax.set_xticks(self.frequencies)
        self.ax.set_xticklabels(self.freq_labels, fontsize = 6)
        self.ax.set_yticks(np.arange(-10, 130, 10))
        self.ax.set_yticklabels([i for i in range(-10, 130, 10)], fontsize = 6)
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Hearing Threshold (dB)")
        self.ax.set_title("Audiogram")
        self.ax.legend()
        self.canvas.draw()


# Main execution
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    audiogram_app = AudiogramApp()
    audiogram_app.show()
    sys.exit(app.exec())
