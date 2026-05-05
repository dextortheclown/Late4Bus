import os
import sys
import customtkinter as ctk

sys.path.insert(0, os.path.dirname(__file__))

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

from utils.config_manager import is_first_run, get_api_key
from api import bus as bus_module


def main():
    from ui.widget import TransitWidget
    app = TransitWidget()

    api_key = get_api_key()
    if api_key:
        bus_module.set_api_key(api_key)

    if is_first_run():
        app.after(300, lambda: _show_onboarding(app))

    app.mainloop()


def _show_onboarding(app):
    from ui.onboarding import OnboardingWindow
    OnboardingWindow(app, on_complete_callback=lambda key: _on_onboarding_done(app, key))


def _on_onboarding_done(app, api_key):
    from api import bus as bus_module
    bus_module.set_api_key(api_key)
    app._render_content()
    app._start_refresh_loop()


if __name__ == "__main__":
    main()