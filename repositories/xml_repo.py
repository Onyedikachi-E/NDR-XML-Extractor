from model import data_model
from typing import List, Optional
from datetime import datetime, date
import mysql.connector as sql



def get_facility_data(connection:sql.MySQLConnection) -> data_model.FacilityData:

     # Creating Cursor instance of MySQLConnection
    cursor = connection.cursor(dictionary=True)

    query_facility_datim_code = "SELECT property_value FROM global_property where property IN (%s, %s, %s, %s)"
    cursor.execute(query_facility_datim_code, ("facility_datim_code", "Facility_Name", "partner_reporting_lga_code", "partner_reporting_state"))
    global_property = cursor.fetchall()

    # Unpacking the list of global properties
    facility_datim_code, facility_name, partner_reporting_lga_code, partner_reporting_state = global_property

    # Creating an instance of the FacilityData class
    facility_data = data_model.FacilityData()
    facility_data.datim_code = facility_datim_code["property_value"]
    facility_data.facility_name = facility_name["property_value"]
    facility_data.partner_reporting_lga_code = partner_reporting_lga_code["property_value"]
    facility_data.partner_reporting_state = partner_reporting_state["property_value"]


    return facility_data


def get_patient_demographics(connection:sql.MySQLConnection, facility_data:data_model.FacilityData, pepfar_id:str) -> data_model.PatientDemographics:
    
    # Creating Cursor instance of MySQLConnection
    cursor = connection.cursor(dictionary=True)

    query = "SELECT identifier from patient_identifier WHERE identifier IN (%s) and identifier_type = 4 and voided = 0 LIMIT 1"
    cursor.execute(query, (pepfar_id,))

    for row in cursor:
        # Creating an instance of the PatientDemographics class
        patient_data = data_model.PatientDemographics()
        patient_data.patient_identifier = row["identifier"]
        patient_data.treatement_facility.datim_code = facility_data.datim_code
        patient_data.treatement_facility.facility_name = facility_data.facility_name
        patient_data.treatement_facility.facility_type_code = facility_data.facility_type_code

        return patient_data


def format_code(id_number:int) -> str:
    "To format the data element to NDR identifier code"
    mapper = {
        0:"false", 1:"true", 
        3:"EID", 4:"TB", 5:"HN", 8:"CT", 
        1107:"1", 1713:"2", 1714:"3", 160292:"6", 5622:"3", #Education Level
        123801:"UNE", 1540:"EMP", 159465:"STU", 159461:"RET", 1175:"NA", 1067:"UNK", #Occupation
        1059:"W", 1057:"S", 5555:"M", 1058:"D", 1056:"A",  #Maritas Status
        164949:"HIVAb", #Mode of HIV Test
        160545:"4", #Care Entry Point
        1204:"1", #WHO Stage
        159468:"W", #Functional Status
        165681:"1m", #Adult 1st line ARV regimen
        164506:"TDF-3TC-DTG" #Current Regimen Line
    }
    code = mapper.get(id_number)

    return code
    

def get_other_identifiers(connection:sql.MySQLConnection, pepfar_id:str) -> List[data_model.OtherIdentifiers]:

    list_of_identifers = []

    # Creating Cursor instance of MySQLConnection
    cursor = connection.cursor(dictionary=True)

    query = """SELECT DISTINCT identifier, identifier_type FROM patient_identifier WHERE patient_id IN (
                        SELECT DISTINCT patient_id FROM patient_identifier WHERE identifier = %s)"""
    cursor.execute(query, (pepfar_id,))
    rows = cursor.fetchall()

    for row in rows:
        other_identifiers = data_model.OtherIdentifiers()
        other_identifiers.id_number = row["identifier"]
        other_identifiers.id_type_code = format_code(row["identifier_type"])

        list_of_identifers.append(other_identifiers)

    return list_of_identifers


