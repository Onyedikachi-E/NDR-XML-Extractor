from datetime import date

class FacilityData:
    def __init__(self):
        self.facility_name:str = ""
        self.datim_code:str = ""
        self.facility_type_code:str = "FAC"
        self.partner_reporting_lga_code = ""
        self.partner_reporting_state = ""

class PatientDemographics:
    def __init__(self):
        self.patient_identifier:str = ""
        self.treatement_facility:FacilityData = FacilityData


class OtherIdentifiers:
    def __init__(self):
        self.id_number:str = ""
        self.id_type_code:str = ""

class PatientProfile:
    def __init__(self):
        self.patient_date_of_birth:date = date
        self.patient_sex_code:str = ""
        self.patient_deceased_indicator:str = ""
        self.patient_education_level:str = ""
        self.occupation_code:str = ""
        self.patient_marital_status_code:str = ""

class FingerPrints:
    def __init__(self):
        self.date_captured:date = date
        self.finger_position:str = ""
        self.image_quality:str = ""
        self.template:str = ""
        self.new_template = ""

class ConditionQuestions:
    def __init__(self):
        self.condition_code:str = "86406008"
        self.program_area_code:str = "HIV"
        self.patient_address_type_code:str = "H"
        self.patient_lga_code:str = ""
        self.patient_state_code:str = ""
        self.patient_country_code:str = "NGA"

class CommonQuestions:
    def __init__(self):
        self.hospital_number = ""
        self.patient_age = ""
        self.date_of_first_report = ""
        self.date_of_last_report = ""
        self.diagonosis_date = ""
        self.patient_age = ""

class ConditionSpecificQuestions:
    def __init__(self):
        self.care_entry_point:str = ""
        self.first_confrimed_hiv_test_date:date = date
        self.first_hiv_test_mode = ""
        self.first_art_regimen_code = ""
        self.first_art_regimen_code_desc_text = ""
        self.patient_art_start_date = ""
        self.who_clinical_stage_art_start = ""
        self.weight_art_start = ""
        self.child_height_art_start = ""
        self.functional_status_art_start = ""
        self.enrolled_hiv_care_date = ""

class HivEncountersReport:
    def __init__(self):
        self.visit_id = ""
        self.visit_Date = ""
        self.duration_on_art = ""
        self.patient_weight = ""
        self.child_height = ""
        self.blood_pressure = ""
        self.edd_pmtct_link = ""
        self.family_planing_code = ""
        self.functional_status = ""
        self.who_clinical_stage = ""
        self.tb_status = ""
        self.art_regimen_code = ""
        self.art_regimen_code_desc_text = ""
        self.prescribed_regimen_indicator = ""
        self.substitution_indicator = ""
        self.switch_indicator = ""
        self.next_appointment_date = ""
        self.stopped_regimen = ""

class LaboratoryReport:
    def __init__(self):
        self.visit_id = ""
        self.visit_date = ""
        self.laboratory_test_identifier = ""
        self.collection_date = ""
        self.lab_test_type_code = ""
        self.lab_ordered_test_date = ""
        self.lab_result_test_code = "80"
        self.lab_result_test_code_desc_txt = "HIV VIRAL LOAD"
        self.lab_result_answer_numeric = ""
        self.lab_result_test_date = ""
        self.reported_by = ""
        self.checked_by = ""

class RegimenReport:
    def __init__(self):
        self.visit_id = ""
        self.visit_date = ""
        self.prescribed_regimen_code = ""
        self.prescribed_code_desc_txt = ""
        self.prescribed_regimen_type_code = "ART"
        self.prescribed_line_code = ""
        self.prescribed_regimen_duration = ""
        self.prescribed_dispense_date = ""
        self.date_regimen_started = ""
        self.date_regimen_started_dd = ""
        self.date_regimen_started_mm = ""
        self.date_regimen_started_yy = ""
        self.date_regimen_ended = ""
        self.date_regimen_ended_dd = ""
        self.date_regimen_ended_mm = ""
        self.date_regimen_ended_yyy = ""
        self.diffrentiated_service_delivery = ""
        self.dispensing = ""
        self.multi_month_dispensing = ""

class MortalityReport:
    def __init__(self):
        self.client_verification = ""
        self.visit_id = ""
        self.visit_date = ""
        self.reason_for_tracking = ""
        self.date_patient_contacted = ""
        self.mode_of_communication = ""
        self.person_contacted = ""
        self.reason_for_defaulting = ""
        self.other_reason_for_defaulting = ""
        self.discontinued = ""
        self.date_of_termination = ""
        self.reason_for_termination = ""
        self.name_of_contact_tracer = ""
        self.contact_tracker_signature_date = ""
    