from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from flask import send_file
import os, uuid
import pyodbc
import pandas as pd
import json
from pathlib import Path
from azureml.core.workspace import Workspace, Webservice

app = Flask(__name__)
server = 'sdmdbserver.database.windows.net'
database = 'sdmtest'
username = 'sdmadmin1'
password = 'Documentum@1234'
driver= '{ODBC Driver 17 for SQL Server}'

local_path = "./uploads"
@app.route("/")
def hello():
    return render_template('LandingPage.html')
    #return "Hello, World!"

@app.route('/uploader', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        uploaded_file = request.files.getlist("file[]")
        # try:
        #     print("Azure Blob storage v12")
        #
        #     # Create a unique name for the container
        #     container_name = "container" + str(uuid.uuid4())
        #
        #     # Create the container
        #     blob_service_client.create_container(container_name)
        #
        for file in uploaded_file:

            print(file)

            filename = secure_filename(file.filename)
                # file_extension = filename.rsplit('.', 1)[1]
            print(filename)
            file.save(os.path.join(local_path, filename))

            local_file_name = filename
            upload_file_path = os.path.join(local_path, local_file_name)
            service_name = 'scoredfraudmodel'
            ws = Workspace.get(
                name='sdmMachineLearning',
                subscription_id='efe60ef5-a4f3-4c91-8037-2f6c88c97246',
                resource_group='T12-SDM'
            )
            service = Webservice(ws, service_name)

            sample_file_path = upload_file_path

            with open(sample_file_path, 'r') as f:
                sample_data = json.load(f)

            score_result = service.run(json.dumps(sample_data))
            print(f'Inference result = {score_result}')
            res = json.loads(score_result)
            raw_scores = (res["Raw Scores"])

            risk_id = 2
            risk_name = 'Data Theft'
            risk_description = 'Theft of Data'
            asset_id = 'FN1002'
            policy_id = '2'
            risk_score = raw_scores
            risk_ownerid = '1'
            risk_status = 'In Progress'
            risk_severity = ''
            # if sum(risk_score) / len(risk_score) > 0.5:
            risk_severity = "High"
            # else:
            #     risk_severity = "Low"


            with pyodbc.connect(
                    'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""INSERT INTO [dbo].[RISK_MONITORING] VALUES ('1','Data Theft','Theft of Data','FN1001','1','0.896','1','In Progress','HIGH')""")

        #
        #

        return render_template('result.html', var=score_result)

