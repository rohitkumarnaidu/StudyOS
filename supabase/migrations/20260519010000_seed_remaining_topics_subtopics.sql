-- StudyOS — Phase 1 Supplemental: Seed remaining topics and subtopics
-- Adds topics/subtopics for Chemistry (25 chapters) and Biology (36 chapters)
-- Target: 450+ total subtopics across all 91 chapters

-- ============================================
-- CHEMISTRY: Chapters 1-25
-- ============================================

-- Chemistry Ch1: Classification of Elements and Periodicity
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2001-0001-0000-000000000001', '13000000-1000-1000-1000-100000000001', 'Periodic Classification', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2001-0001-0001-000000000001', '15000000-2001-0001-0000-000000000001', 'Mendeleev periodic table', 1, 20),
('16000000-2001-0001-0002-000000000001', '15000000-2001-0001-0000-000000000001', 'Modern periodic law', 2, 15),
('16000000-2001-0001-0003-000000000001', '15000000-2001-0001-0000-000000000001', 'Periodic trends (radius, IE, EA, EN)', 3, 30),
('16000000-2001-0001-0004-000000000001', '15000000-2001-0001-0000-000000000001', 'Nomenclature of elements with Z > 100', 4, 15);

-- Chemistry Ch2: Chemical Bonding
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2002-0001-0000-000000000001', '13000000-1000-1000-1000-100000000002', 'Chemical Bonding', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2002-0001-0001-000000000001', '15000000-2002-0001-0000-000000000001', 'Ionic and covalent bonding', 1, 25),
('16000000-2002-0001-0002-000000000001', '15000000-2002-0001-0000-000000000001', 'VSEPR theory and molecular shapes', 2, 30),
('16000000-2002-0001-0003-000000000001', '15000000-2002-0001-0000-000000000001', 'Valence bond theory and hybridization', 3, 30),
('16000000-2002-0001-0004-000000000001', '15000000-2002-0001-0000-000000000001', 'Molecular orbital theory', 4, 30),
('16000000-2002-0001-0005-000000000001', '15000000-2002-0001-0000-000000000001', 'Hydrogen bonding', 5, 15);

-- Chemistry Ch3: Coordination Compounds
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2003-0001-0000-000000000001', '13000000-1000-1000-1000-100000000003', 'Coordination Chemistry', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2003-0001-0001-000000000001', '15000000-2003-0001-0000-000000000001', 'Werner theory and IUPAC nomenclature', 1, 20),
('16000000-2003-0001-0002-000000000001', '15000000-2003-0001-0000-000000000001', 'Isomerism in coordination compounds', 2, 25),
('16000000-2003-0001-0003-000000000001', '15000000-2003-0001-0000-000000000001', 'Crystal field theory', 3, 30),
('16000000-2003-0001-0004-000000000001', '15000000-2003-0001-0000-000000000001', 'Bonding in metal carbonyls', 4, 15);

-- Chemistry Ch4: d and f Block Elements
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2004-0001-0000-000000000001', '13000000-1000-1000-1000-100000000004', 'd and f Block', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2004-0001-0001-000000000001', '15000000-2004-0001-0000-000000000001', 'Electronic configuration of d-block', 1, 20),
('16000000-2004-0001-0002-000000000001', '15000000-2004-0001-0000-000000000001', 'General properties of transition elements', 2, 25),
('16000000-2004-0001-0003-000000000001', '15000000-2004-0001-0000-000000000001', 'Important compounds: K2Cr2O7, KMnO4', 3, 25),
('16000000-2004-0001-0004-000000000001', '15000000-2004-0001-0000-000000000001', 'Lanthanoids and actinoids', 4, 20);

-- Chemistry Ch5: Salt Analysis
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2005-0001-0000-000000000001', '13000000-1000-1000-1000-100000000005', 'Salt Analysis', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2005-0001-0001-000000000001', '15000000-2005-0001-0000-000000000001', 'Qualitative analysis of cations', 1, 30),
('16000000-2005-0001-0002-000000000001', '15000000-2005-0001-0000-000000000001', 'Qualitative analysis of anions', 2, 25),
('16000000-2005-0001-0003-000000000001', '15000000-2005-0001-0000-000000000001', 'Confirmatory tests', 3, 20);

-- Chemistry Ch6: p-Block Elements
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2006-0001-0000-000000000001', '13000000-1000-1000-1000-100000000006', 'p-Block Elements', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2006-0001-0001-000000000001', '15000000-2006-0001-0000-000000000001', 'Group 15: Nitrogen family', 1, 25),
('16000000-2006-0001-0002-000000000001', '15000000-2006-0001-0000-000000000001', 'Group 16: Oxygen family', 2, 25),
('16000000-2006-0001-0003-000000000001', '15000000-2006-0001-0000-000000000001', 'Group 17: Halogens', 3, 25),
('16000000-2006-0001-0004-000000000001', '15000000-2006-0001-0000-000000000001', 'Group 18: Noble gases', 4, 15);

