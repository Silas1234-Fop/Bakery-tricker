"""screens/dashboard_screen.py"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
from database import reconcile, reconcile_by_dept
from screens.login_screen import get_current_user

DEPT_COLORS = {
    "Mandazi": (0.2, 0.6, 0.9, 1),
    "Bread":   (0.9, 0.5, 0.1, 1),
    "Cakes":   (0.8, 0.3, 0.6, 1),
    "Bagne":   (0.2, 0.8, 0.5, 1),
}


def _card(text_top, text_bottom, bg=(0.18, 0.18, 0.24, 1)):
    box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(4),
                    size_hint_y=None, height=dp(72))
    with box.canvas.before:
        Color(*bg)
        box._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(10)])
    box.bind(pos=lambda *a: setattr(box._rect, 'pos', box.pos),
             size=lambda *a: setattr(box._rect, 'size', box.size))
    box.add_widget(Label(text=str(text_top), font_size=dp(22), bold=True,
                         color=(1, 1, 1, 1)))
    box.add_widget(Label(text=str(text_bottom), font_size=dp(11),
                         color=(0.7, 0.7, 0.7, 1)))
    return box


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._widgets = {}
        self._build_ui()

    def on_enter(self):
        self.refresh_data()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            root._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._bg, 'pos', root.pos),
                  size=lambda *a: setattr(root._bg, 'size', root.size))

        # ── Header ──────────────────────────────────────────────────────────
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(15), 0])
        with header.canvas.before:
            Color(0.13, 0.13, 0.19, 1)
            header._r = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda *a: setattr(header._r, 'pos', header.pos),
                    size=lambda *a: setattr(header._r, 'size', header.size))

        header.add_widget(Label(
            text="🍞  Dashboard", font_size=dp(18), bold=True,
            color=(1, 0.75, 0.2, 1), halign="left"
        ))
        logout_btn = Button(
            text="Logout", size_hint=(None, None), size=(dp(70), dp(32)),
            background_color=(0.7, 0.2, 0.2, 1), font_size=dp(12)
        )
        logout_btn.bind(on_press=self.logout)
        header.add_widget(logout_btn)
        root.add_widget(header)

        # ── Scrollable body ──────────────────────────────────────────────────
        scroll = ScrollView()
        body = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(12),
                         size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        # Today's summary cards
        body.add_widget(Label(
            text="TODAY'S SUMMARY", font_size=dp(12), color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=dp(22), halign="left",
            text_size=(None, None)
        ))

        cards_row = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(160))
        self._widgets["card_produced"] = _card("—", "Total Produced", (0.15, 0.4, 0.7, 1))
        self._widgets["card_packed"]   = _card("—", "Total Packed",   (0.15, 0.55, 0.3, 1))
        self._widgets["card_loss"]     = _card("—", "Real Loss",      (0.6, 0.2, 0.2, 1))
        self._widgets["card_eff"]      = _card("—", "Efficiency",     (0.5, 0.3, 0.7, 1))
        for w in self._widgets.values():
            cards_row.add_widget(w)
        body.add_widget(cards_row)

        # Dept breakdown header
        body.add_widget(Label(
            text="BY DEPARTMENT", font_size=dp(12), color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=dp(22)
        ))

        # Dept rows (will be populated in refresh_data)
        self._dept_container = BoxLayout(orientation="vertical", spacing=dp(8),
                                         size_hint_y=None)
        self._dept_container.bind(minimum_height=self._dept_container.setter("height"))
        body.add_widget(self._dept_container)

        # Navigation buttons
        body.add_widget(Label(
            text="ENTER DATA", font_size=dp(12), color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=dp(22)
        ))
        nav_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(110))
        for label, screen, color in [
            ("+ Production",  "production", (0.15, 0.4, 0.7, 1)),
            ("+ Packaging",   "packaging",  (0.15, 0.55, 0.3, 1)),
            ("+ Giveaway",    "giveaway",   (0.5, 0.3, 0.7, 1)),
            ("📋 History",    "history",    (0.35, 0.35, 0.45, 1)),
        ]:
            btn = Button(
                text=label, background_color=color, font_size=dp(14),
                size_hint_y=None, height=dp(50)
            )
            btn.bind(on_press=lambda x, s=screen: self._go(s))
            nav_grid.add_widget(btn)
        body.add_widget(nav_grid)

        # Refresh button
        ref = Button(
            text="🔄  Refresh", size_hint_y=None, height=dp(44),
            background_color=(0.25, 0.25, 0.35, 1), font_size=dp(14)
        )
        ref.bind(on_press=lambda *a: self.refresh_data())
        body.add_widget(ref)

        body.add_widget(Label(size_hint_y=None, height=dp(20)))

        scroll.add_widget(body)
        root.add_widget(scroll)
        self.add_widget(root)

    def refresh_data(self):
        from datetime import date
        today = date.today().isoformat()

        # Overall totals
        stats = reconcile(rec_date=today)
        self._set_card("card_produced", f"{stats['produced']:.0f}")
        self._set_card("card_packed",   f"{stats['packed']:.0f}")
        self._set_card("card_loss",     f"{stats['real_loss']:.0f}")
        self._set_card("card_eff",      f"{stats['efficiency']}%")

        # Dept breakdown
        self._dept_container.clear_widgets()
        by_dept = reconcile_by_dept(rec_date=today)
        for dept, s in by_dept.items():
            self._dept_container.add_widget(self._dept_row(dept, s))

    def _set_card(self, key, value):
        card = self._widgets[key]
        card.children[1].text = value  # top label (first child in reverse)

    def _dept_row(self, dept, stats):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(60),
                        padding=dp(10), spacing=dp(8))
        with row.canvas.before:
            Color(0.18, 0.18, 0.24, 1)
            row._r = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(8)])
        row.bind(pos=lambda *a: setattr(row._r, 'pos', row.pos),
                 size=lambda *a: setattr(row._r, 'size', row.size))

        color = DEPT_COLORS.get(dept, (0.5, 0.5, 0.5, 1))
        dot = Label(text="●", color=color, size_hint_x=None, width=dp(18),
                    font_size=dp(16))
        row.add_widget(dot)

        info = BoxLayout(orientation="vertical")
        info.add_widget(Label(text=dept, font_size=dp(14), bold=True,
                              color=(1, 1, 1, 1), halign="left",
                              text_size=(None, None)))
        eff_color = (0.2, 0.8, 0.3, 1) if stats["efficiency"] >= 90 else \
                    (1, 0.7, 0.1, 1)  if stats["efficiency"] >= 70 else \
                    (0.9, 0.3, 0.3, 1)
        info.add_widget(Label(
            text=f"Produced: {stats['produced']:.0f}  Packed: {stats['packed']:.0f}  "
                 f"Loss: {stats['real_loss']:.0f}",
            font_size=dp(10), color=(0.65, 0.65, 0.65, 1),
            halign="left", text_size=(None, None)
        ))
        row.add_widget(info)

        eff_lbl = Label(
            text=f"{stats['efficiency']}%", font_size=dp(16), bold=True,
            color=eff_color, size_hint_x=None, width=dp(55), halign="right"
        )
        row.add_widget(eff_lbl)
        return row

    def _go(self, screen_name):
        self.manager.current = screen_name

    def logout(self, *args):
        from screens.login_screen import set_current_user
        set_current_user(None)
        self.manager.current = "login"
