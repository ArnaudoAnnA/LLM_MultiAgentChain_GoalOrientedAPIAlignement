SIA_PROJECT_25_26 = {   'name': 'SIA Project 25 26',
    'description': '# SIA PROJECT 25-26\n'
                   '\n'
                   'In the Municipality of Turin, a system called Participium is being developed — '
                   'an information system that enables citizen participation in the management of '
                   'urban environments. It allows citizens to interact with the public '
                   'administration by reporting inconveniences and malfunctions found in the city '
                   '(e.g., potholes in the asphalt, sidewalks with architectural barriers, garbage '
                   'in the streets, broken streetlights, etc.). An example of a similar '
                   'information system is IRIS in Venice: '
                   '[https://iris.sad.ve.it/](https://iris.sad.ve.it/?utm_source=gemini). The '
                   'system, once developed, will be made available as open-source software to all '
                   'Italian public administrations through the portal '
                   '[https://developers.italia.it/](https://developers.italia.it/?utm_source=gemini).\n'
                   '\n'
                   'A. REPORTS\n'
                   'Citizens can submit reports only if they have registered in the system with a '
                   'username, first name, and last name. Once the registration is received, the '
                   'user gets an email with a confirmation link. The registration becomes valid, '
                   'and the user can use the system only after confirming through that link. Once '
                   'registered, a citizen can submit reports by selecting a point on the map of '
                   'Turin (which will be saved with latitude and longitude values) and filling in '
                   'a problem form with the following mandatory fields: title, textual '
                   'description, category (chosen from a predefined list). It is also mandatory to '
                   'attach one or more photos (up to 3 per report, with each photo stored with its '
                   'file path on the server). The possible problem categories are:\n'
                   '• Waterworks – Drinking water\n'
                   '• Architectural Barriers\n'
                   '• Sewerage\n'
                   '• Public Lighting\n'
                   '• Waste\n'
                   '• Road Signs and Traffic Lights\n'
                   '• Roads and Urban Furniture\n'
                   '• Public Green Areas and Playgrounds\n'
                   '• Other\n'
                   'After entering all the information and the pictures, the system asks the '
                   'citizen whether they want the report to be anonymous (the name will not appear '
                   'in the public list of all reports).\n'
                   '\n'
                   'B. REPORT LIFECYCLE\n'
                   'Once submitted, the report is in the “Pending Approval” state until the '
                   'Organization Office of the Municipality of Turin performs a preliminary review '
                   'of citizen reports, marking them as accepted or rejected. The possible states '
                   'for a report are: Pending Approval, In Progress, Work in Progress, Suspended, '
                   'Rejected. After approval, accepted reports move to the “In Progress” state, at '
                   'which point they are assigned to the technical office responsible, based on '
                   'the problem category. Once the intervention is planned, the state changes to '
                   '“Work in Progress”, indicating that the issue resolution has started. In some '
                   'cases, for organizational or technical reasons, the report can be set to '
                   '“Suspended”, awaiting further evaluation or resources. When the problem is '
                   'solved, the technical office updates the status and closes the report. In case '
                   'of rejection, a written explanation from the Organization Office is mandatory '
                   '(see next section).\n'
                   'If the intervention must be carried out by maintenance personnel from an '
                   'external company (for example, Enel X for Public Lighting, or company Y for '
                   'specific reports based on their content), two cases are possible:\n'
                   '\n'
                   '* Case 1: The company has access to Participium. In this case, the technical '
                   'office assigns the report to users from the corresponding company. External '
                   'maintenance personnel can move the report from Assigned to In Progress. Staff '
                   'from the technical office and external maintenance workers can exchange '
                   'information and comments through the report, but these are not visible to the '
                   'reporting citizen (nor to other citizens). Once the work is completed, the '
                   'external maintainer can mark the report as resolved.\n'
                   'Note: Automatic assignment of all reports in a certain category to the '
                   'external company (bypassing the initial review by the public relations officer '
                   'of the municipality) is possible only if previously configured by the '
                   'municipal administrator.\n'
                   '* Case 2: The company does NOT have access to Participium. In this case, the '
                   'external company updates the technical office outside Participium, and once '
                   'the problems are solved, a staff member from the technical office will '
                   'manually move the report to the Resolved state.\n'
                   '\n'
                   'C. CITIZEN UPDATES\n'
                   'To strengthen trust between citizens and institutions, the citizen can receive '
                   'updates regarding their own reports through various channels. First, at every '
                   'state change, the citizen receives a notification on the platform with the '
                   'corresponding update. Furthermore, municipal operators updating reports can '
                   'send the reporting citizen a message through the platform, to which it can '
                   'reply. The system must allow this functionality to be accessible by external '
                   'chatbots as well. Each time the citizen receives a notification on the '
                   'platform, they also get an email (this option can be disabled in the user '
                   'settings panel, where they can also upload a personal photo).\n'
                   'Moreover, after the approval phase, accepted reports immediately become '
                   'visible on the Participium portal: they appear both on an interactive map of '
                   'Turin, geolocated based on the citizen’s selected point, and in a summary '
                   'table that allows filtering and sorting reports by category, status, or date. '
                   'In both views, the reporter’s name (“anonymous” if that option was chosen) and '
                   'the report title are displayed. Clicking on the title opens a page with the '
                   'description.\n'
                   'Even non-registered users can view both the maps and the summary table. Once '
                   'logged into Participium, citizens can follow other citizens’ open reports and '
                   'receive notifications (following the same rules as for their own reports).\n'
                   '\n'
                   'D. STATISTICS\n'
                   'The system allows viewing public and private statistics. Public statistics are '
                   'visible in a dedicated section of the website and concern the number of '
                   'reports per category, and trends over day, week, or month. They are also '
                   'visible to non-registered users. In the private section, accessible only to '
                   'administrators, it is possible to view, in addition to the public statistics, '
                   'charts and tables.\n',
    'actors': [   'Visitor',
                  'Citizen',
                  'Technical Office Staff',
                  'Organization Office Staff',
                  'Municipal Administrator',
                  'External Maintenance Staff'],
    'highLevelGoals': [   'View public statistics',
                          'Register an account',
                          'Report urban issues',
                          'Exchange messages',
                          'Manage report lifecycle',
                          'View private statistics',
                          'Configure automatic report assignment',
                          'Manage account information',
                          'Browse public reports',
                          'Receive updates about reports'],
    'lowLevelGoals': [   'Activate account',
                         'Submit account registration',
                         'Select the report location on the map',
                         'Select anonymity for a report',
                         'Submit a report',
                         'Send a message to the reporting citizen',
                         'Activate email notifications',
                         'Deactivate email notifications',
                         'Upload a profile photo',
                         'Enable or disable automatic assignment of a category to an external '
                         'company',
                         'Approve a report',
                         'Reject a report specifying the rejection reason',
                         'Add an internal comment to a report',
                         'Assign a report to an external company',
                         'Follow a report',
                         'View the details of a report',
                         'Log in',
                         'Attach photos to a report',
                         'Set a report status to In Progress',
                         'Set a report status to Work in Progress',
                         'Suspend a report',
                         'Mark a report as resolved',
                         'Receive a platform notification when the status of an own or followed '
                         'report changes',
                         'Receive an email notification when the status of an own or followed '
                         'report changes',
                         'Reply to a message from a municipal operator',
                         'View accepted reports on the interactive map',
                         'View accepted reports in the summary table',
                         'Filter reports by category, status, or date',
                         'Sort reports by category, status, or date',
                         'View public report statistics',
                         'View private report statistics']}

