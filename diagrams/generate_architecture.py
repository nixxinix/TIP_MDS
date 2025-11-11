#!/usr/bin/env python
"""
Django System Architecture Diagram Generator
Creates a comprehensive Mermaid architecture diagram
"""

def generate_architecture_diagram():
    """Generate Mermaid C4 architecture diagram"""
    
    mermaid = []
    
    # Use C4 Context diagram style
    mermaid.append('graph TB')
    mermaid.append('    %% TIP MDS EMR - System Architecture')
    mermaid.append('')
    
    # Define styling
    mermaid.append('    %% Actors/Users')
    mermaid.append('    Guest["👤 Guest User<br/>(Unauthenticated)"]')
    mermaid.append('    Student["👨‍🎓 Student<br/>(Medical Records Access)"]')
    mermaid.append('    Doctor["👨‍⚕️ Doctor<br/>(Healthcare Provider)"]')
    mermaid.append('    Admin["⚙️ Admin<br/>(System Administrator)"]')
    mermaid.append('    APIClient["🔌 API Client<br/>(External Systems)"]')
    mermaid.append('')
    
    # Presentation Layer
    mermaid.append('    %% Presentation Layer')
    mermaid.append('    subgraph Presentation["🎨 PRESENTATION LAYER"]')
    mermaid.append('        Templates["📄 Django Templates<br/>HTML/CSS/JavaScript"]')
    mermaid.append('        StaticFiles["🖼️ Static Assets<br/>(WhiteNoise)"]')
    mermaid.append('        MediaFiles["📁 Media Storage<br/>(User Uploads)"]')
    mermaid.append('    end')
    mermaid.append('')
    
    # Middleware Layer
    mermaid.append('    %% Middleware Layer')
    mermaid.append('    subgraph Middleware["🔧 MIDDLEWARE LAYER"]')
    mermaid.append('        Security["🔒 Security Middleware"]')
    mermaid.append('        Session["🎫 Session Management"]')
    mermaid.append('        CORS["🌐 CORS Headers"]')
    mermaid.append('        CSRF["🛡️ CSRF Protection"]')
    mermaid.append('        Auth["🔐 Authentication"]')
    mermaid.append('    end')
    mermaid.append('')
    
    # Application Layer - Core Apps
    mermaid.append('    %% Application Layer - Core')
    mermaid.append('    subgraph CoreApps["💼 CORE BUSINESS LOGIC"]')
    mermaid.append('        AccountsApp["👤 Accounts App<br/>• Custom User Model<br/>• Email Auth Backend<br/>• Profile Management"]')
    mermaid.append('        StudentsApp["👨‍🎓 Students App<br/>• Registration<br/>• Medical Records<br/>• Appointments"]')
    mermaid.append('        DoctorsApp["👨‍⚕️ Doctors App<br/>• Doctor Dashboard<br/>• Prescriptions<br/>• Certificates"]')
    mermaid.append('        AppointmentsApp["📅 Appointments App<br/>• Scheduling<br/>• Approval Workflow<br/>• Status Management"]')
    mermaid.append('    end')
    mermaid.append('')
    
    # Application Layer - Supporting Apps
    mermaid.append('    %% Application Layer - Supporting')
    mermaid.append('    subgraph SupportApps["🔔 SUPPORTING SERVICES"]')
    mermaid.append('        NotificationsApp["🔔 Notifications<br/>• Real-time Alerts<br/>• User Preferences<br/>• API Endpoints"]')
    mermaid.append('        AnalyticsApp["📊 Analytics<br/>• System Metrics<br/>• Usage Reports<br/>• Dashboard Data"]')
    mermaid.append('        TemplatesDocsApp["📋 Document Templates<br/>• Prescriptions<br/>• Certificates<br/>• Clearances"]')
    mermaid.append('    end')
    mermaid.append('')
    
    # API Layer
    mermaid.append('    %% API Layer')
    mermaid.append('    subgraph APILayer["🔌 REST API LAYER"]')
    mermaid.append('        DRF["Django REST Framework<br/>• Serialization<br/>• ViewSets<br/>• Authentication"]')
    mermaid.append('    end')
    mermaid.append('')
    
    # Data Layer
    mermaid.append('    %% Data Persistence Layer')
    mermaid.append('    subgraph DataLayer["🗄️ DATA PERSISTENCE"]')
    mermaid.append('        ORM["Django ORM<br/>(Object-Relational Mapper)"]')
    mermaid.append('        Database["💾 SQLite Database<br/>• User Accounts<br/>• Medical Records<br/>• Appointments<br/>• Notifications"]')
    mermaid.append('    end')
    mermaid.append('')
    
    # External Services
    mermaid.append('    %% External Services')
    mermaid.append('    subgraph External["☁️ EXTERNAL SERVICES"]')
    mermaid.append('        PDF["📄 WeasyPrint<br/>(PDF Generation)"]')
    mermaid.append('        Email["📧 Email Service<br/>(SMTP)"]')
    mermaid.append('        FileStorage["📦 File Storage<br/>(Local/Cloud)"]')
    mermaid.append('    end')
    mermaid.append('')
    
    # Infrastructure
    mermaid.append('    %% Infrastructure')
    mermaid.append('    subgraph Infrastructure["🚀 DEPLOYMENT"]')
    mermaid.append('        Gunicorn["🦄 Gunicorn<br/>(WSGI Server)"]')
    mermaid.append('        WhiteNoise["⚡ WhiteNoise<br/>(Static Files)"]')
    mermaid.append('    end')
    mermaid.append('')
    
    # Connections - User to Presentation
    mermaid.append('    %% User Interactions')
    mermaid.append('    Guest --> Templates')
    mermaid.append('    Student --> Templates')
    mermaid.append('    Doctor --> Templates')
    mermaid.append('    Admin --> Templates')
    mermaid.append('    APIClient --> DRF')
    mermaid.append('')
    
    # Presentation to Middleware
    mermaid.append('    %% Request Flow')
    mermaid.append('    Templates --> Security')
    mermaid.append('    StaticFiles --> WhiteNoise')
    mermaid.append('    Security --> Session')
    mermaid.append('    Session --> CORS')
    mermaid.append('    CORS --> CSRF')
    mermaid.append('    CSRF --> Auth')
    mermaid.append('')
    
    # Middleware to Applications
    mermaid.append('    %% Middleware to Apps')
    mermaid.append('    Auth --> AccountsApp')
    mermaid.append('    Auth --> StudentsApp')
    mermaid.append('    Auth --> DoctorsApp')
    mermaid.append('    Auth --> AppointmentsApp')
    mermaid.append('    Auth --> NotificationsApp')
    mermaid.append('    Auth --> AnalyticsApp')
    mermaid.append('    Auth --> TemplatesDocsApp')
    mermaid.append('')
    
    # API Layer connections
    mermaid.append('    %% API Layer')
    mermaid.append('    DRF --> AccountsApp')
    mermaid.append('    DRF --> NotificationsApp')
    mermaid.append('')
    
    # Apps to Data Layer
    mermaid.append('    %% Data Access')
    mermaid.append('    AccountsApp --> ORM')
    mermaid.append('    StudentsApp --> ORM')
    mermaid.append('    DoctorsApp --> ORM')
    mermaid.append('    AppointmentsApp --> ORM')
    mermaid.append('    NotificationsApp --> ORM')
    mermaid.append('    AnalyticsApp --> ORM')
    mermaid.append('    TemplatesDocsApp --> ORM')
    mermaid.append('    ORM --> Database')
    mermaid.append('')
    
    # Apps to External Services
    mermaid.append('    %% External Service Integration')
    mermaid.append('    DoctorsApp --> PDF')
    mermaid.append('    TemplatesDocsApp --> PDF')
    mermaid.append('    NotificationsApp --> Email')
    mermaid.append('    AccountsApp --> Email')
    mermaid.append('    StudentsApp --> FileStorage')
    mermaid.append('    DoctorsApp --> FileStorage')
    mermaid.append('    MediaFiles --> FileStorage')
    mermaid.append('')
    
    # Infrastructure connections
    mermaid.append('    %% Infrastructure')
    mermaid.append('    Gunicorn -.-> Templates')
    mermaid.append('    WhiteNoise -.-> StaticFiles')
    mermaid.append('')
    
    # Styling
    mermaid.append('    %% Styling')
    mermaid.append('    classDef userStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:3px')
    mermaid.append('    classDef presentationStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px')
    mermaid.append('    classDef middlewareStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px')
    mermaid.append('    classDef appStyle fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px')
    mermaid.append('    classDef dataStyle fill:#fce4ec,stroke:#c2185b,stroke-width:2px')
    mermaid.append('    classDef externalStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px')
    mermaid.append('    classDef infraStyle fill:#e0f2f1,stroke:#00695c,stroke-width:2px')
    mermaid.append('')
    mermaid.append('    class Guest,Student,Doctor,Admin,APIClient userStyle')
    mermaid.append('    class Templates,StaticFiles,MediaFiles presentationStyle')
    mermaid.append('    class Security,Session,CORS,CSRF,Auth middlewareStyle')
    mermaid.append('    class AccountsApp,StudentsApp,DoctorsApp,AppointmentsApp,NotificationsApp,AnalyticsApp,TemplatesDocsApp,DRF appStyle')
    mermaid.append('    class ORM,Database dataStyle')
    mermaid.append('    class PDF,Email,FileStorage externalStyle')
    mermaid.append('    class Gunicorn,WhiteNoise infraStyle')
    
    return '\n'.join(mermaid)

