from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
import time
import numpy as np 
import random
import pandas as pd

#import sqlite3
app = FastAPI()
app.mount("/js_code", StaticFiles(directory="js_code"), name="js_code")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize Jinja2Templates
templates = Jinja2Templates(directory="/app/template")

# SQLite connection string
SQLALCHEMY_DATABASE_URL = "sqlite:////chembl_33/chembl_33.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import sqlite3
conn = sqlite3.connect('/chembl_33/chembl_33.db')

orig_df = pd.read_csv('/chembl_33/data/test1.csv', index_col=0)
orig_df.fillna('N/A', inplace=True)
df = orig_df.sample(n=10000)

# Define a route to serve the HTML form
@app.get("/")
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

def get_ligand_cluster(pdb_id_ligands):
    if len(pdb_id_ligands) == 0:
        return -1
    sele_df = orig_df[orig_df['chembl'].isin(pdb_id_ligands)]
    chembl_labels = list(sele_df['chembl'].values)
    smis = list(sele_df['smiles'].values)
    molecule_types = list(sele_df['molecule_type'].values)
    therapeutic_flags = list(sele_df['therapeutic_flag'].values)
    chirality = list(sele_df['chirality'].values)
    first_in_class = list(sele_df['first_in_class'].values)
    withdrawn_flags = list(sele_df['withdrawn_flags'].values)
    activities = list(sele_df['activities'].values)
    tmp_x = list(sele_df['dots_x'].values)
    tmp_y = list(sele_df['dots_y'].values)
    results = {"dots_x": tmp_x, "dots_y": tmp_y,
                "properties":[[chembl_labels[idx], smis[idx], \
                molecule_types[idx], therapeutic_flags[idx], \
                chirality[idx], first_in_class[idx], \
                withdrawn_flags[idx], activities[idx]] for idx in range(len(sele_df))]}
    return results

def get_top_10_distance(chembl_ids):
    res = [[] for _ in range(10)]
    for i in range(10):
        infos = df[['chembl', 'first_in_class', 'activities', 'smiles']].iloc[i].values.tolist()
        res[i] += [infos[0]]
        res[i] += [infos[1]]
        res[i] += [infos[2]]
        res[i] += [infos[3]]
    return res

@app.post("/ligand_submit/")
async def submit_form(pdb_id: str = Form(...)):
    #'''
    # get cluster 
    pdb_id_ligands = get_data_from_db(pdb_id)
    cluster_to_notices = get_ligand_cluster(pdb_id_ligands)
    all_dots = []
    chembl_id = []
    for i in range(20):
        tmp_df = df[df['labels'] == i]  
        #mean = np.array([random.randint(-10, 10), random.randint(-10, 10)])
        #cov = np.array(([1, 0], [0, 1]))
        #dots = np.random.multivariate_normal(mean, cov, 1000) #100000
        chembl_labels = list(tmp_df['chembl'].values)
        smis = list(tmp_df['smiles'].values)
        molecule_types = list(tmp_df['molecule_type'].values)
        therapeutic_flags = list(tmp_df['therapeutic_flag'].values)
        chirality = list(tmp_df['chirality'].values)
        first_in_class = list(tmp_df['first_in_class'].values)
        withdrawn_flags = list(tmp_df['withdrawn_flags'].values)
        activities = list(tmp_df['activities'].values)
        tmp_x = list(tmp_df['dots_x'].values)
        tmp_y = list(tmp_df['dots_y'].values)
        results = {"dots_x": tmp_x, "dots_y": tmp_y,
                   "properties":[[chembl_labels[idx], smis[idx], \
                   molecule_types[idx], therapeutic_flags[idx], \
                   chirality[idx], first_in_class[idx], \
                   withdrawn_flags[idx], activities[idx]] for idx in range(len(tmp_df))]}

        #results = {"dots_x": tmp_x, "dots_y": tmp_y,
        #          "properties":[[chembl_labels[idx], smis[idx], activities[idx]] for idx in range(len(tmp_df))]}
        all_dots += [results]
    all_dots += [cluster_to_notices]
    
    #'''    
    return JSONResponse(content={"data": pdb_id, "plotly_results": all_dots, "top_10_cmpds": get_top_10_distance(10) })

@app.get("/ligand")
async def read_form(request: Request):
    return templates.TemplateResponse("ligand.html", {"request": request})

@app.get("/ligand1")
async def read_form(request: Request):
    return templates.TemplateResponse("new_index.html", {"request": request})

def get_data_from_db(pdb_id):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT
            molecule_dictionary.chembl_id
        FROM
            domains
        JOIN 
            Activities
        JOIN
            molecule_dictionary ON activities.molregno = molecule_dictionary.molregno
        JOIN
            assays ON activities.assay_id = assays.assay_id	
        JOIN
            target_dictionary ON assays.tid = target_dictionary.tid
        JOIN
            target_components ON target_components.tid = target_dictionary.tid
        JOIN	
            component_sequences ON target_components.component_id = component_sequences.component_id
        JOIN
            component_domains ON component_sequences.component_id = component_domains.component_id
        JOIN
            domains AS d1 ON d1.domain_id = component_domains.domain_id
        Join 
            compound_structures ON compound_structures.molregno = molecule_dictionary.molregno
        WHERE
            d1.domain_name = ? AND molecule_dictionary.max_phase >= 1;
        """, (pdb_id,))

        # Fetch and print results
        results = cursor.fetchall()
        res = []
        for result in results:
            res += [result[0]]
        cursor.close()
        print(res)
        return res
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


@app.get("/abc", response_class=HTMLResponse)
async def read_root(request: Request):
    db = SessionLocal()
    sql_query = text("""
        SELECT DISTINCT
            molecule_dictionary.chembl_id,
            compound_structures.canonical_smiles,
            activities.type,
            activities.value,
            activities.units,
            activities.standard_relation
        FROM
            domains
        JOIN 
            Activities
        JOIN
            molecule_dictionary ON activities.molregno = molecule_dictionary.molregno
        JOIN
            assays ON activities.assay_id = assays.assay_id	
        JOIN
            target_dictionary ON assays.tid = target_dictionary.tid
        JOIN
            target_components ON target_components.tid = target_dictionary.tid
        JOIN	
            component_sequences ON target_components.component_id = component_sequences.component_id
        JOIN
            component_domains ON component_sequences.component_id = component_domains.component_id
        JOIN
            domains AS d1 ON d1.domain_id = component_domains.domain_id
        Join 
            compound_structures ON compound_structures.molregno = molecule_dictionary.molregno
        WHERE
            d1.domain_name = 'PRMT5' AND molecule_dictionary.max_phase >= 2 
    """)

    results = db.execute(sql_query)
    print(results)
    for result in results:
        print(result)
    # Fetch the results
    data = [{"chembl_id": "123\n456", "max_phase": result[1], "SMILES": result[2]} for result in results]
    for d in data:
        print(d["SMILES"], d["chembl_id"])

    return templates.TemplateResponse("index.html", {"request": request, "data": data})
