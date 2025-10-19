"""CV/Resume parsing service."""

import logging
import re
from pathlib import Path
from typing import Optional, List
from io import BytesIO

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

from src.models.cv_profile import CVProfile

logger = logging.getLogger(__name__)


class CVParser:
    """Parse CV/Resume files and extract structured information."""

    SUPPORTED_FORMATS = [".pdf", ".txt", ".docx"]

    def parse_file(self, file_path: str) -> CVProfile:
        """
        Parse CV from file path.

        Args:
            file_path: Path to CV file

        Returns:
            CVProfile with extracted information

        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"CV file not found: {file_path}")

        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Read file content
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        return self.parse_bytes(file_bytes, path.suffix.lower())

    def parse_bytes(self, file_bytes: bytes, file_extension: str) -> CVProfile:
        """
        Parse CV from file bytes.

        Args:
            file_bytes: File content as bytes
            file_extension: File extension (e.g., '.pdf', '.txt', '.docx')

        Returns:
            CVProfile with extracted information

        Raises:
            ValueError: If file format is not supported
        """
        if file_extension not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: {file_extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Extract raw text based on file type
        if file_extension == ".pdf":
            raw_text = self._extract_from_pdf(file_bytes)
        elif file_extension == ".docx":
            raw_text = self._extract_from_docx(file_bytes)
        elif file_extension == ".txt":
            raw_text = file_bytes.decode("utf-8", errors="ignore")
        else:
            raise ValueError(f"Unsupported format: {file_extension}")

        # Parse structured information
        return self._parse_text_to_profile(raw_text)

    def _extract_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF file."""
        if PdfReader is None:
            raise ImportError(
                "PyPDF2 is required for PDF parsing. "
                "Install it with: pip install PyPDF2"
            )

        try:
            pdf_file = BytesIO(file_bytes)
            pdf_reader = PdfReader(pdf_file)

            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())

            return "\n".join(text_parts)

        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    def _extract_from_docx(self, file_bytes: bytes) -> str:
        """Extract text from DOCX file."""
        if Document is None:
            raise ImportError(
                "python-docx is required for DOCX parsing. "
                "Install it with: pip install python-docx"
            )

        try:
            docx_file = BytesIO(file_bytes)
            doc = Document(docx_file)

            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)

            return "\n".join(text_parts)

        except Exception as e:
            logger.error(f"Failed to extract text from DOCX: {str(e)}")
            raise ValueError(f"Failed to parse DOCX: {str(e)}")

    def _parse_text_to_profile(self, raw_text: str) -> CVProfile:
        """
        Parse raw CV text into structured CVProfile.

        Uses simple regex patterns to extract common CV sections.

        Args:
            raw_text: Raw text extracted from CV

        Returns:
            CVProfile with parsed information
        """
        # Extract name (usually first line or after "Name:")
        full_name = self._extract_name(raw_text)

        # Extract email
        email = self._extract_email(raw_text)

        # Extract phone
        phone = self._extract_phone(raw_text)

        # Extract summary/objective
        summary = self._extract_summary(raw_text)

        # Extract skills
        skills = self._extract_skills(raw_text)

        # Extract experience
        experience = self._extract_experience(raw_text)

        # Extract education
        education = self._extract_education(raw_text)

        return CVProfile(
            full_name=full_name,
            email=email,
            phone=phone,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            raw_text=raw_text,
        )

    def _extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name from CV."""
        lines = text.strip().split("\n")

        # Try to find "Name:" pattern
        for line in lines[:10]:  # Check first 10 lines
            if re.search(r"name\s*[:：]", line, re.IGNORECASE):
                name = re.sub(r"name\s*[:：]\s*", "", line, flags=re.IGNORECASE).strip()
                if name and len(name) < 100:
                    return name

        # Otherwise, assume first non-empty line is the name
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) < 100 and not re.search(r"@|http|www", line):
                return line

        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from CV."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from CV."""
        # Match common phone formats
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        matches = re.findall(phone_pattern, text)

        # Return first match that looks like a phone number
        for match in matches:
            if 8 <= len(re.sub(r'[^\d]', '', match)) <= 15:
                return match.strip()

        return None

    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary or objective."""
        # Look for summary/objective sections
        patterns = [
            r'(?:summary|objective|profile|about)\s*[:：]?\s*\n(.*?)(?:\n\n|\n[A-Z])',
            r'(?:professional\s+summary|career\s+objective)\s*[:：]?\s*\n(.*?)(?:\n\n|\n[A-Z])',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                # Limit to ~200 words
                words = summary.split()[:200]
                return " ".join(words)

        # If no explicit summary, use first paragraph
        paragraphs = text.split("\n\n")
        for para in paragraphs[:3]:
            para = para.strip()
            if 50 < len(para) < 1000 and not re.search(r"@|http|^[A-Z\s]+$", para):
                return para[:500]

        return None

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from CV."""
        skills = []

        # Look for skills section
        skills_pattern = r'(?:skills|technologies|technical\s+skills)\s*[:：]?\s*\n(.*?)(?:\n\n|\n[A-Z][a-z]+\s*[:：])'
        match = re.search(skills_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            skills_text = match.group(1)
            # Split by common delimiters
            skill_list = re.split(r'[,;•\n]', skills_text)
            skills = [s.strip() for s in skill_list if s.strip() and len(s.strip()) < 50]
            return skills[:20]  # Limit to 20 skills

        # Common tech keywords to look for
        common_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "React", "Angular", "Vue",
            "Node.js", "Django", "Flask", "Spring", "AWS", "Azure", "GCP",
            "Docker", "Kubernetes", "SQL", "NoSQL", "MongoDB", "PostgreSQL",
            "Machine Learning", "AI", "Data Science", "TensorFlow", "PyTorch",
            "Git", "CI/CD", "Agile", "Scrum", "REST API", "GraphQL"
        ]

        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                skills.append(skill)

        return list(set(skills))[:15]  # Remove duplicates, limit to 15

    def _extract_experience(self, text: str) -> List[str]:
        """Extract work experience entries."""
        experience = []

        # Look for experience section
        exp_pattern = r'(?:experience|employment|work\s+history)\s*[:：]?\s*\n(.*?)(?:\n\n[A-Z]|$)'
        match = re.search(exp_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            exp_text = match.group(1)

            # Split by job entries (typically start with company/role)
            # Look for patterns like "Title at Company" or "Company - Title"
            lines = exp_text.split("\n")
            current_entry = []

            for line in lines:
                line = line.strip()
                if not line:
                    if current_entry:
                        experience.append(" ".join(current_entry))
                        current_entry = []
                else:
                    current_entry.append(line)

            if current_entry:
                experience.append(" ".join(current_entry))

            # Limit each entry to reasonable length
            experience = [e[:200] for e in experience if len(e) > 10]
            return experience[:5]  # Return top 5 experiences

        return []

    def _extract_education(self, text: str) -> List[str]:
        """Extract education entries."""
        education = []

        # Look for education section
        edu_pattern = r'(?:education|academic|qualifications)\s*[:：]?\s*\n(.*?)(?:\n\n[A-Z]|$)'
        match = re.search(edu_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            edu_text = match.group(1)
            lines = edu_text.split("\n")

            for line in lines:
                line = line.strip()
                # Look for degree-like patterns
                if re.search(r'\b(B\.?S\.?|M\.?S\.?|Ph\.?D\.?|Bachelor|Master|Doctorate|Diploma)\b', line, re.IGNORECASE):
                    if len(line) > 10:
                        education.append(line[:200])

            return education[:3]  # Return top 3 education entries

        return []
