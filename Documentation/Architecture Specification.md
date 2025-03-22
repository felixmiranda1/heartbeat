# Architecture Specification
Project Name: HeartBeat  
Date: March 21, 2025  
Version: 1.0  
Prepared by: Felix Miranda  

---

## Table of Contents
1. Introduction  
2. Architectural Representation  
3. Architectural Goals and Constraints  
4. Use-Case View  
5. Logical View  
6. Process View  
7. Development View  
8. Physical View  
9. Scenarios  
10. Glossary  

---

## 1. Introduction
The purpose of this document is to describe the software architecture of the HeartBeat system.  
HeartBeat is an echocardiogram report generation tool designed for cardiologists.  
It provides a fast, efficient workflow for managing patients, generating reports (laudos), handling DICOM images, and synchronizing data with a cloud backend.  
This architecture specification outlines the system structure, components, views, and interaction models for both local (offline) and cloud (online) environments.

---

## 2. Architectural Representation
This document follows the "4+1" architectural view model, including:
- Logical view
- Process view
- Development view
- Physical view
- Scenarios

---

## 3. Architectural Goals and Constraints
### Goals:
- Provide a **fast** and **intuitive** report generation system
- Support **offline functionality** with **automatic synchronization** to the cloud when online
- Integrate **DICOM image handling** within the reporting workflow
- Ensure **data integrity** and **security**, particularly for sensitive patient data
- Generate **professional PDF reports** with embedded images

### Constraints:
- No Django migrations; database schema is managed manually via pgAdmin
- Local application packaged as a Windows EXE
- Local database is SQLite; cloud database is PostgreSQL
- Sync for MVP is unidirectional: local ➜ cloud
- HTMX is used for frontend interaction, no SPA frameworks
- Offline/online switch must be **transparent** to the user

---

## 4. Use-Case View
### Actors:
- Cardiologist (Primary User)
- Cloud REST API (Data synchronization target)

### Use-Cases:
1. **Patient Management**
   - Create, update, delete patient records
   - Search patients by name, document ID, birth date
2. **Report (Laudo) Management**
   - Create and edit reports for patients
   - Insert predefined text snippets and free text
   - Attach DICOM images
3. **DICOM Image Handling**
   - Upload DICOM files
   - Convert and preview images
   - Store metadata
4. **PDF Report Generation**
   - Generate PDF with patient info, report content, images
   - Download or print the PDF
5. **Synchronization**
   - Send new/updated patients and reports to cloud
   - Monitor sync status
6. **Cloud Management (Future)**
   - Multi-user management
   - Access control and audit logging

---

## 5. Logical View
### Major Components:
- **Patient Management Module**  
  Handles CRUD operations for patient data.

- **Report Management Module**  
  Manages the creation, editing, and storage of echocardiogram reports.

- **DICOM Handling Module**  
  Manages the upload, conversion, and preview of DICOM images.

- **PDF Generation Module**  
  Produces PDF documents based on report content and attached images.

- **Synchronization Module**  
  Transfers data from the local application to the cloud backend via REST API.

### Packages and Relationships:

backend/
├── patients/
├── reports/
├── images/
├── sync_api/

### Key Classes:
- Patient  
- Report  
- Image  
- SyncService  
- PDFGenerator  

---

## 6. Process View
### Process Description:
- **Local Django Server Process (EXE):**  
  Runs Django locally, interacts with the user via browser (localhost).  
- **REST API Sync Process:**  
  Periodic task (or manual trigger) that posts new/updated data to the cloud backend.  
- **PDF Generation Process:**  
  On-demand PDF generation using WeasyPrint (or xhtml2pdf).  
- **DICOM Processing:**  
  Converts DICOM images to display-friendly formats (JPEG/PNG) during upload.

### Concurrency:
- Django’s default request/response cycle (local server)  
- Sync tasks handled in scheduled intervals (APScheduler or custom task)

---

## 7. Development View
### Module Structure:

heartbeat/
├── settings.py
├── urls.py
├── patients/        # Patient CRUD
├── reports/         # Report management
├── images/          # DICOM handling
├── sync_api/        # REST API endpoints for sync

### Tools and Technologies:
- Django 5.x  
- HTMX (Frontend Interactivity)  
- Python 3.10+  
- SQLite (local), PostgreSQL (cloud)  
- PyInstaller (for EXE packaging)  
- pydicom + Pillow (DICOM image processing)  
- WeasyPrint (PDF generation)

### Build and Packaging:
- Local EXE packaged with PyInstaller  
- Django settings split by environment (local/cloud)

---

## 8. Physical View
### Deployment Diagram:

[Local User Machine (Windows)]
- HeartBeat EXE
- SQLite DB
- Local Django Server (localhost:8000)
- Browser Interface (Chrome)

[Cloud Server (Railway/Render)]
- Django Backend
- PostgreSQL DB
- REST API (Sync endpoints)

### Physical Nodes:
- Local machine: runs standalone Django instance via EXE  
- Cloud: Django app deployed on Railway/Render with PostgreSQL backend

---

## 9. Scenarios
### Scenario 1: Create and Generate Report Offline
1. Cardiologist opens HeartBeat EXE  
2. Creates/selects a patient  
3. Uploads DICOM images  
4. Fills report content  
5. Generates PDF report  
6. Data is stored locally (SQLite)  
7. When online, sync pushes data to the cloud automatically

### Scenario 2: View Reports in the Cloud
1. Cardiologist accesses cloud system via browser (future feature)  
2. Logs in and views previously synced reports  
3. Downloads PDF reports as needed

---

## 10. Glossary
| Term          | Definition                                    |
|---------------|-----------------------------------------------|
| DICOM         | Digital Imaging and Communications in Medicine|
| Laudo         | Medical report (Echocardiogram in this context)|
| HTMX          | Frontend library for dynamic HTML without SPA |
| EXE           | Executable file format for Windows            |
| REST API      | Representational State Transfer API           |

---