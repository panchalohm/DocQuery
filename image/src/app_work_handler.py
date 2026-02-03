from query_model import QueryModel
from rag_app.query_rag import query_rag


# Function that the API Lambda invokes
def handler(event, context):
    query_item = QueryModel(**event)
    invoke_rag(query_item)

# Takes query item passed into query_rag function
# After getting the response, set all the query_item 
# attributes from the response and then save it back into the DB
def invoke_rag(query_item: QueryModel):
    rag_response = query_rag(query_item.query_text)
    query_item.answer_text = rag_response.response_text
    query_item.sources = rag_response.sources
    query_item.is_complete = True
    query_item.put_item()
    print(f"Item is updated: {query_item}")
    return query_item


