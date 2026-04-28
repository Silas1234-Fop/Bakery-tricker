"""screens/production_screen.py"""

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


class ProductionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")
        dark_bg(root)

        root.add_widget(header_bar("📦 Production Entry",
                                   lambda *a: setattr(self.manager, 'current', 'dashboard')))

        scroll = ScrollView()
        body = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10),
                         size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        # Department spinner (locked to user's dept if worker)
        body.add_widget(field_label("Department"))
        user = get_current_user()
        if user and user["role"] == "worker" and user["dept"]:
            depts = [user["dept"]]
        else:
            depts = list(DEPARTMENTS.keys())
        self.dept_spinner = spinner_field(depts, depts[0])
        self.dept_spinner.bind(text=self._on_dept_change)
        body.add_widget(self.dept_spinner)

        # Product spinner
        body.add_widget(field_label("Product"))
        initial_dept = depts[0]
        self.product_spinner = spinner_field(DEPARTMENTS[initial_dept],
                                             DEPARTMENTS[initial_dept][0])
        body.add_widget(self.product_spinner)

        # Sack number
        body.add_widget(field_label("Sack Number"))
        self.sack_input = text_field("e.g. 1", numeric=True)
        body.add_widget(self.sack_input)

        # Input quantity
        body.add_widget(field_label("Input Quantity (kg)"))
        self.input_qty = text_field("e.g. 50", numeric=True)
        body.add_widget(self.input_qty)

        # Output quantity
        body.add_widget(field_label("Output Quantity (units)"))
        self.output_qty = text_field("e.g. 120", numeric=True)
        body.add_widget(self.output_qty)

        # Date
        body.add_widget(field_label("Date (YYYY-MM-DD)"))
        self.date_input = text_field(date.today().isoformat())
        self.date_input.text = date.today().isoformat()
        body.add_widget(self.date_input)

        body.add_widget(save_button(self.save_record))

        # Recent records
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
        dept    = self.dept_spinner.text
        product = self.product_spinner.text
        sack    = self.sack_input.text.strip()
        inp     = self.input_qty.text.strip()
        out     = self.output_qty.text.strip()
        rec_date = self.date_input.text.strip()

        if not all([dept, product, sack, inp, out, rec_date]):
            alert_popup("Please fill in all fields."); return
        try:
            sack_n = int(float(sack))
            in_q   = float(inp)
            out_q  = float(out)
        except ValueError:
            alert_popup("Sack, input and output must be numbers."); return
        if in_q <= 0 or out_q <= 0:
            alert_popup("Quantities must be greater than zero."); return

        db.add_production(dept, product, sack_n, in_q, out_q, rec_date)
        alert_popup(f"✅ Saved!\n{product} – Sack {sack_n} – Output: {out_q:.0f}")
        self.sack_input.text = ""
        self.input_qty.text  = ""
        self.output_qty.text = ""
        self._refresh_records()

    def _refresh_records(self):
        self.records_box.clear_widgets()
        user = get_current_user()
        dept = user["dept"] if user and user["role"] == "worker" else None
        records = db.get_production(department=dept)[:10]
        for r in records:
            self.records_box.add_widget(self._record_row(r))

    def _record_row(self, r):
        row = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(6), spacing=dp(4))
        with row.canvas.before:
            Color(0.18, 0.18, 0.24, 1)
            row._rr = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(6)])
        row.bind(pos=lambda *a: setattr(row._rr, 'pos', row.pos),
                 size=lambda *a: setattr(row._rr, 'size', row.size))

        info = BoxLayout(orientation="vertical")
        info.add_widget(Label(
            text=f"{r['department']} · {r['product']} · Sack {r['sack_number']}",
            font_size=dp(12), color=(1, 1, 1, 1), halign="left",
            text_size=(None, None)
        ))
        info.add_widget(Label(
            text=f"In: {r['input_qty']} kg  Out: {r['output_qty']}  {r['rec_date']}",
            font_size=dp(10), color=(0.6, 0.6, 0.6, 1), halign="left",
            text_size=(None, None)
        ))
        row.add_widget(info)

        del_btn = Button(
            text="✕", size_hint=(None, None), size=(dp(34), dp(34)),
            background_color=(0.7, 0.2, 0.2, 1), font_size=dp(14)
        )
        del_btn.bind(on_press=lambda x, rid=r["id"]: self._delete(rid))
        row.add_widget(del_btn)
        return row

    def _delete(self, record_id):
        db.delete_production(record_id)
        self._refresh_records()
