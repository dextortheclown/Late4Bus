import customtkinter as ctk
import threading
from utils.config_manager import save_api_key, save_config, load_config
from api.bus import set_api_key, fetch_all_bus_stops

DARK_BG     = "#0f0f0f"
CARD_BG     = "#1a1a1a"
CARD_BORDER = "#2a2a2a"
ACCENT      = "#3b82f6"
ACCENT_HOVER= "#2563eb"
TEXT_PRIMARY= "#f1f5f9"
TEXT_MUTED  = "#64748b"
GREEN       = "#4ade80"
RED         = "#f87171"


class OnboardingWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_complete_callback=None):
        super().__init__(parent)
        self.on_complete_callback = on_complete_callback

        self.title("Late4Bus - Setup")
        self.geometry("480x420")
        self.resizable(False, False)
        self.configure(fg_color=DARK_BG)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()

    def _build_ui(self):
        # Logo / title area
        ctk.CTkLabel(self, text="Late4Bus",
                     font=("SF Pro Display", 26, "bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(40, 4))
        ctk.CTkLabel(self, text="Real-time bus and MRT timings for Singapore",
                     font=("SF Pro Display", 13),
                     text_color=TEXT_MUTED).pack()

        # Card
        card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12)
        card.pack(fill="x", padx=32, pady=32)

        ctk.CTkLabel(card, text="Enter your LTA DataMall API Key",
                     font=("SF Pro Display", 14, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(20, 4))

        ctk.CTkLabel(card,
                     text="Sign up free at datamall.lta.gov.sg\nYour key is stored locally and never shared.",
                     font=("SF Pro Display", 12),
                     text_color=TEXT_MUTED,
                     justify="left").pack(anchor="w", padx=20, pady=(0, 12))

        self.key_entry = ctk.CTkEntry(
            card,
            placeholder_text="Paste your API key here",
            fg_color="#111", border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY,
            font=("SF Pro Display", 13),
            height=40, corner_radius=8,
            show="*")
        self.key_entry.pack(fill="x", padx=20, pady=(0, 8))

        # Show/hide toggle
        self.show_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(card, text="Show API key",
                        variable=self.show_var,
                        font=("SF Pro Display", 12),
                        text_color=TEXT_MUTED,
                        fg_color=ACCENT,
                        command=self._toggle_show).pack(anchor="w", padx=20, pady=(0, 16))

        # Status label
        self.status_label = ctk.CTkLabel(card, text="",
                                         font=("SF Pro Display", 12),
                                         text_color=TEXT_MUTED)
        self.status_label.pack(pady=(0, 8))

        # Verify + continue button
        self.verify_btn = ctk.CTkButton(
            card, text="Verify & Continue",
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            font=("SF Pro Display", 14, "bold"),
            corner_radius=8, height=42,
            command=self._verify_key)
        self.verify_btn.pack(fill="x", padx=20, pady=(0, 20))

    def _toggle_show(self):
        try:
            self.key_entry.configure(show="" if self.show_var.get() else "*")
        except Exception:
            pass

    def _verify_key(self):
        key = self.key_entry.get().strip()
        if not key:
            self._set_status("Please enter your API key.", RED)
            return

        self.verify_btn.configure(state="disabled", text="Verifying...")
        self._set_status("Testing connection to LTA DataMall...", TEXT_MUTED)

        def worker():
            import requests
            try:
                resp = requests.get(
                    "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival",
                    headers={"AccountKey": key, "accept": "application/json"},
                    params={"BusStopCode": "83139"},
                    timeout=10
                )
                success = resp.status_code == 200 and "Services" in resp.json()
            except Exception:
                success = False
            self.after(0, lambda: self._on_verify_result(key, success))

        threading.Thread(target=worker, daemon=True).start()

    def _on_verify_result(self, key, success):
        try:
            if success:
                self._set_status("Connected successfully.", GREEN)
                save_api_key(key)
                self.after(800, lambda: self._open_settings(key))
            else:
                self._set_status("Could not connect. Check your API key and try again.", RED)
                self.verify_btn.configure(state="normal", text="Verify & Continue")
        except Exception:
            pass

    def _open_settings(self, api_key):
        try:
            self.destroy()
            from ui.settings import SettingsWindow
            SettingsWindow(
                self.master,
                on_save_callback=lambda: self.on_complete_callback(api_key)
                            if self.on_complete_callback else None
            )
        except Exception:
            pass

    def _set_status(self, msg, color):
        try:
            self.status_label.configure(text=msg, text_color=color)
        except Exception:
            pass

    def _on_close(self):
        # Allow closing onboarding without crashing the app
        self.destroy()