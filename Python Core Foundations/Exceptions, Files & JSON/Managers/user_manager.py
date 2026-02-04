import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class UserManager:
    def __init__(self):
        self._user_file=os.path.join(os.path.dirname(__file__), "..", "Data", "users.json")
        self._ensure_file_exists()
        self._seed_admin()

    def _ensure_file_exists(self):
        if not os.path.exists(os.path.dirname(self._user_file)):
            os.makedirs(os.path.dirname(self._user_file))
        if not os.path.exists(self._user_file):
            with open(self._user_file, 'w') as f:
                json.dump({}, f)

    def _load_users(self):
        try:
            with open(self._user_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_users(self, users):
        with open(self._user_file, 'w') as f:
            json.dump(users, f, indent=4)

    def _seed_admin(self):
        users=self._load_users()
        if "principal" not in users:
            users["principal"]={
                "password": "principal@123",
                "role": "Principal",
                "name": "Principal"
            }
            self._save_users(users)

    def authenticate(self, username, password):
        users=self._load_users()
        if username in users and users[username]["password"]==password:
            return users[username]
        return None

    def add_user(self, username, password, role, name):
        users=self._load_users()
        if username in users:
            return False 
        
        users[username]={
            "password": password,
            "role": role,
            "name": name
        }
        self._save_users(users)
        return True

    def user_exists(self, username):
        users=self._load_users()
        return username in users