-- Chemistry Ch7: IUPAC Naming
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2007-0001-0000-000000000001', '13000000-1000-1000-1000-100000000007', 'IUPAC Nomenclature', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2007-0001-0001-000000000001', '15000000-2007-0001-0000-000000000001', 'Rules for naming organic compounds', 1, 25),
('16000000-2007-0001-0002-000000000001', '15000000-2007-0001-0000-000000000001', 'Naming of functional groups', 2, 25),
('16000000-2007-0001-0003-000000000001', '15000000-2007-0001-0000-000000000001', 'Common and IUPAC names', 3, 20);

-- Chemistry Ch8: Isomerism
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2008-0001-0000-000000000001', '13000000-1000-1000-1000-100000000008', 'Isomerism', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2008-0001-0001-000000000001', '15000000-2008-0001-0000-000000000001', 'Structural isomerism', 1, 25),
('16000000-2008-0001-0002-000000000001', '15000000-2008-0001-0000-000000000001', 'Stereoisomerism (geometrical)', 2, 30),
('16000000-2008-0001-0003-000000000001', '15000000-2008-0001-0000-000000000001', 'Optical isomerism', 3, 30);

-- Chemistry Ch9: General Organic Chemistry
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2009-0001-0000-000000000001', '13000000-1000-1000-1000-100000000009', 'General Organic Chemistry', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2009-0001-0001-000000000001', '15000000-2009-0001-0000-000000000001', 'Inductive and resonance effects', 1, 30),
('16000000-2009-0001-0002-000000000001', '15000000-2009-0001-0000-000000000001', 'Reaction intermediates', 2, 25),
('16000000-2009-0001-0003-000000000001', '15000000-2009-0001-0000-000000000001', 'Electrophiles and nucleophiles', 3, 20),
('16000000-2009-0001-0004-000000000001', '15000000-2009-0001-0000-000000000001', 'Purification and analysis of organic compounds', 4, 20);

-- Chemistry Ch10: Hydrocarbons
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2010-0001-0000-000000000001', '13000000-1000-1000-1000-100000000010', 'Hydrocarbons', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2010-0001-0001-000000000001', '15000000-2010-0001-0000-000000000001', 'Alkanes: preparation and reactions', 1, 25),
('16000000-2010-0001-0002-000000000001', '15000000-2010-0001-0000-000000000001', 'Alkenes: electrophilic addition', 2, 30),
('16000000-2010-0001-0003-000000000001', '15000000-2010-0001-0000-000000000001', 'Alkynes: acidic character and addition', 3, 25),
('16000000-2010-0001-0004-000000000001', '15000000-2010-0001-0000-000000000001', 'Aromatic hydrocarbons and electrophilic substitution', 4, 30);

-- Chemistry Ch11: Haloalkanes and Haloarenes
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2011-0001-0000-000000000001', '13000000-1000-1000-1000-100000000011', 'Haloalkanes and Haloarenes', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2011-0001-0001-000000000001', '15000000-2011-0001-0000-000000000001', 'SN1 and SN2 mechanisms', 1, 30),
('16000000-2011-0001-0002-000000000001', '15000000-2011-0001-0000-000000000001', 'Elimination reactions (E1, E2)', 2, 25),
('16000000-2011-0001-0003-000000000001', '15000000-2011-0001-0000-000000000001', 'Reactions of haloarenes', 3, 20);

-- Chemistry Ch12: Alcohols, Phenols, Ethers
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2012-0001-0000-000000000001', '13000000-1000-1000-1000-100000000012', 'Alcohols Phenols Ethers', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2012-0001-0001-000000000001', '15000000-2012-0001-0000-000000000001', 'Preparation and properties of alcohols', 1, 25),
('16000000-2012-0001-0002-000000000001', '15000000-2012-0001-0000-000000000001', 'Phenols: acidity and electrophilic substitution', 2, 25),
('16000000-2012-0001-0003-000000000001', '15000000-2012-0001-0000-000000000001', 'Ethers: preparation and reactions', 3, 20);

-- Chemistry Ch13: Aldehydes, Ketones, Carboxylic Acids
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2013-0001-0000-000000000001', '13000000-1000-1000-1000-100000000013', 'Carbonyl Compounds', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2013-0001-0001-000000000001', '15000000-2013-0001-0000-000000000001', 'Nucleophilic addition reactions', 1, 30),
('16000000-2013-0001-0002-000000000001', '15000000-2013-0001-0000-000000000001', 'Aldol condensation and Cannizzaro reaction', 2, 30),
('16000000-2013-0001-0003-000000000001', '15000000-2013-0001-0000-000000000001', 'Carboxylic acids: acidity and reactions', 3, 25);

-- Chemistry Ch14: Organic Compounds with Nitrogen
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2014-0001-0000-000000000001', '13000000-1000-1000-1000-100000000014', 'Nitrogen Compounds', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2014-0001-0001-000000000001', '15000000-2014-0001-0000-000000000001', 'Amines: preparation and basicity', 1, 25),
('16000000-2014-0001-0002-000000000001', '15000000-2014-0001-0000-000000000001', 'Diazonium salts and applications', 2, 25),
('16000000-2014-0001-0003-000000000001', '15000000-2014-0001-0000-000000000001', 'Cyanides and isocyanides', 3, 15);

