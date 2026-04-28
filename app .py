"""
Bakery Production Tracker - Main App Entry Point
Run with: python app.py
"""

import os
os.environ['KIVY_NO_ENV_CONFIG'] = '1'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.utils import platform

# Set window size for desktop testing (phone size)
if platform not in ('android', 'ios'):
    Window.size = (400, 700)

from database import init_db
from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.production_screen import ProductionScreen
from screens.packaging_screen import PackagingScreen
from screens.giveaway_screen import GiveawayScreen
from screens.history_screen import HistoryScreen

# ── Department → Product mapping ─────────────────────────────────────────────
DEPARTMENTS = {
    "Mandazi": ["Plain Mandazi", "Jam Mandazi", "Sugar Mandazi"],
    "Bread":   ["Sandwich", "Ubwadesa", "Ibipande", "Boris"],
    "Cakes":   ["Vanilla Cake", "Chocolate Cake", "Fruit Cake"],
    "Bagne":   ["Classic Bagne", "Sweet Bagne"],
}


class BakeryApp(App):
    title = "Bakery Tracker"

    def build(self):
        # Initialise local SQLite database
        init_db()

        # Screen manager handles all navigation
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(ProductionScreen(name="production"))
        sm.add_widget(PackagingScreen(name="packaging"))
        sm.add_widget(GiveawayScreen(name="giveaway"))
        sm.add_widget(HistoryScreen(name="history"))

        sm.current = "login"
        return sm


if __name__ == "__main__":
    BakeryApp().run()
