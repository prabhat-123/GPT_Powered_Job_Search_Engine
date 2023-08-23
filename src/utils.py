import os
import itertools
import pandas as pd
import config as cfg

def store_queries(query, ner_response):
    """
    Store a query in a text file.

    Args:
        query (str): The query to store.

    Returns:
        None

    """
    work_dir = os.getcwd()
    path_to_history = os.path.join(os.path.dirname(work_dir), 'history')
    if not os.path.exists(path_to_history):
        os.mkdir(path_to_history)
    file = open(os.path.join(path_to_history, 'query.txt'), "a")
    file.write(query)
    file.write("->")
    file.write(str(ner_response))
    file.write("\n")
    file.close()

def process_date_column(df):

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date', ascending=False)
    df['Date'] = df['Date'].dt.strftime("%d-%m-%Y")
    return df


def apply_filter_conditions(df, filter_conditions, column_map_dict):
    """
    Apply filter conditions to a DataFrame based on the provided filter conditions and column mappings.

    Args:
        df (pandas.DataFrame): The DataFrame to filter.
        filter_conditions (dict): A dictionary containing the filter conditions.
            The keys represent the filter keys, and the values represent the filter values.
        column_map_dict (dict): A dictionary mapping filter keys to column names in the DataFrame.

    Returns:
        pandas.DataFrame: The filtered DataFrame.

    """
    filter_mask = pd.Series(True, index=df.index)
    for filter_key, filter_value in filter_conditions.items():
        column = column_map_dict.get(filter_key) 
        if column is not None:
            if filter_value.isdigit():  # Check if filter_value contains a numeric value
                filter_value = int(filter_value)  # Convert filter_value to integer
            else:
                filter_value = filter_value.lower()
            filter_mask &= df[column].astype('str').str.lower() == str(filter_value)
    filtered_df = df[filter_mask]
    return filtered_df

def process_query(ner_response, query_handler):

    table_name = ""
    df = None
    exact_match = {}
    flag_not_found = {}
    if "SALARY" in ner_response.keys() or "SALARY_AMOUNT" in ner_response.keys():
        table_name = "jobentries"
        df, exact_match, flag_not_found = query_handler.get_jobentries_table(ner_response, table_name)
    elif "SALARY_RANGE" in ner_response.keys():
        table_name = "candidates"
        df, exact_match, flag_not_found = query_handler.get_candidate_payscale(ner_response, table_name)
    elif "BONUS" in ner_response.keys() or "BONUS_PERCENT" in ner_response.keys():
        table_name = "salarybonus"
        df, exact_match, flag_not_found = query_handler.get_bonus_table(ner_response, table_name)
    elif "BENEFITS" in ner_response.keys() or "BENEFITS_NAME" in ner_response.keys():
        table_name = "benefits"
        df, exact_match, flag_not_found = query_handler.get_benefits_table(ner_response, table_name)
    else:
        if "JOB" in ner_response.keys() or "JOB_TITLE" in ner_response.keys():
            table_name = "jobtitles"
            df, exact_match, flag_not_found = query_handler.get_jobtitles_table(ner_response, table_name)
        else:
            table_name = "clients"
            df, exact_match, flag_not_found = query_handler.get_clients_table(ner_response, table_name)
    return df, exact_match, flag_not_found, table_name


def respond_query(ner_response, search_recommender, query_handler):
    """
    Process the query based on the ner_response and perform database operations using the provided query_handler
    and search recommendations using the search_recommender.

    Args:
        query (str): The original query string.
        ner_response (dict): The NER response containing extracted entities.
        search_recommender (SearchRecommender): An instance of the SearchRecommender class.
        query_handler (DBQueryHandler): An instance of the DBQueryHandler class.

    Returns:
      result (json/string): The result of the query processing, either as a JSON-formatted string or an error message.

    """
    query = ner_response["query"]
    if len(ner_response) > 1:
        df, exact_match, flag_not_found, table_name = process_query(ner_response, query_handler)
        if len(flag_not_found) > 0:
            recommended_ids = search_recommender.recommend_faiss_index(query)
            recommended_df = query_handler.get_recommendation_df(recommended_ids)
            recommended_df = apply_filter_conditions(df=recommended_df, filter_conditions=exact_match, column_map_dict=cfg.column_map_dict[table_name])
            if recommended_df is not None:
                query_handler.close_connection()
                if 'Date' in recommended_df.columns:
                    recommended_df = process_date_column(recommended_df)
                recommended_df = recommended_df[cfg.table_views[table_name]]
                flag_not_found = {cfg.column_map_dict[table_name][key]: value for key, value in flag_not_found.items() if key in cfg.column_map_dict[table_name]}
                questions = {"recommendations": []}
                other_options = {}
                for flag_key in flag_not_found.keys():
                    options = list(recommended_df[flag_key].unique())
                    if flag_key == "Annual_Salary":
                        if "SALARY_AMOUNT" in ner_response:
                            other_options[ner_response["SALARY_AMOUNT"]] = options
                        elif "SALARY_FROM" in ner_response:
                            other_options[ner_response["SALARY_FROM"]] = options
                        elif "SALARY_TO" in ner_response:
                            other_options[ner_response["SALARY_TO"]] = options
                    # elif flag_key == "LOCATION_GROUP":
                    #     other_options[ner_response["SALARY_AMOUNT"]]
                    else:
                        other_options[flag_not_found[flag_key]] = options
                keys = other_options.keys()
                for combo in itertools.product(*[other_options[key] for key in keys]):
                    updated_query = query
                    for key, value in zip(keys, combo):
                        updated_query = updated_query.replace(str(key), str(value))
                    questions['recommendations'].append(updated_query)
                
                final_df = pd.DataFrame(questions)
                return final_df.to_json(orient='records')

            else:
                return {"error": "Recommendation Not Working"}
        else:
            if len(df)!=0:
                query_handler.close_connection()
                if 'Date' in df.columns: 
                    df = process_date_column(df)
                return df.to_json(orient="records")
            else:
                recommended_ids = search_recommender.recommend_faiss_index(query)
                recommended_df = query_handler.get_recommendation_df(recommended_ids)
                recommended_df = recommended_df[cfg.table_views[table_name]]
                if 'Date' in recommended_df.columns:
                    recommended_df = process_date_column(recommended_df)
                query_handler.close_connection()
                exact_match = {cfg.column_map_dict[table_name][key]: value for key, value in exact_match.items() if key in cfg.column_map_dict[table_name]}
                questions = {"recommendations": []}
                other_options = {}
                for flag_key in exact_match.keys():
                    options = list(recommended_df[flag_key].unique())
                    other_options[exact_match[flag_key]] = options
                keys = other_options.keys()
                for combo in itertools.product(*[other_options[key] for key in keys]):
                    updated_query = query
                    for key, value in zip(keys, combo):
                        updated_query = updated_query.replace(str(key), str(value))
                    questions['recommendations'].append(updated_query)
                final_df = pd.DataFrame(questions)
                return final_df.to_json(orient='records')
    else:
        output = {"results": ["No entities found"]}
        final_df = pd.DataFrame(output)
        return final_df.to_json(orient='records')


