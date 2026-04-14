GENOME = {
    "name": "Genome Nexus",
    "link-readme": "https://github.com/WebFuzzing/EMB/tree/master/jdk_8_maven/cs/rest-gui/genome-nexus#readme",
    "swagger": "https://raw.githubusercontent.com/WebFuzzing/EMB/refs/heads/master/openapi-swagger/genome-nexus.json",
    "actors": [
        "Researchers", "Clinicians"
    ],
    "highLevelGoals":  ["Provide fast and automated annotation of genetic variants",
                "Enable high-throughput interpretation of genetic variants",
                "Integrate information from various existing resources",
                "Convert DNA changes to protein changes",
                "Predict functional effects of protein mutations",
                "Provide information about mutation frequencies",
                "Offer insights into gene function",
                "Detail variant effects",
                "Highlight clinical actionability of variants"],
    "lowLevelGoals": [
        # Provide a comprehensive one-stop resource for genetic variant annotation
        "Retrieve genetic variant data_key from multiple databases (e.g., dbSNP, ClinVar, COSMIC)",
        "Search and retrieve variant annotations from a user interface",
        "Annotate variants with clinical significance, mutation types, and related diseases",
        "Map genetic data_key to genome assemblies (e.g., GRCh38, hg19)",
        "Update variant information regularly from authoritative sources",
        
        # Enable fast and automated interpretation of cancer-related genetic variants
        "Analyze cancer-related mutations using automated tools",
        "Integrate gene expression data_key for cancer variant interpretation",
        "Identify cancer-related mutations linked to specific pathways",
        "Interpret large-scale cancer mutation datasets automatically",
        "Classify cancer mutations based on clinical relevance",
        
        # Support high-throughput analysis of genetic mutations
        "Process large genomic datasets in parallel",
        "Extract and transform mutation data_key from high-throughput sequencing formats (e.g., VCF, BAM)",
        "Perform mutation quality control and filtering",
        
        # Integrate data_key from multiple genomic databases
        "Fetch and harmonize data_key from various genomic databases",
        "Query integrated genomic databases for relevant mutation information",
        "Integrate multiple data_key sources with compatible formats for easy retrieval",
        
        # Convert DNA changes to corresponding protein changes
        "Map genetic mutations to corresponding protein-coding effects",
        "Convert mutations to amino acid changes for protein function analysis",
        "Predict the impact of mutations on protein structure using bioinformatics tools",
        
        # Predict the functional impact of protein mutations
        "Use prediction tools (e.g., PolyPhen, SIFT) to estimate mutation effects on protein function",
        "Build and apply machine learning models for functional impact prediction",
        "Rank mutations based on predicted severity of functional impact",
        
        # Provide information on mutation frequencies across datasets
        "Calculate mutation frequencies across various population groups",
        "Generate visual representations of mutation frequencies (e.g., histograms, pie charts)",
        "Provide mutation frequency data_key for specific diseases or conditions",
        
        # Offer insights into gene function and biological relevance
        "Retrieve gene function annotations from public databases like Gene Ontology (GO)",
        "Identify pathways and biological processes related to the mutated gene",
        "Link genetic variants to specific diseases or phenotypes based on annotations",
        
        # Detail the effects of genetic variants on protein function
        "Predict the effects of mutations on protein folding and stability",
        "Identify how mutations alter protein activity or structure",
        "Evaluate the impact of mutations on protein-protein interactions",
        
        # Highlight the clinical actionability of specific mutations
        "Link genetic mutations to clinical guidelines or treatment protocols",
        "Identify mutations with known clinical drug responses or therapeutic implications",
        "Provide actionable insights on mutations based on current clinical research"
    ]
}

