"""Flask web application for the AI Plagiarism Detection System."""

import json
import os
import uuid
from datetime import datetime

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from plagiarism_engine import compare_documents, compare_multiple_documents
from preprocessing import extract_text_from_file

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "plagiarism-detection-secret-key")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")
ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def allowed_file(filename):
    """Return True if the file extension is in ALLOWED_EXTENSIONS."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_history():
    """Load comparison history from the JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(entry):
    """Append a result entry to the history JSON file."""
    history = load_history()
    history.insert(0, entry)
    history = history[:50]  # keep at most 50 entries
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as fh:
            json.dump(history, fh, indent=2)
    except IOError:
        pass


def get_text_from_request_field(field_name, file_field_name):
    """
    Extract text from either a textarea or an uploaded file.

    Args:
        field_name (str): Name of the textarea form field.
        file_field_name (str): Name of the file upload form field.

    Returns:
        str: Extracted text, or empty string if nothing was provided.
    """
    text = request.form.get(field_name, "").strip()
    if text:
        return text

    file = request.files.get(file_field_name)
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        try:
            return extract_text_from_file(save_path)
        except Exception as exc:  # pylint: disable=broad-except
            flash(f"Could not read file '{filename}': {exc}", "danger")
    return ""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Render the main upload / input page."""
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check():
    """Process submitted documents and redirect to results page."""
    # --- Multi-document comparison (batch) --------------------------------
    files = request.files.getlist("files[]")
    valid_files = [f for f in files if f and f.filename and allowed_file(f.filename)]

    if len(valid_files) >= 2:
        texts = []
        names = []
        for f in valid_files:
            filename = secure_filename(f.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            f.save(save_path)
            try:
                texts.append(extract_text_from_file(save_path))
                names.append(filename)
            except Exception as exc:  # pylint: disable=broad-except
                flash(f"Could not read '{filename}': {exc}", "warning")

        if len(texts) < 2:
            flash("At least two readable documents are required.", "danger")
            return redirect(url_for("index"))

        result = compare_multiple_documents(texts)
        result["document_names"] = names
        result["mode"] = "multi"
        result["timestamp"] = datetime.utcnow().isoformat()
        result["id"] = str(uuid.uuid4())
        save_history(
            {
                "id": result["id"],
                "mode": "multi",
                "timestamp": result["timestamp"],
                "document_count": result["document_count"],
                "document_names": names,
            }
        )
        return render_template("results.html", result=result)

    # --- Two-document comparison ------------------------------------------
    text1 = get_text_from_request_field("text1", "file1")
    text2 = get_text_from_request_field("text2", "file2")

    if not text1 or not text2:
        flash("Please provide two documents or text inputs to compare.", "danger")
        return redirect(url_for("index"))

    result = compare_documents(text1, text2)
    result["mode"] = "pair"
    result["timestamp"] = datetime.utcnow().isoformat()
    result["id"] = str(uuid.uuid4())
    result["text1_preview"] = text1[:500]
    result["text2_preview"] = text2[:500]

    save_history(
        {
            "id": result["id"],
            "mode": "pair",
            "timestamp": result["timestamp"],
            "similarity_percentage": result["similarity_percentage"],
            "plagiarism_level": result["plagiarism_level"],
        }
    )
    return render_template("results.html", result=result)


@app.route("/api/check", methods=["POST"])
def api_check():
    """
    REST API endpoint for plagiarism detection.

    Accepts JSON body:
        {
            "text1": "...",
            "text2": "..."
        }

    Returns JSON with similarity_percentage, plagiarism_level, and
    sentence_matches.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    text1 = data.get("text1", "").strip()
    text2 = data.get("text2", "").strip()

    if not text1 or not text2:
        return jsonify({"error": "Both 'text1' and 'text2' are required."}), 400

    result = compare_documents(text1, text2)
    return jsonify(result)


@app.route("/history")
def history():
    """Display past comparison results."""
    entries = load_history()
    return render_template("history.html", entries=entries)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------


@app.errorhandler(413)
def request_entity_too_large(error):  # pylint: disable=unused-argument
    """Handle files that exceed the size limit."""
    flash("File too large. Maximum upload size is 16 MB.", "danger")
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found(error):  # pylint: disable=unused-argument
    """Handle 404 errors."""
    return render_template("404.html"), 404


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)
