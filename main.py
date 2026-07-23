"""
ऊटिन – Camel Bluetooth Chat
Camel ASCII art + full chat functionality.
App icon: add icon.png in source folder (see buildozer.spec).
"""

import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.graphics import Color, Rectangle

# ---------- PyJNIus (Android Bluetooth) ----------
from jnius import autoclass
from android.permissions import request_permissions, Permission

# Java classes
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
BluetoothServerSocket = autoclass('android.bluetooth.BluetoothServerSocket')
UUID = autoclass('java.util.UUID')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Toast = autoclass('android.widget.Toast')

def toast(msg):
    Toast.makeText(PythonActivity.mActivity, msg, Toast.LENGTH_SHORT).show()

# ---------- Camel ASCII Art ----------
CAMEL_ART = """
   🐫
  /    \\
 /  🏜  \\
|  🐫  |
 \\    /
  \\__/
"""
# You can replace with a more detailed ASCII camel or a base64 image.

# ---------- Bluetooth Manager ----------
class BluetoothManager:
    MY_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")

    def __init__(self):
        self.adapter = BluetoothAdapter.getDefaultAdapter()
        self.socket = None
        self.server_socket = None
        self.input_stream = None
        self.output_stream = None
        self.connected = False
        self.running = False

    def is_ready(self):
        if self.adapter is None:
            toast("Bluetooth not supported")
            return False
        if not self.adapter.isEnabled():
            toast("Enable Bluetooth in settings")
            return False
        return True

    def start_server(self, on_connect, on_message):
        if not self.is_ready():
            return False
        try:
            self.server_socket = self.adapter.listenUsingRfcommWithServiceRecord(
                "ऊटिन Chat", self.MY_UUID
            )
            toast("Waiting for connection...")
            def accept_loop():
                self.running = True
                try:
                    self.socket = self.server_socket.accept()
                    if self.socket:
                        self.connected = True
                        self._setup_streams()
                        Clock.schedule_once(lambda dt: on_connect(True))
                        self._start_receiver(on_message)
                except Exception as e:
                    Logger.error(f"Accept error: {e}")
                    Clock.schedule_once(lambda dt: on_connect(False))
            threading.Thread(target=accept_loop, daemon=True).start()
            return True
        except Exception as e:
            Logger.error(f"Server start error: {e}")
            return False

    def connect_to_device(self, mac, on_connect, on_message):
        if not self.is_ready():
            return False
        try:
            device = self.adapter.getRemoteDevice(mac)
            self.socket = device.createRfcommSocketToServiceRecord(self.MY_UUID)
            def connect_thread():
                self.running = True
                try:
                    self.socket.connect()
                    self.connected = True
                    self._setup_streams()
                    Clock.schedule_once(lambda dt: on_connect(True))
                    self._start_receiver(on_message)
                except Exception as e:
                    Logger.error(f"Connect error: {e}")
                    Clock.schedule_once(lambda dt: on_connect(False))
            threading.Thread(target=connect_thread, daemon=True).start()
            return True
        except Exception as e:
            Logger.error(f"Connect init error: {e}")
            return False

    def _setup_streams(self):
        try:
            self.input_stream = self.socket.getInputStream()
            self.output_stream = self.socket.getOutputStream()
        except Exception as e:
            Logger.error(f"Stream setup error: {e}")

    def _start_receiver(self, on_message):
        def receiver():
            while self.running and self.connected:
                try:
                    buffer = bytearray()
                    while True:
                        b = self.input_stream.read()
                        if b == -1:
                            raise Exception("Stream closed")
                        buffer.append(b)
                        if b == 10:
                            break
                    msg = buffer.decode('utf-8').strip()
                    if msg:
                        Clock.schedule_once(lambda dt, m=msg: on_message(m))
                except Exception as e:
                    Logger.error(f"Receive error: {e}")
                    self.connected = False
                    break
        threading.Thread(target=receiver, daemon=True).start()

    def send_message(self, msg):
        if self.connected and self.output_stream:
            try:
                self.output_stream.write((msg + "\n").encode('utf-8'))
                self.output_stream.flush()
                return True
            except Exception as e:
                Logger.error(f"Send error: {e}")
                self.connected = False
        return False

    def close(self):
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        self.input_stream = None
        self.output_stream = None

    def get_paired_devices(self):
        if not self.is_ready():
            return []
        paired = self.adapter.getBondedDevices()
        return [(device.getName(), device.getAddress()) for device in paired]

