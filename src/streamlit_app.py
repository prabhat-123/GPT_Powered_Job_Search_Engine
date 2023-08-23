import json
import requests
import pandas as pd
import streamlit as st


st.set_page_config(layout="wide")

# Render the Streamlit UI
if __name__ == "__main__":
    st.write("# Job Search Engine")
    query = st.text_input("Enter your query")
    if st.button("Search"):
        response = requests.post("http://127.0.0.1:8000/search", data={"query": query})
        if response.status_code == 200:
            prediction_result = response.json()
            df = pd.DataFrame(json.loads(prediction_result))
            if len(df.columns) > 1:
                st.write("Entities found:")
            else:
                st.write("Recommended Queries")
            st.table(df)
        else:
            st.write("Error: Failed to fetch results")
