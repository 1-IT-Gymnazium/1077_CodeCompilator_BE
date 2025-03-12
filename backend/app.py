from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import uuid
import re

app = Flask(__name__)
CORS(app)  # Povolení CORS pro všechny domény

# Funkce pro vytvoření slug z textu
def slugify(text):
    # Převedeme na malá písmena a nahradíme mezery pomlčkami
    slug = text.lower().strip().replace(' ', '-')
    # Odstraníme všechny znaky kromě alfanumerických a pomlček
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Odstraníme duplicitní pomlčky
    slug = re.sub(r'-+', '-', slug)
    return slug

# Složka pro ukládání úloh
TASKS_FOLDER = os.path.join(os.path.dirname(__file__), 'tasks')
if not os.path.exists(TASKS_FOLDER):
    os.makedirs(TASKS_FOLDER)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Vrátí seznam všech úloh"""
    tasks = []
    for filename in os.listdir(TASKS_FOLDER):
        if filename.endswith('.json'):
            with open(os.path.join(TASKS_FOLDER, filename), 'r', encoding='utf-8') as f:
                task = json.load(f)
                tasks.append(task)
    return jsonify(tasks)

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Vrátí detail konkrétní úlohy"""
    try:
        # Najdeme soubor úlohy podle ID
        for filename in os.listdir(TASKS_FOLDER):
            if filename.endswith('.json'):
                with open(os.path.join(TASKS_FOLDER, filename), 'r', encoding='utf-8') as f:
                    task = json.load(f)
                    if task.get('id') == task_id:
                        return jsonify(task)
        
        return jsonify({"error": "Úloha nenalezena"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Vytvoří novou úlohu"""
    task_data = request.json
    
    # Generování ID pro novou úlohu
    task_id = str(uuid.uuid4())
    task_data['id'] = task_id
    
    # Vytvoření slug z názvu úlohy
    title_slug = slugify(task_data.get('title', 'untitled'))
    
    # Přidáme část UUID pro zajištění unikátnosti
    short_uuid = task_id.split('-')[0]
    file_name = f"{title_slug}-{short_uuid}"
    
    # Uložení úlohy do souboru
    with open(os.path.join(TASKS_FOLDER, f"{file_name}.json"), 'w', encoding='utf-8') as f:
        json.dump(task_data, f, ensure_ascii=False, indent=2)
    
    # Uložíme název souboru do task_data
    task_data['file_name'] = file_name
    
    return jsonify(task_data), 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Aktualizuje existující úlohu"""
    task_data = request.json
    task_data['id'] = task_id
    
    # Najdeme existující soubor úlohy
    file_name = None
    for filename in os.listdir(TASKS_FOLDER):
        if filename.endswith('.json'):
            with open(os.path.join(TASKS_FOLDER, filename), 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                if file_data.get('id') == task_id:
                    file_name = filename.replace('.json', '')
                    break
    
    if not file_name:
        # Pokud soubor nenajdeme, vytvoříme nový název
        title_slug = slugify(task_data.get('title', 'untitled'))
        short_uuid = task_id.split('-')[0]
        file_name = f"{title_slug}-{short_uuid}"
    
    # Uložení aktualizované úlohy
    with open(os.path.join(TASKS_FOLDER, f"{file_name}.json"), 'w', encoding='utf-8') as f:
        json.dump(task_data, f, ensure_ascii=False, indent=2)
    
    # Uložíme název souboru do task_data
    task_data['file_name'] = file_name
    
    return jsonify(task_data)

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Smaže úlohu"""
    try:
        # Najdeme soubor úlohy podle ID
        file_to_delete = None
        for filename in os.listdir(TASKS_FOLDER):
            if filename.endswith('.json'):
                with open(os.path.join(TASKS_FOLDER, filename), 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    if file_data.get('id') == task_id:
                        file_to_delete = filename
                        break
        
        if file_to_delete:
            os.remove(os.path.join(TASKS_FOLDER, file_to_delete))
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Úloha nenalezena"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)