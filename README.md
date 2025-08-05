🧠 Intelligent Twitter Media Monitoring System using LLM & Agentic AI
Built an end-to-end automated system to monitor and analyze railway-related media posts on Twitter. The pipeline fetches real-time tweets using the Twitter API, downloads attached images and videos, and performs visual similarity matching through OpenCV-based frame extraction, YOLOv8 object detection, and Tesseract OCR. Matched media is evaluated using an offline LLM (via Ollama) to classify posts as either complaints or appreciation. Based on the LLM’s decision, agentic tools powered by Playwright automatically take contextual actions such as reposting and liking positive posts. (Currently, only repost and like functionalities are implemented; comment generation and tweet reporting are under development.) All actions are logged in structured Excel files for audit and traceability.

Technologies Used: Python, Playwright, YOLOv8, Tesseract OCR, OpenCV, Pandas, Ollama LLM, AsyncIO, Agentic AI

