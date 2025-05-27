import heapq
from datetime import datetime

priority_map = {'Emergency': 0, 'Normal': 1}
pq = []  
patients_dict = {}  

def add_patient(pq, patients_dict, patient):
    pid = patient['id']
    patients_dict[pid] = patient
    heapq.heappush(
        pq,
        (
            priority_map[patient['priority']],
            datetime.strptime(patient['arrival_time'], "%Y-%m-%d %H:%M"),
            pid
        )
    )

def call_next(pq, patients_dict):
    if pq:
        _, _, pid = heapq.heappop(pq)
        return patients_dict.pop(pid)  
    else:
        return None

def update_status(patients_dict, pid, new_status):
    if pid in patients_dict:
        patients_dict[pid]['status'] = new_status
        return True
    return False

add_patient(pq, patients_dict, {
    'id': 1,
    'name': 'Nguyen Van A',
    'priority': 'Emergency',
    'arrival_time': "2024-05-27 15:20",
    'status': 'Waiting'
})
add_patient(pq, patients_dict, {
    'id': 2,
    'name': 'Tran Van B',
    'priority': 'Normal',
    'arrival_time': "2024-05-27 15:21",
    'status': 'Waiting'
})

update_status(patients_dict, 1, 'In treatment')

print("Next patient:", call_next(pq, patients_dict))

print("Remaining patients:", patients_dict)

print(patients_dict[2])
