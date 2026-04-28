"""screens/giveaway_screen.py"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from datetime import date

import database as db
from screens.base_form import (
    DEPARTMENTS, dark_bg, header_bar, field_label,
    text_field, spinner_field, save_button, alert_popup
)
from screens.login_screen import get_current_user


class GiveawayScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()
    def _build_ui(self):
        root = BoxLayout(orientation="vertical")
        dark_bg(root)
        root.add_widget(header_bar("🎁 Giveaway / Sample Entry",
                                   lambda *a: setattr(self.manager, 'current', 'dashboard')))

        scroll = ScrollView()
        body = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10),
                         size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        user = get_current_user()
        if user and user["role"] == "worker" and user["dept"]:
            depts = [user["dept"]]
        else:
            depts = list(DEPARTMENTS.keys())

        body.add_widget(field_label("Department"))
        self.dept_spinner = spinner_field(depts, depts[0])
        self.dept_spinner.bind(text=self._on_dept_change)
        body.add_widget(self.dept_spinner)

        body.add_widget(field_label("Product"))
        initial_dept = depts[0]
        self.product_spinner = spinner_field(DEPARTMENTS[initial_dept],
                                             DEPARTMENTS[initial_dept][0])
        body.add_widget(self.product_spinner)

        body.add_widget(field_label("Quantity Given Away"))
        self.qty_input = text_field("e.g. 10", numeric=True)
        body.add_widget(self.qty_input)

        body.add_widget(field_label("Reason (optional)"))
        self.reason_input = text_field("e.g. Promotion, Owner use, Sample")
        body.add_widget(self.reason_input)

        body.add_widget(field_label("Date (YYYY-MM-DD)"))
        self.date_input = text_field(date.today().isoformat())
        self.date_input.text = date.today().isoformat()
        body.add_widget(self.date_input)

        body.add_widget(save_button(self.save_record))

        body.add_widget(Label(
            text="RECENT RECORDS", font_size=dp(12), color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=dp(28)
        ))
        self.records_box = BoxLayout(orientation="vertical", spacing=dp(6),
                                      size_hint_y=None)
        self.records_box.bind(minimum_height=self.records_box.setter("height"))
        body.add_widget(self.records_box)
        body.add_widget(Label(size_hint_y=None, height=dp(20)))

        scroll.add_widget(body)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        self._refresh_records()

    def _on_dept_change(self, spinner, value):
        prods = DEPARTMENTS.get(value, [])
        self.product_spinner.values = prods
        self.product_spinner.text = prods[0] if prods else "—"

    def save_record(self, *args):
        dept     = self.dept_spinner.text
        product  = self.product_spinner.text
        qty      = self.qty_input.text.strip()
        reason   = self.reason_input.text.strip()
        rec_date = self.date_input.text.strip()

        if not all([dept, product, qty, rec_date]):
            alert_popup("Please fill in department, product, quantity and date."); return
        try:
            qty_f = float(qty)
        except ValueError:
            alert_popup("Quantity must be a number."); return
        if qty_f <= 0:
            alert_popup("Quantity must be greater than zero."); return

        db.add_giveaway(dept, product, qty_f, reason, rec_date)
        alert_popup(f"✅ Saved!\n{product} – Given away: {qty_f:.0f}")
        self.qty_input.text    = ""
        self.reason_input.text = ""
        self._refresh_records()

    def _refresh_records(self):
        self.records_box.clear_widgets()
        user = get_current_user()
        dept = user["dept"] if user and user["role"] == "worker" else None
        records = db.get_giveaway(department=dept)[:10]
        for r in records:
            self.records_box.add_widget(self._record_row(r))

    def _record_row(self, r):
        row = BoxLayout(size_hint_y=None, height=dp(48), padding=dp(6), spacing=dp(4))
        with row.canvas.before:
            Color(0.18, 0.18, 0.24, 1)
            row._rr = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(6)])
        row.bind(pos=lambda *a: setattr(row._rr, 'pos', row.pos),
                 size=lambda *a: setattr(row._rr, 'size', row.size))
        info = BoxLayout(orientation="vertical")
        info.add_widget(Label(
            text=f"{r['department']} · {r['product']}  ({r['reason'] or 'No reason'})",
            font_size=dp(12), color=(1, 1, 1, 1), halign="left",
            text_size=(None, None)
        ))
        info.add_widget(Label(
            text=f"Qty: {r['quantity']}  {r['rec_date']}",
            font_size=dp(10), color=(0.6, 0.6, 0.6, 1), halign="left",
            text_size=(None, None)
        ))
        row.add_widget(info)
        del_btn = Button(text="✕", size_hint=(None, None), size=(dp(34), dp(34)),
                         background_color=(0.7, 0.2, 0.2, 1), font_size=dp(14))
        del_btn.bind(on_press=lambda x, rid=r["id"]: self._delete(rid))
        row.add_widget(del_btn)
        return row

    def _delete(self, record_id):
        db.delete_giveaway(record_id)
        self._refresh_records()
