"""Roadmap generator — AI-powered personalized study plan for NEET aspirants."""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# NEET syllabus structure with weightage and dependencies
NEET_SYLLABUS = {
    "Physics": {
        "weight": 1.2,
        "11th": [
            ("Units and Measurements", 2, []),
            ("Motion in a Straight Line", 3, []),
            ("Motion in a Plane", 4, ["Motion in a Straight Line"]),
            ("Laws of Motion", 5, []),
            ("Work, Energy and Power", 5, ["Laws of Motion"]),
            ("Rotational Motion", 6, ["Laws of Motion", "Motion in a Plane"]),
            ("Gravitation", 4, []),
            ("Mechanical Properties of Solids", 3, []),
            ("Mechanical Properties of Fluids", 3, ["Mechanical Properties of Solids"]),
            ("Thermal Properties of Matter", 4, []),
            ("Thermodynamics", 5, ["Thermal Properties of Matter"]),
            ("Kinetic Theory", 3, ["Thermodynamics"]),
            ("Oscillations", 4, []),
            ("Waves", 4, ["Oscillations"]),
        ],
        "12th": [
            ("Electric Charges and Fields", 5, []),
            ("Electrostatic Potential and Capacitance", 5, ["Electric Charges and Fields"]),
            ("Current Electricity", 6, []),
            ("Moving Charges and Magnetism", 6, ["Current Electricity"]),
            ("Magnetism and Matter", 4, ["Moving Charges and Magnetism"]),
            ("Electromagnetic Induction", 5, ["Magnetism and Matter"]),
            ("Alternating Current", 5, ["Electromagnetic Induction"]),
            ("Electromagnetic Waves", 3, ["Alternating Current"]),
            ("Ray Optics and Optical Instruments", 6, []),
            ("Wave Optics", 5, ["Ray Optics and Optical Instruments"]),
            ("Dual Nature of Radiation and Matter", 4, []),
            ("Atoms", 3, ["Dual Nature of Radiation and Matter"]),
            ("Nuclei", 3, ["Atoms"]),
            ("Semiconductor Electronics", 5, []),
        ],
    },
    "Chemistry": {
        "weight": 1.1,
        "11th": [
            ("Some Basic Concepts of Chemistry", 2, []),
            ("Atomic Structure", 4, []),
            ("Classification of Elements and Periodicity", 3, ["Atomic Structure"]),
            ("Chemical Bonding and Molecular Structure", 5, []),
            ("States of Matter", 3, []),
            ("Thermodynamics", 5, []),
            ("Equilibrium", 6, ["Thermodynamics"]),
            ("Redox Reactions", 3, []),
            ("Hydrogen", 2, []),
            ("The s-Block Elements", 3, []),
            ("The p-Block Elements", 4, ["The s-Block Elements"]),
            ("Organic Chemistry - Some Basic Principles", 5, []),
            ("Hydrocarbons", 4, ["Organic Chemistry - Some Basic Principles"]),
        ],
        "12th": [
            ("The Solid State", 2, []),
            ("Solutions", 4, []),
            ("Electrochemistry", 5, ["Solutions"]),
            ("Chemical Kinetics", 5, ["Equilibrium"]),
            ("Surface Chemistry", 2, []),
            ("General Principles of Metallurgy", 2, []),
            ("The p-Block Elements", 5, []),
            ("The d and f Block Elements", 4, []),
            ("Coordination Compounds", 5, ["Chemical Bonding and Molecular Structure"]),
            ("Haloalkanes and Haloarenes", 4, ["Organic Chemistry - Some Basic Principles"]),
            ("Alcohols, Phenols and Ethers", 4, ["Haloalkanes and Haloarenes"]),
            ("Aldehydes, Ketones and Carboxylic Acids", 5, ["Alcohols, Phenols and Ethers"]),
            ("Amines", 3, ["Aldehydes, Ketones and Carboxylic Acids"]),
            ("Biomolecules", 3, []),
            ("Polymers", 2, []),
            ("Chemistry in Everyday Life", 2, []),
        ],
    },
    "Biology": {
        "weight": 1.0,
        "11th": [
            ("The Living World", 2, []),
            ("Biological Classification", 3, ["The Living World"]),
            ("Plant Kingdom", 3, ["Biological Classification"]),
            ("Morphology of Flowering Plants", 3, []),
            ("Anatomy of Flowering Plants", 4, ["Morphology of Flowering Plants"]),
            ("Cell: The Unit of Life", 3, []),
            ("Biomolecules", 4, ["Cell: The Unit of Life"]),
            ("Cell Cycle and Cell Division", 4, ["Biomolecules"]),
            ("Photosynthesis in Higher Plants", 5, []),
            ("Respiration in Plants", 5, ["Photosynthesis in Higher Plants"]),
            ("Plant Growth and Development", 3, ["Photosynthesis in Higher Plants"]),
            ("Animal Kingdom", 4, []),
            ("Structural Organisation in Animals", 3, ["Animal Kingdom"]),
            ("Body Fluids and Circulation", 4, []),
            ("Breathing and Exchange of Gases", 4, []),
            ("Excretory Products and Their Elimination", 4, []),
            ("Locomotion and Movement", 2, []),
            ("Neural Control and Coordination", 4, []),
            ("Chemical Coordination and Integration", 3, ["Neural Control and Coordination"]),
        ],
        "12th": [
            ("Reproduction in Organisms", 3, []),
            ("Sexual Reproduction in Flowering Plants", 5, ["Reproduction in Organisms"]),
            ("Human Reproduction", 5, ["Reproduction in Organisms"]),
            ("Reproductive Health", 3, ["Human Reproduction"]),
            ("Principles of Inheritance and Variation", 6, ["Cell Cycle and Cell Division"]),
            ("Molecular Basis of Inheritance", 6, ["Principles of Inheritance and Variation"]),
            ("Evolution", 5, ["Molecular Basis of Inheritance"]),
            ("Human Health and Diseases", 4, []),
            ("Strategies for Enhancement in Food Production", 2, []),
            ("Microbes in Human Welfare", 3, []),
            ("Biotechnology: Principles and Processes", 5, ["Molecular Basis of Inheritance"]),
            ("Biotechnology and Its Applications", 4, ["Biotechnology: Principles and Processes"]),
            ("Organisms and Populations", 3, []),
            ("Ecosystem", 4, ["Organisms and Populations"]),
            ("Biodiversity and Conservation", 3, ["Ecosystem"]),
        ],
    },
}


class RoadmapStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    MISSED = "missed"


@dataclass
class ChapterTarget:
    """A single chapter target within a day's plan."""

    id: str
    name: str
    subject: str
    grade: str
    priority_score: int
    estimated_minutes: int
    completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "subject": self.subject,
            "grade": self.grade,
            "priority_score": self.priority_score,
            "estimated_minutes": self.estimated_minutes,
            "completed": self.completed,
        }


@dataclass
class DayPlan:
    """A single day's study plan."""

    date: str
    day_number: int
    day_type: str  # "study", "revision", "mock_test", "buffer"
    chapters: list[ChapterTarget]
    total_minutes: int = 0
    status: RoadmapStatus = RoadmapStatus.PENDING

    def __post_init__(self) -> None:
        if not self.total_minutes:
            self.total_minutes = sum(c.estimated_minutes for c in self.chapters)

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "day_number": self.day_number,
            "day_type": self.day_type,
            "chapters": [c.to_dict() for c in self.chapters],
            "total_minutes": self.total_minutes,
            "status": self.status.value,
        }


@dataclass
class Roadmap:
    """A complete generated roadmap."""

    id: str
    profile_id: str
    exam_date: str
    daily_hours: int
    total_days: int
    study_days: int
    revision_days: int
    mock_test_days: int
    buffer_days: int
    days: list[DayPlan]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "exam_date": self.exam_date,
            "daily_hours": self.daily_hours,
            "total_days": self.total_days,
            "study_days": self.study_days,
            "revision_days": self.revision_days,
            "mock_test_days": self.mock_test_days,
            "buffer_days": self.buffer_days,
            "days": [d.to_dict() for d in self.days],
            "created_at": self.created_at,
        }


