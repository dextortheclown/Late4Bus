from datetime import datetime

# ------------------------------------------------------------
# Last train timings sourced from SMRT / SBS Transit timetables
# Format: "HH:MM" in 24-hour time
# Two schedule types: "weekday" and "weekend"
# Public holidays follow the weekend schedule
# ------------------------------------------------------------

PUBLIC_HOLIDAYS = [
    "2025-01-01",  # New Year's Day
    "2025-01-29",  # Chinese New Year Day 1
    "2025-01-30",  # Chinese New Year Day 2
    "2025-04-18",  # Good Friday
    "2025-05-01",  # Labour Day
    "2025-05-12",  # Vesak Day
    "2025-06-06",  # Hari Raya Haji
    "2025-08-09",  # National Day
    "2025-10-20",  # Deepavali
    "2025-12-25",  # Christmas
    "2026-01-01",  # New Year's Day
]


def get_schedule_type() -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    if today in PUBLIC_HOLIDAYS:
        return "weekend"
    return "weekend" if datetime.now().weekday() >= 5 else "weekday"


# ------------------------------------------------------------
# MRT Station Data
# Each station has one or more lines, each line has directions,
# each direction has weekday and weekend last train times.
# ------------------------------------------------------------

MRT_STATIONS = {
    # ========================
    # NORTH SOUTH LINE (NSL)
    # ========================
    "NS1": {
        "name": "Jurong East",
        "lines": {
            "NSL": {
                "directions": {
                    "Towards Marina South Pier": {
                        "weekday": "23:11",
                        "weekend": "23:41"
                    },
                    "Towards Woodlands": {
                        "weekday": "23:17",
                        "weekend": "23:47"
                    }
                }
            }
        }
    },
    "NS4": {
        "name": "Choa Chu Kang",
        "lines": {
            "NSL": {
                "directions": {
                    "Towards Marina South Pier": {
                        "weekday": "23:22",
                        "weekend": "23:52"
                    },
                    "Towards Woodlands": {
                        "weekday": "23:06",
                        "weekend": "23:36"
                    }
                }
            }
        }
    },
    "NS8": {
        "name": "Braddell",
        "lines": {
            "NSL": {
                "directions": {
                    "Towards Marina South Pier": {
                        "weekday": "23:38",
                        "weekend": "00:08"
                    },
                    "Towards Woodlands": {
                        "weekday": "23:18",
                        "weekend": "23:48"
                    }
                }
            }
        }
    },
    "NS17": {
        "name": "Bishan",
        "lines": {
            "NSL": {
                "directions": {
                    "Towards Marina South Pier": {
                        "weekday": "23:38",
                        "weekend": "00:08"
                    },
                    "Towards Woodlands": {
                        "weekday": "23:15",
                        "weekend": "23:45"
                    }
                }
            }
        }
    },
    "NS21": {
        "name": "Newton",
        "lines": {
            "NSL": {
                "directions": {
                    "Towards Marina South Pier": {
                        "weekday": "23:48",
                        "weekend": "00:18"
                    },
                    "Towards Woodlands": {
                        "weekday": "23:07",
                        "weekend": "23:37"
                    }
                }
            }
        }
    },
    "NS25": {
        "name": "City Hall",
        "lines": {
            "NSL": {
                "directions": {
                    "Towards Marina South Pier": {
                        "weekday": "23:58",
                        "weekend": "00:28"
                    },
                    "Towards Woodlands": {
                        "weekday": "23:00",
                        "weekend": "23:30"
                    }
                }
            }
        }
    },
    "NS27": {
        "name": "Marina Bay",
        "lines": {
            "NSL": {
                "directions": {
                    "Towards Marina South Pier": {
                        "weekday": "00:02",
                        "weekend": "00:32"
                    },
                    "Towards Woodlands": {
                        "weekday": "22:57",
                        "weekend": "23:27"
                    }
                }
            }
        }
    },

    # ========================
    # EAST WEST LINE (EWL)
    # ========================
    "EW1": {
        "name": "Pasir Ris",
        "lines": {
            "EWL": {
                "directions": {
                    "Towards Tuas Link": {
                        "weekday": "23:18",
                        "weekend": "23:18"
                    }
                }
            }
        }
    },
    "EW8": {
        "name": "Paya Lebar",
        "lines": {
            "EWL": {
                "directions": {
                    "Towards Pasir Ris": {
                        "weekday": "23:52",
                        "weekend": "00:12"
                    },
                    "Towards Tuas Link": {
                        "weekday": "23:26",
                        "weekend": "23:26"
                    }
                }
            }
        }
    },
    "EW13": {
        "name": "City Hall",
        "lines": {
            "EWL": {
                "directions": {
                    "Towards Pasir Ris": {
                        "weekday": "00:02",
                        "weekend": "00:22"
                    },
                    "Towards Tuas Link": {
                        "weekday": "23:16",
                        "weekend": "23:16"
                    }
                }
            }
        }
    },
    "EW23": {
        "name": "Clementi",
        "lines": {
            "EWL": {
                "directions": {
                    "Towards Pasir Ris": {
                        "weekday": "00:07",
                        "weekend": "00:27"
                    },
                    "Towards Tuas Link": {
                        "weekday": "23:06",
                        "weekend": "23:06"
                    }
                }
            }
        }
    },
    "EW24": {
        "name": "Jurong East",
        "lines": {
            "EWL": {
                "directions": {
                    "Towards Pasir Ris": {
                        "weekday": "00:09",
                        "weekend": "00:29"
                    },
                    "Towards Tuas Link": {
                        "weekday": "23:04",
                        "weekend": "23:38"
                    }
                }
            }
        }
    },
    "EW27": {
        "name": "Boon Lay",
        "lines": {
            "EWL": {
                "directions": {
                    "Towards Pasir Ris": {
                        "weekday": "00:14",
                        "weekend": "00:34"
                    },
                    "Towards Tuas Link": {
                        "weekday": "22:59",
                        "weekend": "23:33"
                    }
                }
            }
        }
    },

    # ========================
    # CIRCLE LINE (CCL)
    # ========================
    "CC1": {
        "name": "Dhoby Ghaut",
        "lines": {
            "CCL": {
                "directions": {
                    "Towards HarbourFront (via Promenade)": {
                        "weekday": "23:18",
                        "weekend": "23:48"
                    },
                    "Towards Marinebay (Loop)": {
                        "weekday": "23:28",
                        "weekend": "23:58"
                    }
                }
            }
        }
    },
    "CC10": {
        "name": "Bishan",
        "lines": {
            "CCL": {
                "directions": {
                    "Towards HarbourFront (via Promenade)": {
                        "weekday": "23:43",
                        "weekend": "00:03"
                    },
                    "Towards Dhoby Ghaut": {
                        "weekday": "23:33",
                        "weekend": "23:53"
                    }
                }
            }
        }
    },
    "CC17": {
        "name": "Buona Vista",
        "lines": {
            "CCL": {
                "directions": {
                    "Towards HarbourFront (via Promenade)": {
                        "weekday": "23:55",
                        "weekend": "00:15"
                    },
                    "Towards Dhoby Ghaut": {
                        "weekday": "23:23",
                        "weekend": "23:43"
                    }
                }
            }
        }
    },
    "CC29": {
        "name": "HarbourFront",
        "lines": {
            "CCL": {
                "directions": {
                    "Towards Dhoby Ghaut (via Promenade)": {
                        "weekday": "23:43",
                        "weekend": "00:13"
                    }
                }
            }
        }
    },

    # ========================
    # DOWNTOWN LINE (DTL)
    # ========================
    "DT1": {
        "name": "Bukit Panjang",
        "lines": {
            "DTL": {
                "directions": {
                    "Towards Expo": {
                        "weekday": "23:15",
                        "weekend": "23:45"
                    }
                }
            }
        }
    },
    "DT5":{
        "name": "Beauty World",
        "lines": {
            "DTL": {
                "directions": {
                    "Towards Expo": {
                        "weekday": "23:42",
                        "weekend": "23:42"
                    },
                    "Towards Bukit Panjang": {
                        "weekday": "23:42",
                        "weekend": "23:42"
                    }
                }
            }
        }
    },
    "DT9": {
        "name": "Newton",
        "lines": {
            "DTL": {
                "directions": {
                    "Towards Expo": {
                        "weekday": "23:39",
                        "weekend": "00:09"
                    },
                    "Towards Bukit Panjang": {
                        "weekday": "23:24",
                        "weekend": "23:54"
                    }
                }
            }
        }
    },
    "DT14": {
        "name": "Bugis",
        "lines": {
            "DTL": {
                "directions": {
                    "Towards Expo": {
                        "weekday": "23:49",
                        "weekend": "00:19"
                    },
                    "Towards Bukit Panjang": {
                        "weekday": "23:14",
                        "weekend": "23:44"
                    }
                }
            }
        }
    },
    "DT35": {
        "name": "Expo",
        "lines": {
            "DTL": {
                "directions": {
                    "Towards Bukit Panjang": {
                        "weekday": "23:55",
                        "weekend": "00:25"
                    }
                }
            }
        }
    },

    # ========================
    # THOMSON EAST COAST LINE (TEL)
    # ========================
    "TE1": {
        "name": "Woodlands North",
        "lines": {
            "TEL": {
                "directions": {
                    "Towards Woodlands South": {
                        "weekday": "23:11",
                        "weekend": "23:41"
                    }
                }
            }
        }
    },
    "TE14": {
        "name": "Stevens",
        "lines": {
            "TEL": {
                "directions": {
                    "Towards Woodlands North": {
                        "weekday": "23:10",
                        "weekend": "23:40"
                    },
                    "Towards Woodlands South": {
                        "weekday": "23:28",
                        "weekend": "23:58"
                    }
                }
            }
        }
    },
    "TE20": {
        "name": "Gardens by the Bay",
        "lines": {
            "TEL": {
                "directions": {
                    "Towards Woodlands North": {
                        "weekday": "23:44",
                        "weekend": "00:14"
                    },
                    "Towards Woodlands South": {
                        "weekday": "23:10",
                        "weekend": "23:40"
                    }
                }
            }
        }
    },

    # ========================
    # NORTH EAST LINE (NEL)
    # ========================
    "NE1": {
        "name": "HarbourFront",
        "lines": {
            "NEL": {
                "directions": {
                    "Towards Punggol": {
                        "weekday": "23:13",
                        "weekend": "23:43"
                    }
                }
            }
        }
    },
    "NE6": {
        "name": "Dhoby Ghaut",
        "lines": {
            "NEL": {
                "directions": {
                    "Towards Punggol": {
                        "weekday": "23:28",
                        "weekend": "23:58"
                    },
                    "Towards HarbourFront": {
                        "weekday": "23:21",
                        "weekend": "23:51"
                    }
                }
            }
        }
    },
    "NE17": {
        "name": "Punggol",
        "lines": {
            "NEL": {
                "directions": {
                    "Towards HarbourFront": {
                        "weekday": "23:48",
                        "weekend": "00:18"
                    }
                }
            }
        }
    },
}

