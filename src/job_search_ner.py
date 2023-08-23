import json
import openai
import config as cfg
from json import JSONDecodeError



class NamedEntityExtractor:

    openai.api_key = open(cfg.OPENAI_API_PATH, "r").read().strip('\n')
    def __init__(self):
        self.model_name = "gpt-4"
        self.role = "user"

    def filter_json(self, text):
        start_pos = text.find("{")
        end_pos = text.rfind("}") + 1
        json_string = text[start_pos:end_pos]
        return json_string

    def extract_named_entities(self, query):
        self.query = query
        completion = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[
                {"role": self.role,
                "content": f"""You are a NER Extraction Bot and you will also extract entities which are similar to the given entities. 
                ### Named entities to extract:

                JOB: Keywords similar to the words jobs, jobtitle, jobtitles, job titles, vacancies, job vacancies, opportunities, job listings, employment opportunities, employments mentioned in the query
                JOB_TITLE: The job title or position mentioned in the query.
                LOCATION: The specific location mentioned in the query. It include cities, places, or countries.
                LOCATION_GROUP: It should be any one of these location groups: ['uk', 'europe', 'middle east', 'apac', 'north america', 'india', 'central america', 'south america', 'south korea', 'asean', 'nordics', 'africa']
                CLIENT_TYPE: The category that represents the type or industry of the client company. It indicates the specific field or sector in which the company operates.
                It can have only these set of categories: 'Financial Advisory', 'Technology/IT', 'Operations', 'Other', 'Boutique', 'MBB', 'Tier 1', 'Big 4', 'Industry Client',
                'Office', 'Strategy', 'Tier 2', 'Sales', 'HR Consulting', 'Tier 3']
                SKILLS: It represents the skills or qualification required or associated with the relevant job position or industry
                CURRENCY: The currency mentioned in the query.
                SALARY: Keywords similar to the words salary, compensation, remuneration in the query. It cannot include the amount or number.
                SALARY_AMOUNT: Exact amount associated with the salary, compensation, remuneration in the query. If exact salary is mentioned then use SALARY_AMOUNT.
                If 'greater than' or 'less than' keywords are used in a query do not extract that amount as SALARY_AMOUNT.
                SALARY_RANGE: Keywords similar to the words salary range, payscale, or pay range, remuneration range in the query. It cannot include numbers.
                AMOUNT_TO: The upper limit of the salary range, benefits amount or bonus mentioned in the query. It include only numeric values. But sometimes it can also contain string like 50K, 80k, 70,000 and so on.
                AMOUNT_FROM: The lower limit of the salary range, benefits amount or bonus mentioned in the query. It include only numeric values. But sometimes it can also contain string like 50K, 80k, 70,000 and so on.
                MAX_MONEY_ATTRIBUTES: Extract the keywords related to the highest salary, highest bonus percent, highest benefit amount and so on. (Only superlative attributes/adjectives included)
                MIN_MONEY_ATTRIBUTES: Extract the keywords related to the lowest salary, lowest bonus percent, lowest benefits value and so on. (Only superlative attributes/adjectives included)
                BENEFITS: Keyword related to Benefits like benefits, benefit
                BENEFITS_NAME: Name of Benefits that are offered to the employees by the company like car, equity options, health insurance and so on mentioned in the query.
                BENEFITS_AMOUNT: The monetary value associated with the benefits like health insurance value of 20000, dental insurance worth 15000 and so on.
                BONUS: Keyword related to Bonus like Bonus, Bonuses
                BONUS_PERCENT: Percentage of bonus offered to the employees by the company in the query.
                CLIENT: Keywords related to clients, companies, organizations, or institutions mentioned in the query.
                CLIENT_NAME: Actual names of clients, companies, organizations, or institutions mentioned in the query (e.g., Google, Microsoft, Amazon, Fusemachines, etc.).
                
                Example: 
                Text_1: "I am lookiiing for a job for Daaata Analyst located in Kathmandu."
                Output: "JOB_TITLE": "Data Analyst", "LOCATION": "Kathmandu", "query": "I am lookiiing for a job for Daaata Analyst located in Kathmandu."

                Text_2: "What is the saaalarrry of ML Engineer in USD?"
                Output: "JOB_TITLE": "ML Engineer", "SALARY": "salary", "CURRENCY": "USD", "query": "What is the salary of ML Engineer in USD?"

                Text_3: "Show me the list of companiiees in Technology sector in USA"
                Output: "CLIENT": "companies", "CLIENT_TYPE": "Technology/IT", "LOCATION":"USA", "query": "Show me the list of companies in Technology sector in USA"

                Text 4: "Looking for an Analyst roles in Finaance sector in USA"
                Output: "JOB_TITLE" : "Analyst", "SKILLS": "Finance", "LOCATION": "USA", "query": "Looking for an Analyst roles in Finance sector in USA"

                Text 5: "How much client retentionn bonus is received  for a Managerr in canadaa?"
                Output: "JOB_TITLE": "Manager", "BENEFITS_NAME": "client retention bonus", "LOCATION": "canada", "query": "How much client retention bonus is received  for a Manager in canada?"

                Text 6: "Job Titles in USA"
                Output: "JOB" : "Job Titles", "LOCATION" : "USA"

                Text 7: "Data Scientist in UK"
                Output: "JOB_TITLE" : "Data Scientist", "LOCATION" : "UK"

                These are examples on how the output should be like. They should be in a JSON Format even if no named entites are found.

                ### Input Query: "{self.query}"

                ### Instructions: 
                For the given input query, correct the spelling of the query and return the corrected query if it has a spelling mistake and then extract NER.
                Donot generate unnecessary text as an output.
                The output must be in JSON Format.(High Priority)
                Provide the extracted named entities and the corrected query in the form of a JSON response.
                Extract the named entities in the corrected query.
                Ensure that CLIENT_NAME always contains the name of the client, not the CLIENT_TYPE/SKILL.
                CLIENT refers to keywords used to denote the CLIENT_NAME, such as company, organization, or institution.
                CLIENT_NAME, JOB_TITLE, CLIENT, and CLIENT_TYPE/SKILL should not be the same in the output.
                Extract only the entities that are available in the query.
                Do not extract entites which is not found.
                Always extract SALARY, SALARY_RANGE and CLIENT entities if similar keywords for these words are present in the query.
                Donot confuse with SALARY and SALARY RANGE.

                Examples: 
                BENEFITS_NAME: ["Vacation Tour", "Paid Time Off", "Travelling Allowances", "Medical Insurance", "Free snacks", "Remote work Options",
                "Car Fuel Incentives", "Professional Development Opportunities", "On site fitness center", "Health Insurance", "client retention bonus",
                "performance bonus"]
                SKILLS categories: ['E-commerce','Gaming','Engineering','Finance','Real Estate','Recruitment','Consulting','Technology','Energy',
                'Software Development','Manufacturing','Telecommunications','Insurance','Retail','Transportation','Mining','Construction',
                'Food and Beverage','Pharmaceutical','Automotive','Fashion','Media','Logistics','Aerospace','Hospitality',
                'Travel Agencies','Healthcare', 'Investment', 'Environmental','Agriculture']
                SALARY: ["Compensation", "Income", "Earn", "earnings", "Make", "Salary", "Pay","remuneration", "payment", "wages","Stipend"]
                SALARY_RANGE: ["Compensation Range", "Income Distribution", "Earnings Distribution", "Payscale", "Stipend range", "salary brackets", "income brackets", "wages boundaries", "renumeration thresholds"]
                MAX_MONEY_ATTRIBUTES: highest, greatest, biggest, best, strongest, maximum, top
                MIN_MONEY_ATTRIBUTES: lowest, worst, least, smallest, weakest, minimum, bottom
                DONOT extract 'highest salary', 'lowest salary' as MAX_MONEY_ATTRIBUTES or MIN_MONEY_ATTRIBUTES
                """}
            ],
            max_tokens=256,
            temperature=0.05,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        response = completion['choices'][0]['message']['content']
        # Assuming you have already executed the completion and stored the result in the 'completion' variable
        tokens_used = completion['usage']['total_tokens']
        print("Total tokens used:", tokens_used)
        try:
            json_response = self.filter_json(response)
            json_response = json.loads(json_response)
            # Extract keys with non-None values
            final_json_response = {key: value for key, value in json_response.items() if value is not None and value != ""}
            print(final_json_response)
            return final_json_response
        except JSONDecodeError as e:
            return {"query": self.query}


