from lxml import etree
from database.database import generate_uuid
from datetime import datetime
import os



class XmlTree:
    def __init__(self) -> None:
        pass


    def build_xml_block(self, xml_data:list) -> dict:

        # Unpacking the XML Data
        facility_data, patient_demographics_data, other_identifiers_data, patient_profile_data, finger_prints_data, condition_question, common_question_data, condition_specific_questions_data = xml_data[0]

        # Builing the XMLs Blocks with Defined Tags
        container = etree.Element("Container")
        message_header = etree.SubElement(container, "MessageHeader")
        message_status_code = etree.SubElement(message_header, "MessageStatusCode"); message_status_code.text = "UPDATED"
        message_creation_time = etree.SubElement(message_header, "MessageCreationDateTime"); message_creation_time.text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        message_schema_version = etree.SubElement(message_header, "MessageSchemaVersion"); message_schema_version.text = "1.6"
        message_unique_id = etree.SubElement(message_header, "MessageUniqueID"); message_unique_id.text = generate_uuid()
        message_sending_organization = etree.SubElement(message_header, "MessageSendingOrganization")
        facility_name = etree.SubElement(message_sending_organization, "FacilityName"); facility_name.text = facility_data.facility_name
        facility_id = etree.SubElement(message_sending_organization, "FacilityID"); facility_id.text = facility_data.datim_code
        facility_type_code = etree.SubElement(message_sending_organization, "FacilityTypeCode"); facility_type_code.text = facility_data.facility_type_code
        individual_report = etree.SubElement(container, "IndividualReport")
        patient_demographics = etree.SubElement(individual_report, "PatientDemographics")
        patient_identifier = etree.SubElement(patient_demographics, "PatientIdentifier"); patient_identifier.text = patient_demographics_data.patient_identifier
        treatment_facility = etree.SubElement(patient_demographics, "TreatmentFacility")
        patient_facility_name = etree.SubElement(treatment_facility, "FacilityName"); patient_facility_name.text = patient_demographics_data.treatement_facility.facility_name
        patient_facility_id = etree.SubElement(treatment_facility, "FacilityID"); patient_facility_id.text = patient_demographics_data.treatement_facility.datim_code
        patient_facility_type_code = etree.SubElement(treatment_facility, "FacilityTypeCode"); patient_facility_type_code.text = patient_demographics_data.treatement_facility.facility_type_code
        other_patient_identifiers = etree.SubElement(patient_demographics, "OtherPatientIdentifiers")
        for identifier_item in other_identifiers_data:
            identifier = etree.SubElement(other_patient_identifiers, "Identifier")
            id_number = etree.SubElement(identifier, "IDNumber"); id_number.text = identifier_item.id_number
            id_type_code = etree.SubElement(identifier, "IDTypeCode"); id_type_code.text = identifier_item.id_type_code
        patient_date_of_birth = etree.SubElement(patient_demographics, "PatientDateOfBirth"); patient_date_of_birth.text = patient_profile_data.get("patient_date_of_birth")
        patient_sex_code = etree.SubElement(patient_demographics, "PatientSexCode"); patient_sex_code.text = patient_profile_data.get("patient_sex_code")
        patient_deceased_indicator = etree.SubElement(patient_demographics, "PatientDeceasedIndicator"); patient_deceased_indicator.text = patient_profile_data.get("patient_deceased_indicator")
        patient_education_level = etree.SubElement(patient_demographics, "PatientEducationLevelCode"); patient_education_level.text = patient_profile_data.get("patient_education_level")
        occupation_code = etree.SubElement(patient_demographics, "PatientOccupationCode"); occupation_code.text = patient_profile_data.get("occupation_code")
        patient_marital_status_code = etree.SubElement(patient_demographics, "PatientMaritalStatusCode")
        patient_marital_status_code.text = patient_profile_data.get("patient_marital_status_code")
        finger_prints = etree.SubElement(patient_demographics, "FingerPrints")
        date_captured = etree.SubElement(finger_prints, "dateCaptured"); date_captured.text = finger_prints_data["right_hand"][0].date_captured
        right_hand = etree.SubElement(finger_prints, "rightHand")
        for right_hand_prints in finger_prints_data["right_hand"]:
            patient_prints = etree.SubElement(right_hand, f"{right_hand_prints.finger_position}"); patient_prints.text = right_hand_prints.new_template if right_hand_prints.new_template else right_hand_prints.template
            patient_prints_quality = etree.SubElement(right_hand, f"{right_hand_prints.finger_position}Quality"); patient_prints_quality.text = right_hand_prints.image_quality
        left_hand = etree.SubElement(finger_prints, "leftHand")
        for left_hands_prints in finger_prints_data["left_hand"]:
            patient_prints = etree.SubElement(left_hand, f"{left_hands_prints.finger_position}"); patient_prints.text = left_hands_prints.new_template if left_hands_prints.new_template else left_hands_prints.template
            patient_prints_quality = etree.SubElement(left_hand, f"{left_hands_prints.finger_position}Quality"); patient_prints_quality.text = left_hands_prints.image_quality
        condition = etree.SubElement(individual_report, "Condition")
        condition_code = etree.SubElement(condition, "ConditionCode"); condition_code.text = condition_question.condition_code
        program_area = etree.SubElement(condition, "ProgramArea")
        program_area_code = etree.SubElement(program_area, "ProgramAreaCode"); program_area_code.text = condition_question.program_area_code
        patient_address = etree.SubElement(condition, "PatientAddress")
        address_type_code = etree.SubElement(patient_address, "AddressTypeCode"); address_type_code.text = condition_question.patient_address_type_code
        lga_code = etree.SubElement(patient_address, "LGACode"); lga_code.text = condition_question.patient_lga_code
        state_code = etree.SubElement(patient_address, "StateCode"); state_code.text = condition_question.patient_state_code
        country_code = etree.SubElement(patient_address, "CountryCode"); country_code.text = condition_question.patient_country_code
        common_questions = etree.SubElement(condition, "CommonQuestions")
        hospital_number = etree.SubElement(common_questions, "HospitalNumber"); hospital_number.text = common_question_data.hospital_number
        date_of_first_report = etree.SubElement(common_questions, "DateOfFirstReport"); date_of_first_report.text = common_question_data.date_of_first_report
        date_of_last_report = etree.SubElement(common_questions, "DateOfLastReport"); date_of_last_report.text = common_question_data.date_of_last_report
        diagonosis_date = etree.SubElement(common_questions, "DiagnosisDate"); diagonosis_date.text = common_question_data.diagonosis_date
        patient_age = etree.SubElement(common_questions, "PatientAge"); patient_age.text = str(common_question_data.patient_age)
        condition_specific_questions = etree.SubElement(condition, "ConditionSpecificQuestions")
        hiv_questions = etree.SubElement(condition_specific_questions, "HIVQuestions")
        care_entry_point = etree.SubElement(hiv_questions, "CareEntryPoint"); care_entry_point.text = condition_specific_questions_data.get("care_entry_point")
        first_confrimed_hiv_test_date = etree.SubElement(hiv_questions, "FirstConfirmedHIVTestDate"); first_confrimed_hiv_test_date.text = condition_specific_questions_data.get("first_confrimed_hiv_test_date")
        first_hiv_test_mode = etree.SubElement(hiv_questions, "FirstHIVTestMode"); first_hiv_test_mode.text = condition_specific_questions_data.get("first_hiv_test_mode")
        first_art_regimen = etree.SubElement(hiv_questions, "FirstARTRegimen")
        regimen_code = etree.SubElement(first_art_regimen, "Code"); regimen_code.text = condition_specific_questions_data.get("first_art_regimen_code")
        regimen_code_desc_text = etree.SubElement(first_art_regimen, "CodeDescTxt"); regimen_code_desc_text.text = condition_specific_questions_data.get("first_art_regimen_code_desc_text")
        patient_art_start_date = etree.SubElement(hiv_questions, "ARTStartDate"); patient_art_start_date.text = condition_specific_questions_data.get("patient_art_start_date")
        who_clinical_stage_art_start = etree.SubElement(hiv_questions, "WHOClinicalStageARTStart"); who_clinical_stage_art_start.text = condition_specific_questions_data.get("who_clinical_stage_art_start")
        weight_art_start = etree.SubElement(hiv_questions, "WeightAtARTStart"); weight_art_start.text = str(condition_specific_questions_data.get("weight_art_start"))
        child_height_art_start = etree.SubElement(hiv_questions, "ChildHeightAtARTStart"); child_height_art_start.text = str(condition_specific_questions_data.get("child_height_art_start"))
        functional_status_art_start = etree.SubElement(hiv_questions, "FunctionalStatusStartART"); functional_status_art_start.text = condition_specific_questions_data.get("functional_status_art_start")
        enrolled_hiv_care_date = etree.SubElement(hiv_questions, "EnrolledInHIVCareDate"); enrolled_hiv_care_date.text = condition_specific_questions_data.get("enrolled_hiv_care_date")



        




        # Merge all the elements and convert it into a string
        # xml_string = ET.tostring(element=container, encoding="UTF-8", xml_declaration=True)
        xml_string = etree.tostring(element_or_tree=container, pretty_print=True, xml_declaration=True, encoding="UTF-8", standalone=True)
        
        # Create a dictionary specific for each patient
        xml_block_output = {
            "xml_string":xml_string, 
            "datim_code":facility_data.datim_code, 
            "pepfar_id":patient_identifier.text, 
            "lga_code":facility_data.partner_reporting_lga_code, 
            "state":facility_data.partner_reporting_state
        }
        return xml_block_output
    

    def export_xml_block(self, xmls_info:dict):

        # Create a folder for the XML files using today date
        xml_folder = f"{datetime.now().date().strftime('%d-%m-%Y')}"

        # Create the export folder if it does not exist
        os.makedirs(f"export_folder/{xml_folder}", exist_ok=True)


        # Form the name of the xml document using patient parameters
        xml_file_name = "_".join([f'{xmls_info.get("state")}{xmls_info.get("lga_code")}', xmls_info.get("datim_code"), xmls_info.get("pepfar_id"), datetime.now().strftime("%d%m%y")])   
        xml_output = open(f'export_folder/{xml_folder}/{xml_file_name}.xml', "w")
        
        #Export the XMLs files to the designated folder formating with standard indenation
        xml_output.write(xmls_info.get("xml_string").decode("UTF-8").replace('  ', '    '))
        xml_output.close()