SIA_PROJECT_24_25 = {   'name': 'Assegno Unico Universale - SIA Project 24 25',
    'description': 'Information Systems - academic year 24/25\n'
                   'Course Project\n'
                   '\n'
                   'The Universal Single Allowance (Assegno Unico Universale, AUU) is a financial '
                   'support for Italian families with dependent children, which guarantees '
                   'financial aid based on the specific conditions and the age of the children. '
                   'The AUU is paid by the National Social Security Institute (INPS) to those who '
                   'exercise parental responsibility in the presence of children dependent on '
                   'them.\n'
                   '\n'
                   'The online application can be submitted to INPS either directly by the '
                   'interested parties or by patronage institutes (patronati) holding a specific '
                   'mandate. The application must be submitted on the INPS website, by subjects '
                   'authenticated through one of the following options: SPID; Electronic Identity '
                   'Card 3.0; National Services Card; PIN. The application can also be submitted '
                   'from mobile devices and through the call center by calling the toll-free '
                   'number 803.164 or the number 06 164 164. Here, only the case of submission of '
                   'the application through the INPS website by the directly interested parties '
                   'will be described (delegates are therefore excluded from the analysis).\n'
                   '\n'
                   'A. APPLICATION ENTRY: PHASE 1 - USER DATA\n'
                   'It is possible to submit an application as:\n'
                   '- Parent;\n'
                   '- Custodial parent;\n'
                   "- Child's guardian.\n"
                   '\n'
                   'Depending on the type of applicant, more or fewer fields must be filled in, '
                   'according to the table below, and in the order in which they appear in the '
                   'table.\n'
                   '\n'
                   "| Field | Parent | Custodial parent | Child's guardian |\n"
                   '|---|---|---|---|\n'
                   "| Child's tax code | X | X | X |\n"
                   '| Declaration that the child is a dependent | X | X | X |\n'
                   '| Disabled child (yes/no) | X | X | X |\n'
                   '| If the child is disabled, degree of disability (Medium, Severe, '
                   'Non-self-sufficiency) | X | X | X |\n'
                   '| Household (cohabiting parents; non-cohabiting parents; single parent) | X | '
                   '| |\n'
                   '| Parent with sole custody (yes/no) | | X | |\n'
                   '| If the household is not single-parent, tax code of the other parent | X | X '
                   '| |\n'
                   '| If the household is not single-parent, method of distribution of the '
                   'allowance (50% or 100% to the applicant) | X | X | |\n'
                   '\n'
                   'Also consider that:\n'
                   "- as soon as the applicant enters the child's tax code, it is verified "
                   'immediately, in real time: if the child is present in other active '
                   'applications, the application flow is blocked with an explanatory warning;\n'
                   '- upon submission of the application, in the absence of a valid ISEE already '
                   'held by INPS, the allowance will be calculated with the minimum amount '
                   'provided for by the regulations; should the ISEE be submitted to INPS at a '
                   'later time, the user does not need to update their application: as soon as '
                   'INPS comes into possession of the ISEE, the amount of the allowance is '
                   'automatically recalculated.\n'
                   '\n'
                   'The step that completes this phase is entering the tax codes of the dependent '
                   'adult children, for whom it is not possible to request the single allowance '
                   'but who contribute to determining the number of members of the household. If '
                   'the tax code of an adult child is already present, an error is reported: the '
                   'user can decide to try again or to move on to the next step, namely specifying '
                   'the payment data.\n'
                   '\n'
                   'B. APPLICATION ENTRY: PHASE 2 - PAYMENT DATA\n'
                   'When specifying the payment data, if in the previous phase the 50% '
                   'distribution method with the other parent was declared, it will be required to '
                   "also enter the payment data of the other parent. Otherwise, only one's own "
                   'payment data must be entered. In both cases, one of the following payment '
                   'methods can be chosen:\n'
                   '- credit to accounts with an IBAN, in the SEPA area, held in the name of the '
                   'applicant and enabled to receive bank transfers (current account, savings '
                   'book, prepaid card);\n'
                   '- domiciled bank transfer to the applicant at the post office counter;\n'
                   '- credit to a prepaid card for households receiving the Inclusion Income '
                   '(Reddito di Inclusione).\n'
                   '\n'
                   'C. APPLICATION ENTRY: PHASE 3 - DECLARATIONS AND SUBMISSION\n'
                   'The process ends with the reading of the declarations of responsibility and of '
                   'the privacy notice (GDPR). Once the declarations of responsibility and the '
                   'GDPR notice have been accepted, it is possible to view a summary of the data '
                   'entered, useful for checking, before submitting the application, whether '
                   'everything has been entered correctly. From the application summary it is '
                   'possible to confirm everything in order to submit it. In case of an error '
                   '(example: wrong IBAN entered), the application will not be submitted: an '
                   'explicit error message is shown, the process ends and the user will have to '
                   'reopen the application and modify the wrong fields. In case of no error, the '
                   'application will be submitted and it will be possible to download the '
                   'receipt.\n'
                   '\n'
                   'D. APPLICATION VERIFICATION AND PAYMENTS\n'
                   'Once acquired, the application is analyzed by the staff of the competent '
                   'Offices, who can decide whether to: reject it, because the applicant is not '
                   'entitled to it; suspend it to request further documentation; accept it. In all '
                   'cases, the system notifies the applicant. In case of acceptance, the '
                   'application is valid for 12 months. The amount is paid on a monthly basis, and '
                   'the payment takes place automatically. In case of suspension, see paragraph '
                   'F.\n'
                   '\n'
                   'E. CONSULTING AND COMPLETING A DRAFT APPLICATION\n'
                   'At any point of the application submission, it is possible either to abort the '
                   'process without saving any data, or to save the application as a draft - if it '
                   'has not yet been submitted - in order to continue entering the data at a later '
                   'time using the dedicated functionality. The application can thus be consulted '
                   'at any time. From the consultation it is possible to access the application '
                   'completion functionality: after selecting “Complete”, the system asks whether '
                   'one wants to continue editing: if this is confirmed (YES) it is possible to '
                   'continue the submission of the previously saved application (in this case the '
                   'user finds the data already entered previously). If instead it is not '
                   'confirmed (NO) the previously saved data will be deleted and it will be '
                   'possible to proceed with the entry starting from scratch.\n'
                   '\n'
                   'F. ADDING ATTACHMENTS\n'
                   'If the application has been suspended to request further documents (see '
                   'paragraph D), the notification also includes a message from the operator '
                   'indicating the missing document(s). The user will then have to view their '
                   'application and add the requested attachments. At the end of the addition, '
                   'they will have to confirm again all the data present, and read and confirm the '
                   'declarations of responsibility and the privacy notice.\n'
                   '\n'
                   'G. COMPLETING THE APPLICATIONS SUBMITTED BY THE OTHER PARENT\n'
                   'Through this function it is possible to supplement the application filled in '
                   'by the other parent. In this case one is not the applicant, i.e. the person '
                   'who submits the application for the allowance, but the second parent. The main '
                   'functionality that can be performed as the other parent, in addition to '
                   'consulting the application data, is updating the payment method, i.e. it is '
                   'possible to decide whether or not to confirm the allowance distribution '
                   'requests made by the applicant. More precisely, if the applicant requests the '
                   'allowance at 100%, as the other parent it is possible to confirm the request, '
                   'by selecting “Paid 100% to the applicant”, otherwise it is possible not to '
                   'confirm it by selecting “Distributed 50% between the parents”. If the request '
                   "for the allowance at 100% is not confirmed, then one will have to enter one's "
                   'own payment data. If, instead, the applicant requests the allowance at 50% for '
                   'both parents, then it is possible to enter only the payment method. The '
                   'process continues as described in paragraph C.\n'
                   '\n'
                   'H. ADDING CHILDREN\n'
                   'It is possible to add one or more children to a pre-existing application. The '
                   'data of the additional child(ren) are entered one at a time. In this case too, '
                   "as soon as the applicant enters the child's tax code, it is verified "
                   'immediately, in real time: if the child is present in other active '
                   'applications, the application flow is blocked with an explanatory warning. '
                   'Once the new data have been entered, the process continues as reported in '
                   'paragraphs B and C: in this case, however, the data are already entered and it '
                   'is possible to confirm or modify them.\n'
                   '\n'
                   'I. FURTHER FUNCTIONALITIES\n'
                   'Finally, bear in mind that the system also makes the following operations '
                   'possible for the citizen:\n'
                   '- Consult the submitted applications;\n'
                   '- Consult the general information on the single allowance for children;\n'
                   '- Simulate the amount of the monthly allowance.\n'
                   '\n'
                   'Analysis\n'
                   'Analyze the scenario outlined above and define:\n'
                   '1. The conceptual information model (UML class diagram).\n'
                   '2. The process model (BPMN process diagram), with the exception of paragraph '
                   '“I. FURTHER FUNCTIONALITIES”.\n'
                   '3. The use case model (UML UC diagram) at summary and user-goal level.\n'
                   '4. The narrative of the use cases at user-goal level identified in the '
                   'previous point, with the exception of paragraph “I. FURTHER FUNCTIONALITIES”.\n'
                   '5. Evaluate advantages and disadvantages of developing a web system '
                   'corresponding to the use cases described in point 4 by comparing two different '
                   'alternatives (in both cases consider as a reference 250 working days per year, '
                   '8 working hours per day).\n'
                   '   a. The development is carried out by a team composed of 3 new hires '
                   '(graduates in computer engineering for less than one year) and 1 senior '
                   'project manager who has already coordinated a similar project. As for the new '
                   'hires, consider that they will work the whole time exclusively on the AUU '
                   'project and that they have a gross annual salary (RAL) of 35,000 euros. The '
                   'senior, instead, will divide their time among 5 different projects (assume an '
                   'equal distribution of time among projects), and with a RAL of 75,000 euros.\n'
                   '   b. A consulting company takes charge of the development, entrusting it to '
                   'its own team of 5 developers with experience in similar systems. A senior '
                   'analyst, she too with experience in similar systems, has been put in charge of '
                   'the project. All 6 have been assigned to the project for half of their time, '
                   'and the average cost per person of the team is 150 euros per day. In addition '
                   'to these there is an INPS project manager who will follow the progress of the '
                   'project: for her, consider a RAL of 80,000 euros and an occupation of her time '
                   'of 5%.',
    'actors': ['Applicant', 'Other Parent', 'INPS Employee'],
    'highLevelGoals': [   'Submit and manage an AUU application',
                          'Complete an AUU application started by another parent',
                          'Evaluate and manage submitted AUU applications',
                          'Access AUU information and decision-support services'],
    'lowLevelGoals': [   'Specify personal and dependent child information',
                         'Specify custody and household information',
                         'Specify the requested allowance distribution',
                         'Specify applicant payment information',
                         "Specify the other parent's payment information",
                         'Specify information about adult dependent children',
                         'Review application data before submission',
                         'Submit the AUU application',
                         'Download the application receipt',
                         'Save an incomplete application as a draft',
                         'Resume and complete a saved application',
                         'Consult an AUU application',
                         'Upload additional documents requested by INPS',
                         'Add a child to an existing application',
                         'Consult general information about the AUU',
                         'Simulate the monthly AUU amount',
                         'Confirm or modify the requested allowance distribution',
                         'Specify payment information when completing an application started by '
                         'another parent',
                         'Accept an AUU application',
                         'Reject an AUU application',
                         'Suspend an AUU application',
                         'Accept the declarations of responsibility and the GDPR privacy notice',
                         'Correct invalid application information',
                         'Interrupt an application without saving it',
                         'Discard a saved draft and restart the application',
                         'Specify the additional documents required from the applicant',
                         'Reconfirm application data after a suspension',
                         'Log in with a digital identity']}

