# SynCode

**SynCode** is an automation tool that syncs your accepted LeetCode solutions directly to a GitHub repository using a CI/CD pipeline. It helps you effortlessly maintain a portfolio of your problem-solving progress.

## 🚀 Features

- 🔁 Automatically sync accepted LeetCode submissions to GitHub  
- 🐳 Dockerized for easy local or cloud deployment  
- 📈 Prometheus-ready for custom monitoring (optional)  
- 💬 Supports multiple languages (Python, Java, etc.)

## 📦 Prerequisites

- Docker & Docker Compose installed  
- A GitHub Personal Access Token (with repo access)  
- Your LeetCode credentials (username & session token)

## ⚙️ Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/meghaduaa/SynCode.git
   cd SynCode

2. **Configure Environment Variables**
   ```
   GITHUB_USERNAME=your_github_username
   GITHUB_TOKEN=your_github_token
   LEETCODE_USERNAME=your_leetcode_username
   LEETCODE_SESSION=your_leetcode_session_token
3. **Build & Run with Docker**
   ```bash
   docker-compose up --build
📊 Monitoring (Optional)
   If you want to monitor the sync using Prometheus:
   -     Configure prometheus.yml as needed
   -     Mount it inside a Prometheus container
   -     Expose and view metrics in Grafana

