"""screens/history_screen.py"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from datetime import date

import database as db
from screens.base_form import dark_bg, header_bar, DEPARTMENTS
from screens.login_screen import get_current_user

TAB_BG_ON  = (0.2, 0.45, 0.8, 1)
TAB_BG_OFF = (0.22, 0.22, 0.3, 1)


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_tab = "production"
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")
        dark_bg(root)
        root.add_widget(header_bar("📋 History",
                                   lambda *a: setattr(self.manager, 'current', 'dashboard')))

        # Tab bar
        tab_bar = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(2),
                            padding=[dp(8), dp(4)])
        with tab_bar.canvas.before:
            Color(0.13, 0.13, 0.19, 1)
            tab_bar._r = Rectangle(pos=tab_bar.pos, size=tab_bar.size)
        tab_bar.bind(pos=lambda *a: setattr(tab_bar._r, 'pos', tab_bar.pos),
                     size=lambda *a: setattr(tab_bar._r, 'size', tab_bar.size))

        self._tab_btns = {}
        for name, label in [("production", "Production"), ("packaging", "Packaging"),
                             ("giveaway", "Giveaway")]:
            btn = Button(
                text=label, font_size=dp(12),
                background_color=TAB_BG_ON if name == "production" else TAB_BG_OFF
            )
            btn.bind(on_press=lambda x, n=name: self._switch_tab(n))
            self._tab_btns[name] = btn
            tab_bar.add_widget(btn)
        root.add_widget(tab_bar)

        # Filter row
        filter_row = BoxLayout(size_hint_y=None, height=dp(44), padding=dp(8),
                                spacing=dp(6))
        self.dept_filter = Spinner(
            text="All Departments",
            values=["All Departments"] + list(DEPARTMENTS.keys()),
            size_hint_x=0.6, height=dp(36), size_hint_y=None,
            background_color=(0.22, 0.22, 0.3, 1), color=(1, 1, 1, 1),
            font_size=dp(12)
        )
        self.dept_filter.bind(text=lambda *a: self._refresh())
        filter_row.add_widget(self.dept_filter)
        ref = Button(text="🔄", size_hint_x=0.2, size_hint_y=None, height=dp(36),
                     background_color=(0.25, 0.25, 0.35, 1))
        ref.bind(on_press=lambda *a: self._refresh())
        filter_row.add_widget(ref)
        root.add_widget(filter_row)

        # Records list
        scroll = ScrollView()
        self.records_box = BoxLayout(orientation="vertical", spacing=dp(6),
                                      padding=dp(10), size_hint_y=None)
        self.records_box.bind(minimum_height=self.records_box.setter("height"))
        scroll.add_widget(self.records_box)
        root.add_widget(scroll)

        self.add_widget(root)

    def on_enter(self):
        # Restrict worker to their own dept
        user = get_current_user()
        if user and user["role"] == "worker" and user["dept"]:
            self.dept_filter.text = user["dept"]
            self.dept_filter.disabled = True
        else:
            self.dept_filter.disabled = False
        self._refresh()

    def _switch_tab(self, name):
        self._current_tab = name
        for n, btn in self._tab_btns.items():
            btn.background_color = TAB_BG_ON if n == name else TAB_BG_OFF
        self._refresh()

    def _refresh(self):
        self.records_box.clear_widgets()
        dept = self.dept_filter.text
        dept = None if dept == "All Departments" else dept

        if self._current_tab == "production":
            records = db.get_production(department=dept)
            for r in records:
                self.records_box.add_widget(self._prod_row(r))
        elif self._current_tab == "packaging":
            records = db.get_packaging(department=dept)
            for r in records:
                self.records_box.add_widget(self._pack_row(r))
        else:
            records = db.get_giveaway(department=dept)
            for r in records:
                self.records_box.add_widget(self._give_row(r))

        if not records:
            self.records_box.add_widget(Label(
                text="No records found.", color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None, height=dp(50)
            ))

    def _make_row(self, line1, line2, record_id, delete_fn):
        row = BoxLayout(size_hint_y=None, height=dp(52), padding=dp(6), spacing=dp(4))
        with row.canvas.before:
            Color(0.18, 0.18, 0.24, 1)
            row._rr = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(6)])
        row.bind(pos=lambda *a: setattr(row._rr, 'pos', row.pos),
                 size=lambda *a: setattr(row._rr, 'size', row.size))
        info = BoxLayout(orientation="vertical")
        info.add_widget(Label(text=line1, font_size=dp(12), color=(1, 1, 1, 1),
                              halign="left", text_size=(None, None)))
        info.add_widget(Label(text=line2, font_size=dp(10), color=(0.6, 0.6, 0.6, 1),
                              halign="left", text_size=(None, None)))
        row.add_widget(info)
        del_btn = Button(text="✕", size_hint=(None, None), size=(dp(34), dp(34)),
                         background_color=(0.7, 0.2, 0.2, 1), font_size=dp(14))
        del_btn.bind(on_press=lambda x, rid=record_id: delete_fn(rid))
        row.add_widget(del_btn)
        return row

    def _prod_row(self, r):
        return self._make_row(
            f"{r['department']} · {r['product']} · Sack {r['sack_number']}",
            f"In: {r['input_qty']} kg  Out: {r['output_qty']}  {r['rec_date']}",
            r["id"], self._del_prod
        )

    def _pack_row(self, r):
        return self._make_row(
            f"{r['department']} · {r['product']}",
            f"Packed: {r['total_packed']}  {r['rec_date']}",
            r["id"], self._del_pack
        )

    def _give_row(self, r):
        return self._make_row(
            f"{r['department']} · {r['product']}  ({r['reason'] or '—'})",
            f"Given: {r['quantity']}  {r['rec_date']}",
            r["id"], self._del_give
        )

    def _del_prod(self, rid):
        db.delete_production(rid); self._refresh()

    def _del_pack(self, rid):
        db.delete_packaging(rid); self._refresh()

    def _del_give(self, rid):
        db.delete_giveaway(rid); self._refresh()
