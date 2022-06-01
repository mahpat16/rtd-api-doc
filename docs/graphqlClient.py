import subprocess
import requests
import os
from dbhelper import DBHelper
import json
import yaml


def getSwaggerSpec(klass, trn):
    print(f"Fetching swagger spec for {klass} => {trn}")
    graphqlAPI = 'https://5hhkqgefp5ebfbem2rtvmw3ybe.appsync-api.us-west-2.amazonaws.com/graphql'

    tiyaroKey = os.getenv("JWT_TOKEN")
    if tiyaroKey is None:
        raise Exception("Please export JWT_TOKEN to your Tiyaro Key")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{tiyaroKey}"
    }

    data = {
        'operationName': None,
        'variables': None,
        'query': f'query MyQuery {{getOpenAPISpec(id: {{trn: "{trn}" }})}}',
    }
    response = requests.request(
        "POST", graphqlAPI, json=data, headers=headers)
    response.raise_for_status()
    resp = response.json()

    # Load json spec
    spec = json.loads(resp.get("data").get("getOpenAPISpec"))
    for p in spec.get("paths").keys():
        path = p

    # Replace model path with a generic path
    spec["paths"]["/model_specific_path"] = spec["paths"].pop(p)
    print(json.dumps(spec, indent=2))
    spec2yaml = f"source/apiref/{klass}-2.yaml"
    spec3yaml = f"source/apiref/{klass}.yaml"

    with open(spec2yaml, "w") as f:
        yaml.dump(spec, f)

    with open(spec3yaml, "w") as f:
        convertString = f"api-spec-converter --from=openapi_3 --to=swagger_2 --syntax=yaml {spec2yaml}".split(
            " ")
        subprocess.run(convertString, stdout=f)
    os.remove(spec2yaml)


def getAllSpecs():
    klasses = DBHelper.getAllModelClasses()
    for klass in klasses:
        trn = DBHelper.getAModelForClass(klass)
        getSwaggerSpec(klass, trn)


if __name__ == "__main__":
    #trn = "AI4Afrika-health-chatbot"
    #getSwaggerSpec("translation", trn)
    getAllSpecs()
