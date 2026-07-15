"""Analytics service — aggregates progress, quiz, streak, and heatmap data."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------
_analytics_cache: dict[str, dict[str, Any]] = {}

# ---------------------------------------------------------------------------
# NEET syllabus structure (91 chapters)
# ---------------------------------------------------------------------------
SUBJECTS = {
    "physics": {
        "name": "Physics",
        "chapters": [
            "Physical World", "Units & Measurement", "Motion in a Straight Line",
            "Motion in a Plane", "Laws of Motion", "Work, Energy & Power",
            "System of Particles & Rotational Motion", "Gravitation",
            "Mechanical Properties of Solids", "Mechanical Properties of Fluids",
            "Thermal Properties of Matter", "Thermodynamics", "Kinetic Theory",
            "Oscillations", "Waves", "Electric Charges & Fields",
            "Electrostatic Potential & Capacitance", "Current Electricity",
            "Moving Charges & Magnetism", "Magnetism & Matter",
            "Electromagnetic Induction", "Alternating Current",
            "Electromagnetic Waves", "Ray Optics & Optical Instruments",
            "Wave Optics", "Dual Nature of Radiation & Matter", "Atoms",
            "Nuclei", "Semiconductor Electronics",
        ],
    },
    "chemistry": {
        "name": "Chemistry",
        "chapters": [
            "Some Basic Concepts of Chemistry", "Structure of Atom",
            "Classification of Elements", "Chemical Bonding",
            "States of Matter", "Thermodynamics", "Equilibrium",
            "Redox Reactions", "Hydrogen", "s-Block Elements",
            "p-Block Elements", "Organic Chemistry – Basic Principles",
            "Hydrocarbons", "Environmental Chemistry", "Solid State",
            "Solutions", "Electrochemistry", "Chemical Kinetics",
            "Surface Chemistry", "General Principles of Metallurgy",
            "p-Block Elements (XII)", "d- & f-Block Elements",
            "Coordination Compounds", "Haloalkanes & Haloarenes",
            "Alcohols, Phenols & Ethers", "Aldehydes, Ketones & Carboxylic Acids",
            "Amines", "Biomolecules", "Polymers", "Chemistry in Everyday Life",
        ],
    },
    "biology": {
        "name": "Biology",
        "chapters": [
            "The Living World", "Biological Classification", "Plant Kingdom",
            "Animal Kingdom", "Morphology of Flowering Plants", "Anatomy of Flowering Plants",
            "Structural Organisation in Animals", "Cell: The Unit of Life",
            "Biomolecules", "Cell Cycle & Cell Division", "Transport in Plants",
            "Mineral Nutrition", "Photosynthesis in Higher Plants", "Respiration in Plants",
            "Plant Growth & Development", "Digestion & Absorption",
            "Breathing & Exchange of Gases", "Body Fluids & Circulation",
            "Excretory Products & Elimination", "Locomotion & Movement",
            "Neural Control & Coordination", "Chemical Coordination & Integration",
            "Reproduction in Organisms", "Sexual Reproduction in Flowering Plants",
            "Human Reproduction", "Reproductive Health", "Principles of Inheritance",
            "Molecular Basis of Inheritance", "Evolution", "Human Health & Disease",
            "Strategies for Enhancement in Food Production", "Microbes in Human Welfare",
            "Biotechnology: Principles", "Biotechnology: Applications", "Organisms & Populations",
            "Ecosystem", "Biodiversity & Conservation", "Environmental Issues",
            "Animal Husbandry", "Plant Breeding", "Tissue Culture",
            "Genetics & Evolution", "Ecology", "Human Physiology",
            "Plant Physiology", "Cell Biology", "Reproduction",
            "Modern Biology", "Applied Biology", "Environmental Biology",
            "Genetics", "Molecular Biology", "Evolution & Adaptation",
            "Immunology", "Microbiology", "Biotechnology",
            "Ecology & Environment", "Plant Anatomy", "Plant Taxonomy",
            "Animal Anatomy", "Animal Taxonomy", "Physiology",
            "Developmental Biology", "Biochemistry", "Cell & Molecular Biology",
            "Genomics", "Proteomics", "Systems Biology",
        ],
    },
}

TOTAL_CHAPTERS = sum(len(s["chapters"]) for s in SUBJECTS.values())

# ---------------------------------------------------------------------------
# Mock data generators
# ---------------------------------------------------------------------------

def _generate_seed(profile_id: str) -> dict[str, Any]:
    """Generate deterministic-but-varied mock data for a profile."""
    random.seed(hash(profile_id) % (2**32))

    now = datetime.now()
    total_study_days = random.randint(30, 180)
    start_date = now - timedelta(days=total_study_days)

    # Subject completion rates
    subject_data: dict[str, dict[str, Any]] = {}
    total_completed = 0
    for subj_key, subj_info in SUBJECTS.items():
        completed = random.randint(int(len(subj_info["chapters"]) * 0.2),
                                   int(len(subj_info["chapters"]) * 0.85))
        total_completed += completed
        subject_data[subj_key] = {
            "name": subj_info["name"],
            "total": len(subj_info["chapters"]),
            "completed": completed,
            "chapters": subj_info["chapters"],
        }

    # Daily progress
    daily: list[dict[str, Any]] = []
    for i in range(total_study_days):
        d = start_date + timedelta(days=i)
        daily.append({
            "date": d.strftime("%Y-%m-%d"),
            "subtopics_completed": random.randint(0, 8),
            "study_minutes": random.randint(30, 240),
        })

    # Quiz history
    quizzes: list[dict[str, Any]] = []
    num_quizzes = random.randint(10, 60)
    for i in range(num_quizzes):
        d = start_date + timedelta(days=random.randint(0, total_study_days - 1))
        q_count = random.choice([15, 20, 30, 45])
        correct = int(q_count * random.uniform(0.35, 0.92))
        quizzes.append({
            "date": d.strftime("%Y-%m-%d"),
            "score": correct,
            "question_count": q_count,
            "subject": random.choice(list(SUBJECTS.keys())),
        })
    quizzes.sort(key=lambda x: x["date"])

    # Streaks
    longest_streak = random.randint(5, 45)
    current_streak = random.randint(0, longest_streak)

    total_study_hours = round(sum(d["study_minutes"] for d in daily) / 60, 1)
    total_quizzes = len(quizzes)
    avg_quiz = round(sum(q["score"] / q["question_count"] * 100 for q in quizzes) / max(total_quizzes, 1), 1)

    return {
        "total_study_days": total_study_days,
        "total_subtopics_completed": total_completed * 3,  # ~3 subtopics per chapter
        "total_chapters_completed": total_completed,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "avg_quiz_score": avg_quiz,
        "total_quizzes_taken": total_quizzes,
        "total_study_hours": total_study_hours,
        "subject_data": subject_data,
        "daily": daily,
        "quizzes": quizzes,
        "start_date": start_date.strftime("%Y-%m-%d"),
    }


def _get_or_generate(profile_id: str) -> dict[str, Any]:
    if profile_id not in _analytics_cache:
        _analytics_cache[profile_id] = _generate_seed(profile_id)
    return _analytics_cache[profile_id]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_overview(profile_id: str) -> dict[str, Any]:
    """Return top-level analytics overview."""
    data = _get_or_generate(profile_id)
    return {
        "total_study_days": data["total_study_days"],
        "total_subtopics_completed": data["total_subtopics_completed"],
        "total_chapters_completed": data["total_chapters_completed"],
        "current_streak": data["current_streak"],
        "longest_streak": data["longest_streak"],
        "avg_quiz_score": data["avg_quiz_score"],
        "total_quizzes_taken": data["total_quizzes_taken"],
        "total_study_hours": data["total_study_hours"],
    }


def get_daily_progress(profile_id: str, days: int = 30) -> list[dict[str, Any]]:
    """Return daily progress for the last *days*."""
    data = _get_or_generate(profile_id)
    return data["daily"][-days:]


def get_subject_progress(profile_id: str) -> list[dict[str, Any]]:
    """Return per-subject completion breakdown."""
    data = _get_or_generate(profile_id)
    result: list[dict[str, Any]] = []
    for subj_key, subj in data["subject_data"].items():
        pct = round(subj["completed"] / subj["total"] * 100, 1) if subj["total"] else 0
        result.append({
            "subject_id": subj_key,
            "subject_name": subj["name"],
            "completed": subj["completed"],
            "total": subj["total"],
            "percentage": pct,
        })
    return result


def get_quiz_trends(profile_id: str, days: int = 30) -> list[dict[str, Any]]:
    """Return quiz scores over the last *days*."""
    data = _get_or_generate(profile_id)
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    return [
        {"date": q["date"], "score": q["score"], "question_count": q["question_count"]}
        for q in data["quizzes"]
        if q["date"] >= cutoff
    ]


def get_weak_areas(profile_id: str) -> list[dict[str, Any]]:
    """Detect chapters with low completion or poor quiz performance."""
    data = _get_or_generate(profile_id)
    random.seed(hash(profile_id + "weak") % (2**32))

    weak: list[dict[str, Any]] = []
    for subj_key, subj in data["subject_data"].items():
        for ch_name in subj["chapters"]:
            progress_pct = random.randint(5, 95)
            quiz_avg = round(random.uniform(25, 85), 1) if random.random() > 0.3 else None
            last_studied = (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d") if random.random() > 0.2 else None

            if progress_pct < 40 or (quiz_avg is not None and quiz_avg < 50):
                priority = "high" if progress_pct < 25 or (quiz_avg is not None and quiz_avg < 35) else "medium" if progress_pct < 40 else "low"
                weak.append({
                    "chapter_id": f"{subj_key}-{hash(ch_name) % 10000:04d}",
                    "chapter_name": ch_name,
                    "subject_name": subj["name"],
                    "progress_pct": progress_pct,
                    "quiz_avg": quiz_avg,
                    "last_studied": last_studied,
                    "priority": priority,
                })

    weak.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]])
    return weak


def get_heatmap_data(profile_id: str, days: int = 90) -> list[dict[str, Any]]:
    """Return study activity heatmap data (date + intensity)."""
    data = _get_or_generate(profile_id)
    daily = data["daily"][-days:]
    return [
        {"date": d["date"], "minutes": d["study_minutes"], "subtopics": d["subtopics_completed"]}
        for d in daily
    ]


def get_streak_calendar(profile_id: str, month: str | None = None) -> dict[str, Any]:
    """Return streak calendar data for a given month (YYYY-MM) or current month."""
    data = _get_or_generate(profile_id)
    if month:
        year, mon = map(int, month.split("-"))
    else:
        year, mon = datetime.now().year, datetime.now().month

    # Build a set of dates with study activity
    study_dates = {d["date"] for d in data["daily"] if d["study_minutes"] > 0}

    # Build calendar grid
    import calendar
    cal = calendar.Calendar()
    days_in_month = cal.monthdayscalendar(year, mon)

    calendar_days: list[dict[str, Any]] = []
    for week in days_in_month:
        for day_num in week:
            if day_num == 0:
                continue
            d_str = f"{year:04d}-{mon:02d}-{day_num:02d}"
            calendar_days.append({
                "date": d_str,
                "has_activity": d_str in study_dates,
                "day": day_num,
            })

    return {
        "month": month or f"{year:04d}-{mon:02d}",
        "current_streak": data["current_streak"],
        "longest_streak": data["longest_streak"],
        "calendar": calendar_days,
    }


def get_performance_prediction(profile_id: str) -> dict[str, Any]:
    """Generate a performance prediction based on mock trends."""
    data = _get_or_generate(profile_id)
    random.seed(hash(profile_id + "pred") % (2**32))

    avg_score = data["avg_quiz_score"]
    trend = random.uniform(-5, 15)
    predicted = min(99, max(10, avg_score + trend))

    # Subject predictions
    subject_preds: list[dict[str, Any]] = []
    for subj_key, subj in data["subject_data"].items():
        subj_pct = round(subj["completed"] / subj["total"] * 100, 1)
        pred_score = min(99, max(10, subj_pct * random.uniform(0.7, 1.1)))
        subject_preds.append({
            "subject_id": subj_key,
            "subject_name": subj["name"],
            "completion_pct": subj_pct,
            "predicted_score": round(pred_score, 1),
        })

    return {
        "predicted_score": round(predicted, 1),
        "confidence": round(random.uniform(55, 85), 1),
        "trend": "improving" if trend > 0 else "declining" if trend < -2 else "stable",
        "days_to_exam": random.randint(30, 180),
        "subject_predictions": subject_preds,
        "recommendations": _generate_recommendations(data, predicted),
    }


def _generate_recommendations(data: dict[str, Any], predicted: float) -> list[str]:
    """Generate study recommendations based on performance."""
    recs: list[str] = []
    if data["current_streak"] < 3:
        recs.append("Try to maintain a daily study streak of at least 3 days.")
    if data["avg_quiz_score"] < 60:
        recs.append("Focus on concept revision before attempting more quizzes.")
    if data["total_study_hours"] < 100:
        recs.append("Increase daily study time to at least 2 hours.")

    for subj_key, subj in data["subject_data"].items():
        pct = subj["completed"] / subj["total"] * 100
        if pct < 30:
            recs.append(f"{subj['name']} needs more attention — only {pct:.0f}% complete.")

    if predicted < 50:
        recs.append("Consider focusing on high-weightage chapters first.")
    elif predicted > 80:
        recs.append("Great progress! Focus on mock tests and time management.")

    return recs