SIA_PROJECT_23_24 = {   'name': 'La Reine Marlene - SIA Project 23 24',
    'description': 'Information Systems - academic year 23/24\n'
                   'Course Project\n'
                   'Scenario\n'
                   '\n'
                   'La Reine Marlene is a company specialized in the sale of materials and '
                   'products for the home. To improve the efficiency of its operations and the '
                   'service to customers, the company is re-designing its information system. The '
                   'details follow.\n'
                   '\n'
                   'La Reine Marlene has a wide network of suppliers. The suppliers of La Reine '
                   'Marlene will have to register in the system, providing their credentials and '
                   'company details, including VAT number, address and the IBAN for payments. '
                   'Registered suppliers can make proposals of their own products by entering in '
                   'the system the following information for each product: category, sale price '
                   '(the one that La Reine Marlene must pay to the supplier), availability, photo, '
                   'description, guaranteed delivery time. The product categories are 16: Garden, '
                   'Bathroom, Air Conditioning, Lighting, Decoration, Flooring, Doors and Windows, '
                   'Carpentry, Kitchen, Storage, Tools, Electricity, Construction, Paints, '
                   'Hardware, Furniture. Once a proposal has been entered, the supplier can no '
                   'longer modify it until they receive a response notification.\n'
                   '\n'
                   'When a supplier enters a proposal, the administration department of La Reine '
                   'Marlene receives a message notifying the presence of a new proposal from the '
                   'suppliers. At that point, it must verify the proposal and select one of the '
                   'following options: Order accepted, Revisions requested, Order rejected. If the '
                   'order is accepted, a separate order management process will start, to which '
                   'the information on the price to be displayed in the store is added, so that '
                   'this information will already be available in the subsequent processes. If '
                   'instead revisions have been requested, they must be made explicit in a '
                   'comment: at that point the supplier receives a notification and has 5 working '
                   'days to modify the proposal, entering reply comments, and re-submit it. If the '
                   'proposal has been modified within the 5 working days, then the proposal '
                   'evaluation process restarts, otherwise the proposal is deleted from the system '
                   'and the supplier notified. The administrators receive a reminder every 48 '
                   'hours about the presence of a proposal that is waiting to be validated. A '
                   'proposal that has not been verified within 10 working days is automatically '
                   'rejected, and a specific message is sent to the supplier.\n'
                   '\n'
                   'Once the products ordered from the suppliers are shipped and arrive at the '
                   'destination La Reine Marlene site (there are dozens of them throughout Italy), '
                   'they are entered in the inventory of all the products available in the store '
                   '(La Reine Marlene has no warehouse: any available product is on display). Each '
                   'product is catalogued according to its category, available quantity and '
                   'location in the store. The location in the store is entered directly by the '
                   'goods receiving staff: when an order is delivered, the staff members must '
                   'verify each product. If there are no problems, the operator confirms the '
                   'product and the system proposes a list of possible placements: the location is '
                   'chosen, and the product is physically handed over to whoever will take care of '
                   'its placement in the store and of printing the price to be displayed. Should '
                   'there be problems with any product, the operator reports it by entering a '
                   'comment and the product does not enter the store. At the end of these '
                   'operations of verification of an order arrival, the operator closes the '
                   'procedure and a new process starts, managed by the order department: if all '
                   'the products have been accepted, the order is concluded and the payment sent. '
                   'Otherwise, the order is updated and a new arrival that completes it is '
                   'awaited. In both cases specific messages are sent to the supplier.\n'
                   '\n'
                   'The system keeps track of stock in real time. An automatic notification is '
                   'sent to the order department when a product reaches a critical reorder level '
                   '(where it is specified). The administrators, in fact, can schedule automatic '
                   'reordering and replenishment actions for specific products, in order to '
                   'maintain an optimal inventory. In case of automatic reordering, a message is '
                   'sent to the pre-established supplier, who has two working days to confirm '
                   'acceptance of the order. In the absence of critical thresholds and of the '
                   'related automation, the new order is managed by the order department with a '
                   'separate process.\n'
                   '\n'
                   'Customers looking for materials for the home can purchase the products both '
                   'through the physical store and through the online store. In the online store, '
                   'customers who have registered on the site can browse the digital catalogue, '
                   'specify the desired products and quantities and complete the order. The system '
                   'automatically calculates the order total, including taxes and shipping costs. '
                   'Customers can choose among different payment options: credit card (Visa or '
                   'Mastercard), Paypal, Satispay, the La Reine Marlene purchasing card, or '
                   'immediate online bank transfer with the affiliated banks. Once the order is '
                   'paid, the system keeps track of deliveries in real time. Customers receive a '
                   'link by email through which they can follow the status of their shipments. In '
                   'addition, those who have given consent to the use of the mobile phone number '
                   'will receive notifications on updates to delivery times. Once the product '
                   'arrives at its destination, the order is tracked as concluded. Deliveries are '
                   'managed by partner companies, and each online purchase is randomly assigned to '
                   'a shipping carrier. Consider that the online store is also accessible through '
                   'a dedicated app: the operations and procedures are the same as those of the '
                   'site.\n'
                   '\n'
                   'La Reine Marlene offers a complete customer service through the information '
                   'system. Customers can ask questions, request assistance or make complaints '
                   'directly through the system. Support tickets are automatically assigned to a '
                   'customer service agent. Every time a ticket is assigned, the agent receives a '
                   'notification and has 24 hours to respond (if this does not happen, the ticket '
                   'is reassigned to a new operator, and the statistics updated). The customer is '
                   'informed upon receipt of the reply message, and has five working days to '
                   'respond: otherwise, the ticket is considered closed.\n'
                   '\n'
                   'Finally, the system collects data on orders, sales, inventory, customer '
                   'support. These data are used to analyze performance and make strategic '
                   'decisions.',
    'actors': [   'Supplier',
                  'Administration Department',
                  'Goods Receiving Staff',
                  'Order Department',
                  'Customer',
                  'Customer Service Agent',
                  'Company Management',
                  'Store Staff'],
    'highLevelGoals': [   'Supply products to La Reine Marlene',
                          'Manage product proposals',
                          'Manage incoming goods',
                          'Manage supplier orders',
                          'Purchase products',
                          'Request customer support',
                          'Provide customer support',
                          'Analyze company performance',
                          'Manage product inventory and replenishment',
                          'Manage online order delivery'],
    'lowLevelGoals': [   'Submit a product proposal',
                         'Accept a product proposal',
                         'Request revisions to a product proposal with an explanatory comment',
                         'Reject a product proposal',
                         'Prepare a supplier order',
                         'Send a supplier order',
                         'Confirm an automatically generated order',
                         'Verify delivered goods',
                         'Report problems with delivered products',
                         'Select a store location for accepted products',
                         'Mark a supplier order as completed',
                         'Update an incomplete supplier order',
                         'Pay a supplier order',
                         'Configure automatic product reordering',
                         'Monitor product stock levels',
                         'Browse the product catalogue',
                         'Select products and quantities',
                         'Place an online order',
                         'Pay an online order',
                         'Track shipment status',
                         'Open a customer support ticket',
                         'View responses to a support ticket',
                         'Respond to a customer support ticket',
                         'View business statistics',
                         'Register as a supplier',
                         'Set the retail price for an accepted product proposal',
                         'Modify and resubmit a product proposal',
                         'Confirm accepted products for admission into the store',
                         'Print the price of an accepted product',
                         'Reply to a customer service response',
                         'Close the verification of a delivered order',
                         'Register as a customer']}