-- Chemistry Ch15: Biomolecules
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2015-0001-0000-000000000001', '13000000-1000-1000-1000-100000000015', 'Biomolecules', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2015-0001-0001-000000000001', '15000000-2015-0001-0000-000000000001', 'Carbohydrates: classification and properties', 1, 25),
('16000000-2015-0001-0002-000000000001', '15000000-2015-0001-0000-000000000001', 'Amino acids and proteins', 2, 25),
('16000000-2015-0001-0003-000000000001', '15000000-2015-0001-0000-000000000001', 'Vitamins and nucleic acids', 3, 20);

-- Chemistry Ch16: Practical Organic Chemistry
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2016-0001-0000-000000000001', '13000000-1000-1000-1000-100000000016', 'Practical Organic Chemistry', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2016-0001-0001-000000000001', '15000000-2016-0001-0000-000000000001', 'Detection of elements', 1, 15),
('16000000-2016-0001-0002-000000000001', '15000000-2016-0001-0000-000000000001', 'Functional group tests', 2, 25);

-- Chemistry Ch17: Some Basic Concepts
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2017-0001-0000-000000000001', '13000000-1000-1000-1000-100000000017', 'Basic Concepts', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2017-0001-0001-000000000001', '15000000-2017-0001-0000-000000000001', 'Mole concept and stoichiometry', 1, 30),
('16000000-2017-0001-0002-000000000001', '15000000-2017-0001-0000-000000000001', 'Empirical and molecular formula', 2, 20),
('16000000-2017-0001-0003-000000000001', '15000000-2017-0001-0000-000000000001', 'Concentration terms', 3, 20);

-- Chemistry Ch18: Redox Reactions
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2018-0001-0000-000000000001', '13000000-1000-1000-1000-100000000018', 'Redox Reactions', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2018-0001-0001-000000000001', '15000000-2018-0001-0000-000000000001', 'Oxidation and reduction concepts', 1, 20),
('16000000-2018-0001-0002-000000000001', '15000000-2018-0001-0000-000000000001', 'Balancing redox equations', 2, 25),
('16000000-2018-0001-0003-000000000001', '15000000-2018-0001-0000-000000000001', 'Oxidation number rules', 3, 15);

-- Chemistry Ch19: Solutions
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2019-0001-0000-000000000001', '13000000-1000-1000-1000-100000000019', 'Solutions', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2019-0001-0001-000000000001', '15000000-2019-0001-0000-000000000001', 'Colligative properties', 1, 30),
('16000000-2019-0001-0002-000000000001', '15000000-2019-0001-0000-000000000001', 'Raoult law and ideal solutions', 2, 25),
('16000000-2019-0001-0003-000000000001', '15000000-2019-0001-0000-000000000001', 'Van Hoff factor and abnormal molar mass', 3, 20);

-- Chemistry Ch20: Thermodynamics
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2020-0001-0000-000000000001', '13000000-1000-1000-1000-100000000020', 'Chemical Thermodynamics', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2020-0001-0001-000000000001', '15000000-2020-0001-0000-000000000001', 'First law and enthalpy', 1, 25),
('16000000-2020-0001-0002-000000000001', '15000000-2020-0001-0000-000000000001', 'Second law and entropy', 2, 25),
('16000000-2020-0001-0003-000000000001', '15000000-2020-0001-0000-000000000001', 'Gibbs free energy and spontaneity', 3, 25);

-- Chemistry Ch21: Equilibrium
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2021-0001-0000-000000000001', '13000000-1000-1000-1000-100000000021', 'Chemical Equilibrium', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2021-0001-0001-000000000001', '15000000-2021-0001-0000-000000000001', 'Law of mass action and equilibrium constant', 1, 25),
('16000000-2021-0001-0002-000000000001', '15000000-2021-0001-0000-000000000001', 'Le Chatelier principle', 2, 20),
('16000000-2021-0001-0003-000000000001', '15000000-2021-0001-0000-000000000001', 'Acid-base equilibria and pH', 3, 30),
('16000000-2021-0001-0004-000000000001', '15000000-2021-0001-0000-000000000001', 'Solubility product and common ion effect', 4, 25);

-- Chemistry Ch22: Electrochemistry
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2022-0001-0000-000000000001', '13000000-1000-1000-1000-100000000022', 'Electrochemistry', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2022-0001-0001-000000000001', '15000000-2022-0001-0000-000000000001', 'Electrochemical cells and EMF', 1, 25),
('16000000-2022-0001-0002-000000000001', '15000000-2022-0001-0000-000000000001', 'Nernst equation', 2, 30),
('16000000-2022-0001-0003-000000000001', '15000000-2022-0001-0000-000000000001', 'Conductance and Kohlrausch law', 3, 25),
('16000000-2022-0001-0004-000000000001', '15000000-2022-0001-0000-000000000001', 'Batteries and fuel cells', 4, 20);

