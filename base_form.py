"""screens/base_form.py  – reusable helpers for all data-entry screens."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

DEPARTMENTS = {
    "Mandazi": ["Plain Mandazi", "Jam Mandazi", "Sugar Mandazi"],
    "Bread":   ["Sandwich", "Ubwadesa", "Ibipande", "Boris"],
    "Cakes":   ["Vanilla Cake", "Chocolate Cake", "Fruit Cake"],
    "Bagne":   ["Classic Bagne", "Sweet Bagne"],
}
ALL_DEPTS = list(DEPARTMENTS.keys())


def dark_bg(widget):
    with widget.canvas.before:
        Color(0.1, 0.1, 0.15, 1)
        widget._bg = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda *a: setattr(widget._bg, 'pos', widget.pos),
                size=lambda *a: setattr(widget._bg, 'size', widget.size))


def header_bar(title_text, back_callback):
    bar = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(10), 0])
    with bar.canvas.before:
        Color(0.13, 0.13, 0.19, 1)
        bar._r = Rectangle(pos=bar.pos, size=bar.size)
    bar.bind(pos=lambda *a: setattr(bar._r, 'pos', bar.pos),
             size=lambda *a: setattr(bar._r, 'size', bar.size))
    back = Button(text="← Back", size_hint=(None, 1), width=dp(80),
                  background_color=(0.25, 0.25, 0.35, 1), font_size=dp(13))
    back.bind(on_press=back_callback)
    bar.add_widget(back)
    bar.add_widget(Label(text=title_text, font_size=dp(17), bold=True,
                         color=(1, 0.75, 0.2, 1)))
    return bar


def field_label(text):
    return Label(text=text, size_hint_y=None, height=dp(24),
                 color=(0.75, 0.75, 0.75, 1), halign="left",
                 text_size=(None, None))


def text_field(hint="", numeric=False):
    ti = TextInput(
        hint_text=hint,
        multiline=False,
        size_hint_y=None,
        height=dp(44),
        background_color=(0.18, 0.18, 0.26, 1),
        foreground_color=(1, 1, 1, 1),
        cursor_color=(1, 0.75, 0.2, 1),
        padding=[dp(10), dp(12)],
        input_filter="float" if numeric else None,
    )
    return ti


def spinner_field(values, default="Select…"):
    s = Spinner(
        text=default,
        values=values,
        size_hint_y=None,
        height=dp(44),
        background_color=(0.18, 0.18, 0.26, 1),
        color=(1, 1, 1, 1),
        font_size=dp(14),
    )
    return s


def save_button(on_press_fn):
    btn = Button(
        text="💾  SAVE RECORD",
        size_hint_y=None,
        height=dp(50),
        background_color=(1, 0.75, 0.2, 1),
        color=(0.1, 0.1, 0.1, 1),
        font_size=dp(15),
        bold=True,
    )
    btn.bind(on_press=on_press_fn)
    return btn


def alert_popup(message, title="Notice"):
    content = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
    content.add_widget(Label(text=message, color=(1, 1, 1, 1),
                             halign="center", text_size=(dp(260), None)))
    ok = Button(text="OK", size_hint_y=None, height=dp(40),
                background_color=(1, 0.75, 0.2, 1), color=(0.1, 0.1, 0.1, 1))
    p = Popup(title=title, content=content, size_hint=(0.85, 0.38),
              background_color=(0.18, 0.18, 0.26, 1))
    ok.bind(on_press=p.dismiss)
    content.add_widget(ok)
    p.open()
    return p