SIA_PROJECT_22_23 = {   'name': 'Ethical Purchasing Group - SIA Project 22 23',
    'description': 'Information Systems – 2022/2023\n'
                   'Course Project\n'
                   'Consider the following scenario:\n'
                   '\n'
                   'A km-zero fruit and vegetable store wants to develop a management system for '
                   'am Ethical Purchasing Group (EPS; in Italian, Gruppo di Acquisti Solidale, or '
                   'GAS) that connects a number of customers (family groups or generally groups of '
                   'people) and some farmers. The basic philosophy is a conscious approach to '
                   'purchasing, involving knowledge of the origin, quality, and different types of '
                   'products.\n'
                   '\n'
                   'The supporting information system should provide service to customers, '
                   'farmers, and store employees.\n'
                   '\n'
                   'The operating cycle of the EPS is weekly:\n'
                   '- Starting at 12 noon on Friday and by 9 a.m. on Saturday morning, farmers '
                   'provide an estimate of available products, in terms of types, prices, and '
                   'quantities,\n'
                   '- Customer orders are accepted until 11 p.m. on Sunday,\n'
                   '- By 9 a.m. on Monday morning the farmers confirm the availability of '
                   'products,\n'
                   "- At this point the system automatically performs payments from customers' "
                   'virtual wallets,\n'
                   '- After payment has been made, customers can schedule times to pick up '
                   'produce,\n'
                   '- By Tuesday evening, farmers deliver their products to the store,\n'
                   '- Pickups can take place from Wednesday morning to Friday evening.\n'
                   '\n'
                   'The information system has a catalog of products that describes the '
                   'characteristics, contains photos, and indicates the unit of measurement with '
                   'which they are sold (for example: €/kg). In addition, a minimum and a maximum '
                   'quantity that can be ordered is indicated.\n'
                   '\n'
                   'The availabilities entered by farmers refer to a product in the catalog, '
                   'specify the total quantity available and a price (with the same unit of '
                   'measure indicated in the catalog). It is also possible to indicate crop '
                   'characteristics, e.g., small size, excellent quality, very ripe, etc.\n'
                   '\n'
                   'Customers can choose from all the offerings of the various farmers by '
                   'specifying the quantity and completing an order. The order can be placed '
                   "directly by customers via the web or by store employees at the customers' "
                   'request. Once the customer confirms the product entry, the system verifies '
                   'that the minimum quantities are met: if not, the customer must modify the '
                   'order before it can be finally confirmed. Once the order is completed, a '
                   'summary email is sent to the customer.\n'
                   '\n'
                   'Please note that the customer is a representative of a buying group, typically '
                   'family groups or more generally groups of people. Therefore, only the group '
                   'representative can enter group orders into the system.\n'
                   '\n'
                   'Customer orders are in the "entered" state until the farmers confirm available '
                   'quantities. If the available quantities are sufficient to cover the orders, '
                   'the orders move to the "confirmed" status. If there is no availability for all '
                   "orders of a certain product, according to the system's precedence rules, "
                   'unavailable quantities are removed from lower precedence orders. Modified '
                   'orders go into the "modified" status and must be viewed and accepted by '
                   'customers. If all products in an order are unavailable, then the order is '
                   "cancelled. Upon delivery of the farmers' products, the clerk confirms receipt "
                   'of the products in the specified quantity. If by 4 p.m. on Tuesday the goods '
                   'have still not been delivered the system sends a reminder via SMS. If at the '
                   'end of the day (8 p.m.) the goods have not been delivered, the system changes '
                   'the orders related to delivery, re-credits the amount of goods not present '
                   'with a bonus of 20% and reports the inconvenience to customers.\n'
                   '\n'
                   'Payment of orders is made after confirmation of quantities by farmers, for the '
                   'quantities actually in the order. Payment is made from a personal wallet that '
                   'users can top up at any time through the store.\n'
                   '\n'
                   "After order placement, if the customer's wallet balance is insufficient, a "
                   'warning is sent via email but the order is still accepted.\n'
                   '\n'
                   'If the balance is insufficient at the time of payment, a message (SMS) is sent '
                   'to the customer who has until Monday evening to top up their wallet. If the '
                   'balance is not sufficient on Monday evening, the order is cancelled.\n'
                   '\n'
                   'As soon as the payment is made (automatically by the system) customers can '
                   'book an appointment to pick up their products at the store.\n'
                   '\n'
                   'Store employees at the beginning of their shift view the pickup schedule and '
                   'prepare packages for customers, when they arrive they register the pickup of '
                   'products.\n'
                   '\n'
                   'In case of failure to pick up on time, the system sends an SMS alert to the '
                   'customer.\n'
                   '\n'
                   'If the customer has not picked up their order by Friday, it is marked as '
                   '"forfeited" and the customer\'s fair play score is updated as detailed in the '
                   'following.\n'
                   '\n'
                   'The system has a mean of evaluation the “fair play” of customers registered in '
                   'the system. The customer’s fair play score is a measure of how correctly the '
                   'users behave regarding their orders. This score is maintained in the system '
                   'and is used as a mean of precedence in case of limited availability of '
                   'produce. The “fair play” score is computed based on four different indicators: '
                   'O) number of computed orders; R) number of reminders received; F) number of '
                   'forfeited pickups; M) number of modified orders. When there is not enough '
                   'availability of produce for all orders, the customers with higher score are '
                   'given precedence over those with lower score.',
    'actors': ['Customer', 'Farmer', 'Store Employee'],
    'highLevelGoals': [   'Manage customer orders',
                          'Manage product supply and provisioning',
                          'Manage customer payments',
                          'Manage order pickup'],
    'lowLevelGoals': [   'Place an order',
                         'Accept a modified order',
                         'Book an order pickup',
                         'Enter an order on behalf of a customer',
                         'View order details',
                         'Confirm an order pickup',
                         'Recharge a customer wallet',
                         'Confirm product delivery',
                         'Enter product availability',
                         'Confirm product availability',
                         'Browse offers from farmers',
                         'Select products and quantities for an order',
                         'Modify an order that does not meet minimum quantity constraints',
                         'View the order pickup schedule']}

SIA_PROJECT_21_22 = {   'name': 'Event Organization Portal - SIA Project 21 22',
    'description': 'Information Systems - academic year 21/22\n'
                   'Course Project\n'
                   'Version 1.0.1 - 20/12/2021\n'
                   'Consider the following scenario:\n'
                   '\n'
                   'A startup intends to develop a web portal that can help people who intend to '
                   'organize an event, bringing together in a single website the information '
                   'concerning the guests and the various services necessary for the event itself '
                   'to take place.\n'
                   '\n'
                   'The platform to be developed envisages the presence of providers and guests, '
                   'in addition to the organizer.\n'
                   '\n'
                   'At registration, providers supply, in addition to their credentials, their '
                   'personal data and the data of the company they manage (VAT number, company '
                   'address, accepted payment methods).\n'
                   '\n'
                   'The provider, once registered, will be able to enter the services offered by '
                   'their company, each belonging to a category (catering, hairdresser, florist '
                   'etc.), each of which will be associated with a virtual showcase in which the '
                   'provider can upload demonstration photos, together with the corresponding '
                   'prices and the hours corresponding to the particular service shown by the '
                   "showcase (e.g. Hairdresser's blow-dry service has as hours 10:00-12:00 from "
                   'Tuesday to Thursday, Haircut + shampoo service with hours 8:00-12:00 + '
                   '15:00-18:00 from Tuesday to Saturday).\n'
                   '\n'
                   'The event organizer, identified by their tax code, at registration, in '
                   'addition to choosing their credentials, will provide their personal data, '
                   'residence data and their IBAN for the possible payment of the services.\n'
                   '\n'
                   'The organizer, through the portal, will be able to create the event, choosing '
                   'the type of event (wedding, graduation, concert…) to organize, the date, the '
                   'place where it will be held and the budget planned for the organization of the '
                   'event. When creating the event the organizer will be able to choose from a '
                   'pre-existing list the types of service for which they are interested in '
                   'receiving help (for example catering, flowers, taxi service etc.).\n'
                   '\n'
                   'The organizer will also be able to add the guests to the portal, entering the '
                   'corresponding data, specifying, in addition to the personal data, the email '
                   'with which the guest will be identified (and which they will use to log in) '
                   'and the category to which the guest belongs (relative, friend, colleague '
                   'etc.).\n'
                   '\n'
                   'For each guest added, the system will generate an invitation code that will be '
                   'sent by email to the specified address; this code will be used by the guest as '
                   'a password to access the portal.\n'
                   '\n'
                   'The organizer will also have available a blog associated with their event in '
                   'which the organizer or the guests can write information about the event, post '
                   'photos or videos and leave their thoughts by creating new posts or commenting '
                   'on the existing ones.\n'
                   '\n'
                   'The organizer, once the event has been created, will be able to view, for each '
                   'service chosen when creating the event, the showcases of the providers that '
                   'supply the chosen type of service and to arrange an appointment compatible '
                   'with the hours observed by that service, specifying the details and any '
                   'special requests. The provider, through their interface, will be able to view '
                   'the various appointment requests and will have to approve them. The approved '
                   'requests are displayed directly in a calendar on the site associated with the '
                   'event, where the organizer will be able to consult the appointments for the '
                   'agreed services.\n'
                   '\n'
                   'After the meeting between the provider and the organizer (in which they agree '
                   'on the details of the service), the provider calculates the quotation and '
                   'proceeds to upload the amount on the portal, associating it with the completed '
                   'appointment.\n'
                   '\n'
                   'Once the upload has taken place the organizer can choose whether to accept or '
                   'reject the quotation; if it is accepted, the total amount is subtracted from '
                   'the remaining budget. By accepting the amount, the organizer chooses the '
                   'payment mode (instalments, deposit + balance or full amount) and the payment '
                   'method (online or on site). If the payment takes place on site the provider '
                   'will proceed to confirm the amount paid through the portal (in the case of '
                   'payment in several instalments the provider confirms the amount of each '
                   'instalment received).\n'
                   '\n'
                   'At any time the organizer will be able to consult the history of the contracts '
                   '(with the related status and cost) and the budget balance for the entire '
                   'event.',
    'actors': ['Organizer', 'Service Provider', 'Guest'],
    'highLevelGoals': [   'Manage event services',
                          'Manage an event',
                          'Manage the event blog',
                          'Access the platform'],
    'lowLevelGoals': [   'Register as a service provider',
                         'Add offered services',
                         'Confirm an on-site payment',
                         'Register as an organizer',
                         'Create an event',
                         'Add invited guests',
                         'Select the service types needed for an event',
                         'View appointment calendar',
                         'View the remaining event budget',
                         'View contract history',
                         'Create a blog post',
                         'Upload demonstration photos for a service',
                         'Specify the price of a service',
                         'Specify service availability time slots',
                         'Browse service showcases',
                         'Request an appointment with a service provider',
                         'Approve an appointment request',
                         'Upload a quotation for a completed appointment',
                         'Accept a quotation',
                         'Reject a quotation',
                         'Select a payment schedule',
                         'Select a payment method',
                         'Access the platform using an invitation code',
                         'Upload photos or videos to the event blog',
                         'Comment on an event blog post',
                         'View appointment requests',
                         'Log in']}

