# Late4Bus

Desktop application for checking bus timings and last train details. Made for those with friends who depend on you for the bus timings and cant be bothered to check it themselves. A lightweight, borderless Windows desktop widget that displays real-time Singapore bus arrival timings and MRT last train information — sourced directly from LTA DataMall.

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.0.2-brightgreen)

---

## Features

- Real-time bus arrival timings from LTA DataMall, auto-refreshed every 30 seconds
- MRT last train countdowns across all 6 lines (NSL, EWL, CCL, DTL, TEL, NEL)
- Weekday and weekend MRT schedules handled automatically, including public holidays
- Search and select any of 5000+ Singapore bus stops by name, code, or road
- Debounced live search for smooth, responsive stop filtering
- Filter specific bus services per stop, or show all services
- MRT directions at the same station grouped into a single combined card
- Collapsible dropdown cards per bus stop
- Colour-coded arrival times based on urgency
- Borderless, frameless widget that sits cleanly on your desktop
- Draggable and resizable, with position and size remembered across sessions
- Optional auto-launch on Windows startup, toggled from within the app
- Your API key is stored locally in AppData and never shared

---

## Screenshots

> Add your screenshots here.

---

## Windows Security Warning

When launching Late4Bus for the first time, Windows may show a SmartScreen warning saying **"Windows protected your PC"**. This happens because the app is not yet code-signed by a certificate authority.

To proceed:
1. Click **More info**
2. Click **Run anyway**

This is safe to do. The full source code is available in this repository for anyone to inspect.

---

## Getting Your LTA DataMall API Key

Late4Bus requires a free personal API key from LTA DataMall to fetch live bus arrival data.

1. Go to [https://datamall.lta.gov.sg](https://datamall.lta.gov.sg)
2. Click **Request for API Access** in the top navigation
3. Fill in the registration form and select **Individual** as the account type
4. Submit and wait for a confirmation email (usually within 1 working day)
5. Your key will be in the email under **API Account Key**
6. Copy the key — you will paste it into the app on first launch

Your API key is saved locally to your AppData folder and is never transmitted anywhere other than directly to LTA's own servers.

---

## Installation

### Option A — Download the installer (Recommended)

1. Go to the [Releases](../../releases) page
2. Download `Late4Bus_Setup_v1.0.0.exe`
3. Run the installer and follow the prompts
4. Launch Late4Bus from your desktop or Start Menu

### Option B — Run from source

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/late4bus.git
cd late4bus
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the app**

```bash
python main.py
```

---

## First Launch

1. Enter your LTA DataMall API key on the onboarding screen
2. Click **Verify and Continue** — the app will validate your key live
3. In the **Bus Stops** tab, search for your stop by name, code, or road and click Add
4. Optionally type specific service numbers to filter (leave blank to show all services)
5. In the **MRT Stations** tab, search for your station and add the directions you need
6. Click **Save and Apply**

---

## Usage

**Daily use**
- The widget auto-refreshes bus timings every 30 seconds
- Click any bus stop card header to expand or collapse its arrivals
- Drag the widget by its top bar to reposition it anywhere on screen
- Resize by dragging the bottom or side edges
- Click the gear icon to open settings at any time
- Click X to close the widget

**Arrival time colours**

| Colour | Meaning |
|--------|---------|
| Green | More than 6 minutes away |
| Yellow | 3 to 6 minutes away |
| Orange | 1 to 3 minutes away |
| Red | Arriving or less than 1 minute |

**Auto-startup**

To have Late4Bus launch automatically when Windows starts, open Settings via the gear icon and toggle **Launch at startup**. Toggle it off the same way to disable it.

---

## Project Structure

```
late4bus/
├── main.py                  Entry point
├── Late4Bus.spec            PyInstaller build spec
├── installer.iss            Inno Setup installer script
├── rebuild.bat              Build helper script
├── requirements.txt         Python dependencies
├── icon.ico                 App icon
├── api/
│   └── bus.py               LTA DataMall v3 BusArrival API client
├── data/
│   └── last_trains.py       Hardcoded MRT last train schedules
├── ui/
│   ├── widget.py            Main borderless widget window
│   ├── settings.py          Settings screen
│   └── onboarding.py        First-launch API key setup
└── utils/
    └── config_manager.py    Config read/write, startup registry helper
```

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Core language |
| customtkinter | Modern dark-themed UI framework |
| requests | HTTP client for LTA DataMall API calls |
| certifi | SSL certificate bundle for packaged exe |
| Pillow | Image handling |
| PyInstaller | Packaging as a standalone Windows exe |
| Inno Setup | Windows installer creation |
| LTA DataMall v3 API | Real-time bus arrival data |

---

## Building from Source

**1. Install PyInstaller**

```bash
pip install pyinstaller
```

**2. First build**

```bash
pyinstaller Late4Bus.spec
```

Output: `dist/Late4Bus.exe`

**3. Rebuild after changes**

Run `rebuild.bat` from the project root, or manually:

```bat
rd /s /q build
rd /s /q dist
pyinstaller Late4Bus.spec
```

**4. Build the installer**

Open `installer.iss` in [Inno Setup](https://jrsoftware.org/isinfo.php) and click **Build > Compile**. The installer will be output to the `dist` folder.

---

## Configuration

User configuration is stored at:

```
C:\Users\<YourName>\AppData\Roaming\Late4Bus\config.json
```

This file is created automatically on first save. Delete it to reset the app to a completely fresh state including re-running onboarding.

---

## Updating MRT Last Train Timings

MRT last train timings are hardcoded in `data/last_trains.py` based on official SMRT and SBS Transit published timetables. If timings are revised, update the relevant entries in that file and rebuild.

Public holidays are listed under `PUBLIC_HOLIDAYS` in the same file. Update this list annually to ensure correct weekday and weekend schedule selection.

---

## Known Limitations

- MRT last train timings require a manual update when SMRT or SBS Transit revises timetables
- The public holiday list must be updated annually
- The widget cannot be resized from the top edge
- LTA DataMall API usage is subject to LTA's own rate limits and terms of service
- Auto-startup toggle only works when running as a packaged exe, not from source

---

## Roadmap

- [x] Real-time bus arrivals with load and bus type indicators
- [x] MRT last train countdowns with weekday/weekend schedule
- [x] Fully interactive stop and station selection in-app
- [x] Collapsible bus stop cards
- [x] Combined MRT direction cards per station
- [x] Smooth debounced search
- [x] Resizable and draggable widget with saved position and size
- [x] Auto-launch at Windows startup toggle
- [x] Standalone exe via PyInstaller
- [ ] System tray icon with minimise to tray
- [ ] Arrival alert when a bus is under 2 minutes away
- [ ] Automatic public holiday detection via API
- [ ] macOS support
- [ ] Custom accent colour picker
- [ ] Drag-to-reorder stops and stations in settings

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [LTA DataMall](https://datamall.lta.gov.sg) for providing the public transport API
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) by Tom Schimansky
- [Inno Setup](https://jrsoftware.org/isinfo.php) by Jordan Russell
