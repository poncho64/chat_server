import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
import threading
import websocket
import json

BACKEND_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login / Registro - Chat")
        self.setGeometry(100, 100, 350, 250)
        layout = QVBoxLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText("Usuario")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Contraseña")
        self.password.setEchoMode(QLineEdit.Password)
        self.avatar_path = None
        self.avatar_label = QLabel("Sin avatar seleccionado")
        self.avatar_btn = QPushButton("Elegir avatar")
        self.avatar_btn.clicked.connect(self.select_avatar)
        self.login_btn = QPushButton("Iniciar sesión")
        self.register_btn = QPushButton("Registrarse")
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)
        layout.addWidget(QLabel("Usuario:"))
        layout.addWidget(self.username)
        layout.addWidget(QLabel("Contraseña:"))
        layout.addWidget(self.password)
        layout.addWidget(self.avatar_label)
        layout.addWidget(self.avatar_btn)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        self.setLayout(layout)
        self.result = None

    def select_avatar(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar avatar", "", "Imágenes (*.png *.jpg *.jpeg)")
        if file:
            self.avatar_path = file
            self.avatar_label.setText(f"Avatar: {file.split('/')[-1]}")


    def login(self):
        data = {"username": self.username.text(), "password": self.password.text()}
        try:
            r = requests.post(f"{BACKEND_URL}/login", data=data)
            if r.status_code == 200:
                self.result = {"username": self.username.text()}
                self.close()
            else:
                # Mostrar error en la interfaz
                self.password.setText("")
        except Exception as e:
            self.password.setText("")

    def register(self):
        files = {}
        if self.avatar_path:
            files["avatar"] = open(self.avatar_path, "rb")
        data = {"username": self.username.text(), "password": self.password.text()}
        try:
            r = requests.post(f"{BACKEND_URL}/register", data=data, files=files if files else None)
            if r.status_code == 200:
                # Registro exitoso
                pass
            else:
                # Registro fallido
                self.password.setText("")
        except Exception as e:
            self.password.setText("")

class ChatWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"Chat - {username}")
        self.setGeometry(200, 200, 500, 400)
        self.username = username
        layout = QVBoxLayout()
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Escribe un mensaje...")
        self.send_btn = QPushButton("Enviar")
        self.send_btn.clicked.connect(self.send_message)
        hbox = QHBoxLayout()
        hbox.addWidget(self.input)
        hbox.addWidget(self.send_btn)
        layout.addWidget(self.chat_area)
        layout.addLayout(hbox)
        self.setLayout(layout)
        self.ws = None
        self.connect_ws()

    def connect_ws(self):
        def on_message(ws, message):
            self.chat_area.append(message)
        def on_error(ws, error):
            self.chat_area.append(f"Error: {error}")
        def on_close(ws, close_status_code, close_msg):
            self.chat_area.append("Conexión cerrada")
        self.ws = websocket.WebSocketApp(
            WS_URL,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def send_message(self):
        msg = f"{self.username}: {self.input.text()}"
        if self.ws:
            try:
                self.ws.send(msg)
                self.input.clear()
            except Exception as e:
                self.chat_area.append(f"Error al enviar: {e}")

def main():
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    app.exec_()
    if login.result:
        chat = ChatWindow(login.result["username"])
        chat.show()
        app.exec_()

if __name__ == "__main__":
    main()
