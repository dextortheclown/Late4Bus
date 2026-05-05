import customtkinter as ctk
import threading
import queue
import os
from datetime import datetime

from api.bus import get_bus_arrivals
from data.last_trains import get_last_train_info, LINE_COLORS
from utils.config_manager import load_config, save_widget_position, _save_widget_geometry

DARK_BG     = "#0f0f0f"
CARD_BG     = "#161616"
CARD_BORDER = "#222222"
ACCENT      = "#3b82f6"
TEXT_PRIMARY= "#f1f5f9"
TEXT_MUTED  = "#64748b"
TEXT_DIM    = "#374151"
GREEN       = "#4ade80"
YELLOW      = "#facc15"
RED         = "#f87171"
ORANGE      = "#fb923c"


def _load_color(minutes):
    if minutes is None:
        return TEXT_MUTED
    if minutes <= 1:
        return RED
    if minutes <= 3:
        return ORANGE
    if minutes <= 6:
        return YELLOW
    return GREEN


def _mins_label(minutes):
    if minutes is None:
        return "-"
    if minutes <= 0:
        return "Arr"
    return str(minutes)


class TransitWidget(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._drag_x = 0
        self._drag_y = 0
        self._data_queue = queue.Queue()
        self._refresh_job = None
        self._section_widgets = {}  # keyed by section id

        self._setup_window()
        self._build_ui()
        self._start_refresh_loop()
        self._process_queue()

    # ------------------------------------------------------------------
    # Window chrome
    # ------------------------------------------------------------------

    def _setup_window(self):
        ctk.set_appearance_mode("dark")
        self.overrideredirect(True)
        self.attributes("-alpha", 0.96)
        self.configure(fg_color=DARK_BG)
        self.title("Late4Bus")
        try:
            self.iconbitmap(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icon.ico"))
        except Exception:
            pass  # silently skip if icon file not found
        self.minsize(340, 120)

        config = load_config()
        x = config.get("widget", {}).get("x", 100)
        y = config.get("widget", {}).get("y", 100)
        w = config.get("widget", {}).get("width", 360)
        h = config.get("widget", {}).get("height", 400)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._drag_x = 0
        self._drag_y = 0
        self._resizing = False
        self._resize_edge = None
        self._resize_start_x = 0
        self._resize_start_y = 0
        self._resize_start_w = 0
        self._resize_start_h = 0
        self._resize_start_wx = 0
        self._resize_start_wy = 0

        self.bind("<ButtonPress-1>", self._on_mouse_press)
        self.bind("<B1-Motion>", self._on_mouse_drag)
        self.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.bind("<Motion>", self._on_mouse_move)

    RESIZE_MARGIN = 8  # px from edge that triggers resize

    def _get_edge(self, x, y):
        w = self.winfo_width()
        h = self.winfo_height()
        right  = x >= w - self.RESIZE_MARGIN
        bottom = y >= h - self.RESIZE_MARGIN
        left   = x <= self.RESIZE_MARGIN
        if bottom and right:
            return "se"
        if bottom and left:
            return "sw"
        if bottom:
            return "s"
        if right:
            return "e"
        if left:
            return "w"
        return None

    def _on_mouse_move(self, event):
        edge = self._get_edge(event.x, event.y)
        cursors = {
            "se": "size_nw_se", "sw": "size_ne_sw",
            "s": "size_ns", "e": "size_we", "w": "size_we"
        }
        self.configure(cursor=cursors.get(edge, "arrow"))

    def _on_mouse_press(self, event):
        edge = self._get_edge(event.x, event.y)
        if edge:
            self._resizing = True
            self._resize_edge = edge
            self._resize_start_x = event.x_root
            self._resize_start_y = event.y_root
            self._resize_start_w = self.winfo_width()
            self._resize_start_h = self.winfo_height()
            self._resize_start_wx = self.winfo_x()
            self._resize_start_wy = self.winfo_y()
        else:
            self._resizing = False
            self._drag_x = event.x_root - self.winfo_x()
            self._drag_y = event.y_root - self.winfo_y()

    def _on_mouse_drag(self, event):
        if self._resizing:
            dx = event.x_root - self._resize_start_x
            dy = event.y_root - self._resize_start_y
            edge = self._resize_edge
            new_w = self._resize_start_w
            new_h = self._resize_start_h
            new_x = self._resize_start_wx
            new_y = self._resize_start_wy

            if "e" in edge:
                new_w = max(340, self._resize_start_w + dx)
            if "w" in edge:
                new_w = max(340, self._resize_start_w - dx)
                new_x = self._resize_start_wx + (self._resize_start_w - new_w)
            if "s" in edge:
                new_h = max(120, self._resize_start_h + dy)

            self.geometry(f"{int(new_w)}x{int(new_h)}+{int(new_x)}+{int(new_y)}")
        else:
            x = event.x_root - self._drag_x
            y = event.y_root - self._drag_y
            self.geometry(f"+{x}+{y}")

    def _on_mouse_release(self, event):
        self._resizing = False
        self._resize_edge = None
        _save_widget_geometry(self.winfo_x(), self.winfo_y(),
                            self.winfo_width(), self.winfo_height())

    # ------------------------------------------------------------------
    # Base UI frame
    # ------------------------------------------------------------------

    def _build_ui(self):
        # Title bar (header row)
        self.header = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10, height=36)
        self.header.pack(fill="x", padx=1, pady=(1, 0))
        self.header.pack_propagate(False)

        ctk.CTkLabel(self.header, text="Transit",
                     font=("SF Pro Display", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=12)

        self.clock_label = ctk.CTkLabel(self.header, text="",
                                        font=("SF Pro Display", 12),
                                        text_color=TEXT_MUTED)
        self.clock_label.pack(side="left", padx=4)
        self._tick_clock()

        # Settings gear
        settings_btn = ctk.CTkButton(
            self.header, text="⚙", width=28, height=24,
            fg_color="transparent", hover_color="#1f1f1f",
            font=("SF Pro Display", 14), text_color=TEXT_MUTED,
            corner_radius=6, command=self._open_settings)
        settings_btn.pack(side="right", padx=4)

        # Close button
        close_btn = ctk.CTkButton(
            self.header, text="✕", width=28, height=24,
            fg_color="transparent", hover_color="#3f1515",
            font=("SF Pro Display", 12), text_color=TEXT_MUTED,
            corner_radius=6, command=self.destroy)
        close_btn.pack(side="right", padx=(4, 0))

        # Scrollable content area
        self.content = ctk.CTkScrollableFrame(
            self, fg_color=DARK_BG, corner_radius=0,
            scrollbar_button_color=CARD_BORDER,
            scrollbar_button_hover_color=ACCENT)
        self.content.pack(fill="both", expand=True, padx=1, pady=(0, 1))

        # Footer
        self.status_label = ctk.CTkLabel(
            self, text="Refreshing...",
            font=("SF Pro Display", 10), text_color=TEXT_DIM)
        self.status_label.pack(pady=(2, 4))

        self._render_content()

    def _tick_clock(self):
        self.clock_label.configure(text=datetime.now().strftime("%H:%M"))
        self.after(10000, self._tick_clock)

    # ------------------------------------------------------------------
    # Content rendering (dynamic sections)
    # ------------------------------------------------------------------

    def _render_content(self):
        for w in self.content.winfo_children():
            w.destroy()
        self._section_widgets.clear()

        config = load_config()
        bus_stops = config.get("bus_stops", [])
        mrt_stations = config.get("mrt_stations", [])

        if not bus_stops and not mrt_stations:
            self._render_empty_state()
            return

        if bus_stops:
            self._render_section_header("Bus Arrivals")
            for stop in bus_stops:
                self._render_bus_stop_skeleton(stop)

        if mrt_stations:
            self._render_section_header("Last Train")
            # Group stations by station_code + line
            from collections import OrderedDict
            groups = OrderedDict()
            for station in mrt_stations:
                group_key = f"{station['station_code']}|{station['line']}"
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(station)
            for group in groups.values():
                if len(group) > 1:
                    self._render_mrt_card_combined(group)
                else:
                    self._render_mrt_card(group[0])

    def _render_empty_state(self):
        frame = ctk.CTkFrame(self.content, fg_color=CARD_BG, corner_radius=8)
        frame.pack(fill="x", padx=8, pady=8)
        ctk.CTkLabel(frame,
                     text="No stops configured.\nClick ⚙ to get started.",
                     font=("SF Pro Display", 13), text_color=TEXT_MUTED,
                     justify="center").pack(pady=24)

    def _render_section_header(self, title):
        lbl = ctk.CTkLabel(self.content, text=title.upper(),
                           font=("SF Pro Display", 10, "bold"),
                           text_color=TEXT_DIM)
        lbl.pack(anchor="w", padx=14, pady=(10, 2))

    def _render_bus_stop_skeleton(self, stop):
        card = ctk.CTkFrame(self.content, fg_color=CARD_BG, corner_radius=10)
        card.pack(fill="x", padx=8, pady=4)

        # Clickable header using a frame with cursor change
        header_btn = ctk.CTkFrame(card, fg_color="transparent", cursor="hand2")
        header_btn.pack(fill="x")
        header_btn.bind("<Button-1>", lambda e, c=card, s=stop: self._toggle_bus_stop(c, s))

        header_inner = ctk.CTkFrame(header_btn, fg_color="transparent")
        header_inner.pack(fill="x", padx=12, pady=10)
        header_inner.bind("<Button-1>", lambda e, c=card, s=stop: self._toggle_bus_stop(c, s))

        code_badge = ctk.CTkLabel(
            header_inner, text=stop["stop_code"],
            font=("SF Pro Display", 10, "bold"),
            text_color="#1d4ed8", fg_color="#1e3a5f",
            corner_radius=4, width=44, height=18)
        code_badge.pack(side="left")
        code_badge.bind("<Button-1>", lambda e, c=card, s=stop: self._toggle_bus_stop(c, s))

        name_lbl = ctk.CTkLabel(
            header_inner, text=f"  {stop['stop_name']}",
            font=("SF Pro Display", 13, "bold"),
            text_color=TEXT_PRIMARY)
        name_lbl.pack(side="left")
        name_lbl.bind("<Button-1>", lambda e, c=card, s=stop: self._toggle_bus_stop(c, s))

        arrow = ctk.CTkLabel(
            header_inner, text="v",
            font=("SF Pro Display", 11),
            text_color=TEXT_MUTED)
        arrow.pack(side="right")
        arrow.bind("<Button-1>", lambda e, c=card, s=stop: self._toggle_bus_stop(c, s))

        road_lbl = ctk.CTkLabel(
            header_inner, text=stop["road"],
            font=("SF Pro Display", 11),
            text_color=TEXT_MUTED)
        road_lbl.pack(side="right", padx=(0, 4))
        road_lbl.bind("<Button-1>", lambda e, c=card, s=stop: self._toggle_bus_stop(c, s))

        # Collapsible body
        body = ctk.CTkFrame(card, fg_color="transparent")

        div = ctk.CTkFrame(body, fg_color=CARD_BORDER, height=1)
        div.pack(fill="x", padx=12, pady=(0, 4))

        svc_container = ctk.CTkFrame(body, fg_color="transparent")
        svc_container.pack(fill="x", padx=8, pady=(0, 8))

        loading = ctk.CTkLabel(
            svc_container, text="Fetching arrivals...",
            font=("SF Pro Display", 11), text_color=TEXT_MUTED)
        loading.pack(pady=8)

        key = f"bus_{stop['stop_code']}"
        self._section_widgets[key] = svc_container

        self._expanded = getattr(self, "_expanded", {})
        self._body_frames = getattr(self, "_body_frames", {})
        self.arrow_labels = getattr(self, "arrow_labels", {})
        self._expanded[stop["stop_code"]] = False
        self._body_frames[stop["stop_code"]] = body
        self.arrow_labels[stop["stop_code"]] = arrow


    def _toggle_bus_stop(self, card, stop):
        code = stop["stop_code"]
        self._expanded = getattr(self, "_expanded", {})
        self._body_frames = getattr(self, "_body_frames", {})
        self.arrow_labels = getattr(self, "arrow_labels", {})

        expanded = self._expanded.get(code, False)
        body = self._body_frames.get(code)
        arrow = self.arrow_labels.get(code)

        if expanded:
            body.pack_forget()
            self._expanded[code] = False
            if arrow:
                arrow.configure(text="v")
        else:
            body.pack(fill="x")
            self._expanded[code] = True
            if arrow:
                arrow.configure(text="^")

    def _render_mrt_card(self, station):
        card = ctk.CTkFrame(self.content, fg_color=CARD_BG, corner_radius=10)
        card.pack(fill="x", padx=8, pady=4)

        info = get_last_train_info(
            station["station_code"],
            station["line"],
            station["direction"]
        )

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=10)

        # Line pill
        line_color = station.get("line_color", "#888")
        ctk.CTkLabel(row, text=station["line"],
                     font=("SF Pro Display", 10, "bold"),
                     text_color="white",
                     fg_color=line_color,
                     corner_radius=4, width=34, height=20).pack(side="left")

        # Station + direction
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", padx=10)
        ctk.CTkLabel(info_frame, text=station["station_name"],
                     font=("SF Pro Display", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=station["direction"],
                     font=("SF Pro Display", 11),
                     text_color=TEXT_MUTED).pack(anchor="w")

        # Time display
        if info.get("error"):
            time_text = "N/A"
            mins_text = ""
            time_color = TEXT_MUTED
        else:
            mins = info.get("minutes_remaining")
            time_str = info.get("time_str", "")
            time_color = _load_color(mins)

            if mins is None:
                time_text = time_str
                mins_text = ""
            elif mins < 0:
                time_text = "Departed"
                mins_text = ""
                time_color = RED
            else:
                time_text = time_str
                mins_text = f"{mins} min away"

        time_frame = ctk.CTkFrame(row, fg_color="transparent")
        time_frame.pack(side="right")
        ctk.CTkLabel(time_frame, text=time_text,
                     font=("SF Pro Display", 18, "bold"),
                     text_color=time_color).pack(anchor="e")
        if mins_text:
            ctk.CTkLabel(time_frame, text=mins_text,
                         font=("SF Pro Display", 10),
                         text_color=TEXT_MUTED).pack(anchor="e")
    
    def _render_mrt_card_combined(self, stations):
        card = ctk.CTkFrame(self.content, fg_color=CARD_BG, corner_radius=10)
        card.pack(fill="x", padx=8, pady=4)

        # Shared header (station name + line pill)
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 4))

        line_color = stations[0].get("line_color", "#888")
        ctk.CTkLabel(header, text=stations[0]["line"],
                    font=("SF Pro Display", 10, "bold"),
                    text_color="white",
                    fg_color=line_color,
                    corner_radius=4, width=34, height=20).pack(side="left")

        ctk.CTkLabel(header, text=f"  {stations[0]['station_name']}",
                    font=("SF Pro Display", 13, "bold"),
                    text_color=TEXT_PRIMARY).pack(side="left")

        # Divider
        ctk.CTkFrame(card, fg_color=CARD_BORDER, height=1).pack(fill="x", padx=12, pady=(4, 0))

        # One row per direction
        for station in stations:
            info = get_last_train_info(
                station["station_code"],
                station["line"],
                station["direction"]
            )

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=6)

            # Direction label
            ctk.CTkLabel(row, text=station["direction"],
                        font=("SF Pro Display", 11),
                        text_color=TEXT_MUTED).pack(side="left")

            # Time on the right
            if info.get("error"):
                time_text = "N/A"
                mins_text = ""
                time_color = TEXT_MUTED
            else:
                mins = info.get("minutes_remaining")
                time_str = info.get("time_str", "")
                time_color = _load_color(mins)

                if mins is None:
                    time_text = time_str
                    mins_text = ""
                elif mins < 0:
                    time_text = "Departed"
                    mins_text = ""
                    time_color = RED
                else:
                    time_text = time_str
                    mins_text = f"{mins} min"

            time_frame = ctk.CTkFrame(row, fg_color="transparent")
            time_frame.pack(side="right")

            ctk.CTkLabel(time_frame, text=time_text,
                        font=("SF Pro Display", 16, "bold"),
                        text_color=time_color).pack(side="left", padx=(0, 6))

            if mins_text:
                ctk.CTkLabel(time_frame, text=mins_text,
                            font=("SF Pro Display", 10),
                            text_color=TEXT_MUTED).pack(side="left")

    def _fill_bus_stop_data(self, stop_code, data):
        key = f"bus_{stop_code}"
        container = self._section_widgets.get(key)
        if not container:
            return

        if data.get("error"):
            # Only rebuild on error state
            for w in container.winfo_children():
                w.destroy()
            ctk.CTkLabel(container, text=f"Error: {data['error']}",
                        font=("SF Pro Display", 11), text_color=RED).pack(pady=8)
            return

        services = data.get("services", [])
        if not services:
            for w in container.winfo_children():
                w.destroy()
            ctk.CTkLabel(container, text="No services found",
                        font=("SF Pro Display", 11), text_color=TEXT_MUTED).pack(pady=8)
            return

        # Track per-stop label references across refreshes
        self._bus_labels = getattr(self, "_bus_labels", {})
        existing = self._bus_labels.get(stop_code)

        # If services changed (different set of buses), do a full rebuild once
        incoming_services = [s["service_no"] for s in services]
        if existing and existing.get("services") == incoming_services:
            # Just update the time labels in place — no flicker
            for svc in services:
                svc_no = svc["service_no"]
                for i, bus in enumerate(svc["buses"][:3]):
                    mins = bus["minutes"]
                    col = _load_color(mins)
                    lbl_text = _mins_label(mins)
                    bus_type = bus.get("type_label", "")
                    label_key = f"{svc_no}_{i}_time"
                    type_key  = f"{svc_no}_{i}_type"
                    if label_key in existing:
                        existing[label_key].configure(text=f" {lbl_text}", text_color=col)
                    if type_key in existing:
                        existing[type_key].configure(text=bus_type)
            return

        # Full rebuild (first load or service list changed)
        for w in container.winfo_children():
            w.destroy()

        label_store = {"services": incoming_services}

        for svc in services:
            svc_row = ctk.CTkFrame(container, fg_color="transparent")
            svc_row.pack(fill="x", padx=4, pady=3)

            ctk.CTkLabel(svc_row, text=svc["service_no"],
                        font=("SF Pro Display", 20, "bold"),
                        text_color=TEXT_PRIMARY,
                        width=60, anchor="w").pack(side="left", padx=(6, 0))

            times_frame = ctk.CTkFrame(svc_row, fg_color="transparent")
            times_frame.pack(side="right", padx=6)

            for i, bus in enumerate(svc["buses"][:3]):
                mins = bus["minutes"]
                col = _load_color(mins)
                lbl = _mins_label(mins)
                bus_type = bus.get("type_label", "")

                cell = ctk.CTkFrame(times_frame, fg_color="transparent")
                cell.pack(side="left", padx=8)

                time_row = ctk.CTkFrame(cell, fg_color="transparent")
                time_row.pack(anchor="center")

                ctk.CTkLabel(time_row, text="♿",
                            font=("SF Pro Display", 11),
                            text_color=col).pack(side="left")

                time_lbl = ctk.CTkLabel(time_row, text=f" {lbl}",
                                        font=("SF Pro Display", 18, "bold"),
                                        text_color=col)
                time_lbl.pack(side="left")

                type_lbl = ctk.CTkLabel(cell, text=bus_type,
                                        font=("SF Pro Display", 10),
                                        text_color=TEXT_MUTED)
                type_lbl.pack(anchor="center")

                label_store[f"{svc['service_no']}_{i}_time"] = time_lbl
                label_store[f"{svc['service_no']}_{i}_type"] = type_lbl

            sep = ctk.CTkFrame(container, fg_color=CARD_BORDER, height=1)
            sep.pack(fill="x", padx=12, pady=1)

        children = container.winfo_children()
        if children and isinstance(children[-1], ctk.CTkFrame):
            children[-1].destroy()

        self._bus_labels[stop_code] = label_store

    # ------------------------------------------------------------------
    # Data fetching
    # ------------------------------------------------------------------

    def _start_refresh_loop(self):
        self._fetch_all_data()
        config = load_config()
        interval_ms = config.get("widget", {}).get("refresh_interval", 30) * 1000
        self._refresh_job = self.after(interval_ms, self._start_refresh_loop)

    def _fetch_all_data(self):
        config = load_config()
        bus_stops = config.get("bus_stops", [])

        def worker():
            for stop in bus_stops:
                services = stop.get("services", [])
                if services:
                    combined = {"error": None, "services": []}
                    for svc in services:
                        result = get_bus_arrivals(stop["stop_code"], svc)
                        if result.get("error"):
                            combined["error"] = result["error"]
                        else:
                            combined["services"].extend(result.get("services", []))
                else:
                    combined = get_bus_arrivals(stop["stop_code"])

                self._data_queue.put(("bus", stop["stop_code"], combined))

            now = datetime.now().strftime("%H:%M:%S")
            self._data_queue.put(("status", now, None))

        threading.Thread(target=worker, daemon=True).start()

    def _process_queue(self):
        try:
            while True:
                item = self._data_queue.get_nowait()
                kind = item[0]
                if kind == "bus":
                    _, stop_code, data = item
                    self._fill_bus_stop_data(stop_code, data)
                elif kind == "status":
                    _, ts, _ = item
                    self.status_label.configure(
                        text=f"Updated {ts}")
        except queue.Empty:
            pass
        self.after(500, self._process_queue)

    # ------------------------------------------------------------------
    # Window sizing
    # ------------------------------------------------------------------

    def _fit_window(self):
        self.update_idletasks()
        h = min(600, max(120, self.content.winfo_reqheight() + 80))
        w = 360
        self.geometry(f"{w}x{h}")

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def _open_settings(self):
        from ui.settings import SettingsWindow
        SettingsWindow(self, on_save_callback=self._on_settings_saved)

    def _on_settings_saved(self):
        self._render_content()
        if self._refresh_job:
            self.after_cancel(self._refresh_job)
        self._start_refresh_loop()