LINE_COLORS = {
    "NSL": "#e2231a",
    "EWL": "#009645",
    "CCL": "#f9a01b",
    "DTL": "#005ec4",
    "TEL": "#9d5b25",
    "NEL": "#9900aa",
}

LINE_NAMES = {
    "NSL": "North South Line",
    "EWL": "East West Line",
    "CCL": "Circle Line",
    "DTL": "Downtown Line",
    "TEL": "Thomson-East Coast Line",
    "NEL": "North East Line",
}


def get_last_train_info(station_code: str, line: str, direction: str) -> dict:
    """
    Returns last train time string and minutes remaining.
    """
    station = MRT_STATIONS.get(station_code)
    if not station:
        return {"error": "Station not found"}

    line_data = station.get("lines", {}).get(line)
    if not line_data:
        return {"error": "Line not found for station"}

    dir_data = line_data.get("directions", {}).get(direction)
    if not dir_data:
        return {"error": "Direction not found"}

    schedule = get_schedule_type()
    time_str = dir_data.get(schedule, "")

    now = datetime.now()
    try:
        h, m = map(int, time_str.split(":"))
        last = now.replace(hour=h % 24, minute=m, second=0, microsecond=0)
        # handle post-midnight times (e.g. 00:28 means next day)
        if h >= 24 or (h == 0 and now.hour > 1):
            from datetime import timedelta
            last += timedelta(days=1)
            last = last.replace(hour=h % 24, minute=m)
        mins = int((last - now).total_seconds() / 60)
    except (ValueError, AttributeError):
        mins = None

    return {
        "error": None,
        "time_str": time_str,
        "schedule_type": schedule,
        "minutes_remaining": mins,
        "direction": direction,
        "line": line,
        "line_name": LINE_NAMES.get(line, line),
        "line_color": LINE_COLORS.get(line, "#888888"),
        "station_name": station["name"]
    }


def get_all_stations_flat() -> list:
    """
    Returns a flat list of (station_code, station_name, line, direction)
    tuples for use in the settings search UI.
    """
    results = []
    for code, station in MRT_STATIONS.items():
        for line, line_data in station.get("lines", {}).items():
            for direction in line_data.get("directions", {}).keys():
                results.append({
                    "station_code": code,
                    "station_name": station["name"],
                    "line": line,
                    "line_name": LINE_NAMES.get(line, line),
                    "line_color": LINE_COLORS.get(line, "#888"),
                    "direction": direction
                })
    return results
