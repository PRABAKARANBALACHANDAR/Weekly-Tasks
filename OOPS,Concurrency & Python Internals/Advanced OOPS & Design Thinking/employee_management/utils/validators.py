

class Validators:
    
    @staticmethod
    def validate_level(level):
        if not isinstance(level, int) or level < 1 or level > 3:
            raise ValueError("Employee level must be between 1 and 3")
        return True

    @staticmethod
    def validate_difficulty(difficulty):
        if not isinstance(difficulty, int) or difficulty < 1:
            raise ValueError("Difficulty must be a positive integer")
        return True

    @staticmethod
    def validate_team_size(members):
        if len(members) > 6:
            raise ValueError("Team size cannot exceed 6 members")
        return True

    @staticmethod
    def validate_role(role):
        valid_roles=['EMPLOYEE', 'CEO', 'CTO', 'COO', 'CFO', 'HR', 'MANAGER', 'ADMIN']
        if role.upper() not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {valid_roles}")
        return True

    @staticmethod
    def validate_project_status(status):
        valid_statuses=['pending', 'in-progress', 'completed']
        if status.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return True
