# FixAI 🛠️✨

FixAI is a web application designed to help users get instant, smart cost estimations for various repairs based on the Israeli market. Powered by Flask, MySQL, and Google Gemini AI, it allows users to enter a repair request, upload an image, and receive an estimated price range and advice.

The project is fully containerized and includes reverse proxy routing, automated testing, metrics exporting, monitoring, and CI/CD pipelines.

---

## 🚀 Key Features

* **AI-Powered Estimates**: Uses Google's `gemini-flash-lite-latest` model to analyze text and image inputs and generate accurate repair price ranges tailored for the Israeli market.
* **Todo/Tracking System**: Log and track repair items with their completion status and AI advice history.
* **Fully Containerized Architecture**: Easy setup using Docker Compose.
* **Reverse Proxy**: Nginx handles public-facing traffic and serves static content efficiently.
* **Monitoring & Metrics**: Prometheus collects Flask application metrics, which are visualized using Grafana dashboards.
* **CI/CD Pipeline**: GitHub Actions running integration tests, building Docker images, and deploying changes to AWS EC2.

---

## 🛠️ Tech Stack

* **Backend**: Python, Flask, Flask-SQLAlchemy (MySQL)
* **AI Model**: Google GenAI SDK (`google-genai` & `gemini-flash-lite-latest`)
* **Database**: MySQL 5.7
* **Web Server / Reverse Proxy**: Nginx
* **Monitoring**: Prometheus, Grafana, `prometheus-flask-exporter`
* **Infrastructure**: Docker & Docker Compose, Terraform, AWS EC2
* **CI/CD**: GitHub Actions

---

## 📦 Service Architecture

The system is split into multiple Docker containers:

1. **`flask_app`**: Python Flask backend exposing app logic on port `5000` (internal).
2. **`mysql`**: MySQL database.
3. **`nginx`**: Public-facing proxy listening on port `80` routing to `flask_app` or serving local static assets.
4. **`prometheus`**: Scrapes Flask app metrics on port `9090`.
5. **`grafana`**: Visualization tool on port `3000` for querying Prometheus metrics.
6. **`testserver`**: A container executing automated integration tests checking Flask app endpoints and database updates.

---

## ⚙️ Getting Started

### Prerequisites
* Docker and Docker Compose installed on your system.
* A Google Gemini API Key. You can get one from [Google AI Studio](https://aistudio.google.com/).

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/oranmeir-git/FixAI.git
   cd FixAI
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   MYSQL_ROOT_PASSWORD=your_secure_root_password
   MYSQL_USER=flask
   MYSQL_PASSWORD=your_secure_user_password
   GEMINI_KEY=your_gemini_api_key
   ```

3. **Start the application:**
   ```bash
   docker compose up -d --build
   ```

4. **Access the services:**
   * **Web Application**: [http://localhost](http://localhost)
   * **Prometheus Dashboard**: [http://localhost:9090](http://localhost:9090)
   * **Grafana Dashboard**: [http://localhost:3000](http://localhost:3000)

---

## 🧪 Testing

Integration tests are run automatically in a container called `testserver`. You can run them locally with:
```bash
docker compose run --rm testserver
```

---

## 🌐 Deployment & CI/CD

This repository uses GitHub Actions for continuous integration and deployment:

1. **CI/CD Pipeline (`ci.yml`)**:
   * Runs whenever a commit is pushed to the `main` branch.
   * Spins up Docker Compose services inside the runner.
   * Runs the integration tests suite using `testserver`.
   * Builds the Flask application Docker image and pushes it to Docker Hub if tests pass.

2. **Deploy to EC2 (`deploy.yml`)**:
   * Triggered when the CI/CD Pipeline successfully completes.
   * Connects via SSH to the target EC2 server.
   * Pulls the latest changes from the repository.
   * Updates the running containers with the new Docker image.
