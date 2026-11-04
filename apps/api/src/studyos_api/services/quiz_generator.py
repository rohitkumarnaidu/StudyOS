"""AI-powered quiz question generator with template system and deterministic seeding."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class QuestionType(str, Enum):
    MCQ = "mcq"
    NUMERIC = "numeric"
    ASSERTION_REASON = "assertion_reason"
    MATCH_FOLLOWING = "match_following"


class Subject(str, Enum):
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"


# ---------------------------------------------------------------------------
# NEET Syllabus structure
# ---------------------------------------------------------------------------

SYLLABUS: dict[str, dict[str, list[str]]] = {
    Subject.PHYSICS: {
        "11th": [
            "Units and Measurement",
            "Motion in a Straight Line",
            "Motion in a Plane",
            "Laws of Motion",
            "Work, Energy and Power",
            "System of Particles and Rotational Motion",
            "Gravitation",
            "Mechanical Properties of Solids",
            "Mechanical Properties of Fluids",
            "Thermal Properties of Matter",
            "Thermodynamics",
            "Kinetic Theory",
            "Oscillations",
            "Waves",
        ],
        "12th": [
            "Electric Charges and Fields",
            "Electrostatic Potential and Capacitance",
            "Current Electricity",
            "Moving Charges and Magnetism",
            "Magnetism and Matter",
            "Electromagnetic Induction",
            "Alternating Current",
            "Electromagnetic Waves",
            "Ray Optics and Optical Instruments",
            "Wave Optics",
            "Dual Nature of Radiation and Matter",
            "Atoms",
            "Nuclei",
            "Semiconductor Electronics",
        ],
    },
    Subject.CHEMISTRY: {
        "11th": [
            "Some Basic Concepts of Chemistry",
            "Structure of Atom",
            "Classification of Elements and Periodicity",
            "Chemical Bonding and Molecular Structure",
            "States of Matter",
            "Thermodynamics",
            "Equilibrium",
            "Redox Reactions",
            "Hydrogen",
            "The s-Block Elements",
            "The p-Block Elements",
            "Organic Chemistry — Some Basic Principles",
            "Hydrocarbons",
            "Environmental Chemistry",
        ],
        "12th": [
            "The Solid State",
            "Solutions",
            "Electrochemistry",
            "Chemical Kinetics",
            "Surface Chemistry",
            "General Principles of Metallurgy",
            "The p-Block Elements",
            "The d- and f-Block Elements",
            "Coordination Compounds",
            "Haloalkanes and Haloarenes",
            "Alcohols, Phenols and Ethers",
            "Aldehydes, Ketones and Carboxylic Acids",
            "Amines",
            "Biomolecules",
            "Polymers",
            "Chemistry in Everyday Life",
        ],
    },
    Subject.BIOLOGY: {
        "11th": [
            "The Living World",
            "Biological Classification",
            "Plant Kingdom",
            "Morphology of Flowering Plants",
            "Anatomy of Flowering Plants",
            "Cell — The Unit of Life",
            "Biomolecules",
            "Cell Cycle and Cell Division",
            "Photosynthesis in Higher Plants",
            "Respiration in Plants",
            "Plant Growth and Development",
            "Structural Organisation in Animals",
            "Body Fluids and Circulation",
            "Breathing and Exchange of Gases",
            "Excretory Products and Their Elimination",
            "Locomotion and Movement",
            "Neural Control and Coordination",
            "Chemical Coordination and Integration",
        ],
        "12th": [
            "Reproduction in Organisms",
            "Sexual Reproduction in Flowering Plants",
            "Human Reproduction",
            "Reproductive Health",
            "Principles of Inheritance and Variation",
            "Molecular Basis of Inheritance",
            "Evolution",
            "Human Health and Disease",
            "Strategies for Enhancement in Food Production",
            "Microbes in Human Welfare",
            "Biotechnology — Principles and Processes",
            "Biotechnology and Its Applications",
            "Organisms and Populations",
            "Ecosystem",
            "Biodiversity and Conservation",
            "Environmental Issues",
        ],
    },
}

# ---------------------------------------------------------------------------
# Question templates — structured data for generation
# ---------------------------------------------------------------------------

# Each template: {topic, question_text, options, correct, explanation, difficulty}
# Options are keyed A-D; correct is the letter of the right answer.

PHYSICS_TEMPLATES: list[dict[str, Any]] = [
    # ── Units and Measurement ──
    {
        "topic": "Units and Measurement",
        "question_text": "The dimensional formula of {quantity} is:",
        "options": ["{dim_a}", "{dim_b}", "{dim_c}", "{dim_d}"],
        "correct": "A",
        "explanation": "{explanation}",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Units and Measurement",
        "question_text": "Which of the following is a derived unit?",
        "options": ["Metre", "Second", "Newton", "Kilogram"],
        "correct": "C",
        "explanation": "Newton is a derived unit (kg·m/s²), while metre, second, and kilogram are fundamental SI units.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Units and Measurement",
        "question_text": "The number of significant figures in 0.00340 is:",
        "options": ["2", "3", "4", "5"],
        "correct": "B",
        "explanation": "Leading zeros are not significant. The digits 3, 4, and the trailing 0 are significant, giving 3 significant figures.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Units and Measurement",
        "question_text": "A physical quantity has dimensions [M⁰L⁰T⁻¹]. This quantity is:",
        "options": ["Frequency", "Velocity", "Acceleration", "Force"],
        "correct": "A",
        "explanation": "Frequency has dimension [T⁻¹] since it is the reciprocal of time period.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Motion in a Straight Line ──
    {
        "topic": "Motion in a Straight Line",
        "question_text": "A body starting from rest accelerates uniformly at {a} m/s². Its velocity after {t} seconds is:",
        "options": ["{v_a} m/s", "{v_b} m/s", "{v_c} m/s", "{v_d} m/s"],
        "correct": "A",
        "explanation": "Using v = u + at with u = 0: v = {a} × {t} = {v_a} m/s.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Motion in a Straight Line",
        "question_text": "The displacement-time graph of a body moving with uniform velocity is:",
        "options": [
            "A straight line with positive slope",
            "A parabola",
            "A horizontal line",
            "A straight line with negative slope",
        ],
        "correct": "A",
        "explanation": "For uniform velocity, displacement x = vt, which is a straight line through the origin with slope equal to velocity.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Motion in a Straight Line",
        "question_text": "A car covers the first half of a distance at 40 km/h and the second half at 60 km/h. The average speed is:",
        "options": ["48 km/h", "50 km/h", "45 km/h", "55 km/h"],
        "correct": "A",
        "explanation": "Average speed = 2v₁v₂/(v₁+v₂) = 2×40×60/(40+60) = 4800/100 = 48 km/h.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    # ── Motion in a Plane ──
    {
        "topic": "Motion in a Plane",
        "question_text": "A projectile is launched at an angle of 30° with velocity 20 m/s. The maximum height reached is: (g = 10 m/s²)",
        "options": ["5 m", "10 m", "15 m", "20 m"],
        "correct": "A",
        "explanation": "H = u²sin²θ/(2g) = 400 × (1/4) / 20 = 5 m.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Motion in a Plane",
        "question_text": "The horizontal range of a projectile is maximum when the angle of projection is:",
        "options": ["30°", "45°", "60°", "90°"],
        "correct": "B",
        "explanation": "Range R = u²sin(2θ)/g is maximum when sin(2θ) = 1, i.e., 2θ = 90°, so θ = 45°.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Laws of Motion ──
    {
        "topic": "Laws of Motion",
        "question_text": "A force of {f} N acts on a body of mass {m} kg. The acceleration produced is:",
        "options": ["{a_a} m/s²", "{a_b} m/s²", "{a_c} m/s²", "{a_d} m/s²"],
        "correct": "A",
        "explanation": "From Newton's second law, a = F/m = {f}/{m} = {a_a} m/s².",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Laws of Motion",
        "question_text": "Newton's third law implies that action and reaction forces:",
        "options": [
            "Act on the same body",
            "Act on different bodies",
            "Are always equal to weight",
            "Need not be equal",
        ],
        "correct": "B",
        "explanation": "Action and reaction forces always act on two different bodies — they never cancel each other on a single body.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Laws of Motion",
        "question_text": "A body of mass 5 kg is moving with a constant velocity of 10 m/s on a frictionless surface. The net force acting on it is:",
        "options": ["0 N", "50 N", "10 N", "5 N"],
        "correct": "A",
        "explanation": "By Newton's first law, if velocity is constant (no acceleration), the net force must be zero.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Laws of Motion",
        "question_text": "The impulse-momentum theorem states that impulse is equal to:",
        "options": [
            "Change in momentum",
            "Force × time",
            "Both A and B",
            "Rate of change of momentum",
        ],
        "correct": "C",
        "explanation": "Impulse = F × Δt = Δp (change in momentum). Both expressions are equivalent.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Work, Energy and Power ──
    {
        "topic": "Work, Energy and Power",
        "question_text": "A body of mass {m} kg is moving with a velocity of {v} m/s. Its kinetic energy is:",
        "options": ["{ke_a} J", "{ke_b} J", "{ke_c} J", "{ke_d} J"],
        "correct": "A",
        "explanation": "KE = ½mv² = ½ × {m} × {v}² = {ke_a} J.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Work, Energy and Power",
        "question_text": "The work done by the centripetal force on a body moving in a circular path is:",
        "options": ["Zero", "Positive", "Negative", "Depends on the radius"],
        "correct": "A",
        "explanation": "Centripetal force is always perpendicular to displacement, so work done = F·d·cos(90°) = 0.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Work, Energy and Power",
        "question_text": "A machine does 1000 J of work in 5 seconds. Its power output is:",
        "options": ["200 W", "500 W", "100 W", "50 W"],
        "correct": "A",
        "explanation": "Power = Work/Time = 1000/5 = 200 W.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Rotational Motion ──
    {
        "topic": "System of Particles and Rotational Motion",
        "question_text": "The moment of inertia of a solid sphere about its diameter is:",
        "options": ["(2/5)MR²", "(2/3)MR²", "(1/2)MR²", "MR²"],
        "correct": "A",
        "explanation": "For a solid sphere, I = (2/5)MR² about any diameter, derived by integrating mass elements.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "System of Particles and Rotational Motion",
        "question_text": "Angular momentum is conserved when:",
        "options": [
            "Net external torque is zero",
            "Net external force is zero",
            "Kinetic energy is constant",
            "Moment of inertia is constant",
        ],
        "correct": "A",
        "explanation": "dL/dt = τ_ext. When net external torque is zero, angular momentum L is conserved.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "System of Particles and Rotational Motion",
        "question_text": "A ring and a disc of same mass and radius roll down an inclined plane. Which reaches first?",
        "options": ["Disc", "Ring", "Both reach together", "Depends on the angle"],
        "correct": "A",
        "explanation": "The disc has smaller moment of inertia (MR²/2 vs MR² for ring), so it accelerates faster and reaches first.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    # ── Gravitation ──
    {
        "topic": "Gravitation",
        "question_text": "The escape velocity from Earth's surface is approximately:",
        "options": ["11.2 km/s", "7.2 km/s", "15.2 km/s", "3.2 km/s"],
        "correct": "A",
        "explanation": "vₑ = √(2gR) = √(2 × 9.8 × 6.4×10⁶) ≈ 11.2 km/s.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Gravitation",
        "question_text": "If the distance between two masses is doubled, the gravitational force becomes:",
        "options": ["One-fourth", "Half", "Double", "Four times"],
        "correct": "A",
        "explanation": "F = GMm/r². If r → 2r, F → F/4 (inverse square law).",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Gravitation",
        "question_text": "The value of g at a height equal to Earth's radius is:",
        "options": ["g/4", "g/2", "2g", "g"],
        "correct": "A",
        "explanation": "g' = g/(1+h/R)² = g/(1+1)² = g/4.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    # ── Mechanical Properties ──
    {
        "topic": "Mechanical Properties of Solids",
        "question_text": "Young's modulus of a wire is defined as the ratio of:",
        "options": [
            "Stress to strain",
            "Strain to stress",
            "Force to area",
            "Extension to original length",
        ],
        "correct": "A",
        "explanation": "Young's modulus Y = Stress/Strain = (F/A)/(ΔL/L), a measure of stiffness.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Mechanical Properties of Fluids",
        "question_text": "Bernoulli's theorem is based on the conservation of:",
        "options": ["Energy", "Mass", "Momentum", "Angular momentum"],
        "correct": "A",
        "explanation": "Bernoulli's equation P + ½ρv² + ρgh = constant expresses conservation of energy per unit volume for ideal fluid flow.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Mechanical Properties of Fluids",
        "question_text": "The terminal velocity of a sphere falling through a viscous fluid is proportional to:",
        "options": ["r²", "r", "1/r", "r³"],
        "correct": "A",
        "explanation": "From Stokes' law, v_t = 2r²(ρ-σ)g/(9η), so v_t ∝ r².",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    # ── Thermodynamics ──
    {
        "topic": "Thermodynamics",
        "question_text": "For an adiabatic process, the relation between P and V is:",
        "options": ["PV^γ = constant", "PV = constant", "P/V = constant", "P + V = constant"],
        "correct": "A",
        "explanation": "In an adiabatic process (no heat exchange), PV^γ = constant, where γ = Cp/Cv.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Thermodynamics",
        "question_text": "The efficiency of a Carnot engine operating between 500 K and 300 K is:",
        "options": ["40%", "60%", "50%", "30%"],
        "correct": "A",
        "explanation": "η = 1 - T₂/T₁ = 1 - 300/500 = 0.4 = 40%.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Thermodynamics",
        "question_text": "In an isothermal process for an ideal gas, the change in internal energy is:",
        "options": ["Zero", "Positive", "Negative", "Depends on the path"],
        "correct": "A",
        "explanation": "For an ideal gas, U depends only on temperature. Since T is constant in an isothermal process, ΔU = 0.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Kinetic Theory ──
    {
        "topic": "Kinetic Theory",
        "question_text": "The average kinetic energy of a gas molecule is proportional to:",
        "options": ["Absolute temperature", "Pressure", "Volume", "Number of molecules"],
        "correct": "A",
        "explanation": "KE_avg = (3/2)kT, where k is Boltzmann's constant. Average KE depends only on absolute temperature.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Kinetic Theory",
        "question_text": "The root mean square velocity of gas molecules is given by:",
        "options": ["√(3RT/M)", "√(2RT/M)", "√(RT/M)", "√(RT/2M)"],
        "correct": "A",
        "explanation": "v_rms = √(3RT/M), derived from equating kinetic energy to thermal energy.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Oscillations ──
    {
        "topic": "Oscillations",
        "question_text": "The time period of a simple pendulum is doubled when its length is:",
        "options": ["Made four times", "Made two times", "Made eight times", "Halved"],
        "correct": "A",
        "explanation": "T = 2π√(L/g). For T to double, L must be quadrupled (T ∝ √L).",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Oscillations",
        "question_text": "In simple harmonic motion, the acceleration is maximum at:",
        "options": [
            "Extreme position",
            "Mean position",
            "Midway between mean and extreme",
            "Everywhere equally",
        ],
        "correct": "A",
        "explanation": "a = -ω²x. Acceleration is maximum when displacement x is maximum, i.e., at extreme positions.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Waves ──
    {
        "topic": "Waves",
        "question_text": "The speed of sound in air is approximately:",
        "options": ["330 m/s", "3 × 10⁸ m/s", "300 m/s", "3000 m/s"],
        "correct": "A",
        "explanation": "The speed of sound in air at room temperature is approximately 330-340 m/s.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Waves",
        "question_text": "In a standing wave, the distance between two consecutive nodes is:",
        "options": ["λ/2", "λ", "λ/4", "2λ"],
        "correct": "A",
        "explanation": "In a standing wave, nodes occur at intervals of λ/2.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Electrostatics ──
    {
        "topic": "Electric Charges and Fields",
        "question_text": "Two point charges +4 µC and +1 µC are placed 30 cm apart in vacuum. The ratio of forces experienced by them is:",
        "options": ["1 : 1", "4 : 1", "1 : 4", "2 : 1"],
        "correct": "A",
        "explanation": "By Newton's third law, the force on each charge is equal and opposite. The ratio is 1 : 1.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Electric Charges and Fields",
        "question_text": "Gauss's law is valid for:",
        "options": [
            "Any closed surface",
            "Only spherical surfaces",
            "Only planar surfaces",
            "Only cylindrical surfaces",
        ],
        "correct": "A",
        "explanation": "Gauss's law (∮E·dA = Q/ε₀) holds for any closed surface, regardless of shape.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Electrostatic Potential and Capacitance",
        "question_text": "The capacitance of a parallel plate capacitor is doubled when:",
        "options": [
            "The area of plates is doubled",
            "The separation is doubled",
            "The potential is doubled",
            "The charge is doubled",
        ],
        "correct": "A",
        "explanation": "C = ε₀A/d. Doubling the area A doubles the capacitance.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Current Electricity ──
    {
        "topic": "Current Electricity",
        "question_text": "A wire of resistance 10 Ω is stretched to double its length. Its new resistance is:",
        "options": ["40 Ω", "20 Ω", "5 Ω", "80 Ω"],
        "correct": "A",
        "explanation": "When length doubles, area halves (volume constant). R = ρL/A → new R = ρ(2L)/(A/2) = 4R = 40 Ω.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Current Electricity",
        "question_text": "Kirchhoff's junction rule is based on the conservation of:",
        "options": ["Charge", "Energy", "Momentum", "Mass"],
        "correct": "A",
        "explanation": "The junction rule (ΣI_in = ΣI_out) is a statement of charge conservation — charge cannot accumulate at a junction.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Magnetism ──
    {
        "topic": "Moving Charges and Magnetism",
        "question_text": "The magnetic field at the center of a circular coil of radius R carrying current I is:",
        "options": ["µ₀I/2R", "µ₀I/4R", "µ₀I/2πR", "µ₀IR/2"],
        "correct": "A",
        "explanation": "For a single-turn circular coil, B = µ₀I/2R at the center, from the Biot-Savart law.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Moving Charges and Magnetism",
        "question_text": "A charged particle moving perpendicular to a magnetic field follows a:",
        "options": ["Circular path", "Straight line", "Parabolic path", "Helical path"],
        "correct": "A",
        "explanation": "The magnetic force F = qvB provides centripetal force, causing circular motion when v ⊥ B.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── EMI ──
    {
        "topic": "Electromagnetic Induction",
        "question_text": "Lenz's law is a consequence of the law of conservation of:",
        "options": ["Energy", "Charge", "Momentum", "Mass"],
        "correct": "A",
        "explanation": "Lenz's law ensures energy conservation — if induced current aided the change, perpetual motion would be possible.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Electromagnetic Induction",
        "question_text": "The SI unit of inductance is:",
        "options": ["Henry", "Weber", "Tesla", "Farad"],
        "correct": "A",
        "explanation": "Inductance is measured in Henry (H), named after Joseph Henry. 1 H = 1 Wb/A.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── AC ──
    {
        "topic": "Alternating Current",
        "question_text": "In a pure inductive AC circuit, the current:",
        "options": [
            "Lags voltage by π/2",
            "Leads voltage by π/2",
            "Is in phase with voltage",
            "Lags voltage by π",
        ],
        "correct": "A",
        "explanation": "In a pure inductor, the induced EMF opposes the change in current, causing current to lag voltage by 90° (π/2).",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Alternating Current",
        "question_text": "The resonant frequency of an LCR series circuit is:",
        "options": ["1/(2π√LC)", "1/√LC", "2π√LC", "LC/2π"],
        "correct": "A",
        "explanation": "At resonance, ω₀ = 1/√LC, so f₀ = ω₀/(2π) = 1/(2π√LC).",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Optics ──
    {
        "topic": "Ray Optics and Optical Instruments",
        "question_text": "The refractive index of glass is 1.5. The speed of light in glass is:",
        "options": ["2 × 10⁸ m/s", "3 × 10⁸ m/s", "1.5 × 10⁸ m/s", "4.5 × 10⁸ m/s"],
        "correct": "A",
        "explanation": "v = c/n = (3 × 10⁸)/1.5 = 2 × 10⁸ m/s.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Wave Optics",
        "question_text": "In Young's double slit experiment, the fringe width is given by:",
        "options": ["λD/d", "λd/D", "D/λd", "d/λD"],
        "correct": "A",
        "explanation": "Fringe width β = λD/d, where λ is wavelength, D is screen distance, and d is slit separation.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Ray Optics and Optical Instruments",
        "question_text": "Total internal reflection occurs when light travels from:",
        "options": [
            "Denser to rarer medium at angle > critical angle",
            "Rarer to denser medium",
            "Any medium at any angle",
            "Vacuum to glass",
        ],
        "correct": "A",
        "explanation": "TIR requires light to travel from denser to rarer medium with incidence angle exceeding the critical angle.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Dual Nature ──
    {
        "topic": "Dual Nature of Radiation and Matter",
        "question_text": "The de Broglie wavelength of an electron accelerated through potential V is proportional to:",
        "options": ["1/√V", "V", "√V", "1/V"],
        "correct": "A",
        "explanation": "λ = h/√(2meV), so λ ∝ 1/√V.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Dual Nature of Radiation and Matter",
        "question_text": "The work function of a metal is 4 eV. The threshold frequency is approximately:",
        "options": ["9.7 × 10¹⁴ Hz", "6.6 × 10¹⁴ Hz", "3.3 × 10¹⁴ Hz", "1.2 × 10¹⁵ Hz"],
        "correct": "A",
        "explanation": "ν₀ = φ/h = (4 × 1.6 × 10⁻¹⁹)/(6.63 × 10⁻³⁴) ≈ 9.7 × 10¹⁴ Hz.",
        "difficulty": 4,
        "type": QuestionType.MCQ,
    },
    # ── Atoms ──
    {
        "topic": "Atoms",
        "question_text": "The radius of the nth orbit in hydrogen atom is proportional to:",
        "options": ["n²", "n", "1/n", "1/n²"],
        "correct": "A",
        "explanation": "From Bohr's model, r_n = n²a₀, where a₀ is the Bohr radius (0.529 Å).",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Atoms",
        "question_text": "The energy of an electron in the first excited state of hydrogen is:",
        "options": ["-3.4 eV", "-13.6 eV", "-1.51 eV", "-0.85 eV"],
        "correct": "A",
        "explanation": "E_n = -13.6/n² eV. For n = 2 (first excited state), E = -13.6/4 = -3.4 eV.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Nuclei ──
    {
        "topic": "Nuclei",
        "question_text": "The half-life of a radioactive substance is 10 days. The fraction remaining after 30 days is:",
        "options": ["1/8", "1/4", "1/3", "1/16"],
        "correct": "A",
        "explanation": "After 30 days = 3 half-lives. Fraction remaining = (1/2)³ = 1/8.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Nuclei",
        "question_text": "Nuclear fusion occurs at high temperature because:",
        "options": [
            "Nuclei need enough kinetic energy to overcome Coulomb repulsion",
            "Atoms ionize at high temperature",
            "Electrons are removed",
            "Neutrons become active",
        ],
        "correct": "A",
        "explanation": "High temperature gives nuclei enough kinetic energy to overcome the electrostatic repulsion between positively charged nuclei.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Semiconductors ──
    {
        "topic": "Semiconductor Electronics",
        "question_text": "In a p-n junction diode, the depletion region width decreases when:",
        "options": ["Forward biased", "Reverse biased", "Unbiased", "Temperature decreases"],
        "correct": "A",
        "explanation": "In forward bias, the applied voltage opposes the built-in potential, reducing the depletion width.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Semiconductor Electronics",
        "question_text": "A NAND gate with both inputs connected together acts as a:",
        "options": ["NOT gate", "AND gate", "OR gate", "NOR gate"],
        "correct": "A",
        "explanation": "When both inputs of NAND are tied: output = NOT(A AND A) = NOT(A), which is a NOT gate.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
]

CHEMISTRY_TEMPLATES: list[dict[str, Any]] = [
    # ── Basic Concepts ──
    {
        "topic": "Some Basic Concepts of Chemistry",
        "question_text": "The number of moles of {compound} in {mass} g is:",
        "options": ["{mol_a} mol", "{mol_b} mol", "{mol_c} mol", "{mol_d} mol"],
        "correct": "A",
        "explanation": "{explanation}",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Some Basic Concepts of Chemistry",
        "question_text": "The molarity of a solution containing 4 g of NaOH in 500 mL is:",
        "options": ["0.2 M", "0.1 M", "0.4 M", "0.5 M"],
        "correct": "A",
        "explanation": "Moles of NaOH = 4/40 = 0.1 mol. Molarity = 0.1/0.5 = 0.2 M.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Some Basic Concepts of Chemistry",
        "question_text": "Avogadro's number represents the number of particles in:",
        "options": [
            "One mole of any substance",
            "One gram of any substance",
            "One litre of any gas",
            "One atom",
        ],
        "correct": "A",
        "explanation": "Avogadro's number (6.022 × 10²³) is the number of particles in one mole of any substance.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Atomic Structure ──
    {
        "topic": "Structure of Atom",
        "question_text": "The maximum number of electrons in a subshell with l = 3 is:",
        "options": ["14", "10", "6", "18"],
        "correct": "A",
        "explanation": "For l = 3 (f subshell), orbitals = 2l + 1 = 7. Max electrons = 7 × 2 = 14.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Structure of Atom",
        "question_text": "The electronic configuration of Cu (Z = 29) is:",
        "options": ["[Ar] 3d¹⁰ 4s¹", "[Ar] 3d⁹ 4s²", "[Ar] 3d⁸ 4s² 4p¹", "[Ar] 3d¹⁰ 4s²"],
        "correct": "A",
        "explanation": "Cu has an anomalous configuration [Ar] 3d¹⁰ 4s¹ because a fully filled d subshell is more stable.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Structure of Atom",
        "question_text": "The energy of an electron in the nth orbit of hydrogen is given by:",
        "options": ["-13.6/n² eV", "-13.6 × n² eV", "13.6/n eV", "-13.6/n eV"],
        "correct": "A",
        "explanation": "E_n = -13.6/n² eV from Bohr's model, where n is the principal quantum number.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Structure of Atom",
        "question_text": "Which quantum number determines the shape of an orbital?",
        "options": ["Azimuthal (l)", "Principal (n)", "Magnetic (m)", "Spin (s)"],
        "correct": "A",
        "explanation": "The azimuthal quantum number l determines orbital shape: l=0 (spherical s), l=1 (dumbbell p), l=2 (cloverleaf d).",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Periodicity ──
    {
        "topic": "Classification of Elements and Periodicity",
        "question_text": "Which of the following has the highest electronegativity?",
        "options": ["Fluorine", "Oxygen", "Nitrogen", "Chlorine"],
        "correct": "A",
        "explanation": "Fluorine has the highest electronegativity (3.98 on Pauling scale) of all elements.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Classification of Elements and Periodicity",
        "question_text": "The ionization energy generally increases across a period because:",
        "options": [
            "Nuclear charge increases while shielding remains similar",
            "Atomic size increases",
            "Number of shells increases",
            "Electron affinity decreases",
        ],
        "correct": "A",
        "explanation": "Across a period, nuclear charge increases but electrons are added to the same shell, so effective nuclear charge increases, making electrons harder to remove.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Chemical Bonding ──
    {
        "topic": "Chemical Bonding and Molecular Structure",
        "question_text": "The shape of SF₆ molecule is:",
        "options": ["Octahedral", "Square planar", "Trigonal bipyramidal", "Tetrahedral"],
        "correct": "A",
        "explanation": "SF₆ has sp³d² hybridization with 6 bond pairs and 0 lone pairs → octahedral geometry.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Chemical Bonding and Molecular Structure",
        "question_text": "The bond angle in water is less than the tetrahedral angle because of:",
        "options": [
            "Lone pair-lone pair repulsion",
            "Bond pair-bond pair repulsion",
            "Hybridization",
            "Electronegativity difference",
        ],
        "correct": "A",
        "explanation": "Two lone pairs on oxygen exert greater repulsion than bond pairs, compressing the H-O-H angle to 104.5° (vs 109.5°).",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Chemical Bonding and Molecular Structure",
        "question_text": "Which molecule has a zero dipole moment?",
        "options": ["CO₂", "H₂O", "NH₃", "SO₂"],
        "correct": "A",
        "explanation": "CO₂ is linear (O=C=O), so the two C=O bond dipoles cancel, giving zero net dipole moment.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── States of Matter ──
    {
        "topic": "States of Matter",
        "question_text": "At constant temperature, the pressure of a gas is inversely proportional to its volume. This is:",
        "options": ["Boyle's law", "Charles's law", "Avogadro's law", "Gay-Lussac's law"],
        "correct": "A",
        "explanation": "Boyle's law states PV = constant at constant temperature.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Thermodynamics ──
    {
        "topic": "Thermodynamics",
        "question_text": "For a spontaneous reaction at constant T and P, ΔG is:",
        "options": ["Negative", "Positive", "Zero", "Infinite"],
        "correct": "A",
        "explanation": "A spontaneous process at constant T and P has ΔG < 0.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Thermodynamics",
        "question_text": "The enthalpy of formation of elements in their standard state is:",
        "options": ["Zero", "Positive", "Negative", "Undefined"],
        "correct": "A",
        "explanation": "By convention, the standard enthalpy of formation of an element in its most stable form is defined as zero.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Equilibrium ──
    {
        "topic": "Equilibrium",
        "question_text": "The pH of 0.001 M HCl solution is:",
        "options": ["3", "1", "2", "4"],
        "correct": "A",
        "explanation": "HCl is a strong acid, [H⁺] = 0.001 = 10⁻³ M. pH = -log(10⁻³) = 3.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Equilibrium",
        "question_text": "Le Chatelier's principle states that if a system at equilibrium is disturbed, it will:",
        "options": [
            "Shift to counteract the disturbance",
            "Remain unchanged",
            "Always shift right",
            "Always shift left",
        ],
        "correct": "A",
        "explanation": "Le Chatelier's principle: the system shifts in the direction that minimizes the effect of the disturbance.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Equilibrium",
        "question_text": "The solubility product of AgCl is 1.8 × 10⁻¹⁰. Its solubility in mol/L is:",
        "options": ["1.34 × 10⁻⁵", "1.8 × 10⁻¹⁰", "9 × 10⁻¹¹", "3.6 × 10⁻¹⁰"],
        "correct": "A",
        "explanation": "For AgCl: Ksp = s², so s = √(1.8 × 10⁻¹⁰) ≈ 1.34 × 10⁻⁵ mol/L.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    # ── Redox ──
    {
        "topic": "Redox Reactions",
        "question_text": "In the reaction 2Na + Cl₂ → 2NaCl, sodium is:",
        "options": [
            "Oxidized",
            "Reduced",
            "Neither oxidized nor reduced",
            "Both oxidized and reduced",
        ],
        "correct": "A",
        "explanation": "Na loses an electron (Na → Na⁺ + e⁻), so it is oxidized. Chlorine gains electrons and is reduced.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Redox Reactions",
        "question_text": "The oxidation number of Mn in KMnO₄ is:",
        "options": ["+7", "+5", "+3", "+4"],
        "correct": "A",
        "explanation": "K = +1, O = -2 (×4 = -8). So Mn + 1 - 8 = 0, giving Mn = +7.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Hydrogen ──
    {
        "topic": "Hydrogen",
        "question_text": "Heavy water is:",
        "options": ["D₂O", "H₂O₂", "H₂¹⁸O", "HDO"],
        "correct": "A",
        "explanation": "Heavy water (D₂O) contains deuterium (²H) instead of ordinary hydrogen. It is used as a neutron moderator in nuclear reactors.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── s-Block ──
    {
        "topic": "The s-Block Elements",
        "question_text": "Which alkali metal has the lowest melting point?",
        "options": ["Cs", "Na", "K", "Li"],
        "correct": "A",
        "explanation": "Melting point decreases down the group: Li > Na > K > Rb > Cs. Cesium has the weakest metallic bonding.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── p-Block (11th) ──
    {
        "topic": "The p-Block Elements",
        "question_text": "Boron trifluoride (BF₃) acts as a Lewis acid because:",
        "options": [
            "It has an incomplete octet",
            "It is highly electronegative",
            "It has lone pairs",
            "It is a strong oxidizing agent",
        ],
        "correct": "A",
        "explanation": "BF₃ has only 6 electrons around boron (incomplete octet), so it can accept an electron pair → Lewis acid.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Organic Basics ──
    {
        "topic": "Organic Chemistry — Some Basic Principles",
        "question_text": "The IUPAC name of CH₃CH₂OH is:",
        "options": ["Ethanol", "Methanol", "Propanol", "Ethanal"],
        "correct": "A",
        "explanation": "CH₃CH₂OH is a 2-carbon alcohol → ethanol (eth- + -anol suffix).",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Organic Chemistry — Some Basic Principles",
        "question_text": "Which of the following shows resonance?",
        "options": ["Benzene", "Methane", "Ethane", "Propane"],
        "correct": "A",
        "explanation": "Benzene has a delocalized π-electron system with two equivalent resonance structures.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Organic Chemistry — Some Basic Principles",
        "question_text": "The inductive effect involves the displacement of:",
        "options": ["σ electrons", "π electrons", "Lone pair electrons", "Free radicals"],
        "correct": "A",
        "explanation": "The inductive effect is the permanent displacement of σ (sigma) bonding electrons along a carbon chain due to electronegativity differences.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Hydrocarbons ──
    {
        "topic": "Hydrocarbons",
        "question_text": "Markovnikov's rule applies to the addition of HX to:",
        "options": ["Unsymmetrical alkenes", "Symmetrical alkenes", "Alkanes", "Benzene"],
        "correct": "A",
        "explanation": "Markovnikov's rule: in addition of HX to unsymmetrical alkenes, H adds to the carbon with more H atoms.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Solid State ──
    {
        "topic": "The Solid State",
        "question_text": "The number of atoms per unit cell in fcc lattice is:",
        "options": ["4", "2", "1", "6"],
        "correct": "A",
        "explanation": "FCC: 8 corners × 1/8 + 6 faces × 1/2 = 1 + 3 = 4 atoms per unit cell.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "The Solid State",
        "question_text": "Schottky defect in crystals is observed when:",
        "options": [
            "Equal number of cations and anions are missing",
            "Cations move to interstitial sites",
            "Extra electrons are trapped",
            "Impurities are present",
        ],
        "correct": "A",
        "explanation": "Schottky defect involves missing equal numbers of cations and anions from lattice sites, maintaining electrical neutrality.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Solutions ──
    {
        "topic": "Solutions",
        "question_text": "The elevation in boiling point is directly proportional to:",
        "options": ["Molality", "Molarity", "Mole fraction of solvent", "Volume"],
        "correct": "A",
        "explanation": "ΔTb = Kb × m (molality). This is a colligative property depending on particle concentration.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Solutions",
        "question_text": "Raoult's law states that the vapor pressure of a solution is proportional to:",
        "options": ["Mole fraction of solvent", "Mole fraction of solute", "Molarity", "Molality"],
        "correct": "A",
        "explanation": "Raoult's law: P_solution = X_solvent × P°_solvent, where X is the mole fraction of the solvent.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Electrochemistry ──
    {
        "topic": "Electrochemistry",
        "question_text": "The standard electrode potential of hydrogen electrode is:",
        "options": ["0 V", "1 V", "-1 V", "0.5 V"],
        "correct": "A",
        "explanation": "By convention, the standard hydrogen electrode (SHE) is assigned exactly 0 V at all temperatures.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Electrochemistry",
        "question_text": "Faraday's first law of electrolysis states that the mass deposited is proportional to:",
        "options": ["Quantity of electricity passed", "Time only", "Current only", "Concentration"],
        "correct": "A",
        "explanation": "m = ZQ = ZIt, where Q = It is the total charge passed through the electrolyte.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Chemical Kinetics ──
    {
        "topic": "Chemical Kinetics",
        "question_text": "For a first-order reaction, the half-life is:",
        "options": [
            "Independent of initial concentration",
            "Proportional to initial concentration",
            "Inversely proportional to initial concentration",
            "Proportional to square of initial concentration",
        ],
        "correct": "A",
        "explanation": "For first-order: t₁/₂ = 0.693/k, independent of initial concentration.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Chemical Kinetics",
        "question_text": "The Arrhenius equation relates rate constant to:",
        "options": ["Temperature", "Pressure", "Concentration", "Volume"],
        "correct": "A",
        "explanation": "k = Ae^(-Ea/RT) shows how the rate constant varies with temperature and activation energy.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Surface Chemistry ──
    {
        "topic": "Surface Chemistry",
        "question_text": "The Tyndall effect is observed in:",
        "options": ["Colloidal solutions", "True solutions", "Suspensions only", "Pure solvents"],
        "correct": "A",
        "explanation": "The Tyndall effect (scattering of light by particles) is characteristic of colloidal solutions where particle size is 1-1000 nm.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Metallurgy ──
    {
        "topic": "General Principles of Metallurgy",
        "question_text": "Froth floatation process is used for the concentration of:",
        "options": ["Sulphide ores", "Oxide ores", "Carbonate ores", "Chloride ores"],
        "correct": "A",
        "explanation": "Froth floatation exploits the preferential wetting of sulphide ores by oil, allowing them to be separated from gangue.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── p-Block (12th) ──
    {
        "topic": "The p-Block Elements",
        "question_text": "The most acidic oxide of nitrogen is:",
        "options": ["N₂O₅", "N₂O", "NO", "NO₂"],
        "correct": "A",
        "explanation": "Acidity of oxides increases with oxidation state. N₂O₅ has N in +5 state (highest), making it the most acidic.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    # ── d/f-Block ──
    {
        "topic": "The d- and f-Block Elements",
        "question_text": "Which ion is colored in aqueous solution?",
        "options": ["Cu²⁺", "Sc³⁺", "Ti⁴⁺", "Zn²⁺"],
        "correct": "A",
        "explanation": "Cu²⁺ has [Ar]3d⁹ with unpaired electrons → d-d transitions produce color. Sc³⁺, Ti⁴⁺, Zn²⁺ have no unpaired d electrons.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "The d- and f-Block Elements",
        "question_text": "Transition metals show variable oxidation states because:",
        "options": [
            "Both (n-1)d and ns electrons can participate in bonding",
            "They have high ionization energy",
            "They are highly electronegative",
            "They form complexes easily",
        ],
        "correct": "A",
        "explanation": "The small energy difference between (n-1)d and ns orbitals allows both to participate in bonding, giving multiple oxidation states.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Coordination Compounds ──
    {
        "topic": "Coordination Compounds",
        "question_text": "The coordination number of [Co(NH₃)₆]³⁺ is:",
        "options": ["6", "3", "4", "8"],
        "correct": "A",
        "explanation": "Six NH₃ ligands are coordinated to Co³⁺, giving a coordination number of 6.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Coordination Compounds",
        "question_text": "The IUPAC name of [Pt(NH₃)₂Cl₂] is:",
        "options": [
            "Diamminedichloridoplatinum(II)",
            "Diamminedichloroplatinum(IV)",
            "Dichlorodiammineplatinum(II)",
            "Platinum diammine dichloride",
        ],
        "correct": "A",
        "explanation": "Ligands named alphabetically: ammine before chloro. Oxidation state of Pt: x + 0 + 2(-1) = 0, so x = +2.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    # ── Haloalkanes ──
    {
        "topic": "Haloalkanes and Haloarenes",
        "question_text": "SN2 reaction proceeds with:",
        "options": [
            "Inversion of configuration",
            "Retention of configuration",
            "Racemization",
            "No change in configuration",
        ],
        "correct": "A",
        "explanation": "SN2 involves backside attack by the nucleophile, causing Walden inversion (complete stereochemical inversion).",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Alcohols ──
    {
        "topic": "Alcohols, Phenols and Ethers",
        "question_text": "Lucas reagent is a mixture of:",
        "options": [
            "Conc. HCl + anhydrous ZnCl₂",
            "Conc. HNO₃ + ZnCl₂",
            "Conc. H₂SO₄ + ZnCl₂",
            "Conc. HCl + CuCl₂",
        ],
        "correct": "A",
        "explanation": "Lucas reagent = conc. HCl + anhydrous ZnCl₂, used to distinguish 1°, 2°, and 3° alcohols.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Alcohols, Phenols and Ethers",
        "question_text": "Phenol is more acidic than alcohol because:",
        "options": [
            "The phenoxide ion is resonance stabilized",
            "Phenol has higher molecular weight",
            "Phenol forms hydrogen bonds",
            "Phenol is aromatic",
        ],
        "correct": "A",
        "explanation": "The phenoxide ion's negative charge is delocalized over the benzene ring through resonance, stabilizing it.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Aldehydes ──
    {
        "topic": "Aldehydes, Ketones and Carboxylic Acids",
        "question_text": "Tollens' reagent is used to detect:",
        "options": ["Aldehydes", "Ketones", "Alcohols", "Esters"],
        "correct": "A",
        "explanation": "Tollens' reagent [Ag(NH₃)₂]⁺ oxidizes aldehydes to carboxylic acids, depositing metallic silver (silver mirror test).",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Aldehydes, Ketones and Carboxylic Acids",
        "question_text": "The aldol condensation reaction is given by:",
        "options": [
            "Aldehydes with α-hydrogen",
            "All aldehydes",
            "All ketones",
            "Carboxylic acids",
        ],
        "correct": "A",
        "explanation": "Aldol condensation requires at least one α-hydrogen to form the enolate ion intermediate.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    # ── Amines ──
    {
        "topic": "Amines",
        "question_text": "The basicity order of amines in aqueous solution for methyl group is:",
        "options": [
            "(CH₃)₂NH > CH₃NH₂ > (CH₃)₃N > NH₃",
            "CH₃NH₂ > (CH₃)₂NH > (CH₃)₃N > NH₃",
            "(CH₃)₃N > (CH₃)₂NH > CH₃NH₂ > NH₃",
            "NH₃ > CH₃NH₂ > (CH₃)₂NH > (CH₃)₃N",
        ],
        "correct": "A",
        "explanation": "In aqueous solution, basicity depends on inductive effect, solvation, and steric hindrance. For methyl amines: 2° > 1° > 3° > NH₃.",
        "difficulty": 4,
        "type": QuestionType.MCQ,
    },
    # ── Biomolecules ──
    {
        "topic": "Biomolecules",
        "question_text": "The bond between two amino acids in a protein is called:",
        "options": ["Peptide bond", "Glycosidic bond", "Phosphodiester bond", "Hydrogen bond"],
        "correct": "A",
        "explanation": "A peptide bond (—CO—NH—) forms between the carboxyl group of one amino acid and the amino group of another.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Biomolecules",
        "question_text": "Glucose and fructose are:",
        "options": [
            "Functional isomers",
            "Chain isomers",
            "Position isomers",
            "Geometrical isomers",
        ],
        "correct": "A",
        "explanation": "Glucose (aldehyde) and fructose (ketone) have the same formula C₆H₁₂O₆ but different functional groups → functional isomers.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Polymers ──
    {
        "topic": "Polymers",
        "question_text": "Nylon-6,6 is formed from:",
        "options": [
            "Hexamethylenediamine and adipic acid",
            "Caprolactam",
            "Phenol and formaldehyde",
            "Ethylene glycol and terephthalic acid",
        ],
        "correct": "A",
        "explanation": "Nylon-6,6 is a condensation polymer from hexamethylenediamine (6 carbons) and adipic acid (6 carbons).",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
]

BIOLOGY_TEMPLATES: list[dict[str, Any]] = [
    # ── The Living World ──
    {
        "topic": "The Living World",
        "question_text": "The basic unit of classification is:",
        "options": ["Species", "Genus", "Family", "Order"],
        "correct": "A",
        "explanation": "Species is the fundamental unit — a group of organisms that can interbreed and produce fertile offspring.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "The Living World",
        "question_text": "Binomial nomenclature was introduced by:",
        "options": ["Carolus Linnaeus", "Aristotle", "Darwin", "Mendel"],
        "correct": "A",
        "explanation": "Carolus Linnaeus introduced the binomial system (Genus species) in 'Systema Naturae' (1758).",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Biological Classification ──
    {
        "topic": "Biological Classification",
        "question_text": "Five kingdom classification was proposed by:",
        "options": ["R.H. Whittaker", "Linnaeus", "Aristotle", "Copeland"],
        "correct": "A",
        "explanation": "R.H. Whittaker proposed the five kingdom system (Monera, Protista, Fungi, Plantae, Animalia) in 1969.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Biological Classification",
        "question_text": "Viruses are considered non-living because they:",
        "options": [
            "Can be crystallized and lack cellular structure",
            "Are very small",
            "Cause diseases",
            "Have DNA or RNA",
        ],
        "correct": "A",
        "explanation": "Viruses lack cellular organization, cannot reproduce independently, and can be crystallized — all properties of non-living matter.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Plant Kingdom ──
    {
        "topic": "Plant Kingdom",
        "question_text": "Gymnosperms differ from angiosperms in having:",
        "options": ["Naked seeds", "Flowers", "Fruits", "Double fertilization"],
        "correct": "A",
        "explanation": "Gymnosperms have 'naked seeds' not enclosed in an ovary (fruit), unlike angiosperms.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Morphology ──
    {
        "topic": "Morphology of Flowering Plants",
        "question_text": "The arrangement of leaves on a stem is called:",
        "options": ["Phyllotaxy", "Venation", "Aestivation", "Inflorescence"],
        "correct": "A",
        "explanation": "Phyllotaxy refers to the pattern of leaf arrangement on a stem (alternate, opposite, or whorled).",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Anatomy ──
    {
        "topic": "Anatomy of Flowering Plants",
        "question_text": "Vascular bundles in monocot stems are:",
        "options": ["Scattered", "In a ring", "In a single row", "Absent"],
        "correct": "A",
        "explanation": "Monocot stems have scattered vascular bundles (atactostele), while dicot stems have them arranged in a ring.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Cell ──
    {
        "topic": "Cell — The Unit of Life",
        "question_text": "Which organelle is known as the 'powerhouse of the cell'?",
        "options": ["Mitochondria", "Golgi apparatus", "Ribosome", "Lysosome"],
        "correct": "A",
        "explanation": "Mitochondria generate ATP through oxidative phosphorylation, earning the title 'powerhouse of the cell'.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Cell — The Unit of Life",
        "question_text": "The fluid mosaic model of the plasma membrane was proposed by:",
        "options": [
            "Singer and Nicolson",
            "Watson and Crick",
            "Robertson",
            "Schleiden and Schwann",
        ],
        "correct": "A",
        "explanation": "Singer and Nicolson (1972) proposed the fluid mosaic model — a lipid bilayer with embedded proteins.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Biomolecules ──
    {
        "topic": "Biomolecules",
        "question_text": "Enzymes are chemically:",
        "options": ["Proteins", "Carbohydrates", "Lipids", "Nucleic acids"],
        "correct": "A",
        "explanation": "Most enzymes are proteins (some are RNA — ribozymes). They act as biological catalysts.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Biomolecules",
        "question_text": "The primary structure of a protein refers to:",
        "options": [
            "Sequence of amino acids",
            "Alpha helix formation",
            "Beta pleated sheet",
            "3D folding",
        ],
        "correct": "A",
        "explanation": "Primary structure is the linear sequence of amino acids linked by peptide bonds.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Cell Division ──
    {
        "topic": "Cell Cycle and Cell Division",
        "question_text": "Crossing over occurs during which stage of meiosis?",
        "options": ["Pachytene", "Leptotene", "Zygotene", "Diplotene"],
        "correct": "A",
        "explanation": "Crossing over occurs during pachytene of prophase I, when homologous chromosomes exchange genetic material.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Cell Cycle and Cell Division",
        "question_text": "The phase of the cell cycle during which DNA replication occurs is:",
        "options": ["S phase", "G₁ phase", "G₂ phase", "M phase"],
        "correct": "A",
        "explanation": "DNA synthesis (replication) occurs during the S (synthesis) phase of interphase.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Photosynthesis ──
    {
        "topic": "Photosynthesis in Higher Plants",
        "question_text": "The oxygen released during photosynthesis comes from:",
        "options": ["H₂O", "CO₂", "Glucose", "Chlorophyll"],
        "correct": "A",
        "explanation": "During photolysis: 2H₂O → 4H⁺ + 4e⁻ + O₂. The O₂ is released as a byproduct of water splitting.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Photosynthesis in Higher Plants",
        "question_text": "The Calvin cycle occurs in the:",
        "options": ["Stroma of chloroplast", "Thylakoid membrane", "Cytoplasm", "Mitochondria"],
        "correct": "A",
        "explanation": "The Calvin cycle (dark reactions) occurs in the stroma, using ATP and NADPH from light reactions.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Respiration ──
    {
        "topic": "Respiration in Plants",
        "question_text": "The net gain of ATP during glycolysis is:",
        "options": ["2 ATP", "4 ATP", "6 ATP", "38 ATP"],
        "correct": "A",
        "explanation": "Glycolysis produces 4 ATP but uses 2 in the investment phase, giving net 2 ATP per glucose.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Respiration in Plants",
        "question_text": "The electron transport chain in cellular respiration is located in:",
        "options": [
            "Inner mitochondrial membrane",
            "Outer mitochondrial membrane",
            "Matrix",
            "Cytoplasm",
        ],
        "correct": "A",
        "explanation": "The ETC complexes are embedded in the inner mitochondrial membrane, creating a proton gradient for ATP synthesis.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Plant Growth ──
    {
        "topic": "Plant Growth and Development",
        "question_text": "The plant hormone responsible for apical dominance is:",
        "options": ["Auxin", "Gibberellin", "Cytokinin", "Abscisic acid"],
        "correct": "A",
        "explanation": "Auxin produced at the apical bud suppresses lateral bud growth, maintaining apical dominance.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Animal Kingdom ──
    {
        "topic": "Structural Organisation in Animals",
        "question_text": "Which type of epithelium lines the inner surface of blood vessels?",
        "options": [
            "Squamous epithelium",
            "Cuboidal epithelium",
            "Columnar epithelium",
            "Stratified epithelium",
        ],
        "correct": "A",
        "explanation": "Simple squamous epithelium (endothelium) lines blood vessels, allowing easy diffusion of substances.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Body Fluids ──
    {
        "topic": "Body Fluids and Circulation",
        "question_text": "The universal donor blood group is:",
        "options": ["O negative", "AB positive", "A positive", "B negative"],
        "correct": "A",
        "explanation": "O negative blood lacks A, B, and Rh antigens, so it can be given to any blood type.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Body Fluids and Circulation",
        "question_text": "The pacemaker of the heart is:",
        "options": ["SA node", "AV node", "Bundle of His", "Purkinje fibers"],
        "correct": "A",
        "explanation": "The SA (sinoatrial) node generates 70-75 impulses/min, setting the heart's rhythm.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Breathing ──
    {
        "topic": "Breathing and Exchange of Gases",
        "question_text": "The volume of air remaining in the lungs after a forced expiration is called:",
        "options": [
            "Residual volume",
            "Tidal volume",
            "Vital capacity",
            "Expiratory reserve volume",
        ],
        "correct": "A",
        "explanation": "Residual volume (~1200 mL) is the air that remains in lungs even after maximum forced expiration.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Excretion ──
    {
        "topic": "Excretory Products and Their Elimination",
        "question_text": "The functional unit of the kidney is:",
        "options": ["Nephron", "Neuron", "Glomerulus", "Loop of Henle"],
        "correct": "A",
        "explanation": "Each kidney contains about 1 million nephrons, the functional units that filter blood and form urine.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Excretory Products and Their Elimination",
        "question_text": "The counter-current mechanism in the kidney is located in:",
        "options": ["Loop of Henle and vasa recta", "Glomerulus", "PCT", "Collecting duct only"],
        "correct": "A",
        "explanation": "The counter-current multiplier in the Loop of Henle and exchanger in vasa recta concentrate urine.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    # ── Locomotion ──
    {
        "topic": "Locomotion and Movement",
        "question_text": "The sliding filament theory of muscle contraction states that:",
        "options": [
            "Actin filaments slide over myosin filaments",
            "Myosin filaments shorten",
            "Actin filaments shorten",
            "Z-lines move apart",
        ],
        "correct": "A",
        "explanation": "During contraction, thin (actin) filaments slide past thick (myosin) filaments — the filaments themselves do not shorten.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Neural Control ──
    {
        "topic": "Neural Control and Coordination",
        "question_text": "The resting membrane potential of a neuron is approximately:",
        "options": ["-70 mV", "+70 mV", "0 mV", "-40 mV"],
        "correct": "A",
        "explanation": "The resting potential of about -70 mV is maintained by the Na⁺/K⁺ pump and selective ion permeability.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Neural Control and Coordination",
        "question_text": "The part of the brain responsible for balance and posture is:",
        "options": ["Cerebellum", "Cerebrum", "Medulla", "Thalamus"],
        "correct": "A",
        "explanation": "The cerebellum coordinates voluntary movements, balance, and posture.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Reproduction ──
    {
        "topic": "Reproduction in Organisms",
        "question_text": "Binary fission is a method of reproduction found in:",
        "options": ["Amoeba", "Yeast", "Hydra", "Spirogyra"],
        "correct": "A",
        "explanation": "Binary fission is asexual reproduction where a single cell divides into two equal daughter cells, characteristic of Amoeba.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Sexual Reproduction in Flowering Plants",
        "question_text": "Double fertilization in angiosperms involves:",
        "options": [
            "One sperm fuses with egg, another with polar nuclei",
            "Two sperms fuse with egg",
            "Two eggs are fertilized",
            "One sperm fuses with two eggs",
        ],
        "correct": "A",
        "explanation": "One sperm fertilizes the egg (→ zygote), the other fuses with two polar nuclei (→ triploid endosperm).",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Human Reproduction ──
    {
        "topic": "Human Reproduction",
        "question_text": "Fertilization in humans occurs in the:",
        "options": ["Fallopian tube (ampulla)", "Uterus", "Ovary", "Cervix"],
        "correct": "A",
        "explanation": "Fertilization typically occurs in the ampullary region of the fallopian tube.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Genetics ──
    {
        "topic": "Principles of Inheritance and Variation",
        "question_text": "In a monohybrid cross Aa × Aa, the phenotypic ratio is:",
        "options": ["3 : 1", "1 : 1", "1 : 2 : 1", "9 : 3 : 3 : 1"],
        "correct": "A",
        "explanation": "Aa × Aa → AA : Aa : aa = 1 : 2 : 1 genotypically, 3 : 1 phenotypically (dominant : recessive).",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Principles of Inheritance and Variation",
        "question_text": "Linked genes do not show independent assortment because they are:",
        "options": [
            "Located on the same chromosome",
            "Located on different chromosomes",
            "Recessive",
            "Dominant",
        ],
        "correct": "A",
        "explanation": "Linked genes are on the same chromosome and tend to be inherited together, violating Mendel's law of independent assortment.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Molecular Basis ──
    {
        "topic": "Molecular Basis of Inheritance",
        "question_text": "The enzyme responsible for transcription is:",
        "options": ["RNA polymerase", "DNA polymerase", "Helicase", "Ligase"],
        "correct": "A",
        "explanation": "RNA polymerase synthesizes RNA from a DNA template during transcription.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Molecular Basis of Inheritance",
        "question_text": "The lac operon is an example of:",
        "options": [
            "Inducible gene regulation",
            "Repressible gene regulation",
            "Constitutive expression",
            "Post-transcriptional regulation",
        ],
        "correct": "A",
        "explanation": "The lac operon is induced by lactose (allolactose), which inactivates the repressor, allowing transcription.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    # ── Evolution ──
    {
        "topic": "Evolution",
        "question_text": "The theory of natural selection was proposed by:",
        "options": ["Darwin", "Lamarck", "Mendel", "Hugo de Vries"],
        "correct": "A",
        "explanation": "Charles Darwin proposed natural selection in 'On the Origin of Species' (1859), co-discovered with Alfred Russel Wallace.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Evolution",
        "question_text": "Hardy-Weinberg equilibrium is disturbed by all EXCEPT:",
        "options": ["Large population size", "Mutation", "Gene flow", "Natural selection"],
        "correct": "A",
        "explanation": "Hardy-Weinberg equilibrium requires a large population (no genetic drift). Mutation, gene flow, and selection all disturb it.",
        "difficulty": 3,
        "type": QuestionType.MCQ,
    },
    # ── Human Health ──
    {
        "topic": "Human Health and Disease",
        "question_text": "Which of the following is an autoimmune disease?",
        "options": ["Rheumatoid arthritis", "Malaria", "Tuberculosis", "Typhoid"],
        "correct": "A",
        "explanation": "Rheumatoid arthritis is autoimmune — the immune system attacks the body's own joint tissues.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Human Health and Disease",
        "question_text": "HIV attacks which type of immune cells?",
        "options": ["Helper T cells (CD4⁺)", "B cells", "Neutrophils", "Red blood cells"],
        "correct": "A",
        "explanation": "HIV specifically targets and destroys CD4⁺ helper T cells, weakening the immune system.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Biotechnology ──
    {
        "topic": "Biotechnology — Principles and Processes",
        "question_text": "PCR (Polymerase Chain Reaction) requires:",
        "options": [
            "Taq polymerase, primers, dNTPs, template DNA",
            "RNA polymerase, primers, NTPs",
            "Restriction enzymes, ligase, vector",
            "Reverse transcriptase, mRNA",
        ],
        "correct": "A",
        "explanation": "PCR requires thermostable Taq polymerase, specific primers, dNTPs, and template DNA for amplification.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Biotechnology and Its Applications",
        "question_text": "Bt cotton contains a gene from:",
        "options": ["Bacillus thuringiensis", "Escherichia coli", "Agrobacterium", "Rhizobium"],
        "correct": "A",
        "explanation": "Bt cotton contains the cry gene from Bacillus thuringiensis, producing a toxin lethal to bollworms.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    # ── Ecology ──
    {
        "topic": "Organisms and Populations",
        "question_text": "The carrying capacity of an environment is:",
        "options": [
            "The maximum population size it can sustain",
            "The minimum population size",
            "The average population size",
            "The growth rate",
        ],
        "correct": "A",
        "explanation": "Carrying capacity (K) is the maximum population size that an environment can sustain indefinitely.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
    {
        "topic": "Ecosystem",
        "question_text": "The pyramid of energy in an ecosystem is always:",
        "options": ["Upright", "Inverted", "Spindle-shaped", "Variable"],
        "correct": "A",
        "explanation": "Energy decreases at each trophic level (10% law), so the energy pyramid is always upright.",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Biodiversity ──
    {
        "topic": "Biodiversity and Conservation",
        "question_text": "Biodiversity hotspots are regions with:",
        "options": [
            "High endemism and significant habitat loss",
            "High temperature",
            "Low rainfall",
            "High altitude",
        ],
        "correct": "A",
        "explanation": "Hotspots have ≥1500 endemic plant species and have lost ≥70% of original habitat (Myers criteria).",
        "difficulty": 2,
        "type": QuestionType.MCQ,
    },
    # ── Environmental Issues ──
    {
        "topic": "Environmental Issues",
        "question_text": "Eutrophication is caused by excess of:",
        "options": ["Nitrates and phosphates", "Heavy metals", "Carbon dioxide", "Sulphur dioxide"],
        "correct": "A",
        "explanation": "Excess nutrients (nitrates, phosphates) from fertilizers cause algal blooms, depleting oxygen and killing aquatic life.",
        "difficulty": 1,
        "type": QuestionType.MCQ,
    },
]

# ---------------------------------------------------------------------------
# Assertion-Reason templates
# ---------------------------------------------------------------------------

ASSERTION_REASON_TEMPLATES: list[dict[str, Any]] = [
    {
        "topic": "Laws of Motion",
        "assertion": "A body moving with constant velocity has zero acceleration.",
        "reason": "Acceleration is the rate of change of velocity.",
        "correct": "A",
        "explanation": "Both assertion and reason are true, and the reason correctly explains the assertion. If velocity is constant, dv/dt = 0.",
        "difficulty": 2,
        "type": QuestionType.ASSERTION_REASON,
    },
    {
        "topic": "Thermodynamics",
        "assertion": "The efficiency of a heat engine can never be 100%.",
        "reason": "Some heat is always rejected to the sink in a heat engine.",
        "correct": "A",
        "explanation": "Both are true and the reason explains the assertion. By the second law of thermodynamics, η = 1 - Q₂/Q₁ < 1.",
        "difficulty": 2,
        "type": QuestionType.ASSERTION_REASON,
    },
    {
        "topic": "Chemical Bonding and Molecular Structure",
        "assertion": "Water has a higher boiling point than H₂S.",
        "reason": "Water molecules form intermolecular hydrogen bonds.",
        "correct": "A",
        "explanation": "Both are true and the reason explains the assertion. H-bonding in water requires more energy to break than van der Waals forces in H₂S.",
        "difficulty": 2,
        "type": QuestionType.ASSERTION_REASON,
    },
    {
        "topic": "Principles of Inheritance and Variation",
        "assertion": "The phenotypic ratio of a dihybrid cross is 9:3:3:1.",
        "reason": "The two genes assort independently during gamete formation.",
        "correct": "A",
        "explanation": "Both are true and the reason explains the assertion. Independent assortment of two gene pairs gives 16 combinations with 9:3:3:1 ratio.",
        "difficulty": 2,
        "type": QuestionType.ASSERTION_REASON,
    },
    {
        "topic": "Electrostatic Potential and Capacitance",
        "assertion": "The electric field inside a charged conductor is zero.",
        "reason": "Charges reside only on the surface of a conductor.",
        "correct": "A",
        "explanation": "Both are true and the reason explains the assertion. In electrostatic equilibrium, charges redistribute on the surface until the internal field cancels.",
        "difficulty": 3,
        "type": QuestionType.ASSERTION_REASON,
    },
    {
        "topic": "Photosynthesis in Higher Plants",
        "assertion": "C₄ plants are more efficient than C₃ plants in hot climates.",
        "reason": "C₄ plants minimize photorespiration by concentrating CO₂ in bundle sheath cells.",
        "correct": "A",
        "explanation": "Both are true and the reason explains the assertion. The C₄ pathway concentrates CO₂ around RuBisCO, suppressing its oxygenase activity.",
        "difficulty": 3,
        "type": QuestionType.ASSERTION_REASON,
    },
    {
        "topic": "Equilibrium",
        "assertion": "Adding a catalyst does not change the equilibrium constant.",
        "reason": "A catalyst increases the rate of both forward and reverse reactions equally.",
        "correct": "A",
        "explanation": "Both are true and the reason explains the assertion. A catalyst lowers activation energy for both directions equally, speeding up equilibrium attainment without shifting it.",
        "difficulty": 2,
        "type": QuestionType.ASSERTION_REASON,
    },
    {
        "topic": "Dual Nature of Radiation and Matter",
        "assertion": "Photoelectric effect demonstrates the particle nature of light.",
        "reason": "The energy of photoelectrons depends on the frequency of incident light, not its intensity.",
        "correct": "A",
        "explanation": "Both are true and the reason explains the assertion. Einstein's photon theory (E = hν) explains why KE depends on frequency, not intensity.",
        "difficulty": 3,
        "type": QuestionType.ASSERTION_REASON,
    },
    {
        "topic": "Organic Chemistry — Some Basic Principles",
        "assertion": "Benzene undergoes electrophilic substitution rather than addition.",
        "reason": "Addition would destroy the aromatic stability of benzene.",
        "correct": "A",
        "explanation": "Both are true and the reason explains the assertion. Benzene's resonance energy (150 kJ/mol) makes substitution (preserving aromaticity) favorable over addition.",
        "difficulty": 3,
        "type": QuestionType.ASSERTION_REASON,
    },
    {
        "topic": "Cell Cycle and Cell Division",
        "assertion": "Meiosis reduces the chromosome number by half.",
        "reason": "Meiosis involves two successive divisions without an intervening DNA replication.",
        "correct": "A",
        "explanation": "Both are true and the reason explains the assertion. One round of DNA replication followed by two divisions (Meiosis I and II) produces four haploid cells.",
        "difficulty": 2,
        "type": QuestionType.ASSERTION_REASON,
    },
]

# ---------------------------------------------------------------------------
# Match the Following templates
# ---------------------------------------------------------------------------

MATCH_FOLLOWING_TEMPLATES: list[dict[str, Any]] = [
    {
        "topic": "Units and Measurement",
        "column_a": ["Force", "Pressure", "Energy", "Power"],
        "column_b": ["Newton", "Pascal", "Joule", "Watt"],
        "correct": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "explanation": "Force → Newton (N), Pressure → Pascal (Pa), Energy → Joule (J), Power → Watt (W).",
        "difficulty": 1,
        "type": QuestionType.MATCH_FOLLOWING,
    },
    {
        "topic": "Chemical Bonding and Molecular Structure",
        "column_a": ["sp", "sp²", "sp³", "sp³d"],
        "column_b": ["Linear", "Trigonal planar", "Tetrahedral", "Trigonal bipyramidal"],
        "correct": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "explanation": "sp → Linear (180°), sp² → Trigonal planar (120°), sp³ → Tetrahedral (109.5°), sp³d → Trigonal bipyramidal.",
        "difficulty": 2,
        "type": QuestionType.MATCH_FOLLOWING,
    },
    {
        "topic": "Body Fluids and Circulation",
        "column_a": ["SA node", "AV node", "Bundle of His", "Purkinje fibers"],
        "column_b": [
            "Pacemaker",
            "Delay impulse",
            "Conduct to ventricles",
            "Ventricular contraction",
        ],
        "correct": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "explanation": "SA node = pacemaker, AV node delays impulse, Bundle of His conducts to ventricles, Purkinje fibers trigger ventricular contraction.",
        "difficulty": 2,
        "type": QuestionType.MATCH_FOLLOWING,
    },
    {
        "topic": "Principles of Inheritance and Variation",
        "column_a": [
            "Law of Dominance",
            "Law of Segregation",
            "Law of Independent Assortment",
            "Incomplete Dominance",
        ],
        "column_b": ["3:1 ratio", "Gametes are pure", "9:3:3:1 ratio", "1:2:1 ratio"],
        "correct": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "explanation": "Dominance → 3:1 phenotypic ratio, Segregation → gametes carry one allele each, Independent Assortment → 9:3:3:1, Incomplete Dominance → 1:2:1.",
        "difficulty": 3,
        "type": QuestionType.MATCH_FOLLOWING,
    },
    {
        "topic": "Electrochemistry",
        "column_a": ["Galvanic cell", "Electrolytic cell", "Fuel cell", "Dry cell"],
        "column_b": [
            "Chemical → Electrical",
            "Electrical → Chemical",
            "Continuous fuel supply",
            "Leclanché cell",
        ],
        "correct": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "explanation": "Galvanic: chemical to electrical, Electrolytic: electrical to chemical, Fuel cell: continuous fuel, Dry cell: Leclanché type.",
        "difficulty": 2,
        "type": QuestionType.MATCH_FOLLOWING,
    },
]

# ---------------------------------------------------------------------------
# Numeric templates
# ---------------------------------------------------------------------------

NUMERIC_TEMPLATES: list[dict[str, Any]] = [
    {
        "topic": "Motion in a Straight Line",
        "question_text": "A body accelerates from rest at 5 m/s². Its velocity after 8 seconds is ___ m/s.",
        "correct_value": 40.0,
        "tolerance": 0.1,
        "explanation": "v = u + at = 0 + 5 × 8 = 40 m/s.",
        "difficulty": 1,
        "type": QuestionType.NUMERIC,
    },
    {
        "topic": "Work, Energy and Power",
        "question_text": "A force of 20 N displaces a body by 5 m in the direction of force. The work done is ___ J.",
        "correct_value": 100.0,
        "tolerance": 0.1,
        "explanation": "W = F × d = 20 × 5 = 100 J.",
        "difficulty": 1,
        "type": QuestionType.NUMERIC,
    },
    {
        "topic": "Current Electricity",
        "question_text": "A 12 V battery is connected to a 4 Ω resistor. The current flowing is ___ A.",
        "correct_value": 3.0,
        "tolerance": 0.1,
        "explanation": "I = V/R = 12/4 = 3 A.",
        "difficulty": 1,
        "type": QuestionType.NUMERIC,
    },
    {
        "topic": "Thermodynamics",
        "question_text": "A Carnot engine operates between 600 K and 300 K. Its efficiency is ___%.",
        "correct_value": 50.0,
        "tolerance": 0.1,
        "explanation": "η = (1 - T₂/T₁) × 100 = (1 - 300/600) × 100 = 50%.",
        "difficulty": 2,
        "type": QuestionType.NUMERIC,
    },
    {
        "topic": "Gravitation",
        "question_text": "If g = 10 m/s² at Earth's surface, the value of g at a height equal to Earth's radius is ___ m/s².",
        "correct_value": 2.5,
        "tolerance": 0.1,
        "explanation": "g' = g/(1+h/R)² = 10/(1+1)² = 10/4 = 2.5 m/s².",
        "difficulty": 3,
        "type": QuestionType.NUMERIC,
    },
    {
        "topic": "Optics",
        "question_text": "The focal length of a concave mirror is 15 cm. An object is placed at 30 cm. The image distance is ___ cm.",
        "correct_value": -30.0,
        "tolerance": 0.5,
        "explanation": "1/v + 1/u = 1/f → 1/v + 1/(-30) = 1/(-15) → 1/v = -1/15 + 1/30 = -1/30 → v = -30 cm.",
        "difficulty": 3,
        "type": QuestionType.NUMERIC,
    },
    {
        "topic": "Equilibrium",
        "question_text": "The pH of a 0.01 M NaOH solution is ___ (at 25°C).",
        "correct_value": 12.0,
        "tolerance": 0.1,
        "explanation": "[OH⁻] = 0.01 M = 10⁻² M. pOH = 2. pH = 14 - 2 = 12.",
        "difficulty": 2,
        "type": QuestionType.NUMERIC,
    },
    {
        "topic": "Oscillations",
        "question_text": "A mass of 2 kg is attached to a spring with k = 200 N/m. The angular frequency is ___ rad/s.",
        "correct_value": 10.0,
        "tolerance": 0.1,
        "explanation": "ω = √(k/m) = √(200/2) = √100 = 10 rad/s.",
        "difficulty": 2,
        "type": QuestionType.NUMERIC,
    },
]

# ---------------------------------------------------------------------------
# Combine all templates
# ---------------------------------------------------------------------------

ALL_TEMPLATES: list[dict[str, Any]] = (
    PHYSICS_TEMPLATES
    + CHEMISTRY_TEMPLATES
    + BIOLOGY_TEMPLATES
    + ASSERTION_REASON_TEMPLATES
    + MATCH_FOLLOWING_TEMPLATES
    + NUMERIC_TEMPLATES
)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class GeneratedQuestion:
    """A single generated question."""

    id: str
    chapter_id: str
    topic: str
    subject: str
    question_text: str
    question_type: QuestionType
    options: dict[str, str] | None = None
    correct_answer: str = ""
    explanation: str = ""
    difficulty: int = 1
    column_a: list[str] | None = None
    column_b: list[str] | None = None
    correct_value: float | None = None
    tolerance: float | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "chapter_id": self.chapter_id,
            "topic": self.topic,
            "subject": self.subject,
            "question_text": self.question_text,
            "question_type": self.question_type.value,
            "difficulty": self.difficulty,
            "explanation": self.explanation,
        }
        if self.options:
            result.update(self.options)
        if self.column_a:
            result["column_a"] = self.column_a
        if self.column_b:
            result["column_b"] = self.column_b
        if self.correct_value is not None:
            result["correct_value"] = self.correct_value
        if self.tolerance is not None:
            result["tolerance"] = self.tolerance
        return result


# ---------------------------------------------------------------------------
# Chapter ID mapping
# ---------------------------------------------------------------------------

CHAPTER_ID_MAP: dict[str, str] = {
    # Physics 11th
    "Units and Measurement": "ch_physics_11_01",
    "Motion in a Straight Line": "ch_physics_11_02",
    "Motion in a Plane": "ch_physics_11_03",
    "Laws of Motion": "ch_physics_11_04",
    "Work, Energy and Power": "ch_physics_11_05",
    "System of Particles and Rotational Motion": "ch_physics_11_06",
    "Gravitation": "ch_physics_11_07",
    "Mechanical Properties of Solids": "ch_physics_11_08",
    "Mechanical Properties of Fluids": "ch_physics_11_09",
    "Thermal Properties of Matter": "ch_physics_11_10",
    "Thermodynamics": "ch_physics_11_11",
    "Kinetic Theory": "ch_physics_11_12",
    "Oscillations": "ch_physics_11_13",
    "Waves": "ch_physics_11_14",
    # Physics 12th
    "Electric Charges and Fields": "ch_physics_12_01",
    "Electrostatic Potential and Capacitance": "ch_physics_12_02",
    "Current Electricity": "ch_physics_12_03",
    "Moving Charges and Magnetism": "ch_physics_12_04",
    "Magnetism and Matter": "ch_physics_12_05",
    "Electromagnetic Induction": "ch_physics_12_06",
    "Alternating Current": "ch_physics_12_07",
    "Electromagnetic Waves": "ch_physics_12_08",
    "Ray Optics and Optical Instruments": "ch_physics_12_09",
    "Wave Optics": "ch_physics_12_10",
    "Dual Nature of Radiation and Matter": "ch_physics_12_11",
    "Atoms": "ch_physics_12_12",
    "Nuclei": "ch_physics_12_13",
    "Semiconductor Electronics": "ch_physics_12_14",
    # Chemistry 11th (Thermodynamics also in Physics — use subject-prefixed key)
    "Some Basic Concepts of Chemistry": "ch_chemistry_11_01",
    "Structure of Atom": "ch_chemistry_11_02",
    "Classification of Elements and Periodicity": "ch_chemistry_11_03",
    "Chemical Bonding and Molecular Structure": "ch_chemistry_11_04",
    "States of Matter": "ch_chemistry_11_05",
    "Chemistry Thermodynamics": "ch_chemistry_11_06",
    "Equilibrium": "ch_chemistry_11_07",
    "Redox Reactions": "ch_chemistry_11_08",
    "Hydrogen": "ch_chemistry_11_09",
    "The s-Block Elements": "ch_chemistry_11_10",
    "The p-Block Elements": "ch_chemistry_11_11",
    "Organic Chemistry — Some Basic Principles": "ch_chemistry_11_12",
    "Hydrocarbons": "ch_chemistry_11_13",
    # Chemistry 12th
    "The Solid State": "ch_chemistry_12_01",
    "Solutions": "ch_chemistry_12_02",
    "Electrochemistry": "ch_chemistry_12_03",
    "Chemical Kinetics": "ch_chemistry_12_04",
    "Surface Chemistry": "ch_chemistry_12_05",
    "General Principles of Metallurgy": "ch_chemistry_12_06",
    "Haloalkanes and Haloarenes": "ch_chemistry_12_09",
    "Alcohols, Phenols and Ethers": "ch_chemistry_12_10",
    "Aldehydes, Ketones and Carboxylic Acids": "ch_chemistry_12_11",
    "Amines": "ch_chemistry_12_12",
    "Chemistry Biomolecules": "ch_chemistry_12_13",
    "Polymers": "ch_chemistry_12_14",
    # Biology 11th
    "The Living World": "ch_biology_11_01",
    "Biological Classification": "ch_biology_11_02",
    "Plant Kingdom": "ch_biology_11_03",
    "Morphology of Flowering Plants": "ch_biology_11_04",
    "Anatomy of Flowering Plants": "ch_biology_11_05",
    "Cell — The Unit of Life": "ch_biology_11_06",
    "Biomolecules": "ch_biology_11_07",
    "Cell Cycle and Cell Division": "ch_biology_11_08",
    "Photosynthesis in Higher Plants": "ch_biology_11_09",
    "Respiration in Plants": "ch_biology_11_10",
    "Plant Growth and Development": "ch_biology_11_11",
    "Structural Organisation in Animals": "ch_biology_11_12",
    "Body Fluids and Circulation": "ch_biology_11_13",
    "Breathing and Exchange of Gases": "ch_biology_11_14",
    "Excretory Products and Their Elimination": "ch_biology_11_15",
    "Locomotion and Movement": "ch_biology_11_16",
    "Neural Control and Coordination": "ch_biology_11_17",
    # Biology 12th
    "Reproduction in Organisms": "ch_biology_12_01",
    "Sexual Reproduction in Flowering Plants": "ch_biology_12_02",
    "Human Reproduction": "ch_biology_12_03",
    "Reproductive Health": "ch_biology_12_04",
    "Principles of Inheritance and Variation": "ch_biology_12_05",
    "Molecular Basis of Inheritance": "ch_biology_12_06",
    "Evolution": "ch_biology_12_07",
    "Human Health and Disease": "ch_biology_12_08",
    "Biotechnology — Principles and Processes": "ch_biology_12_11",
    "Biotechnology and Its Applications": "ch_biology_12_12",
    "Organisms and Populations": "ch_biology_12_13",
    "Ecosystem": "ch_biology_12_14",
    "Biodiversity and Conservation": "ch_biology_12_15",
    "Environmental Issues": "ch_biology_12_16",
}


# ---------------------------------------------------------------------------
# Subject detection helper
# ---------------------------------------------------------------------------


def _detect_subject(topic: str) -> str:
    """Detect subject from topic name."""
    for subject, grades in SYLLABUS.items():
        for _grade, topics in grades.items():
            if topic in topics:
                return subject.value
    # Fallback: keyword-based detection
    physics_kw = [
        "motion",
        "force",
        "energy",
        "wave",
        "optics",
        "electric",
        "magnet",
        "thermo",
        "oscill",
        "gravit",
        "unit",
        "rotat",
        "kinetic",
        "semiconductor",
        "atom",
        "nuclei",
        "dual",
        "alternating",
        "electromagnetic",
    ]
    chemistry_kw = [
        "bond",
        "atom",
        "periodic",
        "equilibrium",
        "redox",
        "organic",
        "solution",
        "electrochem",
        "kinetics",
        "surface",
        "metallur",
        "coordination",
        "alcohol",
        "aldehyde",
        "amine",
        "biomolecule",
        "polymer",
        "solid state",
        "hydrogen",
        "hydrocarbon",
    ]
    biology_kw = [
        "cell",
        "reproduction",
        "genetics",
        "evolution",
        "health",
        "biotech",
        "ecolog",
        "biodiversity",
        "environment",
        "plant",
        "animal",
        "body",
        "breathing",
        "excret",
        "locomotion",
        "neural",
        "photosynthesis",
        "respiration",
        "living",
        "classification",
        "morphology",
        "anatomy",
        "biomol",
        "division",
        "growth",
        "fluid",
        "organism",
        "population",
        "ecosystem",
    ]

    topic_lower = topic.lower()
    if any(kw in topic_lower for kw in physics_kw):
        return Subject.PHYSICS.value
    if any(kw in topic_lower for kw in chemistry_kw):
        return Subject.CHEMISTRY.value
    if any(kw in topic_lower for kw in biology_kw):
        return Subject.BIOLOGY.value
    return Subject.PHYSICS.value


def _get_chapter_id(topic: str) -> str:
    """Get chapter ID for a topic."""
    return CHAPTER_ID_MAP.get(topic, f"ch_{_detect_subject(topic)}_unknown")


# ---------------------------------------------------------------------------
# Distractor generation helpers
# ---------------------------------------------------------------------------


def _generate_numeric_distractors(
    correct: float, count: int = 3, rng: random.Random | None = None
) -> list[float]:
    """Generate plausible numeric distractors near the correct value."""
    if rng is None:
        rng = random.Random()
    distractors: set[float] = set()
    factors = [0.5, 1.5, 2.0, 0.25, 3.0, 0.75, 4.0]
    offsets = [1, 2, 5, 10, -1, -2, -5]

    for f in factors:
        distractors.add(round(correct * f, 2))
    for o in offsets:
        distractors.add(round(correct + o, 2))

    distractors.discard(correct)
    result = list(distractors)[:count]
    while len(result) < count:
        result.append(round(correct * rng.uniform(0.3, 3.0), 2))
    return result[:count]


def _generate_mcq_distractors(
    correct_option: str,
    all_options: list[str],
    count: int = 3,
    rng: random.Random | None = None,
) -> list[str]:
    """Select distractors from available options, excluding the correct one."""
    if rng is None:
        rng = random.Random()
    distractors = [o for o in all_options if o != correct_option]
    rng.shuffle(distractors)
    return distractors[:count]


# ---------------------------------------------------------------------------
# Question Generator Service
# ---------------------------------------------------------------------------


class QuizGenerator:
    """Generates NEET-style MCQ questions using template-based generation."""

    def __init__(self, seed: int | None = None) -> None:
        self._seed = seed
        self._templates: list[dict[str, Any]] = ALL_TEMPLATES
        self._question_counter: int = 0
        logger.info("quiz.generator.initialized", seed=seed, template_count=len(self._templates))

    def _get_rng(self, chapter_id: str = "", topic: str = "") -> random.Random:
        """Get a deterministic random generator for reproducibility."""
        seed_str = f"{self._seed or 42}:{chapter_id}:{topic}:{self._question_counter}"
        hash_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
        return random.Random(hash_val)

    def _fill_template(self, template: dict[str, Any], rng: random.Random) -> dict[str, Any]:
        """Fill a template with concrete values using parameterized variants."""
        topic = template["topic"]
        question_type = template.get("type", QuestionType.MCQ)

        if question_type == QuestionType.NUMERIC:
            return dict(template)

        if question_type == QuestionType.ASSERTION_REASON:
            return dict(template)

        if question_type == QuestionType.MATCH_FOLLOWING:
            return dict(template)

        # For MCQ templates with placeholders, use parameterized variants
        question_text = template["question_text"]
        options = list(template["options"])

        # Parameterized question variants
        param_questions = _PARAMETERIZED_QUESTIONS.get(topic, [])
        if param_questions:
            idx = rng.randint(0, len(param_questions) - 1)
            params = param_questions[idx]
            question_text = template["question_text"].format(**params)
            options = [opt.format(**params) for opt in template["options"]]

        return {
            **template,
            "question_text": question_text,
            "options": options,
        }

    def _build_question(
        self,
        template: dict[str, Any],
        chapter_id: str,
        topic: str,
        rng: random.Random,
    ) -> GeneratedQuestion:
        """Build a GeneratedQuestion from a filled template."""
        filled = self._fill_template(template, rng)
        question_type = filled.get("type", QuestionType.MCQ)
        subject = _detect_subject(topic)
        self._question_counter += 1
        qid = f"gq_{subject[:3]}_{self._question_counter:04d}"

        kwargs: dict[str, Any] = {
            "id": qid,
            "chapter_id": chapter_id,
            "topic": topic,
            "subject": subject,
            "question_text": filled["question_text"],
            "question_type": question_type,
            "explanation": filled.get("explanation", ""),
            "difficulty": filled.get("difficulty", 1),
        }

        if question_type == QuestionType.MCQ:
            options = filled.get("options", ["A", "B", "C", "D"])
            labels = ["A", "B", "C", "D"]
            correct_idx = labels.index(filled.get("correct", "A"))

            # Shuffle options but track correct answer
            paired = list(zip(labels, options, strict=True))
            rng.shuffle(paired)
            shuffled_options = dict(paired)

            # Find new correct label
            for label, opt in shuffled_options.items():
                if opt == options[correct_idx]:
                    new_correct = label
                    break
            else:
                new_correct = "A"

            kwargs["options"] = shuffled_options
            kwargs["correct_answer"] = new_correct

        elif question_type == QuestionType.NUMERIC:
            kwargs["correct_value"] = filled.get("correct_value", 0.0)
            kwargs["tolerance"] = filled.get("tolerance", 0.1)
            kwargs["correct_answer"] = str(filled.get("correct_value", 0.0))

            # Generate distractors as options for display
            distractors = _generate_numeric_distractors(filled.get("correct_value", 0.0), 3, rng)
            all_vals = [filled.get("correct_value", 0.0)] + distractors
            rng.shuffle(all_vals)
            labels = ["A", "B", "C", "D"]
            kwargs["options"] = {labels[i]: str(v) for i, v in enumerate(all_vals)}
            for label, val in kwargs["options"].items():
                if float(val) == filled.get("correct_value", 0.0):
                    kwargs["correct_answer"] = label
                    break

        elif question_type == QuestionType.ASSERTION_REASON:
            kwargs["options"] = {
                "A": "Both Assertion and Reason are true and Reason is the correct explanation of Assertion",
                "B": "Both Assertion and Reason are true but Reason is NOT the correct explanation of Assertion",
                "C": "Assertion is true but Reason is false",
                "D": "Assertion is false but Reason is true",
            }
            kwargs["correct_answer"] = filled.get("correct", "A")
            kwargs["question_text"] = (
                f"Assertion: {filled['assertion']}\nReason: {filled['reason']}"
            )

        elif question_type == QuestionType.MATCH_FOLLOWING:
            kwargs["column_a"] = filled.get("column_a", [])
            kwargs["column_b"] = filled.get("column_b", [])
            kwargs["correct_answer"] = str(filled.get("correct", {}))

        return GeneratedQuestion(**kwargs)

    def generate_questions(
        self,
        chapter_id: str,
        topic: str,
        count: int = 10,
        difficulty: int | None = None,
        question_type: QuestionType | None = None,
    ) -> list[GeneratedQuestion]:
        """Generate questions for a specific chapter/topic.

        Args:
            chapter_id: The chapter identifier.
            topic: The topic name.
            count: Number of questions to generate.
            difficulty: Filter by difficulty level (1-5).
            question_type: Filter by question type.

        Returns:
            List of GeneratedQuestion objects.
        """
        rng = self._get_rng(chapter_id, topic)

        # Filter templates by topic
        pool = [t for t in self._templates if t["topic"] == topic]

        # Apply difficulty filter
        if difficulty is not None:
            pool = [t for t in pool if t.get("difficulty") == difficulty]

        # Apply question type filter
        if question_type is not None:
            pool = [t for t in pool if t.get("type") == question_type]

        # If no topic-specific templates, use all templates and tag with topic
        if not pool:
            logger.warning(
                "quiz.generator.no_topic_templates",
                topic=topic,
                chapter_id=chapter_id,
            )
            pool = list(self._templates)
            if difficulty is not None:
                pool = [t for t in pool if t.get("difficulty") == difficulty]
            if question_type is not None:
                pool = [t for t in pool if t.get("type") == question_type]

        if not pool:
            logger.error("quiz.generator.no_templates_after_filter")
            return []

        # Select templates (with replacement if needed)
        selected = []
        for _ in range(count):
            idx = rng.randint(0, len(pool) - 1)
            selected.append(pool[idx])

        # Build questions
        questions = []
        for template in selected:
            q = self._build_question(template, chapter_id, topic, rng)
            questions.append(q)

        logger.info(
            "quiz.generator.questions_generated",
            chapter_id=chapter_id,
            topic=topic,
            count=len(questions),
            difficulty=difficulty,
            question_type=question_type.value if question_type else None,
        )

        return questions

    def generate_mixed_quiz(
        self,
        subject: Subject,
        count: int = 30,
        difficulty_range: tuple[int, int] = (1, 5),
    ) -> list[GeneratedQuestion]:
        """Generate a mixed quiz across all topics of a subject.

        Args:
            subject: The subject (Physics, Chemistry, Biology).
            count: Total number of questions.
            difficulty_range: Tuple of (min_difficulty, max_difficulty).

        Returns:
            List of GeneratedQuestion objects.
        """
        rng = self._get_rng(subject.value, "mixed")
        min_diff, max_diff = difficulty_range

        # Collect all topics for the subject
        topics: list[str] = []
        for _grade, topic_list in SYLLABUS.get(subject, {}).items():
            topics.extend(topic_list)

        # Filter templates by subject topics and difficulty
        pool = [
            t
            for t in self._templates
            if t["topic"] in topics and min_diff <= t.get("difficulty", 1) <= max_diff
        ]

        if not pool:
            logger.error(
                "quiz.generator.no_subject_templates",
                subject=subject.value,
            )
            return []

        # Distribute questions across topics
        questions_per_topic = max(1, count // len(topics))
        remainder = count - (questions_per_topic * len(topics))

        questions: list[GeneratedQuestion] = []
        for i, topic in enumerate(topics):
            n = questions_per_topic + (1 if i < remainder else 0)
            chapter_id = _get_chapter_id(topic)
            topic_pool = [t for t in pool if t["topic"] == topic]
            if not topic_pool:
                continue

            for _ in range(n):
                idx = rng.randint(0, len(topic_pool) - 1)
                template = topic_pool[idx]
                q = self._build_question(template, chapter_id, topic, rng)
                questions.append(q)

        rng.shuffle(questions)

        logger.info(
            "quiz.generator.mixed_quiz_generated",
            subject=subject.value,
            count=len(questions),
            difficulty_range=difficulty_range,
        )

        return questions

    def get_syllabus(self) -> dict[str, dict[str, list[str]]]:
        """Return the full NEET syllabus structure."""
        return SYLLABUS

    def get_topics_for_subject(self, subject: Subject) -> list[str]:
        """Get all topics for a subject."""
        topics: list[str] = []
        for _grade, topic_list in SYLLABUS.get(subject, {}).items():
            topics.extend(topic_list)
        return topics

    def get_template_count(self) -> int:
        """Return total number of question templates."""
        return len(self._templates)

    def reset(self) -> None:
        """Reset the generator state."""
        self._question_counter = 0
        logger.info("quiz.generator.reset")


# ---------------------------------------------------------------------------
# Parameterized question data for numeric variation
# ---------------------------------------------------------------------------

_PARAMETERIZED_QUESTIONS: dict[str, list[dict[str, Any]]] = {
    "Motion in a Straight Line": [
        {"a": "2", "t": "10", "v_a": "20", "v_b": "10", "v_c": "15", "v_d": "25"},
        {"a": "5", "t": "8", "v_a": "40", "v_b": "35", "v_c": "45", "v_d": "30"},
        {"a": "3", "t": "6", "v_a": "18", "v_b": "12", "v_c": "24", "v_d": "15"},
    ],
    "Laws of Motion": [
        {"f": "10", "m": "2", "a_a": "5", "a_b": "2", "a_c": "10", "a_d": "20"},
        {"f": "20", "m": "4", "a_a": "5", "a_b": "10", "a_c": "2", "a_d": "8"},
        {"f": "15", "m": "3", "a_a": "5", "a_b": "3", "a_c": "15", "a_d": "45"},
    ],
    "Work, Energy and Power": [
        {"m": "5", "v": "10", "ke_a": "250", "ke_b": "500", "ke_c": "100", "ke_d": "50"},
        {"m": "2", "v": "20", "ke_a": "400", "ke_b": "200", "ke_c": "800", "ke_d": "100"},
        {"m": "10", "v": "5", "ke_a": "125", "ke_b": "250", "ke_c": "50", "ke_d": "500"},
    ],
    "Some Basic Concepts of Chemistry": [
        {
            "compound": "CO₂",
            "mass": "22",
            "mol_a": "0.5",
            "mol_b": "0.25",
            "mol_c": "1.0",
            "mol_d": "2.0",
            "explanation": "Molar mass of CO₂ = 44 g/mol. Moles = 22/44 = 0.5 mol.",
        },
        {
            "compound": "H₂O",
            "mass": "36",
            "mol_a": "2.0",
            "mol_b": "1.0",
            "mol_c": "0.5",
            "mol_d": "4.0",
            "explanation": "Molar mass of H₂O = 18 g/mol. Moles = 36/18 = 2.0 mol.",
        },
    ],
}
