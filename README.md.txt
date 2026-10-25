# 🏛️ CivicClear AI | SaralNotice

### *Actionable Clarity for Everyone*

![Hacktoberfest](https://img.shields.io/badge/Hacktoberfest-2026-FF6B6B?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

A highly sophisticated, open-source, bilingual (English & Hindi) AI-powered assistant designed to simplify complex institutional notices (university circulars, government notifications, scholarship guidelines). 

Built under the Hacktoberfest 2026 theme: **"AI Belongs to Everyone."**

---

### 🌟 Key Features

*   **Multimodal Document Parsing:** Supports both high-quality image uploads (JPG/PNG) and multi-page PDF circulars using PyMuPDF (`fitz`).
*   **Dual-API Fallback Engine:** Uses **OpenRouter** (accessing free open-weight models like Llama 3.2) as the primary engine, and automatically falls back to **Google Gemini Studio** if the primary API fails or rate-limits.
*   **Full Bilingual Pipeline (English / Hindi):** Dynamically translates extracted summaries, deadlines, and checklist items into natural, localized Hindi.
*   **Interactive Action Checklist:** Breaks down bureaucratic procedures into an interactive, checkable progress tracker. Saves state locally in the browser (no login required).
*   **Universal Accessibility (TTS):** Generates custom Text-to-Speech audio (`gTTS`) summaries in both English and Hindi for visually impaired or low-literacy users.
*   **Persistent Dashboard:** Features a local SQLite database to automatically categorize notices into **Active**, **Approaching Soon** (within 3 days), **Expired**, and **Important** tabs.

---

### 🛠️ How It Works (Architecture)

The application uses a **Multi-Agent Pipeline**:
1.  **Perception Agent:** Converts PDFs/images into standardized JPEG base64 images.
2.  **Extraction Agent:** Queries the vision LLM to parse the document and return structured data (Summary, Deadline, Checklist, Notes) in strict JSON format.
3.  **Action Agent:** Generates `.ics` calendar files and interactive checklist steps.
4.  **Voice Agent:** Converts the localized text into high-quality audio files.

---

### 🚀 How to Run Locally

#### 1. Prerequisites
*   Python 3.8 or higher.
*   `pip` package installer.

#### 2. Install Dependencies
Clone this repository and open your terminal in the project folder, then run:
```bash
pip install streamlit requests pymupdf Pillow gtts