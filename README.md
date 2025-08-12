# Canvas-Course-Archiver-Your-Personal-LMS-Content-Downloader-📚

Tired of manually copying and pasting course content from Canvas LMS? 😩 Clicking through every single page, discussion, and assignment to save the information is time-consuming and inefficient.

This script is here to help! It's an automated tool built with Python and Playwright designed to help students and instructors easily download and archive their course materials.

✨ Key Features
Automated Scraping: The script connects to a local Playwright instance to simulate user behavior, automatically traversing all links within your course modules.

Intelligent Content Extraction: It intelligently identifies and extracts the primary content from various page types, including wiki pages, discussions, and assignment descriptions.

Smart File Handling: The script gracefully handles links to external files and websites, noting them so you can easily access them later.

Flexible Format Conversion:

All scraped content is merged into a single, well-formatted HTML file that preserves the original layout and links.

Using the Pandoc library, the merged HTML can be converted into an editable Word (DOCX) document, perfect for offline reading and note-taking.

Easy to Use: Simply configure the COURSE_MODULES_URL and CDP_ENDPOINT, then run the script to generate a complete archive of your course content.

Stop the manual grind and let this script be your personal course content archivist! 🚀

📋 Prerequisites
Before running the script, make sure you have the following installed:

Python 3.7+

Playwright: pip install playwright

Pandoc: Used for converting HTML to DOCX. Download and install Pandoc.

You will also need to run a browser in remote debugging mode. For Google Chrome, you can do this from your terminal:

Bash

chrome.exe --remote-debugging-port=9222
# or on macOS:
# /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
⚙️ How to Use
Clone the repository or download the script.

Open the script and modify the following variables to match your course:

Python

COURSE_MODULES_URL = "https://canvas.lms.unimelb.edu.au/courses/213158/modules"
CDP_ENDPOINT = "http://localhost:9222"
COURSE_MODULES_URL: The URL of your course's modules page.

CDP_ENDPOINT: The remote debugging port of your browser.

Run the browser in remote debugging mode as described in the prerequisites.

Open a new terminal and run the script:

Bash

python your_script_name.py
Wait for the script to finish. The process may take a while depending on the number of pages in your course.

The output files (course_merged.html and course_merged.docx) will be saved in a new canvas_export directory.

🤝 Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.
