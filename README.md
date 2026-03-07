# Emotion Journal

A desktop application that uses real-time AI facial recognition to track your emotional well-being, built as a personal Python learning project.

---

## About

Emotion Journal is a desktop app I built to learn Python through a real, end-to-end project. Rather than following tutorials, I challenged myself to build something practical from scratch: combining computer vision, a local database, data visualisation, and a modern GUI into a single application.

The app uses your webcam to detect your facial expression, identifies the dominant emotion using Deep Face, and logs it locally. Over time, it builds a personal emotional history you can explore through a calendar, a mood graph, and a smart insights panel.

---

##Features

| Feature | Description |
|---|---|
|  **Real-time emotion scan** | Uses your webcam + DeepFace to detect facial expressions. Analysis runs on a background thread so the camera feed stays smooth |
|  **Emotion calendar** | Monthly view showing your dominant emotion per day with colour coding. Click any day to see your journal note and tags |
| **Mood graph** | Line chart of your emotional trend over the last 30 days, built with Matplotlib embedded in the UI |
|  **Smart alerts & insights** | Personalised notifications: streak detection, time-of-day mood patterns, weekly comparisons, journaling reminders and more |
|  **Journal notes** | After each scan, write a note about your day. Stored alongside the emotion data |
|  **CSV export** | Export your full emotion history to CSV with a single click, compatible with Excel |
|  **Dark / Light theme** | Persistent theme preference saved to a local JSON config file |
|  **Configurable scan duration** | Adjust how long each scan lasts (5–30 seconds) from the settings panel |

---

## Tech Stack

| Technology | Role |
|---|---|
| **Python 3.12** | Core language |
| **CustomTkinter** | Modern desktop GUI framework |
| **DeepFace + TensorFlow** | Facial emotion recognition |
| **OpenCV** | Webcam capture and frame processing |
| **SQLite** | Local database for storing emotion logs and notes |
| **Matplotlib** | Mood graph embedded directly into the UI |
| **Threading** | Background emotion analysis to keep the UI non-blocking |
| **JSON** | Settings persistence and emotion tips configuration |

---

## Project Structure

```
Emotion-Journal/
│
├── main.py                     
│
├── analyzer/
│   └── EmotionAnalyzer.py      # Webcam capture + DeepFace analysis 
│
├── database/
│   └── DatabaseManager.py      # All SQLite operations
│
├── gui/
│   ├── AppInterface.py         # Main window, sidebar navigation, routing
│   ├── HomeView.py             # Dashboard with quick-access cards
│   ├── ScanView.py             # Scan flow: start - live feed - result - note
│   ├── CalendarView.py         # Monthly calendar with clickable day popups
│   ├── StatsView.py            # Mood graph with summary statistics
│   ├── AlertsView.py           # Personalised notifications and insights, based on the input
│   ├── SettingsView.py         # Theme, scan duration, data export, data clear
│   ├── SettingsManager.py      # JSON-backed settings persistence
│   └── constants.py            # Shared emotion emojis and colours
│
├── data/
│   ├── journal.db              # SQLite database (auto-created on first run)
│   └── emotion_tips.json       # Emotion-based tips loaded at runtime
│
├── settings.json               # User preferences (theme and scan duration)
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Webcam
- OpenCV
- DeepFace
- Tkinter

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/popam482/Emotion-Journal.git
cd Emotion-Journal

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python main.py
```

---

## How It Works

1. Click **Check-in** and press **Start Scan**
2. The app captures frames from your webcam every ~15 frames and runs DeepFace analysis on a background thread, so the live feed stays smooth throughout
3. After the scan, the dominant emotion is saved to the local SQLite database
4. You can optionally write a **journal note** before navigating away
5. Your emotion history is visible in the **Calendar**, the **Mood Graph**, and the **Alerts** panel

---

## What I Learned

This project was my main hands-on introduction to Python. Some of the key things I learned and applied:

- **OOP in Python** : every view and service is a class with clear responsibilities
- **Threading** : separating the DeepFace analysis from the UI event loop to prevent freezing
- **SQLite** : using `ALTER TABLE` at startup to add new columns without losing existing data
- **Matplotlib** : using `FigureCanvasTkAgg` to render charts inside a CustomTkinter frame
- **Data persistence** — both structured (SQLite) and unstructured (JSON config, JSON tips)
- **Error handling** — graceful fallbacks for missing files, empty data states, and camera errors

## License

This project is open source and available under the [MIT License](LICENSE).
