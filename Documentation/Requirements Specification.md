# ✅ HeartBeat - Requirements Documentation

## A1: Goals, Business Context, and Environment

### 🎯 Goals
- Provide a tool to **streamline the creation of echocardiogram (ecodoppler) reports**.
- Reduce cardiologists' reporting time by **at least 50%**, ensuring speed, accuracy, and security.
- Facilitate **DICOM image attachment** and **professional PDF generation** with embedded images.
- Ensure **seamless offline functionality**, with **automatic data synchronization** to the cloud when internet is available.

---

### 🌐 Business Context
- Designed for **cardiologists like Dr. Otavio**, who handle **high volumes of echocardiogram reports daily**.
- Aims to **solve the inefficiencies** and **time constraints** in traditional echocardiogram report generation.
- Allows cardiologists to **work offline**, maintaining productivity even in **low connectivity environments**.
- Provides **cloud backup and synchronization**, ensuring data security and access from multiple locations.

---

### 🖥️ Environment
- **Local application** packaged as a **Windows executable (EXE)** using PyInstaller.
- Runs a **Django server** locally with a **SQLite database**, accessible through a web browser (HTMX + Django Templates).
- **Cloud backend** with **Django + PostgreSQL**, integrated via **RESTful API** and **JWT authentication**.
- **Offline-first approach**, with **automatic synchronization** to the cloud when connected.

## A2: Actors and User Stories

### 🎭 Actors Overview

The purpose of this section is to **identify the system's key actors**, describe their roles, and **document user stories** for each actor. This ensures a clear understanding of **how users interact** with HeartBeat and their **responsibilities within the system**.

---

### 1. Actors

| Actor         | Description                                                                                 |
|---------------|---------------------------------------------------------------------------------------------|
| **Cardiologist** | Primary user of the system. Responsible for **creating reports**, **managing patients**, **uploading DICOM images**, and **generating PDFs**. |
| **Clinic Admin** | (Optional) User responsible for **managing multiple cardiologists** within the clinic, overseeing reports and data synchronization. |
| **System Admin** | Responsible for **system configuration**, **user management**, and **resolving technical issues** (mostly cloud/backend-related). |
| **Cloud Sync Service** | Automated system actor responsible for **synchronizing local data** with the **cloud backend** and ensuring **data integrity**. |

---

### 2. User Stories

| Identifier | Name                      | Priority | Actor          | Description                                                                                          |
|------------|---------------------------|----------|----------------|------------------------------------------------------------------------------------------------------|
| US01       | Patient Registration      | High     | Cardiologist   | As a cardiologist, I want to register a new patient so that I can generate an echocardiogram report. |
| US02       | Create Report             | High     | Cardiologist   | As a cardiologist, I want to create an echocardiogram report so I can document the patient's exam.   |
| US03       | Upload DICOM Image        | High     | Cardiologist   | As a cardiologist, I want to upload DICOM images so that they can be embedded into the report.       |
| US04       | Generate PDF Report       | High     | Cardiologist   | As a cardiologist, I want to generate a PDF report with images so I can share it with the patient or clinic. |
| US05       | Work Offline              | High     | Cardiologist   | As a cardiologist, I want to work offline so I can create reports without an internet connection.    |
| US06       | Automatic Cloud Sync      | High     | Cloud Sync Service | As the sync service, I need to synchronize data to the cloud automatically when an internet connection is available. |
| US07       | View Patient History      | Medium   | Cardiologist   | As a cardiologist, I want to view previous reports and patient history to support ongoing treatment. |
| US08       | Edit Report               | Medium   | Cardiologist   | As a cardiologist, I want to edit reports before exporting them to correct any mistakes.             |
| US09       | Manage User Access        | Low      | System Admin   | As a system admin, I want to manage user access to ensure only authorized personnel can use the system. |
| US10       | View Sync Status          | Medium   | Clinic Admin   | As a clinic admin, I want to view the synchronization status of each workstation to ensure data is backed up. |
| US11       | Reset Password            | Low      | System Admin   | As a system admin, I want to reset user passwords in case they forget their credentials.             |

---

### 3. Supplementary Requirements

#### Business Rules

| Identifier | Name                        | Description                                                                                   |
|------------|-----------------------------|-----------------------------------------------------------------------------------------------|
| BR01       | Report Ownership            | Cardiologists can only access and modify reports they have created unless authorized otherwise. |
| BR02       | Mandatory Fields            | Patient profiles must include required fields: Name, DOB, Gender, and ID number.              |
| BR03       | Sync Timing Rules           | Synchronization should occur automatically every 5 minutes when an internet connection is detected. |

