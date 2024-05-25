import glfw, imgui, json, serial, serial.tools.list_ports
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
from serial_conn import SerialThread
import queue
import threading
from io_queues import IOQueues
from algorithm import process_data
from pathlib import Path
from filedialogs import save_file_dialog, open_file_dialog, open_folder_dialog
from json_export import create_json_array

RED = [1, 0, 0, 1]
GREEN = [0, 1, 0, 1]
BLUE = [0, 0, 1, 1]
YELLOW = [1, 1, 0, 1]
CYAN = [0, 1, 1, 1]
MAGENTA = [1, 0, 1, 1]
WHITE = [1, 1, 1, 1]


def impl_glfw_init(window_name="minimal ImGui/GLFW3 example", width=1280, height=720):
    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    glfw.maximize_window(window)
    return window


class GUI(object):
    def __init__(self):
        super().__init__()
        self.backgroundColor = (0, 0, 0, 1)
        self.window = impl_glfw_init()
        gl.glClearColor(*self.backgroundColor)
        imgui.create_context()
        self.impl = GlfwRenderer(self.window)


        # Buffer log
        self.buffer_log = []

        # Json export data log
        self.data_log = []

        # Communication with Serial Thread
        self.queues = IOQueues()

        self.connected = False
        self.loop()


    def com_combo(self):
        imgui.text("Puerto COM")
        ports = serial.tools.list_ports.comports()
        current = 0
        items = []
        for port in ports:
            port_type = 'usb' if 'USB' in port.description or 'USB' in port.hwid else 'BT' if 'Bluetooth' in port.description else 'Other'
            items.append(port.device + f' ({port_type})')
        imgui.combo("", current, items)
        if imgui.button("Leer datos") and len(ports) > 0:
            self.buffer_log.append(('> connect ' + ports[current].device, [0, 1, 1, 1]))
            try: 
                self.queues.send_input('connect ' + ports[current].device)
            except Exception as e:
                self.buffer_log.append((str(e), RED))

    def loop(self):
        serial_thread = threading.Thread(target=SerialThread().run, args=(self.queues,), daemon=True)
        serial_thread.start()
        start_read = False  
        while not glfw.window_should_close(self.window):
            try:
                serial_output = self.queues.get_output()
            except queue.Empty:
                serial_output = ""
            if serial_output:
                if 'INFO' in serial_output:
                    self.buffer_log.append((serial_output, [0, 1, 0, 1]))
                elif 'WARNING' in serial_output:
                    self.buffer_log.append((serial_output, [1, 0, 0, 1]))
                elif 'ERROR' in serial_output:
                    self.buffer_log.append((serial_output, [1, 0, 0, 1]))
                else:
                    millis = int(serial_output.split(',')[0])
                    formatted_timestamp = f"{millis//60000}:{(millis//1000)%60}:{millis%1000}"
                    array = [int (el) for el in serial_output.split(',')[1].strip('\r\n')]
                    self.buffer_log.append((f'[{formatted_timestamp}] {list(array)}', [1, 1, 0.2, 1]))
                    self.data_log.append((millis, array))
                    process_data(self.queues, millis, array)
            # Instance full viewport window
            viewport = imgui.get_main_viewport()
            glfw.poll_events()
            self.impl.process_inputs()
            imgui.new_frame()
            imgui.set_next_window_position(*viewport.pos)
            imgui.set_next_window_size(*viewport.size)
            imgui.begin("Line Tracer Maze Solving Robot", True, imgui.WINDOW_NO_TITLE_BAR and imgui.WINDOW_MENU_BAR)

            # Menu Bar
            imgui.begin_menu_bar()
            if imgui.begin_menu("File", True):
                save_file, selected_quit = imgui.menu_item("Save As", 'Ctrl+S', False, True)
                clicked_quit, selected_quit = imgui.menu_item("Quit", 'Ctrl+Q', False, True)
                if clicked_quit:
                    exit(1)
                if save_file:
                    print ("Path: ", Path.home().as_posix())
                    ret = save_file_dialog(directory=f'"{Path.home().as_posix()}"', default_name="test.json", default_ext="json", ext = [("JSON", "json")]  )
                    self.buffer_log.append((f"Save file: {ret}\n", [0, 1, 0, 1] if ret else [1, 0, 0, 1]))
                    json_string = create_json_array(self.data_log)
                    with open(ret, 'w') as f:
                        f.write(json_string)
                        f.close()
                    print (ret)
                imgui.end_menu()
            imgui.end_menu_bar()

            self.com_combo()


            # Log box
            imgui.push_style_var(imgui.STYLE_CHILD_BORDERSIZE, 1.0)
            imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.0, 0.0, 0.0, 0.0)
            imgui.begin_child('scrollable', height=300, width = 0, border=True)
            for entry in self.buffer_log:
                imgui.push_style_color(imgui.COLOR_TEXT, *entry[1])
                imgui.text(entry[0])
                imgui.pop_style_color(1)
            # Scroll to the bottom
            imgui.set_scroll_here_y(1.0)
            imgui.end_child()
            imgui.pop_style_var(1)
            imgui.pop_style_color(1)

            if imgui.button("Stop"):
                self.queues.send_input('disconnect')


            imgui.end()

            imgui.render()

            gl.glClearColor(*self.backgroundColor)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            self.impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)

        self.impl.shutdown()
        glfw.terminate()
        self.queues.send_input('stop')
        serial_thread.join()


if __name__ == "__main__":

    gui = GUI()