SIA_PROJECT_GENOME = {   'name': 'Genome Nexus',
    'description': 'We need a comprehensive, centralized resource for the rapid, automated, and '
                   'high-throughput annotation and interpretation of genetic variants in cancer. '
                   'This system should integrate information from various existing resources, '
                   'including databases that convert DNA changes to protein changes, predict the '
                   'functional effects of protein mutations, and contain information about '
                   'mutation frequencies, gene function, variant effects, and clinical '
                   'actionability.',
    'link-readme': 'https://github.com/WebFuzzing/EMB/tree/master/jdk_8_maven/cs/rest-gui/genome-nexus#readme',
    'swagger': 'https://raw.githubusercontent.com/WebFuzzing/EMB/refs/heads/master/openapi-swagger/genome-nexus.json',
    'actors': ['Researcher', 'Clinician'],
    'highLevelGoals': [   'Annotate genetic variants in cancer',
                          'Interpret genetic variants in cancer',
                          'Look up reference gene and protein data'],
    'lowLevelGoals': [   'Search and retrieve variant annotations from a user interface',
                         'Analyze cancer-related mutations using automated tools',
                         'Classify cancer mutations based on their clinical relevance',
                         'Process large genomic datasets in parallel',
                         'Extract and transform mutation data from high-throughput sequencing '
                         'formats (e.g., VCF, BAM)',
                         'Perform mutation quality control and filtering',
                         'Retrieve and harmonize data from multiple genomic databases',
                         'Query integrated genomic databases for relevant mutation information',
                         'Integrate data from multiple compatible genomic sources for easy '
                         'retrieval',
                         'Convert a DNA change to the corresponding protein change',
                         'Convert mutations to amino acid changes for protein function analysis',
                         'Predict the impact of mutations on protein structure using '
                         'bioinformatics tools',
                         'Use prediction tools (e.g., PolyPhen, SIFT) to estimate mutation effects '
                         'on protein function',
                         'Build and apply machine learning models to predict functional impact',
                         'Rank mutations based on their predicted functional impact',
                         'Retrieve mutation frequencies across different population groups',
                         'Provide mutation frequency data_key for specific diseases or conditions',
                         'Retrieve gene function annotations from public databases like Gene '
                         'Ontology (GO)',
                         'Identify pathways and biological processes related to the mutated gene',
                         'Identify how mutations alter protein activity or structure',
                         'Identify mutations with known clinical drug responses or therapeutic '
                         'implications',
                         'Provide actionable insights on mutations based on current clinical '
                         'research',
                         'Retrieve the annotation of a variant by dbSNP id',
                         'Retrieve the annotation of a variant by genomic location',
                         'Retrieve the canonical Ensembl gene for a gene identifier',
                         'Retrieve the Ensembl transcripts of a gene or protein',
                         'Retrieve the external references of an Ensembl gene',
                         'Retrieve a PFAM protein domain',
                         'Retrieve the header of a PDB structure',
                         'Retrieve the post-translational modifications of a transcript']}

SIA_PROJECT_GESTAO_HOSPITAL = {   'name': 'Gestao Hospital',
    'description': 'We need an API to organize a public health system, specifically to assist the '
                   'Unified Health System (SUS) in Brazil. The goal is to create a tool that helps '
                   'avoid waste and optimize resources based on patient needs. The system should '
                   'manage hospital information, including their stock of products, blood banks, '
                   'and available beds. It should be able to recommend the closest hospital with '
                   'available beds to a patient and facilitate the transfer of products, such as '
                   'blood, between nearby hospitals if one is in need. A hospital with four or '
                   'fewer items or liters of a product is considered to have only enough for its '
                   'own use. The API should allow for registering hospitals, indicating the '
                   "closest hospital to a patient's location, managing patient check-in and "
                   'check-out, checking available beds, and managing product and blood bank '
                   'inventories within hospitals.',
    'link-readme': 'https://github.com/ValchanOficial/GestaoHospital/blob/master/README.md',
    'swagger': 'https://raw.githubusercontent.com/WebFuzzing/Dataset/refs/heads/master/openapi-swagger/gestaohospital.json',
    'actors': ['Hospital Manager', 'Healthcare Staff', 'Hospital Logistics Staff'],
    'highLevelGoals': [   'Manage hospital information',
                          'Manage hospital beds and patients',
                          'Manage hospital stock and blood bank',
                          'Find a suitable hospital for a patient'],
    'lowLevelGoals': [   'Register a new hospital',
                         'Delete a hospital',
                         'Update hospital information',
                         'Find the nearest hospital with available beds',
                         'View hospital information',
                         'View Products and Quantities',
                         'Register a product in stock',
                         'Delete Products',
                         'Update product quantities',
                         'View Info on a Single Product',
                         'Request a product transfer from a nearby hospital',
                         'View patient information',
                         'Register a patient at a hospital',
                         'Update patient information',
                         'Check out a patient from a hospital',
                         'Check available beds',
                         'List patients in a hospital',
                         'Find hospitals near a hospital']}

SIA_PROJECT_LONDON_AMBULANCE_SERVICE = {   'name': 'London Ambulance Service',
    'description': 'The London Ambulance Service dispatches ambulances in emergencies. The key '
                   'goal is to allocate an available ambulance for every call that can reach the '
                   'scene within 11 minutes. The entire dispatch process must not exceed a set '
                   'maximum time limit. The Computer Aided Despatch system analyzes incident forms '
                   'and assigns vehicles. The exact location of moving ambulances must be tracked, '
                   'requiring ambulance staff to follow standard routes and communicate departure '
                   'and destination information so that radio operators and the CAD can accurately '
                   'record the corresponding data.',
    'actors': ['Ambulance Staff', 'Radio Operator'],
    'highLevelGoals': ['Track moving ambulances', 'Dispatch ambulances to emergency calls'],
    'lowLevelGoals': [   'Record the departure and destination of an ambulance',
                         'Communicate departure and destination when leaving']}

SIA_PROJECT_CALCULATOR = {   'name': 'Calculator',
    'description': 'This project develops a smartphone app for a simple '
                   'calculator. In its initial version, it allows the user to do basic '
                   'calculations. More complex calculations will be considered in subsequent '
                   'versions that are added iteratively.",\n'
                   '  \n'
                   '  "epics": [\n'
                   '    {\n'
                   '      "title": "Basic Calculation Functionality",\n'
                   '      "description": "Implement basic arithmetic operations such as addition, '
                   'subtraction, multiplication, and division. This feature is essential for users '
                   'to perform simple calculations conveniently on their smartphones.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Perform Addition",\n'
                   '          "story": "As a user, I want to add two numbers so that I can quickly '
                   'calculate their sum.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The calculator allows the user to input two numbers.",\n'
                   '            "The result of the addition is displayed correctly."\n'
                   '          ]\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Perform Subtraction",\n'
                   '          "story": "As a user, I want to subtract one number from another so '
                   'that I can find the difference.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The calculator allows the user to input two numbers.",\n'
                   '            "The result of the subtraction is displayed correctly."\n'
                   '          ]\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Perform Multiplication",\n'
                   '          "story": "As a user, I want to multiply two numbers so that I can '
                   'obtain their product.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The calculator allows the user to input two numbers.",\n'
                   '            "The result of the multiplication is displayed correctly."\n'
                   '          ]\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Perform Division",\n'
                   '          "story": "As a user, I want to divide one number by another so that '
                   'I can calculate the quotient.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The calculator allows the user to input two numbers.",\n'
                   '            "The result of the division is displayed correctly, and division '
                   'by zero is handled appropriately."\n'
                   '          ]\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "User Interface Design",\n'
                   '      "description": "Create a simple and intuitive user interface that allows '
                   'users to easily input numbers and select operations. A user-friendly interface '
                   'is vital for ensuring a positive user experience.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Input Numbers",\n'
                   '          "story": "As a user, I want to easily input numbers so that I can '
                   'perform calculations without frustration.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The app includes a numeric keypad for input.",\n'
                   '            "The numeric keypad is responsive and allows for easy number '
                   'entry."\n'
                   '          ]\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Select Operations",\n'
                   '          "story": "As a user, I want to select basic arithmetic operations so '
                   'that I can perform calculations effortlessly.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The app displays clearly labeled buttons for each arithmetic '
                   'operation.",\n'
                   '            "Users can tap the operation button after entering the numbers to '
                   'perform the calculation."\n'
                   '          ]\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Display Results",\n'
                   '          "story": "As a user, I want to see the calculation results clearly '
                   'so that I can verify my answers.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The result of the calculation is displayed prominently on the '
                   'screen.",\n'
                   '            "The display updates immediately after the user performs a '
                   'calculation."\n'
                   '          ]\n'
                   '        }\n'
                   '      ]\n'
                   '    }\n'
                   '  ]\n'
                   '}',
    'actors': ['User'],
    'highLevelGoals': [   'Perform basic arithmetic calculations',
                          'Interact with the calculator interface'],
    'lowLevelGoals': [   'Add two numbers and obtain their sum',
                         'Subtract one number from another and obtain the difference',
                         'Multiply two numbers and obtain their product',
                         'Divide one number by another and obtain the quotient',
                         'Enter numbers for a calculation',
                         'Select a basic arithmetic operation',
                         'View the result of a calculation']}