-- Chemistry Ch23: Chemical Kinetics
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2023-0001-0000-000000000001', '13000000-1000-1000-1000-100000000023', 'Chemical Kinetics', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2023-0001-0001-000000000001', '15000000-2023-0001-0000-000000000001', 'Rate of reaction and order', 1, 25),
('16000000-2023-0001-0002-000000000001', '15000000-2023-0001-0000-000000000001', 'Integrated rate equations', 2, 30),
('16000000-2023-0001-0003-000000000001', '15000000-2023-0001-0000-000000000001', 'Collision theory and activation energy', 3, 25);

-- Chemistry Ch24: Structure of Atom
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2024-0001-0000-000000000001', '13000000-1000-1000-1000-100000000024', 'Atomic Structure', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2024-0001-0001-000000000001', '15000000-2024-0001-0000-000000000001', 'Bohr model and hydrogen spectrum', 1, 25),
('16000000-2024-0001-0002-000000000001', '15000000-2024-0001-0000-000000000001', 'Quantum numbers and orbitals', 2, 30),
('16000000-2024-0001-0003-000000000001', '15000000-2024-0001-0000-000000000001', 'Electronic configuration of atoms', 3, 25);

-- Chemistry Ch25: Practical Physical Chemistry
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-2025-0001-0000-000000000001', '13000000-1000-1000-1000-100000000025', 'Practical Physical Chemistry', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-2025-0001-0001-000000000001', '15000000-2025-0001-0000-000000000001', 'Surface tension and viscosity', 1, 15),
('16000000-2025-0001-0002-000000000001', '15000000-2025-0001-0000-000000000001', 'pH measurement and indicators', 2, 15);

-- ============================================
-- BIOLOGY: Chapters 1-36
-- ============================================

-- Biology Ch1: Sexual Reproduction in Flowering Plants
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3001-0001-0000-000000000001', '14000000-1000-1000-1000-100000000001', 'Flower Reproduction', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3001-0001-0001-000000000001', '15000000-3001-0001-0000-000000000001', 'Structure of flower and gametophytes', 1, 25),
('16000000-3001-0001-0002-000000000001', '15000000-3001-0001-0000-000000000001', 'Pollination and fertilization', 2, 25),
('16000000-3001-0001-0003-000000000001', '15000000-3001-0001-0000-000000000001', 'Seed and fruit development', 3, 20),
('16000000-3001-0001-0004-000000000001', '15000000-3001-0001-0000-000000000001', 'Apomixis and polyembryony', 4, 15);

-- Biology Ch2: Human Reproduction
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3002-0001-0000-000000000001', '14000000-1000-1000-1000-100000000002', 'Human Reproduction', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3002-0001-0001-000000000001', '15000000-3002-0001-0000-000000000001', 'Male and female reproductive systems', 1, 25),
('16000000-3002-0001-0002-000000000001', '15000000-3002-0001-0000-000000000001', 'Gametogenesis (spermatogenesis, oogenesis)', 2, 30),
('16000000-3002-0001-0003-000000000001', '15000000-3002-0001-0000-000000000001', 'Fertilization and implantation', 3, 25),
('16000000-3002-0001-0004-000000000001', '15000000-3002-0001-0000-000000000001', 'Pregnancy and embryonic development', 4, 25),
('16000000-3002-0001-0005-000000000001', '15000000-3002-0001-0000-000000000001', 'Parturition and lactation', 5, 15);

-- Biology Ch3: Reproductive Health
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3003-0001-0000-000000000001', '14000000-1000-1000-1000-100000000003', 'Reproductive Health', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3003-0001-0001-000000000001', '15000000-3003-0001-0000-000000000001', 'Population and birth control methods', 1, 20),
('16000000-3003-0001-0002-000000000001', '15000000-3003-0001-0000-000000000001', 'Medical termination of pregnancy', 2, 15),
('16000000-3003-0001-0003-000000000001', '15000000-3003-0001-0000-000000000001', 'Sexually transmitted diseases', 3, 20),
('16000000-3003-0001-0004-000000000001', '15000000-3003-0001-0000-000000000001', 'Infertility and ART (IVF, ZIFT, GIFT)', 4, 20);

-- Biology Ch4: Principles of Inheritance
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3004-0001-0000-000000000001', '14000000-1000-1000-1000-100000000004', 'Inheritance and Variation', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3004-0001-0001-000000000001', '15000000-3004-0001-0000-000000000001', 'Mendel laws of inheritance', 1, 30),
('16000000-3004-0001-0002-000000000001', '15000000-3004-0001-0000-000000000001', 'Incomplete dominance and co-dominance', 2, 20),
('16000000-3004-0001-0003-000000000001', '15000000-3004-0001-0000-000000000001', 'Linkage and crossing over', 3, 25),
('16000000-3004-0001-0004-000000000001', '15000000-3004-0001-0000-000000000001', 'Sex determination and mutations', 4, 25),
('16000000-3004-0001-0005-000000000001', '15000000-3004-0001-0000-000000000001', 'Pedigree analysis and genetic disorders', 5, 25);