GESTAO_HOSPITAL = {
    "name" : "Gestao Hospital",
    "link-readme": "https://github.com/ValchanOficial/GestaoHospital/blob/master/README.md",
    "swagger": "https://raw.githubusercontent.com/WebFuzzing/EMB/refs/heads/master/openapi-swagger/gestaohospital-rest.json",
    "actors": [
        "Hospital Manager",
        "Healthcare Staff",
        "Administrator",
        "Patients",
        "Hospital Logistics Staff",
    ],
    "highLevelGoals": [
        "Allow administrators and hospital managers to manage an hospital",
        "Allow hospital managers and healthcare staff to manage hospital beds and patients",
        "Allow healthcare staff to manage products and the blood bank",
        "Allow patients to look for hospitals",
    ],
    "lowLevelGoals" : [
        #"Allow administrators and hospital managers to manage an hospital",
        "Allow Registration of a New Hospital",
        "Allow Deletion of a Hospital",
        "Allow Modification of a Hospital",
        "Allow administrators to access statistics and manage indicators",
        "Enable hospital staff to manage appointment schedules",

        #"Allow patients to look for hospitals",
        "Recommend Nearest Hospital",
        "Return Information on a Hospital",

        #"Allow healthcare staff to manage products and the blood bank",
        "View Products and Quantities",
        "Allow logistic staff to Register Products",
        "Delete Products",
        "Allow logistic staff to change product quantities",
        "View Info on a Single Product",
        "Request a Product",
        "Allow searching for blood samples",

        #"Allow hospital managers and healthcare staff to manage hospital beds and patients",
        "Enable healthcare staff to view patient info and their medical history",
        "Register a Patient at a Hospital, entering personal information and contact info",
        "Allow patients to confirm their arrival at the ospital online or in presence"
        "Show estimated check in times for patient arriving at the hospital",
        "Allow healthcare staff to save notes regarding patients and their treatment in the system",
        "Change Patient Info and medical history",
    ]
}

SIA_PROJECT_25_26 = {
    "name" : "SIA Project 25 26",
    "description": """
    In the Municipality of Turin, a system called Participium is being developed — an information 
system that enables citizen participation in the management of urban environments. It allows 
citizens to interact with the public administration by reporting inconveniences and malfunctions 
found in the city (e.g., potholes in the asphalt, sidewalks with architectural barriers, garbage in the 
streets, broken streetlights, etc.). An example of a similar information system is IRIS in Venice: 
https://iris.sad.ve.it/. The system, once developed, will be made available as open-source 
software to all Italian public administrations through the portal https://developers.italia.it/.

A. REPORTS 
Citizens can submit reports only if they have registered in the system with a username, first name, 
and last name. Once the registration is received, the user gets an email with a confirmation link. 
The registration becomes valid, and the user can use the system only after confirming through 
that link. Once registered, a citizen can submit reports by selecting a point on the map of Turin 
(which will be saved with latitude and longitude values) and filling in a problem form with the 
following mandatory fields: title, textual description, category (chosen from a predefined list). It is 
also mandatory to attach one or more photos (up to 3 per report, with each photo stored with its 
file path on the server). The possible problem categories are: 
• Waterworks – Drinking water 
• Architectural Barriers 
• Sewerage 
• Public Lighting 
• Waste 
• Road Signs and Traffic Lights 
• Roads and Urban Furniture 
• Public Green Areas and Playgrounds 
• Other 
After entering all the information and the pictures, the system asks the citizen whether they want 
the report to be anonymous (the name will not appear in the public list of all reports).  

B. REPORT LIFECYCLE 
Once submitted, the report is in the “Pending Approval” state until the Organization Office of the 
Municipality of Turin performs a preliminary review of citizen reports, marking them as accepted 
or rejected. The possible states for a report are: Pending Approval, In Progress, Work in Progress, 
Suspended, Rejected. After approval, accepted reports move to the “In Progress” state, at which 
point they are assigned to the technical office responsible, based on the problem category. Once 
the intervention is planned, the state changes to “Work in Progress”, indicating that the issue 
resolution has started. In some cases, for organizational or technical reasons, the report can be 
set to “Suspended”, awaiting further evaluation or resources. When the problem is solved, the 
technical office updates the status and closes the report. In case of rejection, a written explanation 
from the Organization Office is mandatory (see next section).  
If the intervention must be carried out by maintenance personnel from an external company (for 
example, Enel X for Public Lighting, or company Y for specific reports based on their content), 
two cases are possible: - Case 1: The company has access to Participium. In this case, the technical office assigns the 
report to users from the corresponding company. External maintenance personnel can move the 
report from Assigned to In Progress. Staff from the technical office and external maintenance 
workers can exchange information and comments through the report, but these are not visible to 
the reporting citizen (nor to other citizens). Once the work is completed, the external maintainer 
can mark the report as resolved. 
Note: Automatic assignment of all reports in a certain category to the external company 
(bypassing the initial review by the public relations officer of the municipality) is possible only if 
previously configured by the municipal administrator. - Case 2: The company does NOT have access to Participium. In this case, the external company 
updates the technical office outside Participium, and once the problems are solved, a staff 
member from the technical office will manually move the report to the Resolved state. 


C. CITIZEN UPDATES 
To strengthen trust between citizens and institutions, the citizen can receive updates regarding 
their own reports through various channels. First, at every state change, the citizen receives a 
notification on the platform with the corresponding update. Furthermore, municipal operators 
updating reports can send the reporting citizen a message through the platform, to which it can 
reply. The system must allow this functionality to be accessible by external chatbots as well. Each 
time the citizen receives a notification on the platform, they also get an email (this option can be 
disabled in the user settings panel, where they can also upload a personal photo). 
Moreover, after the approval phase, accepted reports immediately become visible on the 
Participium portal: they appear both on an interactive map of Turin, geolocated based on the 
citizen’s selected point, and in a summary table that allows filtering and sorting reports by 
category, status, or date. In both views, the reporter’s name (“anonymous” if that option was 
chosen) and the report title are displayed. Clicking on the title opens a page with the description.  
Even non-registered users can view both the maps and the summary table. Once logged into 
Participium, citizens can follow other citizens’ open reports and receive notifications (following the 
same rules as for their own reports). 


D. STATISTICS 
The system allows viewing public and private statistics. Public statistics are visible in a dedicated 
section of the website and concern the number of reports per category, and trends over day, week, 
or month. They are also visible to non-registered users. In the private section, accessible only to 
administrators, it is possible to view, in addition to the public statistics, charts and tables. 
    """,

    "actors": [
        "Visitor",
        "Citizen",
        "Technical Office Staff",
        "Organizational Office Staff",
        "Municipal Administrator",
        "External Maintenance Staff"
    ],

    "highLevelGoals": [
        "View Public Statistics",
        "Register Account",
        "Submit a report",
        "Follow reports",
        "Exchange messages",
        "Manage report lifecycle",
        "View private statistics",
        "Configure report auto-assignment",
        "Manage account information"
    ],

    "lowLevelGoals": [
        "Activate account",
        "Submit account registration",
        "Fill-in a report",
"Associate a report with a specific location on the map",
"Select anonimity for a report",
        "Submit a report",
        "Send a message",
        "Activate email notifications",
        "Deactivate email notifications",
        "Upload a profile photo",
        "Delete a profile photo",
        "Activate auto-assignment for a category",
        "Deactivate auto-assignment for a category",
        "Approve a report",
        "Reject a report specifying the rejection reason",
        "Update the report's status",
        "Add a comment related to a report",
        "Assign a report to an external company",
        "Add a report to the set of followed reports",
        "View the details of a report",
"Log-in"
    ]
}

