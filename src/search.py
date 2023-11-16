import json
import time
import requests
from collections import Counter
from decouple import config

search_api = "https://incubig-search.search.windows.net"

api_key = config('SEARCH_API_PUBLIC_KEY')
index=config('PRIMARY_INDEX')

params = {
    "api-version":"2021-04-30-Preview",
    "queryLanguage":"en-US",
    "speller":"lexicon",
    "queryType":"semantic",
    "semanticConfiguration":"default",
    "searchMode":"any",
    "top":10
}

def get_results(query,filter,select,search_fields,top,skip,cut_off=30):
    search_url = search_api+"/indexes/"+index+"/docs"
    params["search"]=query
    params["$select"]=select
    params["$filter"] = filter
    params["searchFields"] = search_fields
    params["skip"]=skip
    params["$top"]=top
    
    resp = requests.get(search_url,headers={"api-key":api_key},params=params)
    if resp.status_code==200 and len(resp.json()["value"])>0:
        return analyze_results(resp.json()["value"],cut_off)
    else:
        return {"count":0,"facets":{"assignee_country":[],"assignee":[],"inventors":[] ,"industry":[],"sector":[],"sub_sector": [],"main_cpc":[]} ,"trends":[],"results":[]}


def get_master_array(master_array,incoming_item):
    if type(incoming_item) is list:
        master_array+=incoming_item
    else:
        master_array.append(incoming_item)

    return master_array

def analyze_results(results_array,cut_off):
    final_results = []
    geograhies = []
    assignees = []
    inventors = []
    industries = []
    sectors = []
    sub_sectors = []
    main_cpcs = []
    publication_trends = []
    application_trends = []
    for item in results_array:
        if float(item["@search.score"]) >cut_off:
            final_results.append(item)
            if item["assignee_country"]!="NA":
                geograhies = get_master_array(geograhies,item["assignee_country"])
            assignees = get_master_array(assignees,item["assignee"])
            inventors = get_master_array(inventors,item["inventor"])
            industries = get_master_array(industries,item["industry"])
            sectors = get_master_array(sectors,item["sector"])
            sub_sectors = get_master_array(sub_sectors,item["sub_sector"])
            main_cpcs = get_master_array(main_cpcs,item["main_cpc"])
            if item["publication_year"] is not None:
                if (item["publication_year"]>2010):
                    publication_trends = get_master_array(publication_trends,item["publication_year"])
            if item["application_year"] is not None:
                if (item["application_year"]>2010):
                    application_trends = get_master_array(application_trends,item["application_year"])

    publication_trends = Counter(publication_trends)
    application_trends = Counter(application_trends)
    trends_labels = list(map(lambda x:x[0],{**dict(Counter(application_trends)),**dict(publication_trends)}.items()))
    trends_count = []
    trends_labels.sort()
    
    for item in trends_labels:
        application_count = 0
        publication_count = 0
        if item in dict(application_trends).keys():
            application_count = dict(application_trends)[item]
        if item in dict(publication_trends).keys():
            publication_count = dict(publication_trends)[item]

        trends_count.append([application_count,publication_count])

    trends = {"labels":trends_labels,"count":trends_count}

    return {"count":len(final_results),"facets":{"assignee_country":Counter(geograhies).most_common(),"assignee":Counter(assignees).most_common(),"inventors":Counter(inventors).most_common() ,"industry":Counter(industries).most_common(5),"sector":Counter(sectors).most_common(5),"sub_sector": Counter(sub_sectors).most_common(5),"main_cpc":Counter(main_cpcs).most_common(5)} ,"trends":trends,"results":final_results[0:16]}

def get_cpc(query,filter,select,search_fields,top,skip,cut_off=30):
    search_url = search_api+"/indexes/"+index+"/docs"
    params["search"]=query
    params["$select"]=select
    params["$filter"] = filter
    params["searchFields"] = search_fields
    params["skip"]=skip
    params["$top"]=top
    
    resp = requests.get(search_url,headers={"api-key":api_key},params=params)
    
    if resp.status_code==200:
        fields = select.split(',')
        
        if "main_cpc" in fields:
            cpc =[]
            for item in resp.json()["value"]:
                cpc.append(item["main_cpc"])

            cpc = Counter(cpc).most_common(5)
            
            return [x[0] for x in cpc]
        elif "industry" in fields:
            industry =[]
            for item in resp.json()["value"]:
                industry.append(item["industry"])

            industry = Counter(industry).most_common(5)
            
            return [x[0] for x in industry]
        elif "title" in fields:
            title =[]
            for item in resp.json()["value"]:
                title.append(item["title"])

            title = Counter(title).most_common(5)
            
            return [x[0] for x in title]
        else:
            return ["G06"]

    else:
        return ["G06"]
    
def get_patent(pn):
    search_url = search_api+"/indexes/"+index+"/docs"
    params["search"]=pn
    params["searchFields"] = "publication_number"
    params["$top"]=1
    
    resp = requests.get(search_url,headers={"api-key":api_key},params=params)
    if len(resp.json()["value"])>0:
        return resp.json()["value"][0]
    else:
        return {}

# print(get_patent("MjAxNDAwMjk0MTM1"))