class RoadmapGenerator:
    """Generate personalized NEET study roadmaps."""

    def __init__(self) -> None:
        self._roadmaps: dict[str, Roadmap] = {}
        self._progress: dict[str, dict[str, bool]] = {}

    def generate_roadmap(
        self,
        profile_id: str,
        exam_date: date,
        daily_hours: int = 6,
        completed_chapters: list[str] | None = None,
        weak_areas: list[str] | None = None,
    ) -> Roadmap:
        """Generate a complete study roadmap from today to exam date."""
        today = date.today()
        total_days = (exam_date - today).days
        if total_days < 7:
            total_days = 7

        roadmap_id = str(uuid.uuid4())
        daily_minutes = daily_hours * 60

        # Build chapter list with priorities
        all_chapters = self._build_chapter_list(completed_chapters or [], weak_areas or [])

        # Calculate day types
        study_cycle = 8  # 8 study days, then 1 revision, 1 buffer
        revision_interval = 10
        mock_test_interval = 14

        days: list[DayPlan] = []
        chapter_idx = 0
        study_days = 0
        revision_days = 0
        mock_test_days = 0
        buffer_days = 0

        for day_num in range(1, total_days + 1):
            current_date = today + timedelta(days=day_num - 1)
            date_str = current_date.isoformat()

            # Determine day type
            if day_num % mock_test_interval == 0:
                day_type = "mock_test"
                mock_test_days += 1
                day_plan = DayPlan(
                    date=date_str,
                    day_number=day_num,
                    day_type=day_type,
                    chapters=[
                        ChapterTarget(
                            id=str(uuid.uuid4()),
                            name="Full Mock Test (180 questions, 3 hours)",
                            subject="All",
                            grade="11th/12th",
                            priority_score=95,
                            estimated_minutes=180,
                        )
                    ],
                )
            elif day_num % revision_interval == 0:
                day_type = "revision"
                revision_days += 1
                # Revision: review previous chapters
                revision_chapters = self._get_revision_chapters(days, 3)
                day_plan = DayPlan(
                    date=date_str,
                    day_number=day_num,
                    day_type=day_type,
                    chapters=revision_chapters,
                )
            elif day_num % study_cycle == 0:
                day_type = "buffer"
                buffer_days += 1
                day_plan = DayPlan(
                    date=date_str,
                    day_number=day_num,
                    day_type=day_type,
                    chapters=[],
                )
            else:
                day_type = "study"
                study_days += 1
                # Assign chapters for this day
                day_chapters = self._assign_daily_chapters(all_chapters, chapter_idx, daily_minutes)
                chapter_idx += len(day_chapters)
                day_plan = DayPlan(
                    date=date_str,
                    day_number=day_num,
                    day_type=day_type,
                    chapters=day_chapters,
                )

            days.append(day_plan)

        roadmap = Roadmap(
            id=roadmap_id,
            profile_id=profile_id,
            exam_date=exam_date.isoformat(),
            daily_hours=daily_hours,
            total_days=total_days,
            study_days=study_days,
            revision_days=revision_days,
            mock_test_days=mock_test_days,
            buffer_days=buffer_days,
            days=days,
            created_at=datetime.now(UTC).isoformat(),
        )

        self._roadmaps[roadmap_id] = roadmap
        self._progress[profile_id] = {roadmap_id: False for _ in days}

        logger.info(
            "roadmap.generated",
            profile_id=profile_id,
            roadmap_id=roadmap_id,
            total_days=total_days,
            chapters=len(all_chapters),
        )

        return roadmap

    def get_daily_plan(self, roadmap_id: str, target_date: date) -> DayPlan | None:
        """Get the plan for a specific date."""
        roadmap = self._roadmaps.get(roadmap_id)
        if not roadmap:
            return None

        date_str = target_date.isoformat()
        for day in roadmap.days:
            if day.date == date_str:
                return day
        return None

    def adjust_roadmap(
        self,
        roadmap_id: str,
        completed_chapters: list[str],
    ) -> Roadmap | None:
        """Recalculate roadmap based on completed chapters."""
        roadmap = self._roadmaps.get(roadmap_id)
        if not roadmap:
            return None

        completed_set = set(completed_chapters)
        for day in roadmap.days:
            if day.day_type == "study":
                for chapter in day.chapters:
                    if chapter.id in completed_set:
                        chapter.completed = True

        # Recalculate remaining schedule
        remaining_days = [d for d in roadmap.days if d.status == RoadmapStatus.PENDING]
        if remaining_days:
            today_str = date.today().isoformat()
            for day in remaining_days:
                if day.date < today_str and day.day_type == "study":
                    day.status = RoadmapStatus.MISSED

        logger.info(
            "roadmap.adjusted",
            roadmap_id=roadmap_id,
            completed=len(completed_chapters),
        )

        return roadmap

    def get_roadmap_progress(self, roadmap_id: str) -> dict[str, Any] | None:
        """Get progress summary for a roadmap."""
        roadmap = self._roadmaps.get(roadmap_id)
        if not roadmap:
            return None

        total_chapters = sum(len(d.chapters) for d in roadmap.days)
        completed_chapters = sum(1 for d in roadmap.days for c in d.chapters if c.completed)
        study_days_completed = sum(
            1 for d in roadmap.days if d.day_type == "study" and d.status == RoadmapStatus.COMPLETED
        )

        return {
            "roadmap_id": roadmap_id,
            "total_chapters": total_chapters,
            "completed_chapters": completed_chapters,
            "completion_pct": round(completed_chapters / max(total_chapters, 1) * 100, 1),
            "study_days_completed": study_days_completed,
            "total_study_days": roadmap.study_days,
            "days_remaining": sum(
                1
                for d in roadmap.days
                if d.date >= date.today().isoformat() and d.status == RoadmapStatus.PENDING
            ),
        }

    def _build_chapter_list(
        self,
        completed: list[str],
        weak_areas: list[str],
    ) -> list[dict[str, Any]]:
        """Build prioritized chapter list."""
        chapters = []
        completed_set = set(completed)
        weak_set = set(weak_areas)

        for subject, data in NEET_SYLLABUS.items():
            for grade_key in ["11th", "12th"]:
                for name, weight, deps in data[grade_key]:
                    if name in completed_set:
                        continue

                    # Base priority from NEET weightage
                    priority = weight * 10

                    # Boost weak areas
                    if name in weak_set:
                        priority *= 1.5

                    # Subject weight multiplier
                    priority *= data["weight"]

                    chapters.append(
                        {
                            "name": name,
                            "subject": subject,
                            "grade": grade_key,
                            "priority": min(int(priority), 100),
                            "weight": weight,
                            "dependencies": deps,
                        }
                    )

        # Sort by priority (descending), then by dependencies
        chapters.sort(key=lambda c: (-c["priority"], len(c["dependencies"])))
        return chapters

    def _assign_daily_chapters(
        self,
        all_chapters: list[dict[str, Any]],
        start_idx: int,
        daily_minutes: int,
    ) -> list[ChapterTarget]:
        """Assign chapters for a single day, balancing subjects."""
        if start_idx >= len(all_chapters):
            return []

        # Take 2-3 chapters per day
        remaining_minutes = daily_minutes
        assigned: list[ChapterTarget] = []
        subjects_today: set[str] = set()

        for i in range(start_idx, min(start_idx + 5, len(all_chapters))):
            ch = all_chapters[i]

            # Skip if already assigned a chapter from this subject today
            if ch["subject"] in subjects_today and len(assigned) >= 2:
                continue

            # Estimate time based on weight
            est_minutes = max(30, ch["weight"] * 15)

            if est_minutes > remaining_minutes:
                continue

            assigned.append(
                ChapterTarget(
                    id=str(uuid.uuid4()),
                    name=ch["name"],
                    subject=ch["subject"],
                    grade=ch["grade"],
                    priority_score=ch["priority"],
                    estimated_minutes=est_minutes,
                )
            )

            subjects_today.add(ch["subject"])
            remaining_minutes -= est_minutes

            if len(assigned) >= 3:
                break

        return assigned

    def _get_revision_chapters(
        self,
        days: list[DayPlan],
        count: int,
    ) -> list[ChapterTarget]:
        """Get chapters to revise from previous study days."""
        previous_chapters: list[ChapterTarget] = []
        for day in reversed(days):
            if day.day_type == "study":
                previous_chapters.extend(day.chapters)

        # Pick random chapters for revision
        selected = random.sample(
            previous_chapters,
            min(count, len(previous_chapters)),
        )

        return [
            ChapterTarget(
                id=str(uuid.uuid4()),
                name=f"Revise: {c.name}",
                subject=c.subject,
                grade=c.grade,
                priority_score=max(50, c.priority_score),
                estimated_minutes=min(c.estimated_minutes, 45),
            )
            for c in selected
        ]
