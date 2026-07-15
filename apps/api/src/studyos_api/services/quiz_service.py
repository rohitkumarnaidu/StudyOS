"""Quiz service — session management, question bank, mistake tracking."""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Question bank — NEET-style MCQs (Physics, Chemistry, Biology)
# ---------------------------------------------------------------------------

QUESTION_BANK: list[dict[str, Any]] = [
    # ── Physics 11th ──────────────────────────────────────────────────────
    {
        "id": "q_phys_001",
        "chapter_id": "ch_physics_11_01",
        "topic": "Units and Measurement",
        "question_text": "The dimensional formula of Planck's constant is:",
        "option_a": "[ML²T⁻¹]",
        "option_b": "[ML²T⁻³]",
        "option_c": "[MLT⁻¹]",
        "option_d": "[ML²T⁻²]",
        "correct_answer": "A",
        "explanation": "Planck's constant h = E/ν. Energy E has dimension [ML²T⁻²] and frequency ν has [T⁻¹]. Therefore h = [ML²T⁻²]/[T⁻¹] = [ML²T⁻¹].",
        "difficulty": 2,
    },
    {
        "id": "q_phys_002",
        "chapter_id": "ch_physics_11_02",
        "topic": "Motion in a Straight Line",
        "question_text": "A car accelerates from rest at 2 m/s². What is its velocity after 10 seconds?",
        "option_a": "10 m/s",
        "option_b": "20 m/s",
        "option_c": "15 m/s",
        "option_d": "25 m/s",
        "correct_answer": "B",
        "explanation": "Using v = u + at, with u = 0, a = 2 m/s², t = 10 s: v = 0 + 2 × 10 = 20 m/s.",
        "difficulty": 1,
    },
    {
        "id": "q_phys_003",
        "chapter_id": "ch_physics_11_03",
        "topic": "Laws of Motion",
        "question_text": "A force of 10 N acts on a body of mass 2 kg. The acceleration produced is:",
        "option_a": "2 m/s²",
        "option_b": "5 m/s²",
        "option_c": "10 m/s²",
        "option_d": "20 m/s²",
        "correct_answer": "B",
        "explanation": "From Newton's second law, F = ma. Therefore a = F/m = 10/2 = 5 m/s².",
        "difficulty": 1,
    },
    {
        "id": "q_phys_004",
        "chapter_id": "ch_physics_11_04",
        "topic": "Work, Energy and Power",
        "question_text": "A body of mass 5 kg is moving with a velocity of 10 m/s. Its kinetic energy is:",
        "option_a": "250 J",
        "option_b": "500 J",
        "option_c": "100 J",
        "option_d": "50 J",
        "correct_answer": "A",
        "explanation": "KE = ½mv² = ½ × 5 × 10² = ½ × 5 × 100 = 250 J.",
        "difficulty": 1,
    },
    {
        "id": "q_phys_005",
        "chapter_id": "ch_physics_11_05",
        "topic": "Gravitation",
        "question_text": "The escape velocity from Earth's surface is approximately:",
        "option_a": "7.2 km/s",
        "option_b": "11.2 km/s",
        "option_c": "15.2 km/s",
        "option_d": "21.2 km/s",
        "correct_answer": "B",
        "explanation": "Escape velocity vₑ = √(2gR). For Earth, g = 9.8 m/s², R = 6400 km, giving vₑ ≈ 11.2 km/s.",
        "difficulty": 2,
    },
    {
        "id": "q_phys_006",
        "chapter_id": "ch_physics_11_06",
        "topic": "Mechanical Properties of Fluids",
        "question_text": "Bernoulli's theorem is based on the conservation of:",
        "option_a": "Mass",
        "option_b": "Momentum",
        "option_c": "Energy",
        "option_d": "Angular momentum",
        "correct_answer": "C",
        "explanation": "Bernoulli's theorem states that for an ideal fluid in streamline flow, the sum of pressure energy, kinetic energy, and potential energy per unit volume remains constant — a statement of energy conservation.",
        "difficulty": 2,
    },
    # ── Physics 12th ──────────────────────────────────────────────────────
    {
        "id": "q_phys_007",
        "chapter_id": "ch_physics_12_01",
        "topic": "Electric Charges and Fields",
        "question_text": "Two point charges +4 µC and +1 µC are placed 30 cm apart in vacuum. The ratio of forces experienced by them is:",
        "option_a": "4 : 1",
        "option_b": "1 : 4",
        "option_c": "1 : 1",
        "option_d": "2 : 1",
        "correct_answer": "C",
        "explanation": "By Newton's third law, the force exerted by each charge on the other is equal in magnitude and opposite in direction. The ratio is 1 : 1.",
        "difficulty": 2,
    },
    {
        "id": "q_phys_008",
        "chapter_id": "ch_physics_12_02",
        "topic": "Current Electricity",
        "question_text": "A wire of resistance 10 Ω is stretched to double its length. Its new resistance is:",
        "option_a": "20 Ω",
        "option_b": "40 Ω",
        "option_c": "5 Ω",
        "option_d": "80 Ω",
        "correct_answer": "B",
        "explanation": "When length is doubled, area becomes half (volume constant). R = ρL/A, so new R = ρ(2L)/(A/2) = 4ρL/A = 4R = 40 Ω.",
        "difficulty": 3,
    },
    {
        "id": "q_phys_009",
        "chapter_id": "ch_physics_12_03",
        "topic": "Magnetic Effects of Current",
        "question_text": "The magnetic field at the center of a circular coil of radius R carrying current I is:",
        "option_a": "µ₀I/2R",
        "option_b": "µ₀I/4R",
        "option_c": "µ₀I/2πR",
        "option_d": "µ₀IR/2",
        "correct_answer": "A",
        "explanation": "For a single-turn circular coil, B = µ₀I/2R at the center, derived from the Biot-Savart law.",
        "difficulty": 2,
    },
    {
        "id": "q_phys_010",
        "chapter_id": "ch_physics_12_04",
        "topic": "Electromagnetic Induction",
        "question_text": "Lenz's law is a consequence of the law of conservation of:",
        "option_a": "Charge",
        "option_b": "Momentum",
        "option_c": "Energy",
        "option_d": "Mass",
        "correct_answer": "C",
        "explanation": "Lenz's law states that the direction of induced current opposes the change causing it. This ensures energy is conserved — otherwise, a perpetual motion machine would be possible.",
        "difficulty": 2,
    },
    {
        "id": "q_phys_011",
        "chapter_id": "ch_physics_12_05",
        "topic": "Optics",
        "question_text": "The refractive index of glass is 1.5. The speed of light in glass is:",
        "option_a": "3 × 10⁸ m/s",
        "option_b": "2 × 10⁸ m/s",
        "option_c": "1.5 × 10⁸ m/s",
        "option_d": "4.5 × 10⁸ m/s",
        "correct_answer": "B",
        "explanation": "v = c/n = (3 × 10⁸)/1.5 = 2 × 10⁸ m/s.",
        "difficulty": 1,
    },
    {
        "id": "q_phys_012",
        "chapter_id": "ch_physics_12_06",
        "topic": "Dual Nature of Matter",
        "question_text": "The de Broglie wavelength of an electron accelerated through a potential V is proportional to:",
        "option_a": "V",
        "option_b": "√V",
        "option_c": "1/V",
        "option_d": "1/√V",
        "correct_answer": "D",
        "explanation": "λ = h/√(2meV), so λ ∝ 1/√V.",
        "difficulty": 3,
    },
    # ── Chemistry 11th ────────────────────────────────────────────────────
    {
        "id": "q_chem_001",
        "chapter_id": "ch_chemistry_11_01",
        "topic": "Some Basic Concepts of Chemistry",
        "question_text": "The number of moles of CO₂ in 22 g of CO₂ is:",
        "option_a": "0.25 mol",
        "option_b": "0.5 mol",
        "option_c": "1.0 mol",
        "option_d": "2.0 mol",
        "correct_answer": "B",
        "explanation": "Molar mass of CO₂ = 12 + 2(16) = 44 g/mol. Moles = 22/44 = 0.5 mol.",
        "difficulty": 1,
    },
    {
        "id": "q_chem_002",
        "chapter_id": "ch_chemistry_11_02",
        "topic": "Structure of Atom",
        "question_text": "The maximum number of electrons in a subshell with l = 3 is:",
        "option_a": "6",
        "option_b": "10",
        "option_c": "14",
        "option_d": "18",
        "correct_answer": "C",
        "explanation": "For l = 3 (f subshell), number of orbitals = 2l + 1 = 7. Maximum electrons = 7 × 2 = 14.",
        "difficulty": 2,
    },
    {
        "id": "q_chem_003",
        "chapter_id": "ch_chemistry_11_03",
        "topic": "Classification of Elements",
        "question_text": "Which of the following has the highest electronegativity?",
        "option_a": "Oxygen",
        "option_b": "Nitrogen",
        "option_c": "Fluorine",
        "option_d": "Chlorine",
        "correct_answer": "C",
        "explanation": "Fluorine has the highest electronegativity (3.98 on Pauling scale) among all elements.",
        "difficulty": 1,
    },
    {
        "id": "q_chem_004",
        "chapter_id": "ch_chemistry_11_04",
        "topic": "Chemical Bonding",
        "question_text": "The shape of SF₆ molecule is:",
        "option_a": "Square planar",
        "option_b": "Octahedral",
        "option_c": "Trigonal bipyramidal",
        "option_d": "Tetrahedral",
        "correct_answer": "B",
        "explanation": "SF₆ has sp³d² hybridization with 6 bond pairs and 0 lone pairs, giving an octahedral geometry.",
        "difficulty": 2,
    },
    {
        "id": "q_chem_005",
        "chapter_id": "ch_chemistry_11_05",
        "topic": "Thermodynamics",
        "question_text": "For a spontaneous reaction at constant T and P, the change in Gibbs free energy (ΔG) is:",
        "option_a": "Positive",
        "option_b": "Negative",
        "option_c": "Zero",
        "option_d": "Infinite",
        "correct_answer": "B",
        "explanation": "A spontaneous process at constant temperature and pressure has ΔG < 0 (negative).",
        "difficulty": 1,
    },
    {
        "id": "q_chem_006",
        "chapter_id": "ch_chemistry_11_06",
        "topic": "Equilibrium",
        "question_text": "The pH of 0.001 M HCl solution is:",
        "option_a": "1",
        "option_b": "2",
        "option_c": "3",
        "option_d": "4",
        "correct_answer": "C",
        "explanation": "HCl is a strong acid, so [H⁺] = 0.001 M = 10⁻³ M. pH = -log[H⁺] = -log(10⁻³) = 3.",
        "difficulty": 1,
    },
    # ── Chemistry 12th ────────────────────────────────────────────────────
    {
        "id": "q_chem_007",
        "chapter_id": "ch_chemistry_12_01",
        "topic": "Solid State",
        "question_text": "The number of atoms per unit cell in a face-centered cubic (fcc) lattice is:",
        "option_a": "1",
        "option_b": "2",
        "option_c": "4",
        "option_d": "6",
        "correct_answer": "C",
        "explanation": "In fcc: 8 corner atoms × 1/8 + 6 face atoms × 1/2 = 1 + 3 = 4 atoms per unit cell.",
        "difficulty": 2,
    },
    {
        "id": "q_chem_008",
        "chapter_id": "ch_chemistry_12_02",
        "topic": "Solutions",
        "question_text": "The elevation in boiling point of a solution is directly proportional to:",
        "option_a": "Molarity",
        "option_b": "Molality",
        "option_c": "Mole fraction of solvent",
        "option_d": "Volume of solution",
        "correct_answer": "B",
        "explanation": "ΔTb = Kb × m, where m is the molality of the solution. This is a colligative property.",
        "difficulty": 2,
    },
    {
        "id": "q_chem_009",
        "chapter_id": "ch_chemistry_12_03",
        "topic": "Electrochemistry",
        "question_text": "The standard electrode potential of hydrogen electrode is:",
        "option_a": "0 V",
        "option_b": "1 V",
        "option_c": "-1 V",
        "option_d": "0.5 V",
        "correct_answer": "A",
        "explanation": "By convention, the standard hydrogen electrode (SHE) is assigned a potential of exactly 0 V at all temperatures.",
        "difficulty": 1,
    },
    {
        "id": "q_chem_010",
        "chapter_id": "ch_chemistry_12_04",
        "topic": "Chemical Kinetics",
        "question_text": "For a first-order reaction, the half-life is:",
        "option_a": "Independent of initial concentration",
        "option_b": "Directly proportional to initial concentration",
        "option_c": "Inversely proportional to initial concentration",
        "option_d": "Proportional to the square of initial concentration",
        "correct_answer": "A",
        "explanation": "For a first-order reaction, t₁/₂ = 0.693/k, which is independent of the initial concentration.",
        "difficulty": 2,
    },
    {
        "id": "q_chem_011",
        "chapter_id": "ch_chemistry_12_05",
        "topic": "d- and f-Block Elements",
        "question_text": "Which of the following ions is colored in aqueous solution?",
        "option_a": "Sc³⁺",
        "option_b": "Ti⁴⁺",
        "option_c": "Cu²⁺",
        "option_d": "Zn²⁺",
        "correct_answer": "C",
        "explanation": "Cu²⁺ has the electronic configuration [Ar]3d⁹ with unpaired electrons, allowing d-d transitions that produce color. Sc³⁺, Ti⁴⁺, and Zn²⁺ have no unpaired d electrons.",
        "difficulty": 2,
    },
    {
        "id": "q_chem_012",
        "chapter_id": "ch_chemistry_12_06",
        "topic": "Organic Chemistry — Alcohols",
        "question_text": "Lucas reagent is a mixture of:",
        "option_a": "Conc. HCl + anhydrous ZnCl₂",
        "option_b": "Conc. HNO₃ + anhydrous ZnCl₂",
        "option_c": "Conc. H₂SO₄ + anhydrous ZnCl₂",
        "option_d": "Conc. HCl + anhydrous CuCl₂",
        "correct_answer": "A",
        "explanation": "Lucas reagent is concentrated HCl with anhydrous ZnCl₂, used to distinguish primary, secondary, and tertiary alcohols.",
        "difficulty": 2,
    },
    # ── Biology 11th ──────────────────────────────────────────────────────
    {
        "id": "q_bio_001",
        "chapter_id": "ch_biology_11_01",
        "topic": "The Living World",
        "question_text": "The basic unit of classification is:",
        "option_a": "Genus",
        "option_b": "Species",
        "option_c": "Family",
        "option_d": "Order",
        "correct_answer": "B",
        "explanation": "Species is the fundamental unit of biological classification — a group of organisms that can interbreed and produce fertile offspring.",
        "difficulty": 1,
    },
    {
        "id": "q_bio_002",
        "chapter_id": "ch_biology_11_02",
        "topic": "Cell — The Unit of Life",
        "question_text": "Which organelle is known as the 'powerhouse of the cell'?",
        "option_a": "Golgi apparatus",
        "option_b": "Ribosome",
        "option_c": "Mitochondria",
        "option_d": "Lysosome",
        "correct_answer": "C",
        "explanation": "Mitochondria generate ATP through oxidative phosphorylation, earning the title 'powerhouse of the cell'.",
        "difficulty": 1,
    },
    {
        "id": "q_bio_003",
        "chapter_id": "ch_biology_11_03",
        "topic": "Biomolecules",
        "question_text": "The bond between two amino acids in a protein is called:",
        "option_a": "Glycosidic bond",
        "option_b": "Peptide bond",
        "option_c": "Phosphodiester bond",
        "option_d": "Hydrogen bond",
        "correct_answer": "B",
        "explanation": "A peptide bond (—CO—NH—) forms between the carboxyl group of one amino acid and the amino group of another through a condensation reaction.",
        "difficulty": 1,
    },
    {
        "id": "q_bio_004",
        "chapter_id": "ch_biology_11_04",
        "topic": "Photosynthesis",
        "question_text": "The oxygen released during photosynthesis comes from:",
        "option_a": "CO₂",
        "option_b": "H₂O",
        "option_c": "Glucose",
        "option_d": "Chlorophyll",
        "correct_answer": "B",
        "explanation": "During the light reactions, water is split (photolysis): 2H₂O → 4H⁺ + 4e⁻ + O₂. The O₂ is released as a byproduct.",
        "difficulty": 2,
    },
    {
        "id": "q_bio_005",
        "chapter_id": "ch_biology_11_05",
        "topic": "Respiration in Plants",
        "question_text": "The net gain of ATP molecules during glycolysis is:",
        "option_a": "2 ATP",
        "option_b": "4 ATP",
        "option_c": "6 ATP",
        "option_d": "8 ATP",
        "correct_answer": "A",
        "explanation": "Glycolysis produces 4 ATP but consumes 2 ATP in the investment phase, giving a net gain of 2 ATP per glucose molecule.",
        "difficulty": 2,
    },
    {
        "id": "q_bio_006",
        "chapter_id": "ch_biology_11_06",
        "topic": "Cell Division",
        "question_text": "Crossing over occurs during which stage of meiosis?",
        "option_a": "Leptotene",
        "option_b": "Zygotene",
        "option_c": "Pachytene",
        "option_d": "Diplotene",
        "correct_answer": "C",
        "explanation": "Crossing over (exchange of genetic material between homologous chromosomes) occurs during pachytene of prophase I.",
        "difficulty": 3,
    },
    # ── Biology 12th ──────────────────────────────────────────────────────
    {
        "id": "q_bio_007",
        "chapter_id": "ch_biology_12_01",
        "topic": "Reproduction in Organisms",
        "question_text": "Binary fission is a method of reproduction found in:",
        "option_a": "Yeast",
        "option_b": "Amoeba",
        "option_c": "Hydra",
        "option_d": "Spirogyra",
        "correct_answer": "B",
        "explanation": "Binary fission is an asexual reproduction method where a single cell divides into two equal daughter cells, characteristic of Amoeba and bacteria.",
        "difficulty": 1,
    },
    {
        "id": "q_bio_008",
        "chapter_id": "ch_biology_12_02",
        "topic": "Human Reproduction",
        "question_text": "Fertilization in humans occurs in the:",
        "option_a": "Uterus",
        "option_b": "Ovary",
        "option_c": "Fallopian tube (ampulla)",
        "option_d": "Cervix",
        "correct_answer": "C",
        "explanation": "Fertilization typically occurs in the ampullary region of the fallopian tube (oviduct), not in the uterus or ovary.",
        "difficulty": 2,
    },
    {
        "id": "q_bio_009",
        "chapter_id": "ch_biology_12_03",
        "topic": "Principles of Inheritance",
        "question_text": "In a monohybrid cross between two heterozygous individuals (Aa × Aa), the phenotypic ratio is:",
        "option_a": "1 : 1",
        "option_b": "3 : 1",
        "option_c": "1 : 2 : 1",
        "option_d": "9 : 3 : 3 : 1",
        "correct_answer": "B",
        "explanation": "Aa × Aa gives genotypes AA : Aa : aa = 1 : 2 : 1. Since A is dominant, the phenotypic ratio is 3 (dominant) : 1 (recessive).",
        "difficulty": 2,
    },
    {
        "id": "q_bio_010",
        "chapter_id": "ch_biology_12_04",
        "topic": "Molecular Basis of Inheritance",
        "question_text": "The enzyme responsible for transcription is:",
        "option_a": "DNA polymerase",
        "option_b": "RNA polymerase",
        "option_c": "Helicase",
        "option_d": "Ligase",
        "correct_answer": "B",
        "explanation": "RNA polymerase synthesizes RNA from a DNA template during transcription. DNA polymerase is involved in replication, not transcription.",
        "difficulty": 1,
    },
    {
        "id": "q_bio_011",
        "chapter_id": "ch_biology_12_05",
        "topic": "Evolution",
        "question_text": "The theory of natural selection was proposed by:",
        "option_a": "Lamarck",
        "option_b": "Darwin",
        "option_c": "Mendel",
        "option_d": "Hugo de Vries",
        "correct_answer": "B",
        "explanation": "Charles Darwin proposed the theory of natural selection in 'On the Origin of Species' (1859), independently co-discovered with Alfred Russel Wallace.",
        "difficulty": 1,
    },
    {
        "id": "q_bio_012",
        "chapter_id": "ch_biology_12_06",
        "topic": "Human Health and Disease",
        "question_text": "Which of the following is an autoimmune disease?",
        "option_a": "Malaria",
        "option_b": "Rheumatoid arthritis",
        "option_c": "Tuberculosis",
        "option_d": "Typhoid",
        "correct_answer": "B",
        "explanation": "Rheumatoid arthritis is an autoimmune disease where the immune system attacks the body's own joint tissues. Malaria, TB, and typhoid are infectious diseases.",
        "difficulty": 2,
    },
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class QuizSession:
    """A quiz attempt by a user."""

    id: str
    profile_id: str
    quiz_type: str  # practice | timed | mock
    chapter_id: str | None
    topic_ids: list[str] | None
    question_count: int
    time_limit_minutes: int | None
    difficulty: int | None
    started_at: str
    completed_at: str | None = None
    score: float | None = None
    answers: dict[str, str] = field(default_factory=dict)  # question_id -> answer
    question_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": f"{self.quiz_type.title()} Quiz",
            "quiz_type": self.quiz_type,
            "chapter_id": self.chapter_id,
            "total_questions": self.question_count,
            "time_limit_minutes": self.time_limit_minutes,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "score": self.score,
        }