LONDON_AMBULANCE_SYSTEM = {
    "name": "London Ambulance Service",
    "description": """The London Ambulance Service dispatches ambulances in emergencies. 
    The key goal is to allocate an available ambulance for every call that can reach the scene within 11 minutes. 
    The entire dispatch process must not exceed a set maximum time limit.

    To make this work, the computer system (CAD) analyzes incident forms and assigns vehicles. 
    It is vital to track the exact location of moving ambulances. 
    This requires staff to follow standard routes and correctly communicate departure and destination, 
    allowing radio operators and the CAD to record data accurately.""",
    "actors": [
        "Computer Aided Despatch (CAD)",
        "Ambulance Staff",
        "Radio Operator",
        "Resource Allocator (RA)"
    ],
    "highLevelGoals": [
        "Track moving ambulances continuously",
        "Allocate an ambulance within 11 minutes of an incident"
    ],
    "lowLevelGoals": [
        "Keep exact location data for parked/stationary ambulances",
        "Ensure ambulances stick to expected standard routes",
        "Get exact departure and destination data when leaving",
        "Update location using the departure/destination data",
        "Get location updates via phone",
        "Send location/status info via email",
        "Keep location accurate after reaching a destination",
        "Staff communicates departure and destination upon leaving",
        "Operator encodes the departure and destination info",
        "System records the encoded data"
    ]
}

BART_TRAIN_CONTROL = {
    "name": "Bart Train Control",
    "description": """The purpose of the new system is to serve more passengers
by running trains more closely spaced.
The case study description [Win99] focuses on those aspects of BART that are necessary
to control the speed and acceleration for the trains in the system. The problem is to
develop the speed/acceleration control system whose responsibility is to get trains from
one point to another as fast and smoothly as possible, subject to the following safety constraints:
• A train should not enter a closed gate. (In the context of the BART system, a gate is
not a physical gate, but a signal, received by the speed/acceleration control system,
that establish when a train has the right to enter a track segment.)
• A train should never get so close to a train in front so that if the train in front stopped
suddenly (e.g., derailed) the following train would hit it.
• A train should stay below the maximum speed that track segment can handle.
            """,
    "actors": [
        "Train Tracking System",
        "On-board Train Controller",
        "Train Control System",
        "Communication Infrastructure"
    ],
    "highLevelGoals": [

    ]
}
