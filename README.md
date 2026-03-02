# AI-Based Plagiarism Detection System

A complete, production-ready plagiarism detection web application built with **Python**, **Flask**, and **NLP** techniques. Upload documents or paste text to instantly compare similarity using TF-IDF vectorisation and cosine similarity.

---

## Features

- **Multiple input methods** – paste text directly or upload `.txt`, `.pdf`, `.docx` files
- **AI-powered comparison** – TF-IDF vectorisation + cosine similarity
- **Sentence-level analysis** – highlights the most similar sentence pairs
- **Batch comparison** – upload N documents and get an N×N similarity matrix
- **Plagiarism levels** – Low (0–30%), Medium (30–70%), High (70–100%)
- **REST API** endpoint for programmatic access
- **Comparison history** – browse past checks
- **Downloadable report** – export results as a plain-text file
- **Dark / Light mode** toggle
- **Drag-and-drop** file uploads
- **Loading animation** while processing
- Mobile-responsive design

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.8+, Flask |
| NLP / ML | scikit-learn (TF-IDF, cosine similarity), NLTK |
| File parsing | PyPDF2, python-docx |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Production server | Gunicorn |
| Testing | pytest |

---

## Project Structure

```
├── app.py                  # Main Flask application
├── plagiarism_engine.py    # Core plagiarism detection logic
├── preprocessing.py        # Text preprocessing utilities
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── templates/
│   ├── layout.html         # Base HTML template
│   ├── index.html          # Upload / input page
│   ├── results.html        # Results display page
│   ├── history.html        # Comparison history page
│   └── 404.html            # Error page
├── static/
│   ├── css/style.css       # Styling
│   └── js/main.js          # Frontend JavaScript
├── uploads/                # Uploaded files (temporary storage)
└── tests/
    ├── test_preprocessing.py
    └── test_engine.py
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/ashik2005as/AI-Plagiarism-Detection-System.git
cd AI-Plagiarism-Detection-System

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # Linux / macOS
# venv\Scripts\activate.bat    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. NLTK data is downloaded automatically on first run,
#    but you can pre-download with:
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# 5. Run the development server
python app.py
```

Open your browser at **http://127.0.0.1:5000**.

### Production (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## Usage

### Web Interface

1. Navigate to `http://127.0.0.1:5000`.
2. Choose an input method:
   - **Text Input** – paste two pieces of text.
   - **File Upload** – upload two documents (`.txt`, `.pdf`, `.docx`).
   - **Batch Compare** – upload 2+ documents for an N×N similarity matrix.
3. Click **Check Plagiarism**.
4. View results including similarity percentage, plagiarism level, and sentence matches.
5. Download the report using the **Download Report** button.

### REST API

**Endpoint:** `POST /api/check`

```bash
curl -X POST http://127.0.0.1:5000/api/check \
     -H "Content-Type: application/json" \
     -d '{"text1": "The quick brown fox.", "text2": "A quick brown fox jumps."}'
```

**Response:**

```json
{
  "similarity_percentage": 72.5,
  "plagiarism_level": "High",
  "sentence_matches": [
    {
      "sentence1": "The quick brown fox.",
      "sentence2": "A quick brown fox jumps.",
      "similarity": 0.8123
    }
  ]
}
```

---

## How It Works

1. **Text Preprocessing** – Input text is lowercased, punctuation is removed, stopwords are filtered, and tokens are lemmatised using NLTK.
2. **TF-IDF Vectorisation** – scikit-learn's `TfidfVectorizer` converts preprocessed text into numerical vectors reflecting term importance.
3. **Cosine Similarity** – The angle between document vectors measures their similarity (0 = no overlap, 1 = identical).
4. **Sentence-Level Analysis** – Each sentence pair is individually compared to identify the most similar passages.
5. **Classification** – The overall score is mapped to Low / Medium / High plagiarism levels.

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Future Enhancements

- Database backend (PostgreSQL / SQLite) for persistent history
- User authentication and per-user history
- Support for more file formats (`.odt`, `.rtf`, `.html`)
- Web-crawl checking against public internet sources
- Highlight matching passages inline side-by-side
- Export results as PDF report

---

## License

MIT License – see [LICENSE](LICENSE) for details.