def generate_layered_diagram():
    """Generate simplified layered architecture"""
    
    mermaid = []
    mermaid.append('graph TD')
    mermaid.append('    %% Layered Architecture - TIP MDS EMR')
    mermaid.append('')
    mermaid.append('    subgraph Layer1["🌐 CLIENT LAYER"]')
    mermaid.append('        Browser["Web Browser"]')
    mermaid.append('        Mobile["Mobile Device"]')
    mermaid.append('        API["API Clients"]')
    mermaid.append('    end')
    mermaid.append('')
    mermaid.append('    subgraph Layer2["🎨 PRESENTATION LAYER"]')
    mermaid.append('        Direction LR')
    mermaid.append('        Templates["Django Templates"]')
    mermaid.append('        Static["Static Files<br/>(WhiteNoise)"]')
    mermaid.append('        REST["REST API<br/>(DRF)"]')
    mermaid.append('    end')
    mermaid.append('')
    mermaid.append('    subgraph Layer3["🔒 SECURITY LAYER"]')
    mermaid.append('        AuthN["Authentication<br/>(Email Backend)"]')
    mermaid.append('        AuthZ["Authorization<br/>(Permissions)"]')
    mermaid.append('        CSRF2["CSRF/CORS"]')
    mermaid.append('    end')
    mermaid.append('')
    mermaid.append('    subgraph Layer4["💼 BUSINESS LOGIC LAYER"]')
    mermaid.append('        Direction LR')
    mermaid.append('        Accounts["Accounts"]')
    mermaid.append('        Students2["Students"]')
    mermaid.append('        Doctors2["Doctors"]')
    mermaid.append('        Appts["Appointments"]')
    mermaid.append('        Notifs["Notifications"]')
    mermaid.append('        Analytics2["Analytics"]')
    mermaid.append('        Docs["Templates/Docs"]')
    mermaid.append('    end')
    mermaid.append('')
    mermaid.append('    subgraph Layer5["🗄️ DATA ACCESS LAYER"]')
    mermaid.append('        ORM2["Django ORM"]')
    mermaid.append('        Models["Models<br/>(User, Student, Doctor, etc.)"]')
    mermaid.append('    end')
    mermaid.append('')
    mermaid.append('    subgraph Layer6["💾 DATABASE LAYER"]')
    mermaid.append('        SQLite["SQLite Database"]')
    mermaid.append('    end')
    mermaid.append('')
    mermaid.append('    subgraph Layer7["☁️ EXTERNAL SERVICES"]')
    mermaid.append('        Direction LR')
    mermaid.append('        SMTP["Email (SMTP)"]')
    mermaid.append('        PDFGen["PDF Generation<br/>(WeasyPrint)"]')
    mermaid.append('        Storage["File Storage"]')
    mermaid.append('    end')
    mermaid.append('')
    mermaid.append('    Browser --> Templates')
    mermaid.append('    Mobile --> Templates')
    mermaid.append('    API --> REST')
    mermaid.append('    Templates --> AuthN')
    mermaid.append('    Static --> Templates')
    mermaid.append('    REST --> AuthN')
    mermaid.append('    AuthN --> AuthZ')
    mermaid.append('    AuthZ --> CSRF2')
    mermaid.append('    CSRF2 --> Accounts')
    mermaid.append('    CSRF2 --> Students2')
    mermaid.append('    CSRF2 --> Doctors2')
    mermaid.append('    CSRF2 --> Appts')
    mermaid.append('    CSRF2 --> Notifs')
    mermaid.append('    CSRF2 --> Analytics2')
    mermaid.append('    CSRF2 --> Docs')
    mermaid.append('    Accounts --> ORM2')
    mermaid.append('    Students2 --> ORM2')
    mermaid.append('    Doctors2 --> ORM2')
    mermaid.append('    Appts --> ORM2')
    mermaid.append('    Notifs --> ORM2')
    mermaid.append('    Analytics2 --> ORM2')
    mermaid.append('    Docs --> ORM2')
    mermaid.append('    ORM2 --> Models')
    mermaid.append('    Models --> SQLite')
    mermaid.append('    Notifs --> SMTP')
    mermaid.append('    Docs --> PDFGen')
    mermaid.append('    Doctors2 --> PDFGen')
    mermaid.append('    Students2 --> Storage')
    mermaid.append('    Doctors2 --> Storage')
    mermaid.append('')
    mermaid.append('    classDef clientStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:2px')
    mermaid.append('    classDef presentationStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px')
    mermaid.append('    classDef securityStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px')
    mermaid.append('    classDef businessStyle fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px')
    mermaid.append('    classDef dataStyle fill:#fce4ec,stroke:#c2185b,stroke-width:2px')
    mermaid.append('    classDef dbStyle fill:#ffebee,stroke:#b71c1c,stroke-width:2px')
    mermaid.append('    classDef externalStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px')
    
    return '\n'.join(mermaid)

