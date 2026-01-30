import json
import os
from datetime import datetime


class AnnouncementManager:
    def __init__(self, storage_file=None):
        self._storage_file=storage_file or os.path.join(os.path.dirname(__file__), "announcements.json")
        self._announcements=[]
        self._load()

    def _load(self):
        if os.path.exists(self._storage_file):
            try:
                with open(self._storage_file, "r") as f:
                    self._announcements=json.load(f)
            except Exception:
                self._announcements=[]
        else:
            self._announcements=[]

    def _save(self):
        with open(self._storage_file, "w") as f:
            json.dump(self._announcements, f, indent=2, ensure_ascii=False)

    def post_announcement(self, title, content):
        if not title or not content:
            raise ValueError("Title and content cannot be empty.")
        
        announcement={
            "id": len(self._announcements) + 1,
            "title": title,
            "content": content,
            "posted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "visible": True
        }
        self._announcements.append(announcement)
        self._save()
        return announcement["id"]

    def view_all_announcements(self):
        if not self._announcements:
            print("No announcements available.")
            return
        
        print("\n" + "="*60)
        print("ALL ANNOUNCEMENTS")
        print("="*60)
        for announcement in reversed(self._announcements):
            if announcement.get("visible", True):
                print(f"\nID: {announcement['id']}")
                print(f"Title: {announcement['title']}")
                print(f"Posted: {announcement['posted_at']}")
                print(f"Content: {announcement['content']}")
                print("-" * 60)

    def delete_announcement(self, announcement_id):
        try:
            announcement_id=int(announcement_id)
        except ValueError:
            raise ValueError("Invalid ID format.")
        
        for i, announcement in enumerate(self._announcements):
            if announcement["id"]==announcement_id:
                self._announcements.pop(i)
                self._save()
                return True
        
        raise ValueError(f"Announcement with ID {announcement_id} not found.")

    def edit_announcement(self, announcement_id, title=None, content=None):
        try:
            announcement_id=int(announcement_id)
        except ValueError:
            raise ValueError("Invalid ID format.")
        
        for announcement in self._announcements:
            if announcement["id"]==announcement_id:
                if title:
                    announcement["title"]=title
                if content:
                    announcement["content"]=content
                announcement["updated_at"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save()
                return True
        
        raise ValueError(f"Announcement with ID {announcement_id} not found.")

    def get_announcements_count(self):
        return len([a for a in self._announcements if a.get("visible", True)])
