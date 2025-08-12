# Canvas Course Archiver 📚

Tired of manually copying and pasting course content from Canvas LMS? 😩 Clicking through every single page, discussion, and assignment to save the information is time-consuming and inefficient.

This script is here to help!  
It's an automated tool built with **Python** and **Playwright** designed to help students and instructors easily download and archive their course materials.

---

## ✨ Features

- **Automated Scraping**: Connects to a local Playwright instance to simulate user behavior, automatically traversing all links within your course modules.
- **Intelligent Content Extraction**: Identifies and extracts the primary content from various page types, including wiki pages, discussions, and assignment descriptions.
- **Smart File Handling**: Handles links to external files and websites gracefully, noting them for easy access later.
- **Flexible Format Conversion**: Merges all scraped content into a single, well-formatted HTML file, which can then be converted into an editable Word (`.docx`) document using Pandoc.
- **Easy to Use**: Configure the course URL and browser debugging endpoint, then run the script to generate a complete archive of your course content.

Stop the manual grind and let this script be your personal course content archivist! 🚀

---

## ⚙️ Prerequisites

Before running the script, make sure you have:

- **Python 3.7+**
- **Playwright**
- **Pandoc**

### Install Playwright and its dependencies:
```bash
pip install playwright
playwright install
