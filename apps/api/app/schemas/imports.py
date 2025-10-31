from pydantic import BaseModel, Field


class StudentCsvMapping(BaseModel):
    sis_id: str = Field(..., description="Column containing the SIS/student identifier")
    first_name: str = Field(..., description="Column containing the student's first name")
    last_name: str = Field(..., description="Column containing the student's last name")
    grade_level: str = Field(..., description="Column containing numeric grade level")
    school_name: str = Field(..., description="Column containing the school name")
    enrollment_status: str | None = Field(default=None, description="Column for enrollment status")
    ell_status: str | None = Field(default=None, description="Optional column for ELL flag")
    idea_flag: str | None = Field(default=None, description="Optional column for IDEA flag")


class CsvImportResult(BaseModel):
    rows_processed: int
    students_created: int
    students_updated: int
    errors: list[str]
    ingest_batch_id: str
