import json
import os


class RecordExistsError(Exception):
    pass


class RecordNotFoundError(Exception):
    pass


class InvalidInputError(Exception):
    pass


class StudentRecord:
    def __init__(self, name: str, course: str, age: int, grade: str):
        self.name=name
        self.course=course
        self.age=age
        self.grade=grade

    def to_dict(self):
        return {"name": self.name, "course": self.course, "age": self.age, "grade": self.grade}

    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d["course"], d["age"], d["grade"])


class RecordManager:
    def __init__(self, storage_file=None):
        self._storage_file=storage_file or os.path.join(os.path.dirname(__file__), "students_records.json")
        self._records={}
        self._load()

    def _load(self):
        if os.path.exists(self._storage_file):
            try:
                with open(self._storage_file, "r") as f:
                    self._records=json.load(f)
            except Exception:
                self._records={}

    def _save(self):
        with open(self._storage_file, "w") as f:
            json.dump(self._records, f, indent=2)

    def _generate_id(self):
        if not self._records:
            return 1
        ids=sorted(int(k) for k in self._records.keys())
        for i, val in enumerate(ids, start=1):
            if val != i:
                return i
        return ids[-1] + 1

    def create_record(self, name, age, grade, course):
        name=name.strip().capitalize()

        for sid, details in self._records.items():
            if details["name"]==name:
                raise RecordExistsError(f"Record already exists for {name} with ID {sid}.")

        try:
            age=int(age)
        except ValueError:
            raise InvalidInputError("Invalid numeric input for age.")

        id_num=self._generate_id()
        rec=StudentRecord(name, course, int(age), grade)
        self._records[str(id_num)]=rec.to_dict()
        self._save()
        return id_num

    def create_record_interactive(self):
        name=input("Enter student name: ").strip().capitalize()
        try:
            age=int(input("Enter age: "))
            grade=input("Enter grade: ").strip().upper()
            course=input("Enter course enrolled: ").strip().upper()
            return self.create_record(name, age, grade, course)
        except ValueError:
            raise InvalidInputError("Invalid numeric input for age.")

    def list_records(self):
        return {int(k): StudentRecord.from_dict(v) for k, v in self._records.items()}

    def display_record(self):
        if not self._records:
            print("No records available.")
            return
        choice=input("Do you want to view all records or a specific student? (all/specific): ").lower()
        if choice=="all":
            print("\nAll Student Records:")
            for id_num, details in sorted(self._records.items(), key=lambda x: int(x[0])):
                print(f"ID: {id_num}, Name: {details['name']}, Age: {details['age']}, Grade: {details['grade']}, Course: {details['course']}")
        elif choice=="specific":
            try:
                id_num=str(int(input("Enter student ID to view details: ")))
            except ValueError:
                print("Invalid ID input.")
                return
            if id_num not in self._records:
                print("No records found for the student.")
                return
            details=self._records[id_num]
            print(f"\nStudent Record: ID: {id_num}, Name: {details['name']}, Age: {details['age']}, Grade: {details['grade']}, Course: {details['course']}")
        else:
            print("Invalid choice.")

    def update_record(self, id_num=None):
        try:
            if id_num is None:
                id_num=str(int(input("Enter student ID to update details: ")))
            else:
                id_num=str(int(id_num))
        except ValueError:
            raise InvalidInputError("Invalid ID input.")

        if id_num not in self._records:
            raise RecordNotFoundError("No records found for the student.")

        choice=input("What do you want to update? (age/grade/course): ").lower()
        if choice=="age":
            try:
                self._records[id_num]["age"]=int(input("Enter new age: "))
            except ValueError:
                raise InvalidInputError("Invalid age input.")
        elif choice=="grade":
            self._records[id_num]["grade"]=input("Enter new grade: ").upper()
        elif choice=="course":
            self._records[id_num]["course"]=input("Enter new course: ").upper()
        else:
            raise InvalidInputError("Unknown field to update.")

        self._save()
        return True

    def delete_record(self, id_num=None):
        try:
            if id_num is None:
                id_num=str(int(input("Enter student ID to delete details: ")))
            else:
                id_num=str(int(id_num))
        except ValueError:
            raise InvalidInputError("Invalid ID input.")

        if id_num not in self._records:
            raise RecordNotFoundError("No records found for the student.")

        del self._records[id_num]
        self._save()
        return True


def main():
    manager=RecordManager()
    while True:
        action=input("Choose action:\n 1.Add a record\n 2.View a record\n 3.Update a record\n 4.Delete a record\n 5.Exit\nEnter your choice: ").lower()
        match action:
            case "1" | "add":
                try:
                    sid=manager.create_record_interactive()
                    print(f"Record created with ID: {sid}")
                except Exception as e:
                    print(e)
            case "2" | "view":
                manager.display_record()
            case "3" | "update":
                try:
                    manager.update_record()
                except Exception as e:
                    print(e)
            case "4" | "delete":
                try:
                    manager.delete_record()
                except Exception as e:
                    print(e)
            case "5" | "exit":
                print("Exiting Student Record Manager. Goodbye!")
                break
            case _:
                print("Invalid action. Please try again.")

