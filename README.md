# HeartBeat
**Echodoppler Report Generation System**  
A system designed to simplify and speed up the creation of echodoppler reports for cardiologists.

---

## 🚀 Project Overview
**HeartBeat** is an application developed for cardiologists to efficiently create and manage echodoppler reports (laudos).  
The system supports **offline and online modes**, enabling doctors to work in any environment, with **synchronization** to the cloud when connected.

The primary goal is to reduce report generation time and streamline the workflow, integrating **DICOM image handling** directly into the report.

---

## ✅ MVP Features
- Fast creation of echodoppler reports (laudos)
- Patient and report management
- Upload and visualization of DICOM images
- PDF report generation (with embedded images and text)
- Sync system (local to cloud)  
- Local app runs offline, with automatic sync when internet is available  
- Simple executable for local use (Windows EXE)

---

## 🛠️ Technologies
- **Backend**: Django (Python)
- **Frontend**: Django Templates + HTMX + Bootstrap
- **Database**:  
  - **Local**: SQLite  
  - **Cloud**: PostgreSQL (via Railway/Render)
- **DICOM Handling**: pydicom + PIL
- **PDF Generation**: WeasyPrint (or xhtml2pdf)

---

## 🔧 Setup Instructions (Development)

### Requirements
- Python 3.10+
- PostgreSQL (if using cloud database)
- Virtualenv (recommended)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/felixmiranda1/heartbeat.git
   cd heartbeat
