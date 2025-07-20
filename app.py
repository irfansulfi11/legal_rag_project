from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
import json
import os
from rag_engine import RAGEngine
import threading
import time

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a-strong-default-secret-key')

# --- RAG Engine Initialization ---
rag_engine = None
initialization_status = {"status": "initializing", "message": "System is starting up..."}

def initialize_rag_engine():
    """Initializes the RAGEngine in a background thread."""
    global rag_engine, initialization_status
    try:
        initialization_status["message"] = "Loading RAG engine..."
        rag_engine = RAGEngine()
        
        initialization_status["message"] = "Creating vector store... This may take a moment."
        rag_engine.initialize()
        
        initialization_status["status"] = "ready"
        initialization_status["message"] = "System is ready to answer questions."
        
    except Exception as e:
        initialization_status["status"] = "error"
        initialization_status["message"] = f"Fatal error during initialization: {str(e)}"
        print(f"Error during RAG initialization: {e}")

threading.Thread(target=initialize_rag_engine, daemon=True).start()


# --- Flask Routes ---

@app.route('/')
def index():
    """Acts as a gatekeeper, showing the loading page if the system is not ready."""
    if initialization_status["status"] != "ready":
        return render_template('loading.html')
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    """Renders the main chat interface."""
    if initialization_status["status"] != "ready":
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/status')
def status():
    """Endpoint for the frontend to check the RAG engine's initialization status."""
    return jsonify(initialization_status)

# --- CORRECTED STREAMING ENDPOINT ---
@app.route('/ask_stream', methods=['GET']) # Changed from POST to GET
def ask_question_stream():
    """Handles user questions and provides a streaming response."""
    if initialization_status["status"] != "ready":
        # This error case is for API clients; the frontend should already be enabled.
        return Response(json.dumps({"error": "System not ready"}), status=503, mimetype='application/json')
    
    # Get the question from URL query parameters instead of JSON body
    question = request.args.get('question', '').strip()
    
    if not question:
        return Response(json.dumps({"error": "Question parameter is missing"}), status=400, mimetype='application/json')
    
    def generate():
        """The generator function that streams the response."""
        try:
            yield f"data: {json.dumps({'type': 'start', 'question': question})}\n\n"
            for chunk in rag_engine.get_streaming_response(question):
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
        except Exception as e:
            print(f"Error during stream generation: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/health')
def health_check():
    """A simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "rag_status": initialization_status["status"],
        "message": initialization_status["message"]
    })

@app.errorhandler(404)
def not_found(error):
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "An internal server error occurred."}), 500


# --- Main Execution ---
if __name__ == '__main__':
    if not os.path.exists('data/it_act_2000_updated.pdf'):
        print("CRITICAL: PDF file not found in 'data/' directory. The app will not work.")
    
    if not os.path.exists('.env'):
        print("WARNING: .env file not found. Make sure GOOGLE_API_KEY is set in your environment.")
    
    print("Starting Legal RAG Chatbot...")
    print("Access the application at: http://12c7.0.0.1:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
