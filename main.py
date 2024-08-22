from model import xml_model
from repositories import xml_repo
from datetime import datetime, date
from typing import Optional
from database.database import connect_to_database
import zipfile, os, shutil


def remove_empty_tags_with_xpath(tree):
    # Locate all elements that are empty (no text, no children)
    empty_elements = tree.xpath("//*[not(node())]")

    # Iterate over the empty elements and remove them
    for element in empty_elements:
        parent = element.getparent()
        if parent is not None:
            parent.remove(element)





def main():

    start_date = "2022-05-10" #input('Enter Start Date("%Y-%m-%d"): ')
    end_date = datetime.now().strftime("%Y-%m-%d")

    # Connection String to the Database
    connection = connect_to_database()

    xml_conatainer = []
    list_of_pepfar_ids = ["ABI00305239"]
    for pepfar_id in list_of_pepfar_ids:
    
        xml_data = []

        facility_data = xml_repo.get_facility_data(connection=connection)

        patient_demographics_data = xml_repo.get_patient_demographics(connection=connection, facility_data=facility_data, pepfar_id=pepfar_id)

        other_identifiers_data = xml_repo.get_other_identifiers(connection=connection, pepfar_id=pepfar_id)

        patient_profile_data = xml_repo.get_patient_profile(connection=connection, pepfar_id=pepfar_id)

        finger_prints_data = xml_repo.get_finger_print_data(connection=connection, pepfar_id=pepfar_id)

        condition_question = xml_repo.get_condition_question(connection=connection, pepfar_id=pepfar_id)

        common_question_data = xml_repo.get_common_question(connection=connection, pepfar_id=pepfar_id)

        condition_specific_questions = xml_repo.get_condition_specific_question(connection=connection, pepfar_id=pepfar_id)

        hiv_encounters = xml_repo.get_hiv_encounters(connection=connection, pepfar_id=pepfar_id, start_date=start_date, end_date=end_date)





        # Mapping all the pulled data in a list for form the xml data
        xml_data.append((facility_data, patient_demographics_data, other_identifiers_data, patient_profile_data, finger_prints_data, condition_question, common_question_data, condition_specific_questions, hiv_encounters))

        # Intializing the XML Tree Class
        xml_generator = xml_model.XmlTree()

        # Build the XML Block mapping the objects in defined tags
        validated_xml_data = xml_generator.build_xml_block(xml_data=xml_data)
        xml_conatainer.append(validated_xml_data)


    # Exporting the XMLs from the xml_conatainer list to the desginated folder
    for xmls_info in xml_conatainer:
        xml_generator.export_xml_block(xmls_info=xmls_info)

    
    # Zip the XML folder for upload to NDR
    xml_zip_filepath = "_".join([f'{xmls_info.get("state")}{xmls_info.get("lga_code")}', xmls_info.get("datim_code"), datetime.now().strftime("%d%m%y%H%M%S")])
    with zipfile.ZipFile(f"export_folder/{xml_zip_filepath}.zip", "w") as zipf:
        xml_folder = f"export_folder/{datetime.now().date().strftime('%d-%m-%Y')}"
        
        # Generate xml dictionary tree for the main xml parent folder
        xml_paths = os.walk(xml_folder)
        for main_path, dir, xml_files in xml_paths:

            # split the main directory to access the xml files
            root, temp_folder = os.path.split(main_path)

            # Changing the folder path to pick the xml files from the temp folder
            os.chdir(root)

            # Zipping all the xml files in the temp folder
            [zipf.write(os.path.join(temp_folder, xml_file)) for xml_file in xml_files]
            
            # Removing the temp xml folder path
            shutil.rmtree(temp_folder)

if __name__ == "__main__":
    main()

