from fastapi import HTTPException
class PatientManagementError(Exception):
    def __init__(self, message: str, error_code: str="PATIENT_ERROR"):
        self.message=message
        self.error_code=error_code
        super().__init__(self.message)

class PatientNotFoundError(PatientManagementError):
    def __init__(self, patient_id: int):
        super().__init__(
            message=f"Patient with ID {patient_id} not found",
            error_code="PATIENT_NOT_FOUND"
        )
        self.patient_id=patient_id

class HealthRecordNotFoundError(PatientManagementError):
    def __init__(self, record_id: int):
        super().__init__(
            message=f"Health record with ID {record_id} not found",
            error_code="HEALTH_RECORD_NOT_FOUND"
        )
        self.record_id=record_id

class PatientRecordNotFoundError(PatientManagementError):
    def __init__(self, record_id: int):
        super().__init__(
            message=f"Patient record with ID {record_id} not found",
            error_code="RECORD_NOT_FOUND"
        )
        self.record_id=record_id

class InvalidRecordTypeError(PatientManagementError):
    def __init__(self, record_type: str):
        super().__init__(
            message=f"Invalid record type: {record_type}. Allowed types: summary, prescription, health_data, diagnosis",
            error_code="INVALID_RECORD_TYPE"
        )
        self.record_type=record_type

class DatabaseOperationError(PatientManagementError):
    def __init__(self, operation: str, details: str):
        super().__init__(
            message=f"Database operation '{operation}' failed: {details}",
            error_code="DATABASE_ERROR"
        )
        self.operation=operation
        self.details=details

class DuplicateRecordError(PatientManagementError):
    def __init__(self, patient_id: int, record_type: str):
        super().__init__(
            message=f"Record type '{record_type}' already exists for patient {patient_id}",
            error_code="DUPLICATE_RECORD"
        )
        self.patient_id=patient_id
        self.record_type=record_type

class ValidationError(PatientManagementError):
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Validation failed for field '{field}': {reason}",
            error_code="VALIDATION_ERROR"
        )
        self.field=field
        self.reason=reason