# hospital_dsa.py
import heapq
import random
from datetime import datetime
from collections import deque

# -----------------------------
# Disease → Specialist Mapping
# -----------------------------
DISEASE_SPECIALIST = {
    "Heart Pain": "Cardiology",
    "Chest Pain": "Cardiology",
    "Brain Tumor": "Neurology",
    "Headache": "Neurology",
    "Skin Infection": "Dermatology",
    "Bone Fracture": "Orthopedics",
    "Child Fever": "Pediatrics",
    "Depression": "Psychiatry",
    "Cancer": "Oncology",
    "Stomach Pain": "Gastroenterology",
    "Urine Problem": "Urology",
    "ENT Infection": "ENT",
}


# -----------------------------
# BASIC DSA CLASSES (Cleaned)
# -----------------------------
class Stack:
    """Billing Records (LIFO)"""
    def __init__(self):
        self._stack = []

    def push(self, item):
        self._stack.append(item)

    def all(self):
        return list(reversed(self._stack))
    
    def count(self):
        return len(self._stack)


class Queue:
    """Appointments (FIFO)"""
    def __init__(self):
        self._queue = deque()

    def enqueue(self, item):
        self._queue.append(item)

    def dequeue(self):
        return self._queue.popleft() if self._queue else None

    def all(self):
        return list(self._queue)
    
    def count(self):
        return len(self._queue)


class EmergencyQueue:
    """Emergency Patients (Min-Heap based Priority Queue)"""
    def __init__(self):
        self._heap = []
        self._counter = 0 # Ensures insertion order for ties

    def add(self, patient):
        # Priority: Lower number is higher priority
        priority = int(patient.get('priority', 5))
        heapq.heappush(
            self._heap,
            (priority, self._counter, patient)
        )
        self._counter += 1

    def get_emergency_list(self):
        """Returns sorted list (Highest priority first)"""
        # Sort by priority, then by counter (insertion order)
        return [p[2] for p in sorted(self._heap, key=lambda x: (x[0], x[1]))]

    def count(self):
        return len(self._heap)


class BSTNode:
    """Binary Search Tree Node for Patient IDs"""
    def __init__(self, patient):
        self.patient = patient
        self.left = None
        self.right = None


# -----------------------------
# MAIN HOSPITAL CLASS
# -----------------------------
class HospitalDSA:

    def __init__(self):
        self.doctors = {}
        self.patients = {}
        self.patient_bst_root = None

        self.emergency = EmergencyQueue()
        self.billing = Stack()
        self.appointments = Queue()

        self.specializations = [
            "Cardiology", "Neurology", "Orthopedics", "Dermatology", "ENT",
            "General Medicine", "Pediatrics", "Oncology", "Psychiatry",
            "Urology", "Gastroenterology"
        ]

    # ... (Doctor, Specialist Mapping functions remain the same)

    def generate_doctors(self, count=80, start_id=2000):
        # (Function logic remains the same)
        first = ["Ayesha", "Bilal", "Ali", "Sana", "Raza", "Fatima", "Hira", "Zara"]
        last = ["Khan", "Shah", "Malik", "Rizvi", "Butt", "Mirza"]
        did = start_id
        for _ in range(count):
            did += 1
            name = f"Dr. {random.choice(first)} {random.choice(last)}"
            spec = random.choice(self.specializations)
            self.add_doctor(did, name, spec)
            
    def add_doctor(self, doctor_id, name, specialization):
        self.doctors[doctor_id] = {
            "id": doctor_id,
            "name": name,
            "specialization": specialization
        }

    def filter_doctors(self, specialization=None):
        result = []
        for d in self.doctors.values():
            if specialization and d["specialization"] != specialization:
                continue
            result.append(d)
        return result
    
    def get_specialist_for_disease(self, disease):
        return DISEASE_SPECIALIST.get(disease, "General Medicine")
        
    # -----------------------------
    # PATIENT REGISTRATION (Fixed to accept Priority and Emergency)
    # -----------------------------
    def register_patient_and_suggest_doctors(self, name, age, disease, priority=5, emergency=False):
        
        # 1. Determine Specialist
        specialization = self.get_specialist_for_disease(disease)
        suggested_doctors = self.filter_doctors(specialization=specialization)

        # 2. Register Patient (Simulated auto-confirmation for Flask form submission)
        pid = random.randint(10000, 99999)
        self.add_patient(pid, name, age, disease, priority=priority, emergency=emergency, specialization=specialization)
        
        # 3. Return registration details
        return pid, specialization, suggested_doctors

    # -----------------------------
    # ADD PATIENT (Fixed BST insertion)
    # -----------------------------
    def add_patient(self, pid, name, age, disease, priority=5, emergency=False, specialization=None):
        patient = {
            "id": pid, "name": name, "age": age,
            "disease": disease, "priority": int(priority),
            "emergency": emergency, "specialization": specialization,
            "created_at": datetime.now(), "doctor_id": None
        }

        self.patients[pid] = patient

        # Emergency queue (Priority Heap)
        if emergency or patient["priority"] <= 3:
            self.emergency.add(patient)

        # Insert into BST (for searching/retrieval)
        self.patient_bst_root = self._insert_bst(self.patient_bst_root, patient)

    def _insert_bst(self, root, patient):
        if not root:
            return BSTNode(patient)
        
        # Insert by Patient ID
        if patient["id"] < root.patient["id"]:
            root.left = self._insert_bst(root.left, patient)
        elif patient["id"] > root.patient["id"]:
            root.right = self._insert_bst(root.right, patient)
            
        # Ignore if ID is the same (shouldn't happen with random IDs)
        return root

    # ... (Other methods remain the same)
    
    def all_patients(self):
        return sorted(self.patients.values(), key=lambda x: x["id"])

    def book_specialist_appointment(self, pid, doctor_id, time_str):
        # (Function logic remains the same)
        if pid not in self.patients:
            return False, "❌ Patient not found."

        if doctor_id not in self.doctors:
            return False, "❌ Doctor not found."

        patient_spec = self.patients[pid].get("specialization") # Use .get for safety
        doctor_spec = self.doctors[doctor_id]["specialization"]

        if patient_spec != doctor_spec:
            return False, f"❌ Wrong doctor selected! Patient needs {patient_spec}."

        appointment = {
            "appointment_id": random.randint(1111, 9999),
            "pid": pid,
            "patient_name": self.patients[pid]["name"],
            "doctor_id": doctor_id,
            "doctor_name": self.doctors[doctor_id]["name"],
            "time": time_str,
            "created_at": datetime.now()
        }

        self.appointments.enqueue(appointment)
        return True, "✅ Appointment booked successfully!"

    def list_appointments(self):
        return self.appointments.all()
    
    def add_bill(self, pid, amount):
        # (Function logic remains the same)
        if pid not in self.patients:
            return False

        amount = float(amount)
        self.billing.push(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')} • "
            f"{self.patients[pid]['name']} (ID: {pid}) — Rs{amount:,.2f}"
        )
        return True

    def get_bills(self):
        return self.billing.all()

    def get_emergency_list(self):
        return self.emergency.get_emergency_list()

    def emergency_count(self):
        return self.emergency.count()