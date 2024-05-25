#pip install imgui[glfw]
import serial
from serial.tools.list_ports import comports
from filedialogs import save_file_dialog, open_file_dialog, open_folder_dialog
from pathlib import Path

from algorithm import process_data