@dataclass
class MistakeEntry:
    """A wrong answer logged for review."""

    id: str
    profile_id: str
    question_id: str
    question_text: str
    user_answer: str | None
    correct_answer: str
    explanation: str | None
    reviewed: bool = False
    review_count: int = 0
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "question_id": self.question_id,
            "question_text": self.question_text,
            "user_answer": self.user_answer,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "reviewed": self.reviewed,
            "review_count": self.review_count,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class QuizService:
    """In-memory quiz session and mistake management."""

    def __init__(self) -> None:
        self._sessions: dict[str, QuizSession] = {}
        self._mistakes: dict[str, MistakeEntry] = {}
        self._question_bank: list[dict[str, Any]] = QUESTION_BANK

    # -- question selection ------------------------------------------------

    def select_questions(
        self,
        count: int,
        chapter_id: str | None = None,
        topic_ids: list[str] | None = None,
        difficulty: int | None = None,
    ) -> list[dict[str, Any]]:
        """Select questions from the bank matching the given filters."""
        pool = self._question_bank

        if chapter_id:
            pool = [q for q in pool if q["chapter_id"] == chapter_id]

        if topic_ids:
            pool = [q for q in pool if q.get("topic") in topic_ids]

        if difficulty:
            pool = [q for q in pool if q["difficulty"] == difficulty]

        # If pool is smaller than requested count, use what's available
        selected = random.sample(pool, min(count, len(pool)))

        # Return only the fields the frontend expects
        return [
            {
                "id": q["id"],
                "question_text": q["question_text"],
                "question_type": "mcq",
                "option_a": q["option_a"],
                "option_b": q["option_b"],
                "option_c": q["option_c"],
                "option_d": q["option_d"],
                "difficulty": q["difficulty"],
            }
            for q in selected
        ]

    # -- session management ------------------------------------------------

    def create_session(
        self,
        profile_id: str,
        question_count: int,
        quiz_type: str = "practice",
        chapter_id: str | None = None,
        topic_ids: list[str] | None = None,
        time_limit_minutes: int | None = None,
        difficulty: int | None = None,
    ) -> QuizSession:
        """Create a new quiz session."""
        session_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()

        questions = self.select_questions(question_count, chapter_id, topic_ids, difficulty)
        question_ids = [q["id"] for q in questions]

        session = QuizSession(
            id=session_id,
            profile_id=profile_id,
            quiz_type=quiz_type,
            chapter_id=chapter_id,
            topic_ids=topic_ids,
            question_count=len(questions),
            time_limit_minutes=time_limit_minutes,
            difficulty=difficulty,
            started_at=now,
            question_ids=question_ids,
        )
        self._sessions[session_id] = session
        logger.info("quiz.session.created", session_id=session_id, profile_id=profile_id)
        return session

    def get_session(self, session_id: str, profile_id: str) -> QuizSession | None:
        """Get a session owned by the user."""
        session = self._sessions.get(session_id)
        if session and session.profile_id == profile_id:
            return session
        return None

    def get_questions(self, session_id: str, profile_id: str) -> list[dict[str, Any]] | None:
        """Get the questions for a session (without correct answers)."""
        session = self._sessions.get(session_id)
        if not session or session.profile_id != profile_id:
            return None

        questions = []
        for qid in session.question_ids:
            q = self._find_question(qid)
            if q:
                questions.append({
                    "id": q["id"],
                    "question_text": q["question_text"],
                    "question_type": "mcq",
                    "option_a": q["option_a"],
                    "option_b": q["option_b"],
                    "option_c": q["option_c"],
                    "option_d": q["option_d"],
                    "difficulty": q["difficulty"],
                })
        return questions

    def submit_answer(
        self,
        session_id: str,
        profile_id: str,
        question_id: str,
        answer: str,
    ) -> dict[str, Any] | None:
        """Submit an answer and return whether it's correct."""
        session = self._sessions.get(session_id)
        if not session or session.profile_id != profile_id:
            return None
        if session.completed_at is not None:
            return None

        session.answers[question_id] = answer

        q = self._find_question(question_id)
        if not q:
            return None

        is_correct = answer.upper() == q["correct_answer"]

        # Log mistake
        if not is_correct:
            mistake_id = str(uuid.uuid4())
            now = datetime.now(UTC).isoformat()
            mistake = MistakeEntry(
                id=mistake_id,
                profile_id=profile_id,
                question_id=question_id,
                question_text=q["question_text"],
                user_answer=answer,
                correct_answer=q["correct_answer"],
                explanation=q.get("explanation"),
                created_at=now,
            )
            self._mistakes[mistake_id] = mistake

        return {"is_correct": is_correct}

    def finish_session(self, session_id: str, profile_id: str) -> dict[str, Any] | None:
        """Finish a session and compute the result."""
        session = self._sessions.get(session_id)
        if not session or session.profile_id != profile_id:
            return None
        if session.completed_at is not None:
            # Already finished — return cached result
            return self._compute_result(session)

        now = datetime.now(UTC).isoformat()
        session.completed_at = now

        result = self._compute_result(session)
        logger.info("quiz.session.finished", session_id=session_id, score=result["score_percent"])
        return result

    def get_result(self, session_id: str, profile_id: str) -> dict[str, Any] | None:
        """Get the result of a finished session."""
        session = self._sessions.get(session_id)
        if not session or session.profile_id != profile_id:
            return None
        if session.completed_at is None:
            return None
        return self._compute_result(session)

    def list_sessions(self, profile_id: str, chapter_id: str | None = None) -> list[dict[str, Any]]:
        """List all sessions for a user."""
        sessions = [s for s in self._sessions.values() if s.profile_id == profile_id]
        if chapter_id:
            sessions = [s for s in sessions if s.chapter_id == chapter_id]
        return [s.to_dict() for s in sorted(sessions, key=lambda s: s.started_at, reverse=True)]

    # -- mistake tracking --------------------------------------------------

    def list_mistakes(self, profile_id: str, chapter_id: str | None = None) -> list[dict[str, Any]]:
        """List all mistakes for a user."""
        mistakes = [m for m in self._mistakes.values() if m.profile_id == profile_id]
        if chapter_id:
            # Filter by matching question's chapter
            mistakes = [
                m for m in mistakes
                if self._find_question(m.question_id)
                and self._find_question(m.question_id)["chapter_id"] == chapter_id  # type: ignore[index]
            ]
        return [m.to_dict() for m in sorted(mistakes, key=lambda m: m.created_at, reverse=True)]

    def review_mistake(self, mistake_id: str, profile_id: str) -> bool:
        """Mark a mistake as reviewed."""
        mistake = self._mistakes.get(mistake_id)
        if not mistake or mistake.profile_id != profile_id:
            return False
        mistake.reviewed = True
        mistake.review_count += 1
        return True

    def delete_mistake(self, mistake_id: str, profile_id: str) -> bool:
        """Delete a mistake entry."""
        mistake = self._mistakes.get(mistake_id)
        if not mistake or mistake.profile_id != profile_id:
            return False
        del self._mistakes[mistake_id]
        return True

    # -- internals ---------------------------------------------------------

    def _find_question(self, question_id: str) -> dict[str, Any] | None:
        """Find a question in the bank by ID."""
        for q in self._question_bank:
            if q["id"] == question_id:
                return q
        return None

    def _compute_result(self, session: QuizSession) -> dict[str, Any]:
        """Compute the result for a session."""
        total = len(session.question_ids)
        correct = 0
        responses = []

        for qid in session.question_ids:
            q = self._find_question(qid)
            if not q:
                continue

            user_answer = session.answers.get(qid)
            is_correct = user_answer is not None and user_answer.upper() == q["correct_answer"]
            if is_correct:
                correct += 1

            responses.append({
                "question_id": qid,
                "question_text": q["question_text"],
                "user_answer": user_answer,
                "correct_answer": q["correct_answer"],
                "is_correct": is_correct,
                "explanation": q.get("explanation"),
                "difficulty": q["difficulty"],
            })

        incorrect = sum(1 for r in responses if not r["is_correct"] and r["user_answer"] is not None)
        skipped = total - correct - incorrect
        score_percent = round((correct / total * 100), 1) if total > 0 else 0.0

        session.score = score_percent

        return {
            "session_id": session.id,
            "total_questions": total,
            "correct": correct,
            "incorrect": incorrect,
            "skipped": skipped,
            "score_percent": score_percent,
            "time_taken_seconds": 0,
            "responses": responses,
        }