---

#### Technical Requirements

| Identifier | Name                        | Description                                                                                   |
|------------|-----------------------------|-----------------------------------------------------------------------------------------------|
| TR01       | DICOM Compatibility         | The system must support standard DICOM files for upload and conversion.                       |
| TR02       | Secure Data Storage         | All patient data must be encrypted at rest (SQLite locally, PostgreSQL in the cloud).         |
| TR03       | Sync Conflict Resolution    | The system must handle conflicts during synchronization gracefully, prioritizing the latest modification. |
| TR04       | Offline Availability        | The entire core application must be fully functional offline, including PDF generation.       |

---

#### Restrictions

| Identifier | Name                        | Description                                                                                   |
|------------|-----------------------------|-----------------------------------------------------------------------------------------------|
| RS01       | Operating System Limitation | The local application must run on **Windows 10 or higher**.                                   |
| RS02       | File Size Limitations       | Uploaded DICOM images must not exceed **100MB per file**.                                     |
| RS03       | Browser Compatibility       | The web interface must support **Chrome and Edge**, latest two versions.                      |

## A3: Information Architecture

### 📝 Brief Presentation of Goals
This section defines the **structural design** of the HeartBeat application, illustrating the **relationships between different components** and providing **visual representations** to clarify **navigation and layout**.  
The goal is to ensure that both **developers and stakeholders** have a shared understanding of the system’s **navigation flow and structure**.

---

## 1. Sitemap

### 🗺️ Description
The sitemap outlines the **hierarchical structure** of the HeartBeat application, displaying **how users navigate** between core pages and features.

### Sitemap Diagram  
(Placeholder for future diagram)  
➡️ We can add this later with a **visual tool** (e.g., diagrams.net or Figma).

---

### Key Pages & Sections:

- **Home Page (Dashboard)**  
  - Displays quick actions and system overview (e.g., recent reports, sync status).
  
- **Authentication Pages**
  - **Sign In**: Secure login for cardiologists and admins.
  - **Password Reset** (if applicable in cloud): Password recovery flow (optional).

- **Patients Management**
  - **Patient List**: View/search patients.
  - **Add/Edit Patient**: Create or update patient profiles.
  - **Patient History**: Access past reports for a specific patient.

- **Reports Management**
  - **Create Report**: Start a new echocardiogram report.
  - **Edit Report**: Modify an existing report.
  - **Report Details**: View completed report with option to export.
  - **Upload DICOM Images**: Attach images to the report.
  - **Generate PDF**: Create professional PDF with images embedded.

- **Sync and Status**
  - **Sync Status Panel**: Displays the latest synchronization status and history.
  - **Manual Sync Trigger**: Option to manually trigger sync.

- **Admin Panel (Optional/Cloud)**
  - **User Management**: Manage users and permissions.
  - **System Logs**: View sync logs and error reports (cloud only).

---

## 2. Wireframes

### 🖼️ Description
Wireframes provide a **visual guide** representing the **skeletal framework** of key pages, ensuring clarity in layout and functionality before moving to full UI/UX design.

---

### UI01: Dashboard (Cardiologist)
- **Purpose**: Central hub for cardiologists to manage patients and reports, view sync status.
- **Main Components**:
  - Quick stats (patients, reports, last sync).
  - Buttons: “Add Patient”, “Create Report”, “Manual Sync”.
  - List of recent reports with status indicators.

---

### UI02: Patients List
- **Purpose**: Display all registered patients.
- **Main Components**:
  - Search bar + filters (by name, ID).
  - Table/list of patients with action buttons (Edit, View History, Delete).

---

### UI03: Create/Edit Patient Page
- **Purpose**: Form for adding or editing patient information.
- **Main Components**:
  - Input fields: Name, Date of Birth, Gender, ID Number, Notes.
  - Save/Cancel actions.

---

### UI04: Reports Management
- **Purpose**: Create and edit echocardiogram reports.
- **Main Components**:
  - Structured data inputs: Measurements, Observations, Diagnosis.
  - Upload area for DICOM images.
  - Preview section for images.
  - Save, Generate PDF, Cancel buttons.

---

### UI05: Sync Status Page
- **Purpose**: Display sync history and status.
- **Main Components**:
  - Last sync timestamp.
  - Status indicators (Success, Pending, Failed).
  - Manual sync button.

