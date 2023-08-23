import os
from dotenv import load_dotenv

current_dir = os.getcwd()
load_dotenv()
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
MONGODB_URL = "mongodb+srv://{}:{}@cluster0.npmuj.mongodb.net/talentmatrics?retryWrites=true&w=majority&connectTimeoutMS=60000".format(MONGODB_USERNAME, MONGODB_PASSWORD)
OPENAI_API_PATH = os.path.join(os.path.dirname(current_dir), "fm_api_key.txt")
VECTOR_DB_PATH = os.path.join(os.path.dirname(current_dir), "data", "vector_db_jobsearch.csv")
MODEL_NAME = "all-mpnet-base-v2"
FAISS_INDEX_PATH = os.path.join(os.path.dirname(current_dir), "models", "faiss_index.bin")


table_views = {"clients": ["Client_Name", "Client_Location", "Client_Type", "Currency"],
               "jobtitles": ['Client_Name', 'Client_Job_Title', 'Our_Job_Title', 'Client_Location', 'Date'],
               "jobentries": ['Client_Name', 'Our_Job_Title', 'Client_Location', 'Currency', 'Annual_Salary', 'Date'],
               "candidates": ['Client_Name', 'Our_Job_Title', 'Client_Job_Title', 'Skill', 'Client_Location', 
                              'Candidate_Location', 'Salary_From', 'Salary_To', 'Currency', 'Date'],
               "benefits": ['Benefit_Name', 'Client_Location', 'Client_Name', 'Our_Job_Title', 'Value', 'Currency', 'Date'],
               "salarybonus": ['Client_Name', 'Our_Job_Title', 'Client_Location', 'Currency', 'Paid_Bonus', 'Date']
               }


column_map_dict = {
    "clients": {
        "CLIENT_NAME": "Client_Name",
        "LOCATION": "Client_Location",
        "LOCATION_GROUP": "Client_Location",
        "CLIENT_TYPE": "Client_Type",
        "CURRENCY": "Currency"
    },
    "jobtitles": {
        "JOB_TITLE": "Our_Job_Title",
        "LOCATION": "Client_Location",
        "LOCATION_GROUP": "Client_Location",
        "CLIENT_NAME": "Client_Name",
        "DATE": "Date"
    },
    "jobentries": {
        "CLIENT_NAME": "Client_Name",
        "JOB_TITLE": "Our_Job_Title",
        "LOCATION": "Client_Location",
        "LOCATION_GROUP": "Client_Location",
        "CURRENCY": "Currency",
        "SALARY": "Salary",
        "AMOUNT_FROM": "Annual_Salary",
        "AMOUNT_TO": "Annual_Salary",
        "SALARY_AMOUNT": "Annual_Salary"
    },
    "candidates": {
        "CLIENT_NAME": "Client_Name",
        "JOB_TITLE": "Our_Job_Title",
        "SKILLS": "Skill",
        "LOCATION": "Client_Location",
        "LOCATION_GROUP": "Client_Location",
        "AMOUNT_FROM": "Salary_From",
        "AMOUNT_TO": "Salary_To",
        "SALARY_RANGE": "Salary_Range",
        "CURRENCY": "Currency"
    },
    "benefits": {
        "BENEFITS_NAME": "Benefit_Name",
        "LOCATION": "Client_Location",
        "LOCATION_GROUP": "Client_Location",
        "JOB_TITLE": "Our_Job_Title",
        "CURRENCY": "Currency",
        "BENEFITS_AMOUNT": "Value"
    },
    "salarybonus": {
        "CLIENT_NAME": "Client_Name",
        "JOB_TITLE": "Our_Job_Title",
        "LOCATION": "Client_Location",
        "LOCATION_GROUP": "Client_Location",
        "CURRENCY": "Currency",
        "BONUS_PERCENT": "Paid_Bonus"
    }
}




clients = {"CLIENT_NAME":"Client_Name",
           "LOCATION": "Client_Location",
           "CLIENT_TYPE":"Client_Type",
           "CURRENCY": "Currency"}

jobtitles= {"JOB_TITLE": "Our_Job_Title", 
            "LOCATION": "Client_Location",
            "CLIENT_NAME": "Client_Name",
            "DATE": "Date"
            }

jobentries= {
    "CLIENT_NAME": "Client_Name",
    "JOB_TITLE": "Our_Job_Title",
    "LOCATION": "Client_Location",
    "CURRENCY": "Currency",
    "AMOUNT_FROM": "Annual_Salary",
    "AMOUNT_TO": "Annual_Salary"
}

candidates = {"CLIENT_NAME": "Client_Name",
              "JOB_TITLE": "Our_Job_Title",
              "SKILLS": "Skill",
              "LOCATION": "Client_Location",
              "AMOUNT_FROM": "Salary_From",
              "AMOUNT_TO": "Salary_To",
              "CURRENCY": "Currency",
            }

benefits = {"BENEFITS_NAME": "Benefit_Name",
            "LOCATION": "Client_Location",
            "JOB_TITLE": "Our_Job_Title",
            "CURRENCY": "Currency",
            "BENEFITS_AMOUNT": "Value"}

salarybonus = {"CLIENT_NAME": "Client_Name",
               "JOB_TITLE": "Our_Job_Title",
               "LOCATION": "Client_Location",
               "CURRENCY": "Currency",
               "BONUS_PERCENT": "Paid_Bonus"
               }

