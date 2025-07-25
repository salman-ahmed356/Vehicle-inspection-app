# Vehicle Inspection Web App

⚠️ **PROPRIETARY SOFTWARE** - All rights reserved. Commercial use, modification, or distribution requires written permission. See [LICENSE](LICENSE) for details.

## Overview
The **Vehicle Inspection Web App** is a web-based application designed to facilitate vehicle inspections, appointments, and report generation. The app provides features for managing customers, appointments, reports, and more, making it a comprehensive tool for vehicle inspection centers.

## Features
- **Appointment Scheduling**: Manage and schedule vehicle inspection appointments.
- **Customer Management**: Store and manage customer details.
- **Report Generation**: Generate detailed vehicle inspection reports.
- **Staff Management**: Handle staff information and roles.
- **PDF Report Creation**: Create and download PDF versions of inspection reports.
- **Branch and Company Management**: Organize branches and manage company information.
- **Blueprint Architecture**: Modular structure with blueprints for various routes.

## Tech Stack
- **Backend**: Python, Flask, Flask-SQLAlchemy
- **Database**: SQLAlchemy ORM (supports various database backends)
- **Frontend**: HTML, CSS, JavaScript (Flask templates)
- **PDF Generation**: WeasyPrint
- **Environment Management**: Python dotenv for environment variable handling
- **Containerization**: Docker

## Installation and Setup

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started) & Docker Compose
- [Git](https://git-scm.com/downloads)

### Quick Start with Docker (Recommended)

1. **Clone the repository**:
    ```bash
    git clone https://github.com/salman-ahmed356/Vehicle-inspection-app.git
    cd Vehicle-inspection-app
    ```

2. **Start the application with database**:
    ```bash
    docker-compose up -d
    ```

3. **Access the application**:
    - Open your browser and go to `http://localhost:5000`
    - The MySQL database will be automatically set up

4. **Stop the application**:
    ```bash
    docker-compose down
    ```

### Alternative: Single Container

1. **Build and run without database**:
    ```bash
    docker build -t vehicle-inspection-web-app .
    docker run -p 5000:5000 vehicle-inspection-web-app
    ```

### Local Development Setup

1. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2. **Set up environment variables**:
    ```bash
    cp .env.example .env  # Edit with your database settings
    ```

3. **Run the application**:
    ```bash
    python run.py
    ```


## Production Deployment

### VPS Hosting (Hostinger, DigitalOcean, etc.)

1. **Install Docker on your VPS**:
    ```bash
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    ```

2. **Clone and deploy**:
    ```bash
    git clone https://github.com/salman-ahmed356/Vehicle-inspection-app.git
    cd Vehicle-inspection-app
    docker-compose up -d
    ```

3. **Set up reverse proxy (Nginx)**:
    ```bash
    # Configure Nginx to proxy port 5000
    # Add SSL certificate with Certbot
    ```

## Troubleshooting
- **Port 5000 in use**: Change port mapping in `docker-compose.yml`
- **Database connection issues**: Check MySQL container logs with `docker-compose logs db`
- **PDF generation errors**: Docker image includes all WeasyPrint dependencies
- **Permission issues**: Ensure Docker has proper permissions on your system

## License

This software is proprietary and all rights are reserved. You may view the source code for educational purposes only. Any commercial use, modification, distribution, or derivative works require explicit written permission from the author.

**Author**: Salman Ahmed  
**Repository**: https://github.com/salman-ahmed356/Vehicle-inspection-app.git  
**Contact**: salmanahmad356240@gmail.com

See [LICENSE](LICENSE) file for complete terms and conditions.