SIA_PROJECT_FITNESSTRACKER = {   'name': 'Fitness Tracker',
    'description': 'This project develops a fitness application aimed at '
                   'helping users track their physical activities, monitor progress, set fitness '
                   'goals, and receive personalized workout recommendations. This app is designed '
                   'to cater to both fitness enthusiasts and beginners, providing valuable tools '
                   'and insights to support their fitness journey.",\n'
                   '  "epics": [\n'
                   '    {\n'
                   '      "title": "User Activity Tracking",\n'
                   '      "description": "Allow users to track their physical activities, such as '
                   'running, walking, or cycling, to monitor their performance over time. This '
                   'helps users stay consistent and measure their progress in their fitness '
                   'journey.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Track Daily Physical Activities",\n'
                   '          "story": "As a user, I want to track my daily physical activities '
                   '(e.g., steps, distance, and duration) so that I can monitor my exercise '
                   'habits.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The app records the duration and distance of activities such as '
                   'running, walking, or cycling.",\n'
                   '            "The app displays a summary of all activities recorded each day."\n'
                   '          ]\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Manual Activity Logging",\n'
                   '          "story": "As a user, I want to manually log activities that cannot '
                   'be automatically tracked so that all my workouts are recorded in one place.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "Users can manually add details of activities such as yoga or '
                   'weightlifting.",\n'
                   '            "The manually logged activities appear in the daily summary along '
                   'with automatically tracked activities."\n'
                   '          ]\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Progress Monitoring and Visualization",\n'
                   '      "description": "Provide visual representations of users\' activity data '
                   'to help them easily monitor their fitness progress. Visualizing progress '
                   'encourages motivation and helps users understand trends and improvements.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "View Weekly and Monthly Progress Reports",\n'
                   '          "story": "As a user, I want to view my weekly and monthly progress '
                   'so that I can assess my consistency and improvements over time.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The app generates weekly and monthly summaries of activity '
                   'data.",\n'
                   '            "The progress reports include charts and graphs for visual '
                   'representation."\n'
                   '          ]\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Receive Achievement Notifications",\n'
                   '          "story": "As a user, I want to receive notifications when I reach '
                   'fitness milestones so that I stay motivated.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The app sends a notification when the user reaches a specific '
                   'goal or personal record.",\n'
                   '            "Notifications are customizable based on user preferences."\n'
                   '          ]\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Fitness Goal Setting",\n'
                   '      "description": "Enable users to set personalized fitness goals such as '
                   'daily steps, calories burned, or workout frequency, to give them a target to '
                   'work towards and help maintain focus.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Set and Edit Fitness Goals",\n'
                   '          "story": "As a user, I want to set and edit my fitness goals so that '
                   'I can tailor my targets to my current fitness level.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "Users can set goals for metrics such as steps, calories burned, '
                   'and active minutes.",\n'
                   '            "Users can edit their goals at any time, and changes are reflected '
                   'in their progress tracking."\n'
                   '          ]\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Track Goal Achievement",\n'
                   '          "story": "As a user, I want to track my goal achievement status so '
                   'that I can see how close I am to reaching my targets.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The app shows progress towards each goal in percentage form.",\n'
                   '            "Users receive updates on how much more effort is needed to reach '
                   'their goals."\n'
                   '          ]\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Personalized Workout Recommendations",\n'
                   '      "description": "Offer personalized workout plans and recommendations '
                   "based on the user's fitness level, preferences, and goals. This helps users "
                   'maximize the efficiency of their workouts and achieve their desired '
                   'outcomes.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Receive Personalized Workout Suggestions",\n'
                   '          "story": "As a user, I want to receive personalized workout '
                   'suggestions based on my fitness level and goals so that I can improve '
                   'effectively.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The app recommends workouts based on user preferences (e.g., '
                   'cardio, strength).",\n'
                   '            "Recommendations adapt based on the user\'s activity history and '
                   'progress."\n'
                   '          ]\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Adjust Workouts Based on Feedback",\n'
                   '          "story": "As a user, I want to provide feedback on workout '
                   'difficulty so that the app can adjust future recommendations to suit my '
                   'needs.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "Users can rate the difficulty of a workout after completing '
                   'it.",\n'
                   '            "The app uses the feedback to adjust the intensity of future '
                   'recommendations."\n'
                   '          ]\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Wearable Device Integration",\n'
                   '      "description": "Integrate with wearable devices to automatically collect '
                   'fitness data such as heart rate, steps, and calories burned. This provides a '
                   'more seamless experience for users who want accurate data tracking.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Connect to Wearable Devices",\n'
                   '          "story": "As a user, I want to connect my wearable device to the app '
                   'so that my physical activity data is automatically synced.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The app can connect to popular wearable devices (e.g., '
                   'smartwatches, fitness bands).",\n'
                   '            "Activity data such as steps, heart rate, and calories burned is '
                   'automatically updated in the app."\n'
                   '          ]\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Sync Data in Real-Time",\n'
                   '          "story": "As a user, I want the app to sync data from my wearable '
                   'device in real-time so that I have up-to-date information on my fitness '
                   'progress.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The app automatically syncs with the wearable device when '
                   'connected.",\n'
                   '            "Users can view real-time metrics such as current heart rate and '
                   'step count."\n'
                   '          ]\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Social Media Sharing",\n'
                   '      "description": "Enable users to share their fitness activities, '
                   'achievements, and progress on social media to engage with friends, celebrate '
                   'milestones, and motivate others.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Share Activities on Social Media",\n'
                   '          "story": "As a user, I want to share my completed activities on '
                   'social media so that I can celebrate my progress with friends.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "Users can share details of completed workouts (e.g., distance, '
                   'duration) to popular social media platforms.",\n'
                   '            "The shared posts include customizable messages and images '
                   'generated by the app."\n'
                   '          ]\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Post Achievements and Milestones",\n'
                   '          "story": "As a user, I want to post my fitness achievements and '
                   'milestones on social media so that I can motivate others and receive '
                   'support.",\n'
                   '          "acceptance_criteria": [\n'
                   '            "The app allows users to share milestones (e.g., reaching a goal) '
                   'as social media posts.",\n'
                   '            "Achievements include celebratory graphics and messages to engage '
                   'the user\'s social network."\n'
                   '          ]\n'
                   '        }\n'
                   '      ]\n'
                   '    }\n'
                   '  ]\n'
                   '}',
    'actors': ['User'],
    'highLevelGoals': [   'Track physical activities',
                          'Monitor fitness progress',
                          'Set and manage fitness goals',
                          'Receive personalized workout recommendations',
                          'Use a wearable device with the app',
                          'Share fitness activities and achievements on social media'],
    'lowLevelGoals': [   'Track the duration and distance of daily activities',
                         'Manually log physical activities',
                         'View weekly and monthly progress reports',
                         'Set fitness goals',
                         'Edit fitness goals',
                         'Track goal achievement',
                         'View personalized workout suggestions',
                         'Rate the difficulty of a completed workout',
                         'Connect to wearable devices',
                         'View activity metrics from a wearable device',
                         'Share a completed activity on social media',
                         'Post achievements and milestones on social media',
                         'View the daily activity summary']}