-- Biology Ch5: Molecular Basis of Inheritance
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3005-0001-0000-000000000001', '14000000-1000-1000-1000-100000000005', 'Molecular Genetics', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3005-0001-0001-000000000001', '15000000-3005-0001-0000-000000000001', 'DNA structure and packaging', 1, 25),
('16000000-3005-0001-0002-000000000001', '15000000-3005-0001-0000-000000000001', 'DNA replication', 2, 30),
('16000000-3005-0001-0003-000000000001', '15000000-3005-0001-0000-000000000001', 'Transcription and genetic code', 3, 30),
('16000000-3005-0001-0004-000000000001', '15000000-3005-0001-0000-000000000001', 'Translation and gene regulation (lac operon)', 4, 30),
('16000000-3005-0001-0005-000000000001', '15000000-3005-0001-0000-000000000001', 'DNA fingerprinting and HGP', 5, 20);

-- Biology Ch6: Evolution
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3006-0001-0000-000000000001', '14000000-1000-1000-1000-100000000006', 'Evolution', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3006-0001-0001-000000000001', '15000000-3006-0001-0000-000000000001', 'Origin of life and evidence of evolution', 1, 25),
('16000000-3006-0001-0002-000000000001', '15000000-3006-0001-0000-000000000001', 'Darwin theory and natural selection', 2, 25),
('16000000-3006-0001-0003-000000000001', '15000000-3006-0001-0000-000000000001', 'Hardy-Weinberg equilibrium', 3, 25),
('16000000-3006-0001-0004-000000000001', '15000000-3006-0001-0000-000000000001', 'Adaptive radiation and human evolution', 4, 20);

-- Biology Ch7: Human Health and Disease
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3007-0001-0000-000000000001', '14000000-1000-1000-1000-100000000007', 'Health and Disease', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3007-0001-0001-000000000001', '15000000-3007-0001-0000-000000000001', 'Common diseases and pathogens', 1, 25),
('16000000-3007-0001-0002-000000000001', '15000000-3007-0001-0000-000000000001', 'Immunity and vaccines', 2, 30),
('16000000-3007-0001-0003-000000000001', '15000000-3007-0001-0000-000000000001', 'Cancer and AIDS', 3, 25),
('16000000-3007-0001-0004-000000000001', '15000000-3007-0001-0000-000000000001', 'Drugs and alcohol abuse', 4, 20);

-- Biology Ch8: Microbes in Human Welfare
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3008-0001-0000-000000000001', '14000000-1000-1000-1000-100000000008', 'Microbes', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3008-0001-0001-000000000001', '15000000-3008-0001-0000-000000000001', 'Microbes in household and industrial products', 1, 20),
('16000000-3008-0001-0002-000000000001', '15000000-3008-0001-0000-000000000001', 'Microbes in sewage treatment', 2, 20),
('16000000-3008-0001-0003-000000000001', '15000000-3008-0001-0000-000000000001', 'Microbes in biocontrol and biofertilizers', 3, 20);

-- Biology Ch9: Biotechnology Principles
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3009-0001-0000-000000000001', '14000000-1000-1000-1000-100000000009', 'Biotechnology Principles', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3009-0001-0001-000000000001', '15000000-3009-0001-0000-000000000001', 'Restriction enzymes and vectors', 1, 25),
('16000000-3009-0001-0002-000000000001', '15000000-3009-0001-0000-000000000001', 'PCR and gel electrophoresis', 2, 25),
('16000000-3009-0001-0003-000000000001', '15000000-3009-0001-0000-000000000001', 'Recombinant DNA technology steps', 3, 30);

-- Biology Ch10: Biotechnology Applications
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3010-0001-0000-000000000001', '14000000-1000-1000-1000-100000000010', 'Biotechnology Applications', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3010-0001-0001-000000000001', '15000000-3010-0001-0000-000000000001', 'Bt cotton and pest resistance', 1, 20),
('16000000-3010-0001-0002-000000000001', '15000000-3010-0001-0000-000000000001', 'Gene therapy and molecular diagnosis', 2, 25),
('16000000-3010-0001-0003-000000000001', '15000000-3010-0001-0000-000000000001', 'Transgenic animals and ethical issues', 3, 20);

-- Biology Ch11: Organisms and Populations
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3011-0001-0000-000000000001', '14000000-1000-1000-1000-100000000011', 'Organisms and Populations', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3011-0001-0001-000000000001', '15000000-3011-0001-0000-000000000001', 'Organism and environment adaptations', 1, 25),
('16000000-3011-0001-0002-000000000001', '15000000-3011-0001-0000-000000000001', 'Population interactions and growth', 2, 25),
('16000000-3011-0001-0003-000000000001', '15000000-3011-0001-0000-000000000001', 'Population attributes and life cycles', 3, 20);

-- Biology Ch12: Ecosystem
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3012-0001-0000-000000000001', '14000000-1000-1000-1000-100000000012', 'Ecosystem', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3012-0001-0001-000000000001', '15000000-3012-0001-0000-000000000001', 'Ecosystem structure and productivity', 1, 25),
('16000000-3012-0001-0002-000000000001', '15000000-3012-0001-0000-000000000001', 'Ecological pyramids and energy flow', 2, 25),
('16000000-3012-0001-0003-000000000001', '15000000-3012-0001-0000-000000000001', 'Ecological succession', 3, 20),
('16000000-3012-0001-0004-000000000001', '15000000-3012-0001-0000-000000000001', 'Nutrient cycling (carbon, phosphorus)', 4, 20);

