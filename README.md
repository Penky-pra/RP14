# Clinical Pathway Discovery Based on EHR Data

This repository presents the early phase of a research project focused on clinical pathway discovery for melanoma patients using Electronic Health Record (EHR) data. The research leverages stochastic modeling, deep learning, and process mining techniques to model patient trajectories and support clinical decision-making.

> **RP14 Project | WisPerMed**  
> Conducted by **Praveen Jagan Nath** 
> Department of Computer Science, FH Dortmund  
> Institute for Artificial Intelligence in Medicine (IKIM), University Hospital Essen

---

## 🎯 Project Overview

In melanoma treatment, timely and accurate decisions are crucial but often hindered by the fragmented nature of EHR data. This project aims to create a data-driven decision support system that aligns clinical pathways with patient-specific data, improving decision quality and treatment personalization. The project operates under the WisPerMed initiative and contributes to the broader field of clinical process modeling and real-world data utilization.

---

## 📌 Objectives

- Integrate patient-specific EHR data with clinical guidelines and SOPs
- Apply stochastic models (HMMs) and deep learning (VAEs/PAEs) to learn patient pathways
- Use process mining (BPMN) to visualize and optimize healthcare workflows
- Ensure data ethics and privacy compliance while working with FHIR data

---

## 🧠 Techniques

- **FHIR Data Modeling**: Understanding and integrating core FHIR resources like `Patient`, `Encounter`, `Observation`, `Condition`, and `Procedure`
- **Process Mining**: Event log extraction, process discovery, and conformance checking using BPMN
- **Hidden Markov Models (HMMs)**: For modeling transitions between health states
- **Variational Autoencoders (VAEs)** & **Predictive Autoencoders (PAEs)**: For trajectory prediction and latent space learning

---

## 🧪 Tools and Technologies

- Python under Anaconda (which is a free and open-source distribution of Python and other programming languages, primarily used for scientific computing, data science, machine learning, and big data applications)
- `fhir-pyrate` for FHIR data handling and extracting
- `pm4py` for process mining and event log analysis and comparisons
- Machine learning libraries: TensorFlow, PyTorch, Scikit-learn (to be reviewed)
- Datasets: Prospective live FHIR datasets from IKIM
- Data managing tool: KITE

---

## 📂 Data Structure

- `data/`: Contains datasets and metadata
- `datà collection`: 1. SHIP dashboard, supervises the patient data from Uniklinikum Essen
                     2. Extraction of patient data from SHIP through Fhir Pyrate
                     3. Extraction to create a full patient dataset with different Fhir resources from various sources under Uniklinikum Essen in one data set
                     4.  
  
---

## 📈 Current Status



---