# ---------- Kivy UI with Camel ----------
class ChatScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.bt = BluetoothManager()
        self.connected = False
        self.is_host = False
        self.chat_history = []

        # ---- Camel Header ----
        header = BoxLayout(size_hint_y=0.15, orientation='horizontal')
        # Camel ASCII label
        camel_label = Label(text=CAMEL_ART, font_size='30sp', halign='center', valign='middle')
        header.add_widget(camel_label)
        # App name
        name_label = Label(text="ऊटिन", font_size='24sp', bold=True, halign='center', valign='middle')
        header.add_widget(name_label)
        self.add_widget(header)

        # Status
        self.status_label = Label(text="Not connected", size_hint_y=0.06)
        self.add_widget(self.status_label)

        # Chat display
        scroll = ScrollView(size_hint_y=0.5)
        self.chat_label = Label(text="", markup=True, halign='left', valign='top')
        self.chat_label.bind(size=self.chat_label.setter('text_size'))
        scroll.add_widget(self.chat_label)
        self.add_widget(scroll)

        # Input row
        input_box = BoxLayout(size_hint_y=0.08)
        self.msg_input = TextInput(multiline=False)
        self.send_btn = Button(text='Send', disabled=True)
        self.send_btn.bind(on_press=self.send_message)
        input_box.add_widget(self.msg_input)
        input_box.add_widget(self.send_btn)
        self.add_widget(input_box)

        # Control row
        control_box = BoxLayout(size_hint_y=0.1)
        self.host_btn = Button(text='Host')
        self.host_btn.bind(on_press=self.host_chat)
        self.join_btn = Button(text='Join')
        self.join_btn.bind(on_press=self.join_chat)
        self.refresh_btn = Button(text='Refresh')
        self.refresh_btn.bind(on_press=self.refresh_devices)
        self.disconnect_btn = Button(text='Disconnect', disabled=True)
        self.disconnect_btn.bind(on_press=self.disconnect)
        control_box.add_widget(self.host_btn)
        control_box.add_widget(self.join_btn)
        control_box.add_widget(self.refresh_btn)
        control_box.add_widget(self.disconnect_btn)
        self.add_widget(control_box)

        # Device spinner
        spinner_box = BoxLayout(size_hint_y=0.08)
        spinner_box.add_widget(Label(text='Device:', size_hint_x=0.2))
        self.device_spinner = Spinner(text='Select device', values=['No devices'])
        self.device_spinner.size_hint_x = 0.8
        spinner_box.add_widget(self.device_spinner)
        self.add_widget(spinner_box)

        # Request permissions and load devices
        self.request_permissions()
        self.refresh_devices()

    def request_permissions(self):
        perms = [
            Permission.BLUETOOTH,
            Permission.BLUETOOTH_ADMIN,
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
        ]
        try:
            perms.append(Permission.BLUETOOTH_SCAN)
            perms.append(Permission.BLUETOOTH_CONNECT)
            perms.append(Permission.BLUETOOTH_ADVERTISE)
        except:
            pass
        request_permissions(perms, self.on_permissions_result)

    def on_permissions_result(self, permissions, grants):
        if all(g == 0 for g in grants):
            toast("Permissions granted")
        else:
            toast("Some permissions denied – app may not work")

    def refresh_devices(self, *args):
        devices = self.bt.get_paired_devices()
        if not devices:
            self.device_spinner.values = ['No devices']
            self.device_spinner.text = 'No devices'
        else:
            values = [f"{name} ({addr})" for name, addr in devices]
            self.device_spinner.values = values
            self.device_spinner.text = values[0]

    def host_chat(self, *args):
        if self.connected:
            toast("Already connected")
            return
        if self.bt.start_server(self.on_connect, self.on_message_received):
            self.is_host = True
            self.status_label.text = "Host: Waiting..."
            self.host_btn.disabled = True
            self.join_btn.disabled = True
            self.refresh_btn.disabled = True

    def join_chat(self, *args):
        if self.connected:
            toast("Already connected")
            return
        selection = self.device_spinner.text
        if selection in ('No devices', 'Select device'):
            toast("Select a paired device")
            return
        try:
            mac = selection.split('(')[1].split(')')[0]
        except:
            toast("Invalid device")
            return
        if self.bt.connect_to_device(mac, self.on_connect, self.on_message_received):
            self.status_label.text = "Connecting..."
            self.host_btn.disabled = True
            self.join_btn.disabled = True
            self.refresh_btn.disabled = True

    def on_connect(self, success):
        if success:
            self.connected = True
            self.status_label.text = "Connected!"
            self.send_btn.disabled = False
            self.msg_input.disabled = False
            self.disconnect_btn.disabled = False
            toast("Connected")
        else:
            self.connected = False
            self.status_label.text = "Connection failed"
            self.host_btn.disabled = False
            self.join_btn.disabled = False
            self.refresh_btn.disabled = False

    def on_message_received(self, msg):
        self.add_message(f"Other: {msg}")

    def send_message(self, *args):
        msg = self.msg_input.text.strip()
        if not msg:
            return
        if not self.connected:
            toast("Not connected")
            return
        if self.bt.send_message(msg):
            self.add_message(f"Me: {msg}")
            self.msg_input.text = ""
        else:
            toast("Send failed")
            self.disconnect()

    def add_message(self, msg):
        self.chat_history.append(msg)
        self.chat_label.text = "\n".join(self.chat_history)

    def disconnect(self, *args):
        self.bt.close()
        self.connected = False
        self.is_host = False
        self.status_label.text = "Disconnected"
        self.host_btn.disabled = False
        self.join_btn.disabled = False
        self.refresh_btn.disabled = False
        self.send_btn.disabled = True
        self.msg_input.disabled = True
        self.disconnect_btn.disabled = True
        toast("Disconnected")

    def on_stop(self):
        self.bt.close()

class OotinApp(App):
    def build(self):
        Window.size = (400, 600)
        return ChatScreen()

    def on_stop(self):
        if hasattr(self.root, 'on_stop'):
            self.root.on_stop()

if __name__ == '__main__':
    OotinApp().run()