-- Biology Ch13: Biodiversity and Conservation
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3013-0001-0000-000000000001', '14000000-1000-1000-1000-100000000013', 'Biodiversity', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3013-0001-0001-000000000001', '15000000-3013-0001-0000-000000000001', 'Patterns and importance of biodiversity', 1, 20),
('16000000-3013-0001-0002-000000000001', '15000000-3013-0001-0000-000000000001', 'Loss of biodiversity and extinction', 2, 20),
('16000000-3013-0001-0003-000000000001', '15000000-3013-0001-0000-000000000001', 'Conservation strategies (in-situ, ex-situ)', 3, 25);

-- Biology Ch14: Environmental Issues
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3014-0001-0000-000000000001', '14000000-1000-1000-1000-100000000014', 'Environmental Issues', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3014-0001-0001-000000000001', '15000000-3014-0001-0000-000000000001', 'Air and water pollution control', 1, 20),
('16000000-3014-0001-0002-000000000001', '15000000-3014-0001-0000-000000000001', 'Greenhouse effect and ozone depletion', 2, 25),
('16000000-3014-0001-0003-000000000001', '15000000-3014-0001-0000-000000000001', 'Deforestation and case studies', 3, 20);

-- Biology Ch15: The Living World
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3015-0001-0000-000000000001', '14000000-1000-1000-1000-100000000015', 'Living World', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3015-0001-0001-000000000001', '15000000-3015-0001-0000-000000000001', 'What is living and diversity', 1, 15),
('16000000-3015-0001-0002-000000000001', '15000000-3015-0001-0000-000000000001', 'Taxonomic categories and aids', 2, 20);

-- Biology Ch16: Biological Classification
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3016-0001-0000-000000000001', '14000000-1000-1000-1000-100000000016', 'Biological Classification', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3016-0001-0001-000000000001', '15000000-3016-0001-0000-000000000001', 'Five kingdom classification', 1, 20),
('16000000-3016-0001-0002-000000000001', '15000000-3016-0001-0000-000000000001', 'Monera, Protista, Fungi', 2, 25),
('16000000-3016-0001-0003-000000000001', '15000000-3016-0001-0000-000000000001', 'Viruses, viroids, prions, lichens', 3, 20);

-- Biology Ch17: Plant Kingdom
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3017-0001-0000-000000000001', '14000000-1000-1000-1000-100000000017', 'Plant Kingdom', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3017-0001-0001-000000000001', '15000000-3017-0001-0000-000000000001', 'Algae, bryophytes, pteridophytes', 1, 25),
('16000000-3017-0001-0002-000000000001', '15000000-3017-0001-0000-000000000001', 'Gymnosperms and angiosperms', 2, 20),
('16000000-3017-0001-0003-000000000001', '15000000-3017-0001-0000-000000000001', 'Plant life cycles and alternation of generations', 3, 20);

-- Biology Ch18: Animal Kingdom
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3018-0001-0000-000000000001', '14000000-1000-1000-1000-100000000018', 'Animal Kingdom', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3018-0001-0001-000000000001', '15000000-3018-0001-0000-000000000001', 'Basis of classification and phyla overview', 1, 25),
('16000000-3018-0001-0002-000000000001', '15000000-3018-0001-0000-000000000001', 'Invertebrate phyla (Porifera to Echinodermata)', 2, 30),
('16000000-3018-0001-0003-000000000001', '15000000-3018-0001-0000-000000000001', 'Chordata classification', 3, 25);

-- Biology Ch19: Morphology of Flowering Plants
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3019-0001-0000-000000000001', '14000000-1000-1000-1000-100000000019', 'Plant Morphology', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3019-0001-0001-000000000001', '15000000-3019-0001-0000-000000000001', 'Root, stem, leaf modifications', 1, 25),
('16000000-3019-0001-0002-000000000001', '15000000-3019-0001-0000-000000000001', 'Inflorescence and flower structure', 2, 25),
('16000000-3019-0001-0003-000000000001', '15000000-3019-0001-0000-000000000001', 'Fruit and seed types', 3, 20),
('16000000-3019-0001-0004-000000000001', '15000000-3019-0001-0000-000000000001', 'Semi-technical descriptions of families', 4, 25);

-- Biology Ch20: Anatomy of Flowering Plants
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3020-0001-0000-000000000001', '14000000-1000-1000-1000-100000000020', 'Plant Anatomy', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3020-0001-0001-000000000001', '15000000-3020-0001-0000-000000000001', 'Tissue systems (meristematic, permanent)', 1, 25),
('16000000-3020-0001-0002-000000000001', '15000000-3020-0001-0000-000000000001', 'Anatomy of dicot and monocot root/stem', 2, 30),
('16000000-3020-0001-0003-000000000001', '15000000-3020-0001-0000-000000000001', 'Secondary growth', 3, 25);

-- Biology Ch21: Structural Organisation in Animals
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3021-0001-0000-000000000001', '14000000-1000-1000-1000-100000000021', 'Animal Tissues', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3021-0001-0001-000000000001', '15000000-3021-0001-0000-000000000001', 'Epithelial and connective tissues', 1, 25),
('16000000-3021-0001-0002-000000000001', '15000000-3021-0001-0000-000000000001', 'Muscular and neural tissues', 2, 25),
('16000000-3021-0001-0003-000000000001', '15000000-3021-0001-0000-000000000001', 'Organ systems in cockroach', 3, 25);

-- Biology Ch22: Cell The Unit of Life
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3022-0001-0000-000000000001', '14000000-1000-1000-1000-100000000022', 'Cell Biology', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3022-0001-0001-000000000001', '15000000-3022-0001-0000-000000000001', 'Cell theory and types of cells', 1, 20),
('16000000-3022-0001-0002-000000000001', '15000000-3022-0001-0000-000000000001', 'Cell organelles and their functions', 2, 30),
('16000000-3022-0001-0003-000000000001', '15000000-3022-0001-0000-000000000001', 'Nucleus and ribosomes', 3, 20);

-- Biology Ch23: Biomolecules
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3023-0001-0000-000000000001', '14000000-1000-1000-1000-100000000023', 'Biomolecules', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3023-0001-0001-000000000001', '15000000-3023-0001-0000-000000000001', 'Carbohydrates, proteins, lipids', 1, 25),
('16000000-3023-0001-0002-000000000001', '15000000-3023-0001-0000-000000000001', 'Enzymes and factors affecting activity', 2, 25),
('16000000-3023-0001-0003-000000000001', '15000000-3023-0001-0000-000000000001', 'Nucleic acids and metabolism', 3, 20);

-- Biology Ch24: Cell Cycle and Cell Division
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3024-0001-0000-000000000001', '14000000-1000-1000-1000-100000000024', 'Cell Division', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3024-0001-0001-000000000001', '15000000-3024-0001-0000-000000000001', 'Cell cycle phases', 1, 20),
('16000000-3024-0001-0002-000000000001', '15000000-3024-0001-0000-000000000001', 'Mitosis and its significance', 2, 25),
('16000000-3024-0001-0003-000000000001', '15000000-3024-0001-0000-000000000001', 'Meiosis and its significance', 3, 25);

-- Biology Ch25: Transport in Plants
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3025-0001-0000-000000000001', '14000000-1000-1000-1000-100000000025', 'Plant Transport', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3025-0001-0001-000000000001', '15000000-3025-0001-0000-000000000001', 'Water potential and osmosis', 1, 25),
('16000000-3025-0001-0002-000000000001', '15000000-3025-0001-0000-000000000001', 'Transpiration and ascent of sap', 2, 25),
('16000000-3025-0001-0003-000000000001', '15000000-3025-0001-0000-000000000001', 'Phloem transport and mass flow hypothesis', 3, 20);

-- Biology Ch26: Mineral Nutrition
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3026-0001-0000-000000000001', '14000000-1000-1000-1000-100000000026', 'Mineral Nutrition', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3026-0001-0001-000000000001', '15000000-3026-0001-0000-000000000001', 'Essential mineral elements', 1, 20),
('16000000-3026-0001-0002-000000000001', '15000000-3026-0001-0000-000000000001', 'Nitrogen metabolism and nitrogen fixation', 2, 25);

-- Biology Ch27: Photosynthesis
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3027-0001-0000-000000000001', '14000000-1000-1000-1000-100000000027', 'Photosynthesis', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3027-0001-0001-000000000001', '15000000-3027-0001-0000-000000000001', 'Light reactions and photophosphorylation', 1, 30),
('16000000-3027-0001-0002-000000000001', '15000000-3027-0001-0000-000000000001', 'Calvin cycle and C4 pathway', 2, 30),
('16000000-3027-0001-0003-000000000001', '15000000-3027-0001-0000-000000000001', 'Factors affecting photosynthesis', 3, 20);

-- Biology Ch28: Respiration in Plants
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3028-0001-0000-000000000001', '14000000-1000-1000-1000-100000000028', 'Plant Respiration', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3028-0001-0001-000000000001', '15000000-3028-0001-0000-000000000001', 'Glycolysis and fermentation', 1, 25),
('16000000-3028-0001-0002-000000000001', '15000000-3028-0001-0000-000000000001', 'Krebs cycle and ETS', 2, 30),
('16000000-3028-0001-0003-000000000001', '15000000-3028-0001-0000-000000000001', 'Respiratory quotient and amphibolic pathway', 3, 20);

-- Biology Ch29: Plant Growth and Development
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3029-0001-0000-000000000001', '14000000-1000-1000-1000-100000000029', 'Plant Growth', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3029-0001-0001-000000000001', '15000000-3029-0001-0000-000000000001', 'Growth phases and differentiation', 1, 20),
('16000000-3029-0001-0002-000000000001', '15000000-3029-0001-0000-000000000001', 'Plant growth regulators (auxin, GA, cytokinin)', 2, 30),
('16000000-3029-0001-0003-000000000001', '15000000-3029-0001-0000-000000000001', 'Photoperiodism and vernalization', 3, 20);