SIA_PROJECT_PLANNINGPOKER = {   'name': 'Planning Poker',
    'description': 'This project describes \'Planning Poker\' a digital '
                   'card game designed to help empower agile and scrum development teams to '
                   'collectively set their sprint goals. Using anonymous pointing, Planning Poker '
                   'helps to elicit productive conversations across the team to create shared '
                   'ownership, knowledge, and understanding.",\n'
                   '  "epics": [\n'
                   '    {\n'
                   '      "title": "Game Creation and Management",\n'
                   '      "description": "This epic covers the functionalities required for '
                   'moderators to create, manage, and modify games. It allows moderators to start '
                   'new games, manage items to be estimated, and invite participants '
                   'effectively.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Create a New Game",\n'
                   '          "story": "As a moderator, I want to create a new game by entering a '
                   'name and an optional description, so that I can start inviting estimators.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Invite Estimators",\n'
                   '          "story": "As a moderator, I want to invite estimators by giving them '
                   'a URL where they can access the game, so that we can start the game.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Add Item for Estimation",\n'
                   '          "story": "As a moderator, I want to add an item to the list of items '
                   'to be estimated, so that we can be flexible and accommodate situations where '
                   'we think of a new story while playing.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Edit Item for Estimation",\n'
                   '          "story": "As a moderator, I want to edit an item in the list of '
                   "items to be estimated, so that I can make it better reflect the team's "
                   'understanding of the item.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Delete Item from Estimation",\n'
                   '          "story": "As a moderator, I want to delete an item from the list of '
                   'items to be estimated, so that we can remove it and not estimate it.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "View All Items for Estimation",\n'
                   '          "story": "As a moderator, I want to see all items we try to estimate '
                   'this session, so that I can answer questions about the current story such as '
                   '\'does this include ___\'.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Select Item for Estimation",\n'
                   '          "story": "As a moderator, I want to select an item to be estimated '
                   'or re-estimated, so that the team sees that item and can estimate it.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Show Estimates Immediately",\n'
                   '          "story": "As a moderator, I want to show all estimates immediately, '
                   'so that I can decide to show the estimates that have been given even though '
                   'not all estimators have given their estimate.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Accept Average Estimate",\n'
                   '          "story": "As a moderator, I want to accept the average of all '
                   'estimates, so that we can move on to the next item when we agree.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Automatically Fill Estimate Field",\n'
                   '          "story": "As a moderator, I want to have the \'estimate\' field '
                   'filled in automatically if all estimators show the same card, so that I can '
                   'accept it more quickly.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Enter Agreed-Upon Estimate",\n'
                   '          "story": "As a moderator, I want to enter the agreed-upon estimate, '
                   'so that we can move on to the next item when we agree.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Re-estimate Previous Story",\n'
                   '          "story": "As a moderator, I want to estimate a story we estimated '
                   'earlier in the session again, so that we can give a new estimate if we feel '
                   'different about the story after estimating other related stories.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Import Stories from Spreadsheet",\n'
                   '          "story": "As a moderator, I want to import stories from a '
                   'spreadsheet, so that I don\'t have to copy and paste each individual story.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Copy/Paste Stories from Spreadsheet",\n'
                   '          "story": "As a moderator, I want to copy/paste stories from a '
                   'spreadsheet, so that I can get started more quickly.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Browse Previous Games",\n'
                   '          "story": "As a moderator, I want to browse through previous games, '
                   'so that I can find the previous game I\'m looking for.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "View Game Transcript",\n'
                   '          "story": "As a moderator, I want to view a transcript of a game, so '
                   'that I can see the stories and estimates.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Export Game Transcript as HTML",\n'
                   '          "story": "As a moderator, I want to export a transcript of a game as '
                   'an HTML file, so that I can save the stories and estimates locally.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Export Game Transcript as CSV",\n'
                   '          "story": "As a moderator, I want to export a transcript of a game as '
                   'a CSV file, so that I can further process the stories and estimates.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Delete a Game",\n'
                   '          "story": "As a moderator, I want to delete a game, so that stories '
                   'and estimates for this game are no longer stored.",\n'
                   '          "acceptance_criteria": []\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Account Management",\n'
                   '      "description": "This epic provides functionalities related to user '
                   'account management, allowing moderators to create, log in, modify, and delete '
                   'their accounts securely.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Create an Account",\n'
                   '          "story": "As a moderator, I want to create an account for the '
                   'application by entering my name, email address, a password, and a username, so '
                   'that I can start using the application.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Log In to Account",\n'
                   '          "story": "As a moderator, I want to log in using my account name and '
                   'password, so that I can start using the application.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Change Account Details",\n'
                   '          "story": "As a moderator, I want to change my account details, so '
                   'that I can keep my account details up-to-date.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Delete My Account",\n'
                   '          "story": "As a moderator, I want to delete my account, so that '
                   'account information and games are no longer stored.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Get Password Reminder",\n'
                   '          "story": "As a moderator, I want to get a password reminder by '
                   "email, so that I can get back to using the application when I've forgotten my "
                   'password.",\n'
                   '          "acceptance_criteria": []\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Time and Estimation Settings",\n'
                   '      "description": "This epic enables moderators to manage time settings and '
                   'estimation configurations to suit the needs of their teams during estimation '
                   'sessions.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "View Local Timezone",\n'
                   '          "story": "As a moderator, I want to see dates and times in my local '
                   'timezone, so that I don\'t have to do timezone conversion myself.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Select Estimation Scale",\n'
                   '          "story": "As a moderator, I want to select whether to have the team '
                   'estimate with {0, 1/2, 1, 2, 3, 5, 8, etc.} or {0, 1, 2, 4, 8, 16, 32, etc.}, '
                   'so that the team can use either the modified Fibonacci sequence or powers of '
                   '2.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Invite Up to 15 Estimators",\n'
                   '          "story": "As a moderator, I want to invite up to 15 estimators, so '
                   'that we can play with large but not immense teams.",\n'
                   '          "acceptance_criteria": []\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Estimator Participation",\n'
                   '      "description": "This epic encompasses functionalities for estimators to '
                   'participate in games, including submitting estimates and viewing relevant '
                   'information about the items being estimated.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Join a Game",\n'
                   '          "story": "As an estimator, I want to join a game by entering my name '
                   'on the page I received the URL for, so that I can participate.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "View Item Being Estimated",\n'
                   '          "story": "As an estimator, I want to see the item we’re estimating, '
                   'so that I know what I’m giving an estimate for.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "See All Items for Estimation",\n'
                   '          "story": "As an estimator, I want to see all items we will try to '
                   'estimate this session, so that I have a feel for the sizes of the various '
                   'items.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "See Who Gave Estimates",\n'
                   '          "story": "As a participant, I want to see who gave what estimates '
                   'during the current round, so that I know this when we’re discussing the '
                   'estimates.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "See Estimate Notifications",\n'
                   '          "story": "As a participant, I want to immediately see that an '
                   'estimate has been given by a specific estimator, so that I know who has '
                   'already given an estimate and who we’re still waiting for.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "View Prior Estimates",\n'
                   '          "story": "As a participant, I want to be able to see each '
                   "estimator's prior estimates for the story being estimated, so that I can see "
                   'how his or her opinion has changed so I can ask questions.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Change Estimate Until Last Card Selected",\n'
                   '          "story": "As a participant, I want to change my estimate as long as '
                   'the draw has not been completed, so that I can change my mind.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Change Estimate Up Until Last Person Selects",\n'
                   '          "story": "As a participant, I want to be able to change my estimate '
                   'up until the last person selects a card and all are shown, so that I can '
                   'change my mind based on information I hear.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Start a Countdown Timer",\n'
                   '          "story": "As a participant, I want to be able to start a two-minute '
                   'countdown timer that all participants can see, so that I can limit the time '
                   'spent discussing the estimates when I think we’ve talked long enough.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Reset Timer After Estimate",\n'
                   '          "story": "As a participant, I want to have the two-minute timer '
                   "reset itself as soon as we all play an estimate, so that it's ready for use on "
                   'the next round.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Scroll Through Previous Estimates",\n'
                   '          "story": "As a participant, I want to scroll back through the '
                   'stories and estimates from prior rounds, so that I can use this information '
                   'when I estimate the item of the current round.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Display Thumbnail Photo",\n'
                   '          "story": "As a participant, I want to have a small thumbnail photo '
                   'displayed near where my cards are played, so that the game is more personal '
                   'because I see who I\'m estimating with.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Keep Card Order Consistent",\n'
                   '          "story": "As a participant, I want to always have the cards in the '
                   'same order across multiple draws, so that it\'s easy to compare estimates.",\n'
                   '          "acceptance_criteria": []\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Development Standards",\n'
                   '      "description": "This epic focuses on development standards and practices '
                   'to ensure that the application is user-friendly, accessible, and '
                   'performant.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Compliance with XHTML and CSS Standards",\n'
                   '          "story": "As a developer, I want to have written a site which is '
                   'compliant with XHTML and CSS standards, so that as many people as possible can '
                   'access the site and view it as intended.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Create Database Indexes",\n'
                   '          "story": "As a developer, I want to have created database indexes, '
                   'so that the queries run as fast as possible.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Functionality Across Browsers",\n'
                   '          "story": "As a developer, I want to have the application function '
                   'correctly in Internet Explorer 6 and 7, Firefox 1.5 and 2, and Safari 2, so '
                   'that as many people as possible can fully use the application.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "W3C Accessibility Compliance",\n'
                   '          "story": "As a developer, I want to have the site comply with the '
                   'W3C accessibility guidelines where possible, so that people with accessibility '
                   'issues can use the application.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Fast Application Response",\n'
                   '          "story": "As a user, I want to have the application respond quickly '
                   'to my actions, so that I don\'t get bored.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Unicode Support",\n'
                   '          "story": "As a user, I want to be able to use Unicode, so that I can '
                   'use any language I like.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Sensible and Predictable URLs",\n'
                   '          "story": "As a user, I want to see sensible and predictable URLs, so '
                   'that the application feels logical and transparent.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "User-Friendly Error Pages",\n'
                   '          "story": "As a user, I want to have nice error pages when something '
                   'goes wrong, so that I can trust the system and its developers.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Non-Identifiable Data Storage",\n'
                   '          "story": "As a Researcher, I want results to be stored in a '
                   'non-identifiable way, so that I can study the data to see things like whether '
                   'estimates converged around the first opinion given by \'estimator A\'.",\n'
                   '          "acceptance_criteria": []\n'
                   '        }\n'
                   '      ]\n'
                   '    }\n'
                   '  ]\n'
                   '}',
    'actors': ['Moderator', 'Estimator'],
    'highLevelGoals': [   'Set up a planning poker game',
                          'Run an estimation round',
                          'Manage past games',
                          'Manage account',
                          'Participate in estimation sessions'],
    'lowLevelGoals': [   'Create a new game',
                         'Invite estimators to a game',
                         'Add an item for estimation',
                         'Edit an item for estimation',
                         'Delete an item from estimation',
                         'View all items to be estimated in the session',
                         'Select an item for estimation',
                         'Show estimates before all estimators have voted',
                         'Accept the average estimate',
                         'Enter the agreed-upon estimate',
                         'Re-estimate a previously estimated story',
                         'Import stories from a spreadsheet',
                         'Copy and paste stories from a spreadsheet',
                         'Browse previous games',
                         'View a game transcript',
                         'Export a game transcript as HTML',
                         'Export a game transcript as CSV',
                         'Delete a game',
                         'Create an account',
                         'Log in to an account',
                         'Change account details',
                         'Delete an account',
                         'Request a password reminder by email',
                         'Select an estimation scale',
                         'Join a game',
                         'View the item being estimated',
                         'View who gave each estimate',
                         'View which estimators have already given an estimate',
                         'View prior estimates for the current story',
                         'Change an estimate before all cards are revealed',
                         'Start a countdown timer',
                         'Reset the countdown timer after an estimation round',
                         'View stories and estimates from previous rounds']}

