import re
import pymongo
import pandas as pd
import config as cfg
from pymongo.errors import ConfigurationError, PyMongoError

class DBQueryHandler:
    """
    A class that handles database queries for talent metrics.

    Attributes:
        client: A MongoClient object representing the MongoDB client.
        db: A MongoDB database object representing the talent metrics database.

    Methods:
        __init__(): Initializes the DBQueryHandler object and connects to the MongoDB client.
        get_bonus_table(prediction_result, table_name): Retrieves a bonus table based on prediction results.
        get_benefits_table(prediction_result, table_name): Retrieves a benefits table based on prediction results.
        get_jobentries_dict(results): Static method that converts query results to a job entries dictionary.
        get_jobentries_table(prediction_result, table_name): Retrieves a job entries table based on prediction results.
        close_connection(): Closes the MongoDB client connection.
    """

    def __init__(self):
        """
        Initializes the DBQueryHandler object and connects to the MongoDB client.
        """
        try:

            self.client = pymongo.MongoClient(cfg.MONGODB_URL)
            self.db = self.client[cfg.DB_NAME]

        except AttributeError:
            print("The 'db' attribute is missing or not properly initialized.")
        except ConfigurationError as e:
            # Handle the exception gracefully
            print(f"ConfigurationError: Database connection failed due to configuration error. Please retry it again")
        except PyMongoError as e:
            # Handle the connection-related error
            print(f"PyMongoError: {e}")


    @staticmethod
    def extract_value(value):
        # Check if the salary amount has a "K" suffix and extract the numeric part
        value_extracted = re.search(r'(\d+(\.\d+)?)K', value, re.IGNORECASE)
        if value_extracted:
            value = float(value_extracted.group(1)) * 1000
        else:
            # If no "K" suffix, use the regular expression to extract the numeric part
            value_extracted = re.search(r'\d+(\.\d+)?', value)
            value = int(value_extracted.group()) if '.' in value_extracted.group() else int(value_extracted.group())
        return value



    @staticmethod
    def get_clients_dict(results):
        """
        Converts query results to a job entries dictionary.

        Args:
            results: The query results from the database.

        Returns:
            A dictionary representing the job entries.
        """
        clients_dict = {
            "Client_Name": [],
            "Client_Location": [],
            "Client_Type": [],
            "Currency": [],
        }
        for result in results:
            clients_dict["Client_Name"].append(result["name"])
            clients_dict["Client_Location"].append(result["location"]["name"])
            clients_dict["Client_Type"].append(result["clienttype"]["name"])
            clients_dict["Currency"].append(result["currency"]["code"])
        return clients_dict


    def get_clients_table(self, prediction_result, table_name):
        """
        Retrieves a bonus table based on prediction results.
        Args:
            prediction_result: A dictionary containing prediction results.
            table_name: A string representing the name of the collection/table to query.

        Returns:
            A pandas DataFrame representing the bonus table.
        """
        query = {}
        exact_match = {}
        flag_not_found = {}
        table = self.db[table_name]
        for key in ["LOCATION", "LOCATION_GROUP", "CLIENT_TYPE", "CURRENCY", "CLIENT_NAME"]:
            if key in prediction_result:
                value = prediction_result[key]
                escaped_value = re.escape(value)
                pattern = "^" + escaped_value.replace("/", "/\\s*") + "$"
                pattern = re.compile(pattern, re.IGNORECASE)
                if key == "CLIENT_NAME":
                    query_key = "name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "CURRENCY":
                    query_key = "currency.code"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "CLIENT_TYPE":
                    query_key = "clienttype.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "LOCATION":
                    query_key = "location.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value
                
                elif key == "LOCATION_GROUP":
                    query_key = "location.locationgroup.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

        client_results = table.find(query)
        clients_dict = DBQueryHandler.get_clients_dict(client_results)
        df = pd.DataFrame(clients_dict)
        return df, exact_match, flag_not_found
    
    @staticmethod
    def get_jobtitles_dict(results):
        """
        Converts query results to a job titles dictionary.

        Args:
            results: The query results from the database.

        Returns:
            A dictionary representing the job titles.
        """
        jobtitles_dict = {
        "Client_Name": [],
        "Client_Job_Title": [],
        "Our_Job_Title": [],
        "Client_Location": [],
        "Date": []
        }
        for result in results:
            jobtitles_dict["Client_Name"].append(result["client"]["name"])
            jobtitles_dict["Client_Job_Title"].append(result["job_title"])
            jobtitles_dict["Our_Job_Title"].append(result["jobgrade"]["name"])
            jobtitles_dict["Client_Location"].append(result["location"]["name"])
            jobtitles_dict["Date"].append(result["date"].date())
        return jobtitles_dict
    

    def get_jobtitles_table(self, prediction_result, table_name):

        query = {}
        exact_match = {}
        flag_not_found = {}
        table = self.db[table_name]
        for key in ["LOCATION", "LOCATION_GROUP", "CLIENT_NAME", "JOB_TITLE"]:
            if key in prediction_result:
                value = prediction_result[key]
                escaped_value = re.escape(value)
                pattern = "^" + escaped_value.replace("/", "/\\s*") + "$"
                pattern = re.compile(pattern, re.IGNORECASE)
                if key == "CLIENT_NAME":
                    query_key = "client.name"
                    count = table.count_documents({query_key : pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "JOB_TITLE":
                    query_key = "job_title"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "LOCATION":
                    query_key = "location.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value
                
                elif key == "LOCATION_GROUP":
                    query_key = "location.locationgroup.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value


        job_results = table.find(query)
        jobtitles_dict = DBQueryHandler.get_jobtitles_dict(job_results)
        df = pd.DataFrame(jobtitles_dict)
        return df, exact_match, flag_not_found


    @staticmethod
    def get_bonus_dict(results):
        """
        Converts query results to a job entries dictionary.

        Args:
            results: The query results from the database.

        Returns:
            A dictionary representing the job entries.
        """
        salarybonus_dict = {
            "Client_Name": [],
            "Our_Job_Title": [],
            "Client_Location": [],
            "Currency": [],
            "Paid_Bonus": [],
            "Date": [],
        }
        for result in results:
            salarybonus_dict["Client_Name"].append(result["client"]["name"])
            salarybonus_dict["Our_Job_Title"].append(result["jobgrade"]["name"])
            salarybonus_dict["Client_Location"].append(result["location"]["name"])
            salarybonus_dict["Currency"].append(result["currency"]["code"])
            salarybonus_dict["Paid_Bonus"].append(result["paidbonus_percentage"])
            salarybonus_dict["Date"].append(result["date"].date())
        return salarybonus_dict


    def get_bonus_table(self, prediction_result, table_name):
        """
        Retrieves a bonus table based on prediction results.
        Args:
            prediction_result: A dictionary containing prediction results.
            table_name: A string representing the name of the collection/table to query.

        Returns:
            A pandas DataFrame representing the bonus table.
        """
        query = {}
        exact_match = {}
        flag_not_found = {}
        table = self.db[table_name]
        for key in ["CLIENT_NAME", "LOCATION", "LOCATION_GROUP", "JOB_TITLE", 
                    "CURRENCY", "BONUS_PERCENT", "AMOUNT_FROM", "AMOUNT_TO"]:
            if key in prediction_result:
                value = prediction_result[key]
                escaped_value = re.escape(value)
                pattern = "^" + escaped_value.replace("/", "/\\s*") + "$"
                pattern = re.compile(pattern, re.IGNORECASE)
                if key == "BONUS_PERCENT":
                    bonus_value = prediction_result["BONUS_PERCENT"]
                    bonus_value = DBQueryHandler.extract_value(bonus_value)
                    query_key = "paidbonus_percentage"
                    bonus_value = str(bonus_value)
                    count = table.count_documents({query_key: bonus_value})
                    print(count)
                    if count > 0:
                        query[query_key] = bonus_value
                        exact_match[key] = bonus_value
                    else:
                        print(bonus_value)
                        flag_not_found[key] = bonus_value

                elif key == "CLIENT_NAME":
                    query_key = "client.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "JOB_TITLE":
                    query_key = "jobgrade.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "LOCATION":
                    query_key = "location.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "LOCATION_GROUP":
                    query_key = "location.locationgroup.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "CURRENCY":
                    query_key = "currency.code"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == 'AMOUNT_FROM':
                    bonus_from = prediction_result['AMOUNT_FROM']
                    bonus_from = DBQueryHandler.extract_value(bonus_from)
                    query_key = "paidbonus_percentage"
                    count = table.count_documents({query_key: {'$gte': bonus_from}})
                    if count > 0:
                        query[query_key] = {'$gte': bonus_from}
                        exact_match["BONUS_PERCENT"] = bonus_from
                    else:
                        flag_not_found["BONUS_PERCENT"] = bonus_from

                elif 'AMOUNT_TO' in prediction_result:
                    bonus_to = prediction_result['AMOUNT_TO']
                    bonus_to = DBQueryHandler.extract_value(bonus_to)
                    query_key = "paidbonus_percentage"
                    count = table.count_documents({query_key: {'$lte': bonus_to}})
                    if count > 0:
                        query[query_key] = {'$lte': bonus_to}
                        exact_match["BONUS_PERCENT"] = bonus_to
                    else:
                        flag_not_found["BONUS_PERCENT"] = bonus_to


        if "MAX_MONEY_ATTRIBUTES" in prediction_result:
            results = table.find(query).sort("paidbonus_percentage", -1).limit(1)
        elif "MIN_MONEY_ATTRIBUTES" in prediction_result:
            results = table.find(query).sort("paidbonus_percentage", 1).limit(1)
        else:
            results = table.find(query)
        salarybonus_dict = DBQueryHandler.get_bonus_dict(results)
        df = pd.DataFrame(salarybonus_dict)
        return df, exact_match, flag_not_found

    
    @staticmethod
    def get_benefits_dict(results):
        """
        Converts query results to a job entries dictionary.

        Args:
            results: The query results from the database.

        Returns:
            A dictionary representing the job entries.
        """
        benefits_dict = {
            "Benefit_Name": [],
            "Client_Location": [],
            "Client_Name": [],
            "Our_Job_Title": [],
            "Value": [],
            "Currency": [],
            "Date": [],
        }

        for result in results:
            benefits_dict["Benefit_Name"].append(result["name"])
            benefits_dict["Client_Location"].append(result["location"]["name"])
            benefits_dict["Client_Name"].append(result["client"]["name"])
            benefits_dict["Our_Job_Title"].append(result["jobgrade"]["name"])
            benefits_dict["Value"].append(result["value"])
            benefits_dict["Currency"].append(result["currency"]["code"])
            benefits_dict["Date"].append(result["date"].date())
        return benefits_dict


    def get_benefits_table(self, prediction_result, table_name):
        """
        Retrieves a benefits table based on prediction results.

        Args:
            prediction_result: A dictionary containing prediction results.
            table_name: A string representing the name of the collection/table to query.

        Returns:
            A pandas DataFrame representing the benefits table.
        """
        query = {}
        exact_match = {}
        flag_not_found = {}
        table = self.db[table_name]
        for key in ["CLIENT_NAME", "LOCATION", "LOCATION_GROUP", "JOB_TITLE",
                    "CURRENCY", "BENEFITS_NAME", "BENEFITS_AMOUNT", "AMOUNT_FROM", 
                    "AMOUNT_TO"]:
            if key in prediction_result:
                value = prediction_result[key]
                escaped_value = re.escape(value)
                pattern = "^" + escaped_value.replace("/", "/\\s*") + "$"
                pattern = re.compile(pattern, re.IGNORECASE)
                if key == "BENEFITS_NAME":
                    query_key = "name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "CLIENT_NAME":
                    query_key = "client.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "JOB_TITLE":
                    query_key = "jobgrade.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "LOCATION":
                    query_key = "location.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value
                
                elif key == "LOCATION_GROUP":
                    query_key = "location.locationgroup.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value


                elif key == "CURRENCY":
                    query_key = "currency.code"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "BENEFITS_AMOUNT":
                    query_key = "value"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value
                        
                elif key == 'AMOUNT_FROM':
                    benefits_from = prediction_result['AMOUNT_FROM']
                    benefits_from = DBQueryHandler.extract_value(benefits_from)
                    query_key = "value"
                    count = table.count_documents({query_key: {'$gte': benefits_from}})
                    if count > 0:
                        query[query_key] = {'$gte': benefits_from}
                        exact_match["BENEFITS_AMOUNT"] = benefits_from
                    else:
                        flag_not_found["BENEFITS_AMOUNT"] = benefits_from        

                elif key == 'AMOUNT_TO':
                    benefits_to = prediction_result['AMOUNT_TO']
                    benefits_to = DBQueryHandler.extract_value(benefits_to)
                    query_key = "value"
                    count = table.count_documents({query_key: {'$lte': benefits_to}})
                    if count > 0:
                        query[query_key] = {'$lte': benefits_to}
                        exact_match["BENEFITS_AMOUNT"] = benefits_to
                    else:
                        flag_not_found["BENEFITS_AMOUNT"] = benefits_to        

        if "MAX_MONEY_ATTRIBUTES" in prediction_result:
            results = table.find(query).sort("value", -1).limit(1)

        elif "MIN_MONEY_ATTRIBUTES" in prediction_result:
            results = table.find(query).sort("value", 1).limit(1)
        else:
            results = table.find(query)
        benefits_dict = DBQueryHandler.get_benefits_dict(results)
        df = pd.DataFrame(benefits_dict)
        return df, exact_match, flag_not_found

    @staticmethod
    def get_jobentries_dict(results):
        """
        Converts query results to a job entries dictionary.

        Args:
            results: The query results from the database.

        Returns:
            A dictionary representing the job entries.
        """
        jobentries_dict = {
            "Client_Name": [],
            "Our_Job_Title": [],
            "Client_Job_Title": [],
            "Candidate_Location": [],
            "Annual_Salary": [],
            "Currency": [],
            "Date": [],
        }
        for result in results:
            jobentries_dict["Client_Name"].append(result["client"])
            jobentries_dict["Our_Job_Title"].append(result["jobTitle"])
            jobentries_dict["Client_Job_Title"].append(result["jobgrade"]["name"])
            jobentries_dict["Candidate_Location"].append(result["location"]["name"])
            jobentries_dict["Annual_Salary"].append(result["salary"])
            jobentries_dict["Currency"].append(result["currency"]["code"])
            jobentries_dict["Date"].append(result["date"].date())
        return jobentries_dict


    def get_jobentries_table(self, prediction_result, table_name):
        """
        Retrieves job entries from a database table based on the provided prediction result.

        Args:
            prediction_result (dict): A dictionary containing predicted values for specific keys.
                - "LOCATION": The location value.
                - "JOB_TITLE": The job title value.
                - "CURRENCY": The currency value.
                - "CLIENT_NAME": The client name value.
            table_name (str): The name of the database table to query.

        Returns:
            pandas.DataFrame: A DataFrame containing the retrieved job entries.

        """
        query = {}
        exact_match = {}
        flag_not_found = {}
        table = self.db[table_name]
        for key in ["LOCATION", "LOCATION_GROUP", "JOB_TITLE", "CURRENCY", "CLIENT_NAME", 
                    "MAX_MONEY_ATTRIBUTES", "MIN_MONEY_ATTRIBUTES", "AMOUNT_FROM", "AMOUNT_TO",
                    "SALARY_AMOUNT"]:
            if key in prediction_result:
                value = prediction_result[key]
                escaped_value = re.escape(value)
                pattern = "^" + escaped_value.replace("/", "/\\s*") + "$"
                pattern = re.compile(pattern, re.IGNORECASE)
                if key == "CLIENT_NAME":
                    query_key = "client"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "SALARY_AMOUNT":
                    query_key = "salary"
                    salary_amount = prediction_result["SALARY_AMOUNT"]
                    salary_amount = DBQueryHandler.extract_value(salary_amount)
                    count = table.count_documents({query_key: salary_amount})
                    if count > 0:
                        query[query_key] = salary_amount
                        exact_match[key] = salary_amount
                    else:
                        flag_not_found[key] = salary_amount

                elif key == "CURRENCY":
                    query_key = "currency.code"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "JOB_TITLE":
                    query_key = "jobTitle"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "LOCATION":
                    query_key = "location.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "LOCATION_GROUP":
                    query_key = "location.locationgroup.name"
                    count = table.count_documents({query_key: pattern})
                    print(count)
                    print(pattern)
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key =='AMOUNT_FROM':
                    salary_from = prediction_result['AMOUNT_FROM']
                    salary_from = DBQueryHandler.extract_value(salary_from)
                    query_key = "salary"
                    count = table.count_documents({query_key: {"$gte" : salary_from}})
                    if count > 0:
                        query[query_key] = {'$gte': salary_from}
                        exact_match["SALARY_AMOUNT"] = salary_from
                    else:
                        flag_not_found["SALARY_AMOUNT"] = salary_from

                elif key == 'AMOUNT_TO':
                    salary_to = prediction_result['AMOUNT_TO']
                    salary_to = DBQueryHandler.extract_value(salary_to)
                    query_key = "salary"
                    count = table.count_documents({query_key: {"$lte" : salary_to}})
                    if count > 0:
                        query[query_key] = {'$lte': salary_to}
                        exact_match["SALARY_AMOUNT"] = salary_to
                    else:
                        flag_not_found["SALARY_AMOUNT"] = salary_to

        if "MAX_MONEY_ATTRIBUTES" in prediction_result:
            job_results = table.find(query).sort("salary", -1).limit(1)
        elif "MIN_MONEY_ATTRIBUTES" in prediction_result:
            job_results = table.find(query).sort("salary", 1).limit(1)
        else:
            job_results = table.find(query)
        jobentries_dict = DBQueryHandler.get_jobentries_dict(job_results)
        df = pd.DataFrame(jobentries_dict)
        return df, exact_match, flag_not_found
    
    @staticmethod
    def get_candidates_dict(results):
        candidates_dict = {
            "Client_Name": [],
            "Our_Job_Title": [],
            "Client_Job_Title": [],
            "Skill": [],
            "Client_Location": [],
            "Candidate_Location": [],
            "Salary_From": [],
            "Salary_To": [],
            "Currency": [],
            "Date": [],
        }
        for result in results:
            candidates_dict["Client_Name"].append(result["client"]["name"])
            candidates_dict["Our_Job_Title"].append(result["jobTitle"])
            candidates_dict["Client_Job_Title"].append(result["jobTitle"])
            candidates_dict["Skill"].append(result["skill_code"])
            candidates_dict["Client_Location"].append(result["location"]["name"])
            candidates_dict["Candidate_Location"].append(result["location"]["name"])
            candidates_dict["Salary_From"].append(result["salary_from"])
            candidates_dict["Salary_To"].append(result["salary_to"])
            candidates_dict["Currency"].append(result["currency"]["code"])
            candidates_dict["Date"].append(result["date"].date())
        return candidates_dict

    
    def get_candidate_payscale(self, prediction_result, table_name):
        """
        Retrieves candidate pay scale information from a database table based on the provided prediction result.

        Args:
            prediction_result (dict): A dictionary containing predicted values for specific keys.
                - 'CLIENT_NAME': The client name value.
                - 'JOB_TITLE': The job title value.
                - 'CLIENT_TYPE': The client type/skill value.
                - 'LOCATION': The location value.
                - 'SALARY_FROM': The lower limit of the salary range value.
                - 'SALARY_TO': The upper limit of the salary range value.
                - 'CURRENCY': The currency value.
            table_name (str): The name of the database table to query.

        Returns:
            pandas.DataFrame: A DataFrame containing the retrieved candidate pay scale information.

        """
        query = {}
        exact_match = {}
        flag_not_found = {}
        table = self.db[table_name]
        for key in ['CLIENT_NAME', 'JOB_TITLE', 'SKILLS', 'LOCATION', 'LOCATION_GROUP',
                    'CURRENCY', 'MAX_MONEY_ATTRIBUTES', 'MIN_MONEY_ATTRIBUTES',
                    'AMOUNT_FROM', 'AMOUNT_TO']:
            if key in prediction_result:
                value = prediction_result[key]
                escaped_value = re.escape(value)
                pattern = "^" + escaped_value.replace("/", "/\\s*") + "$"
                pattern = re.compile(pattern, re.IGNORECASE)
                if key == 'CLIENT_NAME':
                    query_key = 'client.name'
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == 'CURRENCY':
                    query_key = 'currency.code'
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == 'JOB_TITLE':
                    query_key = 'jobTitle'
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == 'LOCATION':
                    query_key = 'location.name'
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == "LOCATION_GROUP":
                    query_key = "location.locationgroup.name"
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == 'SKILLS':
                    query_key = 'skill_code'
                    count = table.count_documents({query_key: pattern})
                    if count > 0:
                        query[query_key] = pattern
                        exact_match[key] = value
                    else:
                        flag_not_found[key] = value

                elif key == 'AMOUNT_FROM':
                    salary_from = prediction_result['SALARY_FROM']
                    salary_from = DBQueryHandler.extract_value(salary_from)
                    query_key = "salary_from"
                    count = table.count_documents({query_key: {"$gte" : salary_from}})
                    if count > 0:
                        query[query_key] = {'$gte': salary_from}
                        exact_match["SALARY_FROM"] = salary_from
                    else:
                        flag_not_found["SALARY_FROM"] = salary_from

                elif key == 'AMOUNT_TO':
                    salary_to = prediction_result['SALARY_TO']
                    salary_to = DBQueryHandler.extract_value(salary_to)
                    query_key = 'salary_to'
                    count = table.count_documents({query_key: {"$lte" : salary_to}})
                    if count > 0:
                        query[query_key] = {'$lte': salary_to}
                        exact_match["SALARY_TO"] = salary_to
                    else:
                        flag_not_found["SALARY_TO"] = salary_to

        if "MAX_MONEY_ATTRIBUTES" in prediction_result:
            job_results = table.find(query).sort("salary_to", -1).limit(1)
        elif "MIN_MONEY_ATTRIBUTES" in prediction_result:
            job_results = table.find(query).sort("salary_to", 1).limit(1)
        else:
            job_results = table.find(query)

        candidates_dict = DBQueryHandler.get_candidates_dict(job_results)
        df = pd.DataFrame(candidates_dict)
        return df, exact_match, flag_not_found
    
    def get_recommendation_df(self, faiss_index_ids):

        table_name = "jobsearch_vectordb"
        table = self.db[table_name]
        query = {"faiss_index_id": {"$in": faiss_index_ids}}
        matching_documents = list(table.find(query))
        df = pd.DataFrame(matching_documents)
        return df
  

    def close_connection(self):
        """
        Closes the MongoDB client connection.
        """
        self.client.close()
