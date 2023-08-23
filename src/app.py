import uvicorn
import config as cfg
from fastapi import FastAPI, Request
from dbquery_handler import DBQueryHandler
from utils import store_queries, respond_query
from faiss_search_recommender import SearchRecommender
from job_search_ner import NamedEntityExtractor

app = FastAPI()

# Expose the prediction functionality, make a prediction from the
# passed JSON data and return the similar job postings with confidence.
@app.post("/search")
async def search(request: Request):
    form_data = await request.form()
    query = form_data.get("query")
    ner_obj = NamedEntityExtractor()
    search_recommender = SearchRecommender(model_name=cfg.MODEL_NAME, faiss_index_path=cfg.FAISS_INDEX_PATH)
    ner_response = ner_obj.extract_named_entities(query)
    store_queries(query, ner_response)
    query_handler = DBQueryHandler()
    result = respond_query(ner_response, search_recommender, query_handler)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# uvicorn app:app --reload --host 0.0.0.0 --port 8000
