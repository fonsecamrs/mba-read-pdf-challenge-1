# PDF Semantic Search & Ingestion CLI

This project is a Command Line Interface (CLI) application capable of reading a PDF file, vectorizing its content, storing it in a PostgreSQL database (pgVector), and allowing users to perform semantic searches based strictly on the document's content using LangChain and Google Gemini models.

## Requirements

- Python 3
- Docker & Docker Compose
- Google Gemini API Key

## Setup Instructions

1. **Virtual Environment**
   Create and activate a virtual environment before installing dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate