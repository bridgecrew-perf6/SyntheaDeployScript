import pyTigerGraph as tg 
import time
import sys
import os 

url = "https://<instance>.i.tgcloud.io"
user = "tigergraph" 
password = "<your_password>"
secret = "<your_secret>"
graph = "synthea"

DEBUG = True



###### DEFINE PYTG ###########
try:
    conn = tg.TigerGraphConnection(host=url,username=user,password=password)
    conn.graphname = graph
    conn.apiToken = conn.getToken(secret)
except Exception as e:
    print(e)
    sys.exit(0)

################ DEPLOY Script 
QUERIES_PATH = "scripts/query"
DATA_PATH = "data/"
JOB_PATH = "scripts/loads"

CSV_LIST = {
    'patients.csv' : 'loadPatient.gsql',
    'medications.csv' : 'loadMedications.gsql',
    'organizations.csv' : 'loadOrganizations.gsql',
    'normalizedSymptoms.csv' : 'loadPatientSymptoms.gsql',
    'encounters.csv' : 'loadEncounters.gsql',
    'zipcodes.csv' : 'loadZips.gsql',
    'imaging_studies.csv' : 'loadImaging.gsql',
    # 'Notes.csv' : 'loadAttributes.gsql' ,
    'careplans.csv': 'loadCareplans.gsql' ,
    'procedures.csv' : 'loadProcedures.gsql' ,
    'devices.csv' : 'loadDevices.gsql' ,
    'demographics.csv' : 'loadLocations.gsql' ,
    'payers.csv' : 'loadPayers.gsql' ,
    'immunizations.csv' : 'loadImmunizations.gsql' ,
    'allergies.csv' : 'loadAllergies.gsql' ,
    'conditions.csv' : 'loadConditions.gsql' ,
    'observations.csv' : 'loadObservations.gsql' ,
    'providers.csv' : 'loadProviders.gsql' ,
    'Notes tokenized.csv' : 'loadPatientNotes.gsql' ,
    'payer_transitions.csv' : 'loadPayerTransitions.gsql' 
    }



def schema(conn,graph):
    f = open("scripts/schema/createSchema.gsql")
    gsql = "".join(f.readlines())
    f.close()
    conn.graphname = graph
    res = conn.gsql(gsql,graphname=graph)
    if DEBUG:
        print(res)


def queries(conn,graph):
    for file in os.listdir(QUERIES_PATH):
        if file.endswith(".gsql"):
            f = open(QUERIES_PATH+"/"+file)
            gsql = "".join(f.readlines()).replace("@graphname@",graph)
            res = conn.gsql(gsql,graphname=graph)
            
            if DEBUG:
                print(res)
            f.close()
        


def data_loader(conn,graph):
    for file,job in CSV_LIST.items():
        try:
            f = open(JOB_PATH + "/" + job)
            gsql = "".join(f.readlines()).replace("@graphname@",graph)
            res = conn.gsql(gsql)
            if DEBUG:
                print("#######################")
                print(res)
                print("#######################")
                
            conn.uploadFile(DATA_PATH+file,"f1",job.replace(".gsql",""))
            time.sleep(3)
            f.close()
    

        except:
            pass
    try:
        print(conn.gsql("""
        USE GRAPH synthea
        INSTALL QUERY ALL
        """))
    except:
        pass


def deploy(conn,graph,secret):
    # TigerGraph
    Message = ""
    start = time.time()
    print("######### TigerGraph Data Schema")
    try:
        res = conn.gsql("""CREATE GRAPH synthea ()""",graphname="GLOBAL")
        print(res)
    except Exception as e:
        print(e)
    conn.graphname = "synthea"
    graph = "synthea"
    conn.apiToken = conn.getToken(secret)
    end = time.time()
    print(end - start)
    ###

    print("### schema")
    start = time.time()
    schema(conn,graph)
    queries(conn,graph)
    end = time.time()
    print(end - start)
    try:
        conn.upsertVertex("User","1",attributes={"username":"admin","password":"admin","salt":"salt","active":True})
    except:
        print("(error) can't write to TigerGraph db ... ")


    # Data Loading
    print("####    data")
    start = time.time()
    data_loader(conn,graph)
    end = time.time()
    print(end - start)


##################### END OF Deploy Function #############   


deploy(conn,graph,secret)