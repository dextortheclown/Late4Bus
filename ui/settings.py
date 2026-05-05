import customtkinter as ctk
import threading
from api.bus import fetch_all_bus_stops, search_bus_stops
from data.last_trains import MRT_STATIONS, LINE_NAMES, LINE_COLORS, get_all_stations_flat
from utils.config_manager import load_config, save_config
from utils.config_manager import get_startup_enabled, set_startup


DARK_BG      = "#0f0f0f"
CARD_BG      = "#1a1a1a"
CARD_BORDER  = "#2a2a2a"
ACCENT       = "#3b82f6"
ACCENT_HOVER = "#2563eb"
TEXT_PRIMARY = "#f1f5f9"
TEXT_MUTED   = "#64748b"
GREEN        = "#4ade80"
RED          = "#f87171"
YELLOW       = "#facc15"


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_save_callback=None):
        super().__init__(parent)
        self.on_save_callback = on_save_callback
        self.config_data = load_config()
        self.all_bus_stops = []
        self.bus_stops_loaded = False

        self.title("Late4Bus - Settings")
        self.geometry("700x850")
        self.resizable(False, False)
        self.configure(fg_color=DARK_BG)
        self.grab_set()

        self._build_ui()
        self._load_bus_stops_async()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Settings", font=("SF Pro Display", 20, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(header, text="Choose your bus stops and MRT stations",
                     font=("SF Pro Display", 13), text_color=TEXT_MUTED).pack(side="left", padx=4, pady=15)

        # Tabs
        self.tab_view = ctk.CTkTabview(self, fg_color=DARK_BG,
                                       segmented_button_fg_color=CARD_BG,
                                       segmented_button_selected_color=ACCENT,
                                       segmented_button_selected_hover_color=ACCENT_HOVER,
                                       segmented_button_unselected_color=CARD_BG,
                                       segmented_button_unselected_hover_color="#2a2a2a",
                                       text_color=TEXT_PRIMARY)
        self.tab_view.pack(fill="both", expand=True, padx=16, pady=(8, 0))

        self.tab_view.add("Bus Stops")
        self.tab_view.add("MRT Stations")

        self._build_bus_tab(self.tab_view.tab("Bus Stops"))
        self._build_mrt_tab(self.tab_view.tab("MRT Stations"))

        startup_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=8)
        startup_frame.pack(fill="x", padx=16, pady=(0, 4))

        ctk.CTkLabel(startup_frame, text="Launch at startup",
                    font=("SF Pro Display", 12, "bold"),
                    text_color=TEXT_PRIMARY).pack(side="left", padx=12, pady=10)

        ctk.CTkLabel(startup_frame, text="Automatically open Late4Bus when Windows starts",
                    font=("SF Pro Display", 11),
                    text_color=TEXT_MUTED).pack(side="left")

        self.startup_var = ctk.BooleanVar(value=get_startup_enabled())
        ctk.CTkSwitch(startup_frame,
                    text="",
                    variable=self.startup_var,
                    fg_color="#1e3a5f",
                    progress_color=ACCENT,
                    width=44, height=22,
                    command=self._toggle_startup).pack(side="right", padx=12, pady=10)

        # API Key section
        api_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=8)
        api_frame.pack(fill="x", padx=16, pady=(0, 4))

        ctk.CTkLabel(api_frame, text="LTA DataMall API Key",
                     font=("SF Pro Display", 12, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=12, pady=10)

        from utils.config_manager import get_api_key
        self.api_key_entry = ctk.CTkEntry(
            api_frame,
            placeholder_text="API key",
            fg_color="#111", border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY,
            font=("SF Pro Display", 12),
            height=32, corner_radius=6,
            show="*", width=220)
        self.api_key_entry.insert(0, get_api_key())
        self.api_key_entry.pack(side="right", padx=12, pady=10)

        # Save button
        btn_frame = ctk.CTkFrame(self, fg_color=DARK_BG, height=60)
        btn_frame.pack(fill="x", padx=16, pady=12)
        btn_frame.pack_propagate(False)
        ctk.CTkButton(btn_frame, text="Save & Apply",
                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      font=("SF Pro Display", 14, "bold"),
                      corner_radius=8, height=40,
                      command=self._save).pack(side="right")
        ctk.CTkButton(btn_frame, text="Cancel",
                      fg_color=CARD_BG, hover_color="#222",
                      font=("SF Pro Display", 14),
                      corner_radius=8, height=40,
                      command=self.destroy).pack(side="right", padx=(0, 8))

    # ------------------------------------------------------------------
    # Bus Stops Tab
    # ------------------------------------------------------------------

    def _build_bus_tab(self, parent):
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", pady=(12, 8))

        self.bus_search_var = ctk.StringVar()
        self.bus_search_var.trace_add("write", self._on_bus_search_typed)
        self.bus_search_entry = ctk.CTkEntry(
            search_frame, textvariable=self.bus_search_var,
            placeholder_text="Search by stop name, code, or road...",
            fg_color=CARD_BG, border_color=CARD_BORDER, text_color=TEXT_PRIMARY,
            font=("SF Pro Display", 13), height=38, corner_radius=8)
        self.bus_search_entry.pack(fill="x")

        self.bus_loading_label = ctk.CTkLabel(
            parent, text="Loading bus stops from LTA DataMall...",
            font=("SF Pro Display", 12), text_color=TEXT_MUTED)
        self.bus_loading_label.pack(pady=4)

        self.bus_results_frame = ctk.CTkScrollableFrame(
            parent, fg_color=CARD_BG, corner_radius=8, height=200)
        self.bus_results_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(parent, text="Selected Bus Stops",
                    font=("SF Pro Display", 13, "bold"),
                    text_color=TEXT_PRIMARY).pack(anchor="w", pady=(4, 6))

        self.selected_bus_frame = ctk.CTkScrollableFrame(
            parent, fg_color=CARD_BG, corner_radius=8, height=200)
        self.selected_bus_frame.pack(fill="x")
        self._refresh_selected_bus_stops()

        self._search_debounce_job = None
    
    def _on_bus_search_typed(self, *_):
        # Cancel any previously scheduled search
        if self._search_debounce_job:
            self.after_cancel(self._search_debounce_job)
        # Schedule search 200ms after user stops typing
        self._search_debounce_job = self.after(200, self._run_bus_search)

    def _run_bus_search(self):
        if not self.bus_stops_loaded:
            return
        q = self.bus_search_var.get().strip()
        if not q:
            self._render_bus_results([])
            return

        def worker():
            results = search_bus_stops(q, self.all_bus_stops)
            self.after(0, lambda: self._render_bus_results(results))

        threading.Thread(target=worker, daemon=True).start()

    def _on_bus_stops_loaded(self):
        try:
            self.bus_loading_label.configure(
                text=f"{len(self.all_bus_stops)} stops loaded. Start typing to search.")
            self._render_bus_results([])
        except Exception:
            pass

    def _add_bus_stop(self, stop):
        entry = {
            "stop_code": stop["BusStopCode"],
            "stop_name": stop["Description"],
            "road": stop["RoadName"],
            "services": []
        }
        stops = self.config_data.setdefault("bus_stops", [])
        if not any(s["stop_code"] == entry["stop_code"] for s in stops):
            stops.append(entry)
        self._refresh_selected_bus_stops()
        self._run_bus_search()  # refresh results to show Added state

    def _remove_bus_stop(self, stop):
        stops = self.config_data.get("bus_stops", [])
        self.config_data["bus_stops"] = [
            s for s in stops if s["stop_code"] != stop["stop_code"]]
        self._refresh_selected_bus_stops()
        self._run_bus_search()

    def _load_bus_stops_async(self):
        def worker():
            stops = fetch_all_bus_stops()
            self.all_bus_stops = stops
            self.bus_stops_loaded = True
            self.after(0, self._on_bus_stops_loaded)

        threading.Thread(target=worker, daemon=True).start()

    def _render_bus_results(self, results):
        try:
            for w in self.bus_results_frame.winfo_children():
                w.destroy()
        except Exception:
            return

        if not results:
            ctk.CTkLabel(self.bus_results_frame,
                        text="Type to search for a bus stop",
                        font=("SF Pro Display", 12), text_color=TEXT_MUTED).pack(pady=12)
            return

        for stop in results:
            code = stop.get("BusStopCode", "")
            desc = stop.get("Description", "")
            road = stop.get("RoadName", "")

            already = any(s["stop_code"] == code
                          for s in self.config_data.get("bus_stops", []))

            row = ctk.CTkFrame(self.bus_results_frame, fg_color="#1e1e1e",
                               corner_radius=6, height=48)
            row.pack(fill="x", pady=2, padx=4)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=f"{desc}",
                         font=("SF Pro Display", 13, "bold"),
                         text_color=TEXT_PRIMARY).pack(side="left", padx=12, pady=4)
            ctk.CTkLabel(row, text=f"{code}  •  {road}",
                         font=("SF Pro Display", 11), text_color=TEXT_MUTED).pack(side="left")

            btn_text = "Added" if already else "+ Add"
            btn_color = "#2a2a2a" if already else ACCENT
            ctk.CTkButton(row, text=btn_text, width=70, height=28,
                          fg_color=btn_color, hover_color=ACCENT_HOVER,
                          font=("SF Pro Display", 11), corner_radius=6,
                          state="disabled" if already else "normal",
                          command=lambda s=stop: self._add_bus_stop(s)
                          ).pack(side="right", padx=12)

    def _refresh_selected_bus_stops(self):
        for w in self.selected_bus_frame.winfo_children():
            w.destroy()

        stops = self.config_data.get("bus_stops", [])
        if not stops:
            ctk.CTkLabel(self.selected_bus_frame,
                         text="No bus stops added yet",
                         font=("SF Pro Display", 12), text_color=TEXT_MUTED).pack(pady=12)
            return

        for stop in stops:
            self._render_selected_bus_card(stop)

    def _render_selected_bus_card(self, stop):
        card = ctk.CTkFrame(self.selected_bus_frame, fg_color="#1e1e1e",
                            corner_radius=8)
        card.pack(fill="x", pady=4, padx=4)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(top_row, text=stop["stop_name"],
                     font=("SF Pro Display", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(top_row, text=f"  {stop['stop_code']}  •  {stop['road']}",
                     font=("SF Pro Display", 11), text_color=TEXT_MUTED).pack(side="left")

        ctk.CTkButton(top_row, text="Remove", width=70, height=26,
                      fg_color="#3f1515", hover_color="#5a1f1f",
                      text_color=RED, font=("SF Pro Display", 11),
                      corner_radius=6,
                      command=lambda s=stop: self._remove_bus_stop(s)
                      ).pack(side="right")

        # Service filter row
        svc_row = ctk.CTkFrame(card, fg_color="transparent")
        svc_row.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(svc_row, text="Filter services (leave blank = show all):",
                     font=("SF Pro Display", 11), text_color=TEXT_MUTED).pack(side="left")

        svc_var = ctk.StringVar(value=", ".join(stop.get("services", [])))
        svc_entry = ctk.CTkEntry(svc_row, textvariable=svc_var, width=160,
                                 fg_color=CARD_BG, border_color=CARD_BORDER,
                                 text_color=TEXT_PRIMARY, font=("SF Pro Display", 12),
                                 height=28, corner_radius=6,
                                 placeholder_text="e.g. 61, 67, 77")
        svc_entry.pack(side="left", padx=8)

        def on_svc_change(*_):
            raw = svc_var.get()
            services = [s.strip() for s in raw.split(",") if s.strip()]
            stop["services"] = services

        svc_var.trace_add("write", on_svc_change)

    def _remove_bus_stop(self, stop):
        stops = self.config_data.get("bus_stops", [])
        self.config_data["bus_stops"] = [
            s for s in stops if s["stop_code"] != stop["stop_code"]]
        self._refresh_selected_bus_stops()
        self._on_bus_search()

    # ------------------------------------------------------------------
    # MRT Stations Tab
    # ------------------------------------------------------------------

    def _build_mrt_tab(self, parent):
        ctk.CTkLabel(parent, text="Search MRT Stations",
                     font=("SF Pro Display", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(12, 6))

        self.mrt_search_var = ctk.StringVar()
        self.mrt_search_var.trace_add("write", self._on_mrt_search)
        ctk.CTkEntry(parent, textvariable=self.mrt_search_var,
                     placeholder_text="Search by station name or line...",
                     fg_color=CARD_BG, border_color=CARD_BORDER, text_color=TEXT_PRIMARY,
                     font=("SF Pro Display", 13), height=38,
                     corner_radius=8).pack(fill="x", pady=(0, 8))

        self.mrt_results_frame = ctk.CTkScrollableFrame(
            parent, fg_color=CARD_BG, corner_radius=8, height=200)
        self.mrt_results_frame.pack(fill="x", pady=(0, 12))
        self._render_mrt_results([])

        ctk.CTkLabel(parent, text="Selected MRT Stations",
                     font=("SF Pro Display", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(4, 6))

        self.selected_mrt_frame = ctk.CTkScrollableFrame(
            parent, fg_color=CARD_BG, corner_radius=8, height=180)
        self.selected_mrt_frame.pack(fill="x")
        self._refresh_selected_mrt()

    def _on_mrt_search(self, *_):
        q = self.mrt_search_var.get().lower().strip()
        all_entries = get_all_stations_flat()
        if not q:
            self._render_mrt_results([])
            return
        results = [
            e for e in all_entries
            if q in e["station_name"].lower() or
               q in e["line_name"].lower() or
               q in e["station_code"].lower() or
               q in e["direction"].lower()
        ]
        self._render_mrt_results(results[:30])

    def _render_mrt_results(self, results):
        for w in self.mrt_results_frame.winfo_children():
            w.destroy()

        if not results:
            ctk.CTkLabel(self.mrt_results_frame,
                         text="Type to search for an MRT station",
                         font=("SF Pro Display", 12), text_color=TEXT_MUTED).pack(pady=12)
            return

        for entry in results:
            key = f"{entry['station_code']}|{entry['line']}|{entry['direction']}"
            already = any(
                f"{s['station_code']}|{s['line']}|{s['direction']}" == key
                for s in self.config_data.get("mrt_stations", [])
            )

            row = ctk.CTkFrame(self.mrt_results_frame, fg_color="#1e1e1e",
                               corner_radius=6, height=50)
            row.pack(fill="x", pady=2, padx=4)
            row.pack_propagate(False)

            # Line color pill
            pill = ctk.CTkLabel(row, text=entry["line"],
                                font=("SF Pro Display", 10, "bold"),
                                text_color="white",
                                fg_color=entry["line_color"],
                                corner_radius=4, width=36, height=20)
            pill.pack(side="left", padx=(10, 8), pady=4)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="y", pady=4)
            ctk.CTkLabel(info, text=entry["station_name"],
                         font=("SF Pro Display", 13, "bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w")
            ctk.CTkLabel(info, text=entry["direction"],
                         font=("SF Pro Display", 11), text_color=TEXT_MUTED).pack(anchor="w")

            btn_text = "Added" if already else "+ Add"
            btn_color = "#2a2a2a" if already else ACCENT
            ctk.CTkButton(row, text=btn_text, width=70, height=28,
                          fg_color=btn_color, hover_color=ACCENT_HOVER,
                          font=("SF Pro Display", 11), corner_radius=6,
                          state="disabled" if already else "normal",
                          command=lambda e=entry: self._add_mrt_station(e)
                          ).pack(side="right", padx=12)

    def _add_mrt_station(self, entry):
        item = {
            "station_code": entry["station_code"],
            "station_name": entry["station_name"],
            "line": entry["line"],
            "line_name": entry["line_name"],
            "line_color": entry["line_color"],
            "direction": entry["direction"]
        }
        stations = self.config_data.setdefault("mrt_stations", [])
        key = f"{item['station_code']}|{item['line']}|{item['direction']}"
        if not any(f"{s['station_code']}|{s['line']}|{s['direction']}" == key
                   for s in stations):
            stations.append(item)
        self._refresh_selected_mrt()
        self._on_mrt_search()

    def _refresh_selected_mrt(self):
        for w in self.selected_mrt_frame.winfo_children():
            w.destroy()

        stations = self.config_data.get("mrt_stations", [])
        if not stations:
            ctk.CTkLabel(self.selected_mrt_frame,
                         text="No MRT stations added yet",
                         font=("SF Pro Display", 12), text_color=TEXT_MUTED).pack(pady=12)
            return

        for station in stations:
            row = ctk.CTkFrame(self.selected_mrt_frame, fg_color="#1e1e1e",
                               corner_radius=6, height=50)
            row.pack(fill="x", pady=2, padx=4)
            row.pack_propagate(False)

            pill = ctk.CTkLabel(row, text=station["line"],
                                font=("SF Pro Display", 10, "bold"),
                                text_color="white",
                                fg_color=station["line_color"],
                                corner_radius=4, width=36, height=20)
            pill.pack(side="left", padx=(10, 8))

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="y", pady=6)
            ctk.CTkLabel(info, text=station["station_name"],
                         font=("SF Pro Display", 13, "bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w")
            ctk.CTkLabel(info, text=station["direction"],
                         font=("SF Pro Display", 11), text_color=TEXT_MUTED).pack(anchor="w")

            ctk.CTkButton(row, text="Remove", width=70, height=26,
                          fg_color="#3f1515", hover_color="#5a1f1f",
                          text_color=RED, font=("SF Pro Display", 11),
                          corner_radius=6,
                          command=lambda s=station: self._remove_mrt(s)
                          ).pack(side="right", padx=12)

    def _remove_mrt(self, station):
        key = f"{station['station_code']}|{station['line']}|{station['direction']}"
        self.config_data["mrt_stations"] = [
            s for s in self.config_data.get("mrt_stations", [])
            if f"{s['station_code']}|{s['line']}|{s['direction']}" != key
        ]
        self._refresh_selected_mrt()
        self._on_mrt_search()

    

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save(self):
        from utils.config_manager import save_api_key
        from api import bus as bus_module

        new_key = self.api_key_entry.get().strip()
        if new_key:
            save_api_key(new_key)
            bus_module.set_api_key(new_key)

        save_config(self.config_data)
        if self.on_save_callback:
            self.on_save_callback()
        self.destroy()

    # ------------------------------------------------------------------
    # toggle startup
    # ------------------------------------------------------------------

    def _toggle_startup(self):
        from utils.config_manager import set_startup
        set_startup(self.startup_var.get())
