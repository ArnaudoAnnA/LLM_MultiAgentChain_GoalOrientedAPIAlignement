# LLM Multi-Agent Chain for Goal Oriented API Alignement

## Overview

This repository presents a system that automates the alignment of high-level goals with API endpoints using Goal-Oriented Requirements Engineering (GORE) principles and Large Language Models (LLMs). The system extracts goals from natural language requirement documents, decomposes them into structured objectives, and maps them to corresponding API endpoints. This approach enhances the automation of software requirement analysis by translating system goals into actionable API calls.

## Architecture: LLM Multi-Agent Chain

![System Architecture](Architecture.png)

Our framework integrates multiple LLM agents working in a Chain to iteratively extract, refine, and validate goals before mapping them to API functionalities. The key components of this system include:

- 📄 **Documentation Processing:** Converts unstructured natural language requirement documents (e.g., README files, requirement specifications) into structured descriptions.
- 🎯 **Goal Extraction:** Identifies high-level strategic goals based on stakeholder needs.
- 🔍 **Goal Decomposition:** Breaks down high-level goals into detailed, low-level technical objectives.
- 🔗 **API Mapping:** Aligns the extracted low-level goals with existing API endpoints using available API documentation (e.g., Swagger files).
- 🔄 **Iterative Validation:** Employs a feedback loop where LLM-generated outputs are evaluated and refined based on quality thresholds.

## Installation

### Prerequisites

Ensure you have Python installed along with the necessary dependencies.

### Steps

1. **Clone this repository:**
   ```bash
   git clone https://github.com/dadoluca/LLM_MultiAgentChain_GoalOrientedAPIAlignement.git
   cd LLM_MultiAgentChain_GoalOrientedAPIAlignement
   ```
2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the notebook experiments.ipynb in notebook folder**

## License

This project has been forked from https://github.com/dadoluca/LLM_MultiAgentChain_GoalOrientedAPIAlignement
This project is licensed under the **GNU GPL Version 3 License**. See the [LICENSE](LICENSE) file for details.
 





