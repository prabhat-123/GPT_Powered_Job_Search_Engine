# Job Search Engine

The Job Search Engine is a powerful tool designed to facilitate efficient job searching. This application combines Streamlit for the user interface and FastAPI as the backend API. By entering job-related queries into the user interface, users can leverage the engine's capabilities to retrieve relevant job postings.

## Project Structure

The project directory has the following structure:

```
|- TM-python-search
    |- models
        |- models-last
        |- models-best
    |- src
        |- app.py
        |- config.py
        |- dbquery_handler.py
        |- streamlit_app.py
        |- utils.py
    |- .gitignore
    |- requirements.txt
```

- The `models` directory contains the custom NER models trained on job-related queries. The `models-last` and `models-best` directories store the models at different stages.
- The `src` directory holds the source code of the application, including the FastAPI endpoint (`app.py`), configuration file (`config.py`), database query handler (`dbquery_handler.py`), Streamlit UI (`streamlit_app.py`), and utility functions (`utils.py`).
- The `.gitignore` file specifies files and directories to be ignored by version control.
- The `requirements.txt` file lists the dependencies required to run the application.



## Job Search Engine Workflow

The Job Search Engine follows a streamlined workflow to provide users with an efficient and effective job search experience. The following steps outline the workflow of the system:

1. User Interaction:
   - Users interact with the user-friendly interface created using Streamlit.
   - They input their job-related queries into the interface to search for relevant job postings.

2. Query Submission:
   - Once a query is submitted by the user, it is sent to the FastAPI endpoint at `http://127.0.0.1:8000/search` for processing.

3. Named Entity Recognition (NER) Model:
   - The FastAPI endpoint utilizes a custom NER model specifically trained for job-related queries.
   - The NER model analyzes the submitted query and extracts key information, such as job title, salary, salary range, location, and more.

4. Database Query Handler:
   - After the NER model successfully extracts the required information from the query, the results are passed on to the Database Query Handler.

5. Rule-Based Search:
   - The Database Query Handler, a rule-based module, takes the extracted information as input.
   - Using a set of predefined rules, the Query Handler performs targeted searches within the MongoDB database.
   - It efficiently resolves the query by assigning it to the appropriate table in the TalentMetrics database.

6. Database Retrieval:
   - The Query Handler retrieves the relevant information from the assigned table based on the query.
   - It fetches job postings or related data that match the user's search criteria.

7. Result Presentation:
   - The retrieved results are presented back to the user through the Streamlit user interface.
   - Users can view the job search insights, including relevant job postings, salary information, location details, and more.

This workflow ensures that users can easily interact with the Job Search Engine, receive accurate and targeted results, and make informed decisions during their job search process.

## Database

The Job Search Engine relies on a MongoDB database as its underlying data storage. The TalentMetrics database consists of six distinct tables, each serving a specific purpose in organizing and storing job-related data.


## Job Search Engine

The Job Search Engine is a powerful tool that enables users to search for relevant job postings based on their queries. This repository provides the necessary code and components to run the Job Search Engine locally. Follow the steps below to set up and use the Job Search Engine:

### Prerequisites

- Python 3.x
- Git

### Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/jranand01/TM-python-search.git
   ```

2. Navigate to the cloned directory:
   ```
   cd TM-python-search
   ```

3. Create a Python virtual environment:
   ```
   python -m venv env
   ```

4. Activate the virtual environment:
   - For Windows:
     ```
     env\Scripts\activate
     ```
   - For macOS/Linux:
     ```
     source env/bin/activate
     ```

5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Usage

1. Start the FastAPI server:
   - Navigate to the `src` directory:
     ```
     cd src
     ```

   - Run the following command to start the FastAPI server:
     ```
     uvicorn app:app --reload
     ```

   The FastAPI server will start running and listen on port 8000.

2. Open a new terminal or command prompt, navigate to the `src` directory, and activate the virtual environment.

3. Start the Streamlit UI:
   - Run the following command to launch the Streamlit user interface:
     ```
     streamlit run streamlit_app.py
     ```

   The Streamlit UI will open in your default web browser.

4. Interact with the Job Search Engine:
   - Enter job-related queries in the search bar of the Streamlit UI.
   - The queries will be sent to the FastAPI endpoint at `http://127.0.0.1:8000/search`.
   - The FastAPI endpoint will process the queries using a custom Named Entity Recognition (NER) model and perform database searches to retrieve relevant job postings.
   - The results will be displayed in the Streamlit UI, providing valuable job search insights to the users.

Now you can effectively search for job postings using the Job Search Engine. Enjoy your job search experience!

Note: Make sure to have MongoDB installed and running with the appropriate database and tables configured as mentioned in the project's documentation.
## Additional Notes

- Ensure that the custom NER models are present in the `models` directory before running the application.
- The `config.py` file can be modified to specify the database connection details, table names, etc., as needed.