def main():
    print("🏗️ Generating System Architecture Diagrams...\n")
    
    # Generate detailed architecture
    print("📊 Creating detailed architecture diagram...")
    detailed = generate_architecture_diagram()
    with open('architecture_detailed.mmd', 'w', encoding='utf-8') as f:
        f.write(detailed)
    print("✅ Saved: architecture_detailed.mmd")
    
    # Generate layered architecture
    print("📊 Creating layered architecture diagram...")
    layered = generate_layered_diagram()
    with open('architecture_layered.mmd', 'w', encoding='utf-8') as f:
        f.write(layered)
    print("✅ Saved: architecture_layered.mmd")
    
    print("\n🎯 Architecture Diagrams Generated!")
    print("\n📋 Files created:")
    print("  1. architecture_detailed.mmd  → Comprehensive component diagram")
    print("  2. architecture_layered.mmd   → Clean layered architecture")
    
    print("\n🎨 View your diagrams:")
    print("  • Open: https://mermaid.live/")
    print("  • Copy content from .mmd files")
    print("  • Paste into editor")
    
    print("\n💡 Tips:")
    print("  • Detailed diagram shows all components and connections")
    print("  • Layered diagram shows clean separation of concerns")
    print("  • Both diagrams are color-coded by layer type")

if __name__ == '__main__':
    main()