-- Biology Ch30: Digestion and Absorption
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3030-0001-0000-000000000001', '14000000-1000-1000-1000-100000000030', 'Digestive System', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3030-0001-0001-000000000001', '15000000-3030-0001-0000-000000000001', 'Alimentary canal and digestive glands', 1, 25),
('16000000-3030-0001-0002-000000000001', '15000000-3030-0001-0000-000000000001', 'Digestion of food and absorption', 2, 25),
('16000000-3030-0001-0003-000000000001', '15000000-3030-0001-0000-000000000001', 'Disorders of digestive system', 3, 15);

-- Biology Ch31: Breathing and Exchange of Gases
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3031-0001-0000-000000000001', '14000000-1000-1000-1000-100000000031', 'Respiratory System', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3031-0001-0001-000000000001', '15000000-3031-0001-0000-000000000001', 'Human respiratory system', 1, 20),
('16000000-3031-0001-0002-000000000001', '15000000-3031-0001-0000-000000000001', 'Mechanism of breathing and gas exchange', 2, 25),
('16000000-3031-0001-0003-000000000001', '15000000-3031-0001-0000-000000000001', 'Transport of gases and regulation', 3, 25),
('16000000-3031-0001-0004-000000000001', '15000000-3031-0001-0000-000000000001', 'Respiratory disorders', 4, 15);

-- Biology Ch32: Body Fluids and Circulation
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3032-0001-0000-000000000001', '14000000-1000-1000-1000-100000000032', 'Circulatory System', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3032-0001-0001-000000000001', '15000000-3032-0001-0000-000000000001', 'Blood composition and groups', 1, 25),
('16000000-3032-0001-0002-000000000001', '15000000-3032-0001-0000-000000000001', 'Human heart and cardiac cycle', 2, 30),
('16000000-3032-0001-0003-000000000001', '15000000-3032-0001-0000-000000000001', 'Double circulation and ECG', 3, 25),
('16000000-3032-0001-0004-000000000001', '15000000-3032-0001-0000-000000000001', 'Disorders of circulatory system', 4, 15);

-- Biology Ch33: Excretory Products and Elimination
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3033-0001-0000-000000000001', '14000000-1000-1000-1000-100000000033', 'Excretory System', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3033-0001-0001-000000000001', '15000000-3033-0001-0000-000000000001', 'Human excretory system and urine formation', 1, 25),
('16000000-3033-0001-0002-000000000001', '15000000-3033-0001-0000-000000000001', 'Counter current mechanism and regulation', 2, 25),
('16000000-3033-0001-0003-000000000001', '15000000-3033-0001-0000-000000000001', 'Micturition and disorders', 3, 15);

-- Biology Ch34: Locomotion and Movement
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3034-0001-0000-000000000001', '14000000-1000-1000-1000-100000000034', 'Locomotion', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3034-0001-0001-000000000001', '15000000-3034-0001-0000-000000000001', 'Types of movement and muscle structure', 1, 25),
('16000000-3034-0001-0002-000000000001', '15000000-3034-0001-0000-000000000001', 'Sliding filament theory', 2, 30),
('16000000-3034-0001-0003-000000000001', '15000000-3034-0001-0000-000000000001', 'Skeletal system and joints', 3, 20),
('16000000-3034-0001-0004-000000000001', '15000000-3034-0001-0000-000000000001', 'Disorders of muscular and skeletal system', 4, 15);

-- Biology Ch35: Neural Control and Coordination
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3035-0001-0000-000000000001', '14000000-1000-1000-1000-100000000035', 'Nervous System', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3035-0001-0001-000000000001', '15000000-3035-0001-0000-000000000001', 'Neuron and nerve impulse generation', 1, 25),
('16000000-3035-0001-0002-000000000001', '15000000-3035-0001-0000-000000000001', 'Human brain and reflex action', 2, 30),
('16000000-3035-0001-0003-000000000001', '15000000-3035-0001-0000-000000000001', 'Eye and ear structure and function', 3, 25);

-- Biology Ch36: Chemical Coordination and Integration
INSERT INTO topics (id, chapter_id, name, sort_order) VALUES
('15000000-3036-0001-0000-000000000001', '14000000-1000-1000-1000-100000000036', 'Endocrine System', 1);

INSERT INTO subtopics (id, topic_id, name, sort_order, estimated_minutes) VALUES
('16000000-3036-0001-0001-000000000001', '15000000-3036-0001-0000-000000000001', 'Endocrine glands and hormones', 1, 25),
('16000000-3036-0001-0002-000000000001', '15000000-3036-0001-0000-000000000001', 'Hormone mechanism of action', 2, 20),
('16000000-3036-0001-0003-000000000001', '15000000-3036-0001-0000-000000000001', 'Disorders of endocrine system', 3, 20);