---

### UI06: Admin Panel (Optional for Cloud)
- **Purpose**: Manage system users and review logs.
- **Main Components**:
  - User table with permissions.
  - Add/Edit/Remove user actions.
  - Sync and error logs viewer.

---

👉 Next Steps:
- Create **visual wireframes** based on these descriptions (suggest using Figma or diagrams.net).
- Review navigation flow in early UI prototype to ensure **usability for cardiologists** (especially Dr. Otavio’s workflow!).


## A4: Non-Functional Requirements

### 📝 Brief Presentation of Goals
This section defines the **non-functional requirements (NFRs)** that ensure the **performance**, **usability**, **reliability**, **security**, and **scalability** of the HeartBeat system. These are critical for guaranteeing a **high-quality experience** for cardiologists and maintaining **data integrity** in both local and cloud environments.

---

## 1. Performance Requirements

| Identifier | Name                           | Description                                                                                 |
|------------|--------------------------------|---------------------------------------------------------------------------------------------|
| NFR01      | Local Response Time            | The system must load patient lists and reports within **1 second** in the local application. |
| NFR02      | PDF Generation Speed           | The system must generate PDF reports, including embedded images, in **under 5 seconds**.    |
| NFR03      | Sync Frequency                 | Synchronization with the cloud must occur **automatically every 5 minutes** (or manually on demand). |

---

## 2. Usability Requirements

| Identifier | Name                           | Description                                                                                 |
|------------|--------------------------------|---------------------------------------------------------------------------------------------|
| NFR04      | Low Learning Curve             | The system must be usable by cardiologists with **minimal training** (less than 10 minutes of onboarding). |
| NFR05      | Simplified Data Entry          | Patient and report forms must be **minimalist**, requiring no more than **2 minutes** to fill per report. |
| NFR06      | Language and Terminology       | The system must use **medical terminology** familiar to cardiologists specializing in echocardiography. |

---

## 3. Reliability Requirements

| Identifier | Name                           | Description                                                                                 |
|------------|--------------------------------|---------------------------------------------------------------------------------------------|
| NFR07      | Offline Availability           | All critical features (patient registration, report creation, PDF generation) must be fully functional **offline**. |
| NFR08      | Sync Reliability               | The synchronization process must **retry automatically** in case of connection failure, with **no data loss**. |
| NFR09      | Local Backup                   | Patient data and reports must be **automatically backed up locally** at least once every **24 hours**. |

---

## 4. Security Requirements

| Identifier | Name                           | Description                                                                                 |
|------------|--------------------------------|---------------------------------------------------------------------------------------------|
| NFR10      | Data Encryption (At Rest)      | Patient data must be encrypted on disk (SQLite encryption locally, PostgreSQL encryption on cloud). |
| NFR11      | Data Encryption (In Transit)   | All communication between local EXE and cloud backend must be secured via **HTTPS (TLS 1.2+)**. |
| NFR12      | User Authentication            | All users must be authenticated via **JWT tokens** for REST API communication with the cloud backend. |
| NFR13      | Access Control                 | Users must have **role-based access control** (Cardiologist, Admin, Clinic Admin).          |

---

## 5. Scalability Requirements

| Identifier | Name                           | Description                                                                                 |
|------------|--------------------------------|---------------------------------------------------------------------------------------------|
| NFR14      | Clinic Expansion               | The system must support **multi-user environments**, allowing clinics to add more cardiologists without impacting performance. |
| NFR15      | Cloud Storage Scaling          | The cloud backend must scale to store **at least 10,000 reports and 5TB of DICOM images** in the first year. |

---

## 6. Maintainability Requirements

| Identifier | Name                           | Description                                                                                 |
|------------|--------------------------------|---------------------------------------------------------------------------------------------|
| NFR16      | Update Mechanism               | The local EXE must support **automatic updates**, downloadable from the cloud backend.      |
| NFR17      | Modular Codebase               | The backend (Django) must follow **modular architecture** to simplify **maintenance and future updates**. |
| NFR18      | Logging and Monitoring         | The system must maintain **logs** of sync processes and report generation, with alerts for failures (cloud-side). |

---

## 7. Compliance Requirements

