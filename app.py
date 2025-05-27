#!/usr/bin/env python

from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'queue.json'

def load_queue():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_queue(queue):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=4)

def sort_queue(queue):
    priority_order = {'Emergency': 0,'Normal': 1}
    return sorted(queue, key=lambda p: (priority_order[p['priority']], p['arrival_time']))

@app.route('/')
def index():
    queue = load_queue()
    queue = sort_queue(queue)
    return render_template('index.html', queue=queue, title="Trang chính", active_page='home')

@app.route('/add_patient', methods=['POST'])
def add_patient():
    queue = load_queue()
    name = request.form['name']
    priority = request.form['priority']
    arrival_time = request.form['arrival_time']
    status = request.form['status']
    patient_id = len(queue) + 1 
    queue.append({
        'id': patient_id,
        'name': name,
        'priority': priority,
        'arrival_time': arrival_time,
        'status': status
    })
    save_queue(queue)
    return redirect(url_for('index'))

@app.route('/queue_display')
def queue_display():
    queue = load_queue()
    queue = sort_queue(queue)
    return render_template('queue_list.html', queue=queue)

@app.route('/queue_stub')
def queue_stub():
    queue = load_queue()
    queue = sort_queue(queue)
    return render_template('queue_stub.html', queue=queue)

@app.route('/patient_info/<int:patient_id>')
def patient_info(patient_id):
    queue = load_queue()
    patient = next((p for p in queue if p['id'] == patient_id), None)
    if patient:
        return render_template('patient_info.html', patient=patient, title="Thông tin bệnh nhân")
    return redirect(url_for('index'))

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    queue = load_queue()
    queue = [p for p in queue if p['id'] != patient_id]
    save_queue(queue)
    return redirect(url_for('index'))

@app.route('/update_status/<int:patient_id>', methods=['POST'])
def update_status(patient_id):
    queue = load_queue()
    patient = next((p for p in queue if p['id'] == patient_id), None)
    if patient:
        patient['status'] = request.form['status']
        save_queue(queue)
    return redirect(url_for('index'))

@app.route('/call_next', methods=['POST'])
def call_next():
    queue = load_queue()
    if queue:
        queue = sort_queue(queue)
        queue.pop(0)
    save_queue(queue)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