def get_patient_profile(connection:sql.MySQLConnection, pepfar_id:str) -> data_model.PatientProfile:

    # Creating Cursor instance of MySQLConnection
    cursor = connection.cursor(dictionary=True)

    query = """SELECT p.birthdate, p.gender, p.dead, o.concept_id, o.value_coded FROM person p 
                    INNER JOIN obs o on o.person_id = p.person_id and o.voided = 0 and concept_id in (1712, 1542, 1054) WHERE p.person_id IN (
                        SELECT DISTINCT patient_id FROM patient_identifier where identifier = %s and identifier_type = 4 and voided = 0) and p.voided = 0 """
    cursor.execute(query, (pepfar_id,))
    patient_profile = cursor.fetchall()

    profile = data_model.PatientProfile()
    profile.patient_date_of_birth = patient_profile[0].get("birthdate").strftime("%Y-%m-%d")
    profile.patient_sex_code = patient_profile[0].get("gender")
    profile.patient_deceased_indicator = format_code(patient_profile[0].get("dead"))
    profile.patient_education_level = [format_code(profile_tat.get("value_coded")) for profile_tat in patient_profile if profile_tat.get("concept_id") == 1712]
    profile.occupation_code = [format_code(profile_code.get("value_coded")) for profile_code in patient_profile if profile_code.get("concept_id") == 1542]  
    profile.patient_marital_status_code = [format_code(profile_tat.get("value_coded")) for profile_tat in patient_profile if profile_tat.get("concept_id") == 1054]

    # Restructure the profile object to form a dictionary
    profile_mapper = {
        "patient_date_of_birth":profile.patient_date_of_birth,
        "patient_sex_code":profile.patient_sex_code,
        "patient_deceased_indicator":profile.patient_deceased_indicator,
        "patient_education_level":profile.patient_education_level[0],
        "occupation_code":profile.occupation_code[0],
        "patient_marital_status_code":profile.patient_marital_status_code[0]
    }

    return profile_mapper


def get_finger_print_data(connection:sql.MySQLConnection, pepfar_id:str) -> dict[str, list]:
    
    right_hand = []
    left_hand = []

    # Creating Cursor instance of MySQLConnection
    cursor = connection.cursor(dictionary=True)

    query = """SELECT template, CONVERT(new_template USING utf8) AS new_template, fingerPosition, imageQuality, date_created FROM biometricinfo 
                         WHERE patient_id IN (SELECT DISTINCT patient_id FROM patient_identifier 
                                         WHERE identifier = %s AND identifier_type = 4 AND voided = 0)"""
    cursor.execute(query, (pepfar_id,))
    finger_prints_records = cursor.fetchall()

    # Map the query result in an instance of the class
    for row in finger_prints_records:
        if row is not None:
            finger_print_data = data_model.FingerPrints()
            finger_print_data.template = row["template"]
            finger_print_data.new_template = row["new_template"]
            finger_print_data.finger_position = row["fingerPosition"]
            finger_print_data.image_quality = str(row["imageQuality"])
            finger_print_data.date_captured = row["date_created"].strftime("%Y-%m-%d")

            # Append right fingers
            if finger_print_data.finger_position[: 4] == "Righ":
                right_hand.append(finger_print_data)
                continue

            # Append left fingers
            if finger_print_data.finger_position[: 4] == "Left":
                left_hand.append(finger_print_data)
                continue
        else:
            return None

    # Map the grouped fingers in a dictionary 
    finger_prints_group = {"right_hand":right_hand, "left_hand":left_hand}
    return finger_prints_group


def get_condition_question(connection:sql.MySQLConnection, pepfar_id:str) -> data_model.ConditionQuestions:

    # Creating Cursor instance of MySQLConnection
    cursor = connection.cursor(dictionary=True)

    query = """ SELECT distinct lga_code, state_code FROM owaza_db.nigeria_datimcode_mapping WHERE lga_name in (
                        SELECT city_village FROM person_address WHERE person_id in (
                            SELECT distinct patient_id FROM patient_identifier WHERE identifier = %s and identifier_type = 4))"""
    cursor.execute(query, (pepfar_id, ))
    row = cursor.fetchone()

    if row is not None:
        condition_question_data = data_model.ConditionQuestions()
        condition_question_data.patient_lga_code = str(row["lga_code"])
        condition_question_data.patient_state_code = str(row["state_code"])

    return condition_question_data


def get_common_question(connection:sql.MySQLConnection, pepfar_id:str) -> data_model.CommonQuestions:

    cursor = connection.cursor(dictionary=True)

    query = """SELECT pi.identifier AS hospital_number, p.birthdate as birthdate, o.concept_id, o.value_datetime AS first_report, 
                (SELECT MAX(obs_datetime) FROM obs WHERE person_id = o.person_id AND voided = 0) AS last_report FROM obs o
                    INNER JOIN patient_identifier pi ON pi.patient_id = o.person_id AND pi.voided = 0 AND o.voided = 0 AND pi.identifier_type = 5 
                        INNER JOIN person p on p.person_id = o.person_id AND p.voided = 0
                            WHERE o.concept_id = 160554 AND o.person_id IN (SELECT DISTINCT patient_id FROM patient_identifier 
                                WHERE identifier = %s AND identifier_type = 4);"""

    cursor.execute(query, (pepfar_id,))
    row = cursor.fetchone()

    if row is not None:
        common_question_data = data_model.CommonQuestions()
        common_question_data.hospital_number = row["hospital_number"]
        common_question_data.date_of_first_report = row["first_report"].strftime("%Y-%m-%d")
        common_question_data.date_of_last_report = row["last_report"].strftime("%Y-%m-%d")
        common_question_data.diagonosis_date = row["first_report"].strftime("%Y-%m-%d")
        common_question_data.patient_age = ((datetime.now().year) - (row["birthdate"].year))

    return common_question_data
        

