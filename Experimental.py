import json
from DataStructures import Study
import sys
import logging

logger = logging.getLogger("Phenotype Finder")


def load_study(directory, file_name):
    study = None
    json_text_data = None
    json_table_data = None
    pmc_id = None
    try:
        with open(F"{directory}/full_text/{file_name}", 'r', encoding="utf-8") as file:
            json_text_data = json.load(file)
    except IOError as io:
        logger.error(F"IO Error: {io}")
        return None
    except Exception as e:
        logger.error(
            F"An error occurred attempting to read publication file {file_name}:\n {e}")
        return None
    if json_text_data:
        pmc_id = file_name[3:-14]
        try:
            with open(F"{directory}/tables/PMC{pmc_id}_tables.json", 'r', encoding="utf-8") as file:
                json_table_data = json.load(file)
        except IOError as io:
            logger.error(F"IO Error: {io}")
            return None
        except Exception as e:
            logger.error(F"An error occurred attempting to read publication table file PMC{pmc_id}_tables.json:\n {e}")
            return None
    study = Study(json_text_data, json_table_data)
    study.pmid = pmc_id
    return study