| Identifier | Name                           | Description                                                                                 |
|------------|--------------------------------|---------------------------------------------------------------------------------------------|
| NFR19      | Data Privacy Laws              | The system must comply with **LGPD (Brazil)** and **GDPR (Europe)** for data handling and storage. |
| NFR20      | Medical Data Standards         | The system must comply with **HIPAA guidelines** for data security when deployed in the US (optional future consideration). |

## A5: System Architecture and Diagrams

### 📝 Brief Presentation of Goals
This section provides a **visual and conceptual overview** of HeartBeat's system architecture. It illustrates how different **components interact**, how **data flows** through the system, and how **local and cloud environments** are structured. These diagrams help stakeholders and developers understand the **technical foundation** of the application.

---

## 1. High-Level System Architecture Diagram

### 🏗️ Description
HeartBeat is composed of two **primary environments**:
1. **Local Application (Windows EXE)**  
   Runs a Django-based server locally with a SQLite database. Works offline and includes all core features (patient registration, report creation, PDF generation).
2. **Cloud Backend (Django + PostgreSQL)**  
   Provides centralized storage, user management, and backups. Synchronizes data from multiple local instances.

---

### 📡 Diagram (Conceptual Description)

[User] –> [Local Web App (HTMX + Django Templates)]
|
|—> [Local Django Server]
|
|—> [SQLite Database]
|
|—> [DICOM Processor (pydicom + Pillow)]
|
|—> [PDF Generator (WeasyPrint)]
|
|—> [Sync Service (REST API + JWT)]
|
|—> [Cloud Django Server (API Endpoint)]
|
|—> [PostgreSQL Database (Cloud)]
|
|—> [Cloud Storage (DICOM files)]
|
|—> [Admin Interface (Optional)]


---

## 2. Component Breakdown

| Component               | Description                                                                                   |
|-------------------------|-----------------------------------------------------------------------------------------------|
| **Local Django Server**  | Provides core functionalities: patient registration, report creation, DICOM processing.       |
| **SQLite Database**      | Stores local patient records and reports.                                                     |
| **DICOM Processor**      | Converts uploaded DICOM images to formats suitable for preview and PDF embedding.             |
| **PDF Generator**        | Produces professional-grade PDF reports with images and clinical data.                       |
| **Sync Service**         | Manages data synchronization between local and cloud environments. Uses REST API secured by JWT. |
| **Cloud Django Server**  | Receives data from local instances, provides centralized access and management.              |
| **PostgreSQL Database**  | Stores all synchronized patient data, reports, and user accounts in the cloud.               |
| **Cloud Storage**        | Stores DICOM images securely for cloud access and backup.                                    |
| **Admin Interface**      | (Optional) Used by system admins to manage clinics, users, and logs.                         |

---

## 3. Data Flow Diagram (Sync Process)

### 🔄 Description
Illustrates how data moves from the **local instance** to the **cloud backend**, ensuring **data integrity** and **conflict management**.

---

### 📡 Data Flow (Conceptual Description)

[Local User Actions]
↓
Create/Edit Patient → Save to SQLite → Flag for Sync
↓
Create/Edit Report  → Save to SQLite → Upload DICOM → Flag for Sync
↓
Generate PDF        → Local File (Optional Cloud Upload)

[Sync Service Triggers]
↓
Detects Internet Connection → Authenticates via JWT → Sends Updated Data
↓
Uploads Patient Data → Cloud PostgreSQL
Uploads Reports + PDFs → Cloud PostgreSQL
Uploads DICOM Files → Cloud Storage
↓
Receives Confirmation → Updates Local Sync Status

---

## 4. Deployment Diagram

### 🌐 Local Deployment
- Windows EXE running:
  - Django Server
  - SQLite Database
  - Local file storage for PDFs/DICOM
- Accessible via browser at `http://localhost:8000`

### ☁️ Cloud Deployment
- Django REST API (Deployed on DigitalOcean, AWS, etc.)
- PostgreSQL database (managed or self-hosted)
- Cloud storage (Amazon S3 or equivalent)
- Admin interface (optional)

---

## 5. Sync Conflict Handling

| Scenario                      | Resolution Strategy                                                                     |
|-------------------------------|-----------------------------------------------------------------------------------------|
| **Concurrent Edits**          | Last-Modified Wins. The most recent edit (timestamp-based) will overwrite older data.   |
| **Connection Drop During Sync** | Automatic retry. Sync service will retry failed uploads after connection is restored.    |
| **Data Corruption Detection** | Integrity check with hashes. Inconsistent files are flagged for manual review.          |

---