def get_condition_specific_question(connection:sql.MySQLConnection, pepfar_id:str) -> data_model.ConditionSpecificQuestions:

    cursor = connection.cursor(dictionary=True)

    query = """SELECT obs_datetime, concept_id, value_coded, value_numeric, value_datetime FROM obs WHERE person_id IN (
                    SELECT DISTINCT patient_id FROM patient_identifier WHERE identifier = %s) AND concept_id IN (
                            164947, 160540, 160554, 159599, 5356, 165582, 165581, 165039, 1342, 165708, 164506) AND voided = 0
                                AND encounter_id in (SELECT encounter_id FROM encounter WHERE form_id IN (23, 56) AND voided = 0)"""
    
    cursor.execute(query, (pepfar_id,))
    condition_specific_question = cursor.fetchall()

    # Create an instance of the class
    if condition_specific_question is not None:
        condition_specific_question_data = data_model.ConditionSpecificQuestions()
        condition_specific_question_data.care_entry_point = [format_code(specific_question.get("value_coded")) for specific_question in condition_specific_question if specific_question.get("concept_id") == 160540]
        condition_specific_question_data.first_hiv_test_mode = [format_code(specific_question.get("value_coded")) for specific_question in condition_specific_question if specific_question.get("concept_id") == 164947]
        condition_specific_question_data.first_art_regimen_code = [format_code(specific_question.get("value_coded")) for specific_question in condition_specific_question if specific_question.get("concept_id") == 164506]
        condition_specific_question_data.first_art_regimen_code_desc_text = [format_code(specific_question.get("value_coded")) for specific_question in condition_specific_question if specific_question.get("concept_id") == 165708]
        condition_specific_question_data.who_clinical_stage_art_start = [format_code(specific_question.get("value_coded")) for specific_question in condition_specific_question if specific_question.get("concept_id") == 5356]
        condition_specific_question_data.functional_status_art_start = [format_code(specific_question.get("value_coded")) for specific_question in condition_specific_question if specific_question.get("concept_id") == 165039]
        condition_specific_question_data.weight_art_start = [specific_question.get("value_numeric") for specific_question in condition_specific_question if specific_question.get("concept_id") == 165582]
        condition_specific_question_data.child_height_art_start = [specific_question.get("value_numeric") for specific_question in condition_specific_question if specific_question.get("concept_id") == 165581]
        condition_specific_question_data.first_confrimed_hiv_test_date = [specific_question.get("value_datetime").strftime("%Y-%m-%d") for specific_question in condition_specific_question if specific_question.get("concept_id") == 160554]
        condition_specific_question_data.patient_art_start_date = [specific_question.get("value_datetime").strftime("%Y-%m-%d") for specific_question in condition_specific_question if specific_question.get("concept_id") == 159599]
        condition_specific_question_data.enrolled_hiv_care_date = condition_specific_question[0].get("obs_datetime").strftime("%Y-%m-%d")

    # Restructure the profile object to form a dictionary
    condition_specific_question_mapper = {
        "care_entry_point":condition_specific_question_data.care_entry_point[0],
        "first_hiv_test_mode":condition_specific_question_data.first_hiv_test_mode[0],
        "first_art_regimen_code":condition_specific_question_data.first_art_regimen_code[0],
        "first_art_regimen_code_desc_text":condition_specific_question_data.first_art_regimen_code_desc_text[0],
        "who_clinical_stage_art_start":condition_specific_question_data.who_clinical_stage_art_start[0],
        "functional_status_art_start":condition_specific_question_data.functional_status_art_start[0],
        "weight_art_start":int(condition_specific_question_data.weight_art_start[0]),
        "child_height_art_start":int(condition_specific_question_data.child_height_art_start[0]),
        "first_confrimed_hiv_test_date":condition_specific_question_data.first_confrimed_hiv_test_date[0],
        "patient_art_start_date":condition_specific_question_data.patient_art_start_date[0],
        "enrolled_hiv_care_date":condition_specific_question_data.enrolled_hiv_care_date
    }

    return condition_specific_question_mapper
   

