# 🎓 AI Attendance System

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Face%20Recognition-green?style=for-the-badge&logo=opencv)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

> An intelligent attendance management system that uses **AI-powered face recognition** and **phone camera integration** to automate and simplify attendance tracking.

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)
- [Contributors](#-contributors)

---

## 🧠 About the Project

The **AI Attendance System** is a smart, contactless attendance solution built for classrooms, offices, or any organization. It leverages real-time **face recognition** through a **phone camera** to automatically detect and mark attendance — eliminating the need for manual roll calls or ID cards.

---

## ✨ Features

- 📸 **Real-time Face Recognition** — Detects and identifies faces instantly
- 📱 **Phone Camera Support** — Use your phone as a wireless camera
- 🧾 **Automatic Attendance Logging** — Records attendance with timestamp
- 👤 **Multi-face Detection** — Recognizes multiple people simultaneously
- 🔒 **Secure & Contactless** — No physical interaction required
- 📊 **Attendance Records** — Stores data for future reference

---

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| OpenCV | Face detection & recognition |
| face_recognition | AI face matching library |
| Streamlit | Web-based UI |
| Twilio | SMS / notification support |
| Phone Camera (IP Webcam) | Remote camera streaming |

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)
- A smartphone with **IP Webcam** app installed (for phone camera)

---

## 📦 Installation

**1. Clone the repository**
```bash
git clone https://github.com/jayraval30/AI-Attendance-System.git
cd AI-Attendance-System
```

**2. Install required dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the application**
```bash
streamlit run app.py
```

---

## 📱 Usage

### Using Phone Camera
1. Install **IP Webcam** app on your Android phone
2. Start the server in the app
3. Copy the IP address shown (e.g., `http://192.168.x.x:8080`)
4. Paste it in the app when prompted

### Taking Attendance
1. Launch the app with `streamlit run app.py`
2. Register faces by uploading photos or using live camera
3. Start attendance — the system will auto-detect and mark present students/employees
4. View and export the attendance log

---

## 📁 Project Structure

```
AI-Attendance-System/
│
├── assets/              # Images and static files
├── pages/               # Streamlit multi-page components
├── app.py               # Main application entry point
├── face_rec.py          # Face recognition logic
├── phone_camera.py      # Phone camera stream handler
├── test_phone_cam.py    # Camera testing script
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```

---

## 📸 Screenshots

> Screenshots and demo coming soon...

---

## 👨‍💻 Contributors

| Name | Role |
|---|---|
| **Jay Raval** | Developer |

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use and modify it.

---

<p align="center">Made with ❤️ by Jay Raval</p>