"""Mongo db functions."""
from bson.objectid import ObjectId
from django.conf import settings
from pymongo import MongoClient

MONGO = None
TIMEOUT = 3000
# client = MongoClient(host=settings.DATABASES["search"]["HOST"])
# db = client[settings.DATABASES["search"]["DB_NAME"]]


def mongoconnection(dbport=27017, to=TIMEOUT):
    """Global connection handle for mongo"""
    global MONGO
    if MONGO:
        return MONGO

    MONGO = MongoClient(host=settings.DATABASES["search"]["HOST"],
                        port=settings.DATABASES["search"]['PORT'],
                        username=settings.DATABASES["search"]["USER"],
                        password=settings.DATABASES["search"]["PASSWORD"],
                        authSource="admin"
                        )

    # db = client[settings.DATABASES['search']['NAME']]
    # if dburl:
    #     MONGO = MongoClient(host=dburl, serverSelectionTimeoutMS=to)
    # else:
    #     MONGO = MongoClient(port=dbport, serverSelectionTimeoutMS=to)
    return MONGO


def mongodb():
    """Get the dbhandle for the database"""
    dbconnection = mongoconnection()
    dbname = settings.DATABASES["search"]["DB_NAME"]
    db = dbconnection[dbname]
    return db


def count_documents(
    collection, proj=None, query=None, sort=None, limit=None, skip=None
):
    """Find the documents based on the query"""
    docs = None
    db = mongodb()
    collection = db[collection] if db and collection else None
    count = 0
    if collection:
        query = {} if query is None else query

        if proj:
            results = collection.find(filter=query, projection=proj)
        else:
            results = collection.find(filter=query)

        if sort:
            results = results.sort(sort)
        if limit:
            results = results.limit(limit)
        if skip:
            results = results.skip(skip)
        count = results.count()
    return count


def find_documents(
    collection,
    proj=None,
    aggregate=None,
    query=None,
    sort=None,
    limit=None,
    skip=None,
    distinct=None,
):
    """Find the documents based on the query"""
    docs = None
    db = mongodb()
    collection = db[collection] if db and collection else None
    if collection:
        query = {} if query is None else query

        if aggregate:
            results = collection.aggregate(aggregate)
        elif distinct:
            results = collection.distinct(distinct, query)
        else:
            if proj:
                results = collection.find(filter=query, projection=proj)
            else:
                results = collection.find(filter=query)
        if sort:
            results = results.sort(sort)
        if limit:
            results = results.limit(limit)
        if skip:
            results = results.skip(skip)
        docs = [result for result in results]
    return docs


def update_one_document(doc, collection):
    """update the document into the collection."""
    db = mongodb()
    collection = db[collection] if db and collection else None
    if collection and doc:
        collection.save(doc)
        return True
    return False


def find_and_update_document(collection, query, set_value):
    """find and update single document into the collection."""
    db = mongodb()
    collection = db[collection] if db and collection else None
    if collection:
        collection.update_many(query, {"$set": set_value})
        return True
    return False


def insert_one_document(doc, collection, check_keys=True):
    """insert one document into the collection."""
    db = mongodb()
    collection = db[collection] if db and collection else None
    doc_id_str = None
    if collection:
        if check_keys:
            doc_id = collection.insert_one(doc)
        else:
            doc_id = collection.insert(doc, check_keys=False)
        doc_id_str = str(doc_id) if doc_id else None
    return doc_id_str


def delete_documents(collection, query):
    """Delete the document based on the query"""
    db = mongodb()
    collection = db[collection] if db and collection else None
    if collection:
        doc = collection.delete_many(query)
        return True
    return False
