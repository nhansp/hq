#!/usr/bin/env python

from flask import Flask, render_template, request, redirect, url_for, send_file
import json
import os
from datetime import datetime
import hashlib
import qrcode
import io
import base64

app = Flask(__name__)
DATA_FILE = 'queue.json'
USERDATA_FILE = 'userdata.json'

def load_queue():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_queue(queue):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=4)
        
def load_userdata():
    if not os.path.exists(USERDATA_FILE):
        return []
    with open(USERDATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def check_userdata(name: str) -> bool:
    f = load_userdata()
    for j in f:
        if j['id'] == name:
            print(f'check_userdata: {name} found')
            return True
    print(f'check_userdata: {name} not found')
    return False

def save_userdata(queue):
    with open(USERDATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=4)

def generate_qr_code_base64(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{qr_base64}"

def sort_queue(queue):
    priority_order = {
        'Emergency': 0, 
        'Normal': 1
    }
    patient_curr_status = {
        'Consulting': 0,
        'Waiting': 1,
        'Completed': 2
    }
    return sorted(queue, key=lambda p: (
        patient_curr_status[p['status']],
        priority_order[p['priority']], 
        p['arrival_time']
    ))

@app.route('/')
def index():
    queue = load_queue()
    queue = sort_queue(queue)
    return render_template('index.html', queue=queue, title="Trang chính", active_page='home')

@app.route('/add_patient', methods=['POST'])
def add_patient():
    queue = load_queue()
    userdata = load_userdata()
    name = request.form['name']
    priority = request.form['priority']
    arrival_time = request.form['arrival_time']
    status = request.form['status']
    patient_id = hashlib.md5((name + arrival_time).encode()).hexdigest()
    
    if (name[0:3] == "ID:"): 
        name = name[3:]
        print(f"Type: id, ID is {name}")
        if check_userdata(name):
            print(f"Server: found {name} in userdata. Modifying existing props")
            for x in queue:
                if x['id'] == name or x['name'] == name:
                    x['arrival_time'] = arrival_time
                    x['status'] = status
                    x['priority'] = priority
        else:
            print(f"Server: could not find {name} in userdata. Append as new")
            queue.append({
                'id': patient_id,
                'name': name,
                'priority': priority,
                'arrival_time': arrival_time,
                'status': status
            })
            userdata.append({
                'id': patient_id,
                'name': name
            })
    else:
        print(f"Type: name, Name is {name}")
        queue.append({
                'id': patient_id,
                'name': name,
                'priority': priority,
                'arrival_time': arrival_time,
                'status': status
            })
        userdata.append({
                'id': patient_id,
                'name': name
            })
    save_queue(queue)
    save_userdata(userdata)
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

@app.route('/patient_info/<string:patient_id>')
def patient_info(patient_id):
    queue = load_queue()
    patient = next((p for p in queue if p['id'] == patient_id), None)
    current_page_url = request.url
    qr_img_base64 = generate_qr_code_base64(current_page_url)
    if patient:
        return render_template('patient_info.html', patient=patient, title="Thông tin bệnh nhân", qr_img_base64=qr_img_base64)
    return redirect(url_for('index'))

@app.route('/delete_patient/<string:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    queue = load_queue()
    queue = [p for p in queue if p['id'] != patient_id]
    save_queue(queue)
    return redirect(url_for('index'))

@app.route('/update_status/<string:patient_id>', methods=['POST'])
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