def get_hiv_encounters(connection:sql.MySQLConnection, pepfar_id:str, start_date, end_date):
    
    cursor = connection.cursor(dictionary=True)

    # To retrieve all the encounter IDs based on specified date
    query = """SELECT encounter_id FROM encounter WHERE form_id = 14 AND patient_id IN (
                    SELECT DISTINCT patient_id from patient_identifier WHERE identifier = %s and identifier_type = 4) AND voided = 0
                        AND date_created between %s AND %s"""

    cursor.execute(query, (pepfar_id, start_date, end_date,))

    # Retrieve all the encounters with form id of 14 (Care Card)
    encounter_ids = cursor.fetchall()

    # Form a list of all encounter ids
    encounter_id_list = [encounter_id.get("encounter_id") for encounter_id in encounter_ids]

    # Form a list of Encounter Objects
    encounter_object_list = []
    for encounter_no in  encounter_id_list:
        # Query the OBS to retrieve all data element for each encounter_id
        query = """SELECT obs_datetime, concept_id, value_coded, value_datetime, value_numeric 
                        FROM obs WHERE encounter_id = %s AND person_id IN (
                            SELECT DISTINCT patient_id FROM patient_identifier WHERE identifier = %s and identifier_type = 4) AND voided = 0"""

        cursor.execute(query, (encounter_no, pepfar_id,))
        encounters = cursor.fetchall()

        if encounters is not None:
            hiv_encounter_data = data_model.HivEncountersReport()
            hiv_encounter_data.visit_id = ""
            hiv_encounter_data.visit_date = ""
            hiv_encounter_data.duration_on_art = ""
            hiv_encounter_data.patient_weight = ""
            hiv_encounter_data.child_height = ""
            hiv_encounter_data.blood_pressure = ""
            hiv_encounter_data.edd_pmtct_link = ""
            hiv_encounter_data.family_planing_code = ""
            hiv_encounter_data.functional_status = ""
            hiv_encounter_data.who_clinical_stage = ""
            hiv_encounter_data.tb_status = ""
            hiv_encounter_data.art_regimen_code = ""
            hiv_encounter_data.art_regimen_code_desc_text = ""
            hiv_encounter_data.prescribed_regimen_indicator = ""
            hiv_encounter_data.substitution_indicator = ""
            hiv_encounter_data.next_appointment_date = ""
            hiv_encounter_data.stopped_regimen = ""

        # Restructure the HIV Encounter object to form a dictionary
        hiv_encounter_mapper = {
            "visit_id":hiv_encounter_data.visit_id[0],
            "visit_date":hiv_encounter_data.visit_date[0],
            "duration_on_art":hiv_encounter_data.duration_on_art[0],
            "patient_weight":hiv_encounter_data.patient_weight[0],
            "child_height":hiv_encounter_data.child_height[0],
            "blood_pressure":hiv_encounter_data.blood_pressure[0],
            "edd_pmtct_link":hiv_encounter_data.edd_pmtct_link[0],
            "family_planing_code":hiv_encounter_data.family_planing_code[0],
            "functional_status":hiv_encounter_data.functional_status[0],
            "who_clinical_stage":hiv_encounter_data.who_clinical_stage[0],
            "tb_status":hiv_encounter_data.tb_status[0],
            "art_regimen_code":hiv_encounter_data.art_regimen_code[0],
            "art_regimen_code_desc_text":hiv_encounter_data.art_regimen_code_desc_text[0],
            "prescribed_regimen_indicator":hiv_encounter_data.prescribed_regimen_indicator[0],
            "substitution_indicator":hiv_encounter_data.substitution_indicator[0],
            "next_appointment_date":hiv_encounter_data.next_appointment_date[0],
            "stopped_regimen":hiv_encounter_data.stopped_regimen[0]
        }

        encounter_object_list.append(hiv_encounter_mapper)

    return encounter_object_list


def get_laboratory_report(connection:sql.MySQLConnection, pepfar_id:str, start_date:date, end_date:date):
    
    cursor = connection.cursor(dictionary=True)


def get_regimen_report(connection:sql.MySQLConnection, pepfar_id:str, start_date:date, end_date:date):
    
    cursor = connection.cursor(dictionary=True)


def get_mortality_report(connection:sql.MySQLConnection, pepfar_id:str, start_date:date, end_date:date):
    
    cursor = connection.cursor(dictionary=True)