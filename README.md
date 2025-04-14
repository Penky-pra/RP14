# Clinical Pathway Discovery Based on EHR Data

This repository presents the early phase of a research project focused on clinical pathway discovery for melanoma patients using Electronic Health Record (EHR) data. The research leverages stochastic modeling, deep learning, and process mining techniques to model patient trajectories and support clinical decision-making.

> **RP14 Project | WisPerMed**  
> Conducted by **Praveen Jagan Nath** under the supervision of **Prof. Dr. Britta Böckmann**  
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

---

## 📂 Data Structure

- `data/`: Contains datasets and metadata
- `notebooks/`: Jupyter notebooks for model experimentation
- `src/`: Core codebase for preprocessing, modeling, and analysis
- `docs/`: Project documentation including the six-month summary and presentation
- `figures/`: Visuals and workflow diagrams from the slides and models

---

## 📈 Current Status

- Initial experiments using MIMIC-III and expired FHIR data completed
- Awaiting ethical clearance to analyze active FHIR datasets from Uniklinikum Essen
- Provisional pathways and pilot models under development
- Process mining strategy under validation with BPMN modeling of patient journeys

---

## 🧾 References

See full citations in [docs/six_month_summary.pdf](docs/six_month_summary.pdf)

Key sources:
- WisPerMed RP14 Project Documentation
- Beckmann et al. (2023). *Semantic integration of BPMN models and FHIR data...*
- Masti & Bemporad (2021), Kingma & Welling (2019), Chiang (1993) – on modeling techniques

---

## 👥 Contributors

- **Praveen Jagan Nath**  
  PhD Researcher  
  Department of Computer Science, FH Dortmund  
  Institute for Artificial Intelligence in Medicine (IKIM), University Hospital Essen

- **Prof. Dr. Britta Böckmann**  
  Supervisor, FH Dortmund / IKIM

---

## 🏥 Acknowledgments

This project is part of the **WisPerMed** initiative and supported by interdisciplinary collaborations between FH Dortmund and IKIM, Essen. Special thanks to the data science and clinical informatics teams for their insights into EHR integration and ethical handling.

---