SIA_PROJECT_RECYCLING = {   'name': 'Recycling',
    'description': 'The software project will develop a user-friendly '
                   'web application that allows users to discover and manage recycling facilities. '
                   'Key features include searching for nearby centers by zip code, viewing '
                   'operational hours, accessing maps of recycling locations, and receiving '
                   'notifications about events. Administrators will manage facility information '
                   'and user feedback, ensuring data security while enabling communication between '
                   'facility representatives and site admins to improve community recycling '
                   'efforts.",\n'
                   '  "epics": [\n'
                   '    {\n'
                   '      "title": "Manage User Accounts and Preferences",\n'
                   '      "description": "This epic encompasses features related to user account '
                   'creation, customization, and personal preferences. It aims to provide users '
                   'with control over their profiles and ensure they receive relevant '
                   'notifications and a personalized experience.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Create an Account",\n'
                   '          "story": "As a user, I want to be able to create an account, so that '
                   'I can create my own profile.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Add Favorites",\n'
                   '          "story": "As a user, I want to add donation centers as favorites on '
                   'my profile, so that I can view them later.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Link Email to Profile",\n'
                   '          "story": "As a user, I want to link my email account to my profile, '
                   'so that I can get a temporary password in case I forget my own one.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Receive Notifications",\n'
                   '          "story": "As a user, I want to be able to give my email ID, so that '
                   'I can receive notifications for new events as they are posted.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Secure Personal Information",\n'
                   '          "story": "As a user, I want to have my personal information kept '
                   'securely in the database of the website, so that I will not suffer from '
                   'identity theft or telephone harassment.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Receive Rewards",\n'
                   '          "story": "As a user, I want to be able to receive tempting rewards, '
                   'so that I have a reason to use the website.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "View User Documentation",\n'
                   '          "story": "As a user, I want to view user documentation for the '
                   'website, so that I know how to use the web app.",\n'
                   '          "acceptance_criteria": []\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Discover and Navigate Recycling Facilities",\n'
                   '      "description": "This epic provides users with the ability to find and '
                   'navigate recycling facilities and public recycling options. It aims to improve '
                   'accessibility to recycling centers and public bins through maps and convenient '
                   'location-based searches.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Search Recycling Facilities by Zip Code",\n'
                   '          "story": "As a user, I want to be able to enter my zip code and get '
                   'a list of nearby recycling facilities, so that I can determine which ones I '
                   'should consider.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "View Recycling Centers on a Map",\n'
                   '          "story": "As a user, I want to view all locations of recycling '
                   'centers on a map, so that I can check which routes to take to drop off '
                   'waste.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "View Public Recycling Bins",\n'
                   '          "story": "As a user, I want to be able to view a map display of the '
                   'public recycling bins around my area.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "View Special Waste Drop-off Sites",\n'
                   '          "story": "As a user, I want to be able to view a map display of the '
                   'special waste drop-off sites around my area.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "View Safe Disposal Events",\n'
                   '          "story": "As a user, I want to be able to view the safe disposal '
                   'events currently being organized around my area.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Click on Address to Open Google Maps",\n'
                   '          "story": "As a user, I want to click on the address, so that it '
                   'takes me to a new tab with Google Maps.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Browse Environment-friendly Facilities",\n'
                   '          "story": "As a user, I want to be able to browse through the list of '
                   'facilities and see which ones are environment-friendly, so that I can know for '
                   'sure my waste is not going to leave a negative ecological footprint.",\n'
                   '          "acceptance_criteria": []\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Schedule and Optimize Recycling Visits",\n'
                   '      "description": "This epic is focused on enabling users to schedule and '
                   'optimize their visits to recycling centers. It aims to provide flexibility and '
                   'convenience for users to match their availability with facility hours and '
                   'reduce planning complexity.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Flexible Pickup Time",\n'
                   '          "story": "As a user, I want to have a flexible pick-up time, so that '
                   'I can more conveniently use the website.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Choose Flexible Pickup Time",\n'
                   '          "story": "As a user, I want to choose a flexible pick-up time, so '
                   'that I can more conveniently use the website.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Get Recommendations Based on Weekly Schedule",\n'
                   '          "story": "As a user, I want to upload my week\'s schedule, so that I '
                   'can get recommendations for recycling centers that best fit my '
                   'availability.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Select Different Types of Recyclable Waste",\n'
                   '          "story": "As a user, I want to be able to select different types of '
                   'recyclable waste, so that I have and get a list of facilities that accept each '
                   'type and their opening hours, so that I can find an optimal route and '
                   'schedule.",\n'
                   '          "acceptance_criteria": []\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Administer Recycling Facility Information",\n'
                   '      "description": "This epic allows admins and superusers to manage '
                   'recycling facility information on the platform, ensuring users receive '
                   'accurate and up-to-date information about available services.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Add or Remove Facility Information",\n'
                   '          "story": "As an admin, I want to be able to add or remove recycling '
                   'facilities\' information, so that users get the most recent information.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Onboard Recycling Centers",\n'
                   '          "story": "As an admin, I want to onboard recycling centers on the '
                   'platform, so that I can increase information accuracy.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Update Facility Information",\n'
                   '          "story": "As an admin, I want to add recycling center information, '
                   'so that I can keep the database up-to-date over time.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Superuser Updates Information",\n'
                   '          "story": "As a superuser, I want to update the recycling center '
                   'information, so that I can provide the latest information about the recycling '
                   'center.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Facility Representative Updates Information",\n'
                   '          "story": "As a recycling facility representative, I want to be able '
                   'to update my information and the type of material I accept, so that I can '
                   'avoid any miscommunication with users.",\n'
                   '          "acceptance_criteria": []\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Provide User Support and Engage with Users",\n'
                   '      "description": "This epic provides users and admins with communication '
                   'channels to report issues, give feedback, and respond to queries, fostering '
                   'interaction and improving support for users.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Contact Administrators",\n'
                   '          "story": "As a user, I want to contact the administrators, so that I '
                   'can give feedback or ask for help.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Read Feedback and Complaints",\n'
                   '          "story": "As an admin, I want to be able to read users\' feedback '
                   'and complaints, so that we can add more features and keep improving the '
                   'service we provide to them.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Reply to User Questions",\n'
                   '          "story": "As a superuser, I want to reply to user questions, so that '
                   'I can answer any questions about my recycling center.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Communicate with Facilities",\n'
                   '          "story": "As an admin, I want to be able to communicate directly '
                   'with facilities, so that I can keep them updated about features we have on our '
                   'website.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Facility to Admin Communication",\n'
                   '          "story": "As a recycling facility, I want to be able to communicate '
                   'directly with the site admin and convey any issues or concerns I have, so that '
                   'they fix them.",\n'
                   '          "acceptance_criteria": []\n'
                   '        }\n'
                   '      ]\n'
                   '    },\n'
                   '    {\n'
                   '      "title": "Ensure a Smooth and Reliable User Experience",\n'
                   '      "description": "This epic addresses the usability and responsiveness of '
                   'the system, including providing real-time feedback, accessibility, and '
                   'ensuring a positive user experience.",\n'
                   '      "user_stories": [\n'
                   '        {\n'
                   '          "title": "Invalid Zip Code Feedback",\n'
                   '          "story": "As a user, I want to get feedback when I enter an invalid '
                   'zip code.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Access Site on All Devices",\n'
                   '          "story": "As a user, I want to be able to access the site and do all '
                   'the other stuff on all of my electronic devices.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Great UI and UX",\n'
                   '          "story": "As a user, I want to have a great UI and UX from the '
                   'sites, so that I have a pleasant experience when navigating through them.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "Easy Website Navigation",\n'
                   '          "story": "As a company, I want to have a website that is easy to '
                   'use, so that I can upload or delete stuff step by step.",\n'
                   '          "acceptance_criteria": []\n'
                   '        },\n'
                   '        {\n'
                   '          "title": "UI/UX Lessons for Developers",\n'
                   '          "story": "As a developer, I want to attend some UI/UX lessons, so '
                   'that I can develop an awesome and beautiful features website.",\n'
                   '          "acceptance_criteria": []\n'
                   '        }\n'
                   '      ]\n'
                   '    }\n'
                   '  ]\n'
                   '}',
    'actors': ['User', 'Admin', 'Superuser', 'Recycling Facility Representative'],
    'highLevelGoals': [   'Manage user accounts and preferences',
                          'Discover and navigate recycling facilities',
                          'Schedule and optimize recycling visits',
                          'Administer recycling facility information',
                          'Handle user feedback and communication'],
    'lowLevelGoals': [   'Create a user account',
                         'Add recycling facilities to favorites',
                         'Link an email account to a profile',
                         'Subscribe to notifications about new events',
                         'View user documentation',
                         'Search recycling facilities by zip code',
                         'View recycling centers on a map',
                         'View public recycling bins',
                         'View special waste drop-off sites',
                         'View safe disposal events',
                         'Open a facility address in Google Maps',
                         'Browse environment-friendly recycling facilities',
                         'Choose a flexible pickup time',
                         'Get recycling center recommendations based on a weekly schedule',
                         'Filter recycling facilities by type of recyclable waste',
                         'Add recycling facility information',
                         'Remove recycling facility information',
                         'Onboard recycling centers on the platform',
                         'Update recycling facility information',
                         'Update facility information and accepted material types',
                         'Contact administrators',
                         'Read user feedback and complaints',
                         'Reply to user questions',
                         'Communicate directly with recycling facilities',
                         'Communicate directly with the site admin']}

# Canonical dataset registry shared by the execution and evaluation notebooks.
_REQUIRED_GROUNDTRUTH_FIELDS = {
    "name",
    "description",
    "actors",
    "highLevelGoals",
    "lowLevelGoals",
}


def _discover_groundtruths(namespace):
    projects = []
    for variable_name, value in namespace.items():
        if not variable_name.startswith("SIA_PROJECT_"):
            continue
        if not isinstance(value, dict):
            raise TypeError(f"{variable_name} must be a dictionary")

        missing_fields = _REQUIRED_GROUNDTRUTH_FIELDS - value.keys()
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"{variable_name} is missing fields: {missing}")
        projects.append(value)

    if not projects:
        raise RuntimeError("No SIA_PROJECT_* ground truths were found")

    names = [project["name"] for project in projects]
    duplicate_names = sorted({name for name in names if names.count(name) > 1})
    if duplicate_names:
        raise ValueError(
            "Ground-truth project names must be unique: "
            + ", ".join(duplicate_names)
        )

    return projects


ALL_GROUNDTRUTHS = _discover_groundtruths(globals())

GROUNDTRUTH_BY_NAME = {
    groundtruth["name"]: groundtruth
    for groundtruth in ALL_GROUNDTRUTHS
}
