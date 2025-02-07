# GDELT Data Dashboard

This project is a self-hosted GDELT data pipeline and visualization dashboard, designed to process, store, and display real-time global event data. Running on a virtual machine hosted in Proxmox, the setup leverages AlmaLinux, Docker Compose, and a PCIe-passed Ethernet port for secure, isolated network access.

### Features
- **Automated Data Ingestion**: Fetches and loads new GDELT data every 15 minutes, ensuring up-to-date global event insights.
- **Data Storage in PostgreSQL**: Structured event data stored in PostgreSQL for efficient querying and analysis.
- **Real-Time Visualization**: Grafana visualizes patterns, event counts, and police-related incidents with dynamically updated panels.
- **Secure Public Access**: Nginx serves the dashboard with Cloudflare Tunnel for remote access, encapsulating the local network securely.

This project demonstrates skills in Docker, Grafana, PostgreSQL, advanced networking, and virtualization. It provides a critical analysis tool to evaluate GDELT’s data coverage and accuracy.

You can visit the dashboard at fifteen.postplateaux.com