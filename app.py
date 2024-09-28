from flask import Flask, request, jsonify, send_file
from flask_restful import Api, Resource
import os
import markdown2
import uuid
import language_tool_python

app = Flask(__name__)
api = Api(app)

# Directory to store notes
NOTES_DIR = 'notes'
os.makedirs(NOTES_DIR, exist_ok=True)

# Initialize the LanguageTool API
tool = language_tool_python.LanguageTool('en-US')

def home():
    return "Welcome to the Markdown Note-taking App! Available endpoints: /check-grammar, /save-note, /list-notes, /render-note/<note_id>"


class CheckGrammar(Resource):
    def post(self):
        data = request.json
        if 'text' not in data:
            return {"error": "Text is required for grammar check"}, 400
        
        text = data['text']
        matches = tool.check(text)
        corrections = [{"error": match.message, "suggestions": match.replacements, "offset": match.offset, "length": match.errorLength} for match in matches]
        
        return {"corrections": corrections}, 200


class SaveNote(Resource):
    def post(self):
        data = request.json
        if 'markdown_text' not in data:
            return {"error": "Markdown text is required"}, 400
        
        markdown_text = data['markdown_text']
        note_id = str(uuid.uuid4())
        file_path = os.path.join(NOTES_DIR, f"{note_id}.md")
        
        with open(file_path, "w") as f:
            f.write(markdown_text)
        
        return {"message": "Note saved successfully", "note_id": note_id}, 201


class ListNotes(Resource):
    def get(self):
        notes = [file.split('.')[0] for file in os.listdir(NOTES_DIR) if file.endswith(".md")]
        return {"notes": notes}, 200


class RenderNoteHTML(Resource):
    def get(self, note_id):
        file_path = os.path.join(NOTES_DIR, f"{note_id}.md")
        if not os.path.exists(file_path):
            return {"error": "Note not found"}, 404
        
        with open(file_path, "r") as f:
            markdown_content = f.read()
        
        html_content = markdown2.markdown(markdown_content)
        
        return {"html_content": html_content}, 200


# Add the endpoints to the API
api.add_resource(CheckGrammar, "/check-grammar")
api.add_resource(SaveNote, "/save-note")
api.add_resource(ListNotes, "/list-notes")
api.add_resource(RenderNoteHTML, "/render-note/<string:note_id>")


if __name__ == "__main__":
    app.run(debug=True)
