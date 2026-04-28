"""screens/login_screen.py"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from database import authenticate

# store current user globally for all screens
current_user = {"data": None}


def get_current_user():
    return current_user["data"]


def set_current_user(user):
    current_user["data"] = user


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(30), spacing=dp(15))

        # Logo / Title
        with root.canvas.before:
            Color(0.13, 0.13, 0.18, 1)
            self._bg = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg, 'pos', root.pos),
                  size=lambda *a: setattr(self._bg, 'size', root.size))

        root.add_widget(Label(size_hint_y=0.1))  # spacer

        title = Label(
            text="🍞 Bakery Tracker",
            font_size=dp(28),
            bold=True,
            color=(1, 0.75, 0.2, 1),
            size_hint_y=None,
            height=dp(50),
        )
        root.add_widget(title)

        sub = Label(
            text="Production Management System",
            font_size=dp(13),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=dp(30),
        )
        root.add_widget(sub)

        root.add_widget(Label(size_hint_y=0.08))  # spacer

        # Username
        root.add_widget(Label(
            text="Username", halign="left", color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None, height=dp(25), text_size=(None, None)
        ))
        self.username_input = TextInput(
            hint_text="Enter username",
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_color=(0.2, 0.2, 0.27, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 0.75, 0.2, 1),
            padding=[dp(10), dp(12)],
        )
        root.add_widget(self.username_input)

        # Password
        root.add_widget(Label(
            text="Password", halign="left", color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None, height=dp(25)
        ))
        self.password_input = TextInput(
            hint_text="Enter password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_color=(0.2, 0.2, 0.27, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 0.75, 0.2, 1),
            padding=[dp(10), dp(12)],
        )
        root.add_widget(self.password_input)

        root.add_widget(Label(size_hint_y=0.05))

        # Login button
        btn = Button(
            text="LOGIN",
            size_hint_y=None,
            height=dp(50),
            background_color=(1, 0.75, 0.2, 1),
            color=(0.1, 0.1, 0.1, 1),
            font_size=dp(16),
            bold=True,
        )
        btn.bind(on_press=self.do_login)
        root.add_widget(btn)

        # Default credentials hint
        hint = Label(
            text="Default: manager / manager123\nWorker: bread / bread123",
            font_size=dp(11),
            color=(0.5, 0.5, 0.5, 1),
            halign="center",
            size_hint_y=None,
            height=dp(45),
        )
        root.add_widget(hint)

        root.add_widget(Label())  # bottom spacer

        self.add_widget(root)

    def do_login(self, *args):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not username or not password:
            self._alert("Please enter both username and password.")
            return

        user = authenticate(username, password)
        if user:
            set_current_user(user)
            self.manager.current = "dashboard"
            # Clear inputs
            self.username_input.text = ""
            self.password_input.text = ""
        else:
            self._alert("Invalid username or password.")

    def _alert(self, msg):
        content = BoxLayout(orientation="vertical", padding=dp(20))
        content.add_widget(Label(text=msg, color=(1, 1, 1, 1)))
        btn = Button(text="OK", size_hint_y=None, height=dp(40))
        p = Popup(title="Notice", content=content,
                  size_hint=(0.8, 0.35), background_color=(0.2, 0.2, 0.27, 1))
        btn.bind(on_press=p.dismiss)
        content.add_widget(btn)
        p.open()
