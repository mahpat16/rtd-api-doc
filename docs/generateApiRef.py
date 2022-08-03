import subprocess
import requests
import os
from dbhelper import DBHelper
import json
import yaml


def baseAPIRefRST():
    s = '''
API Reference
==============

.. _apiref: 

The following API reference is organized by :ref:`Model Type <modeltype>`. The actual 'Post' path below should be 
replaced with the path to the specific model :ref:`API endpoint URL <modeltypeoncard>`.
'''
    return s


def addApiRefRST(rst, klass):
    template = f'''

{klass}
{"-"*len(klass)}

.. _{klass}:

.. openapi:: ./apiref/{klass}.yaml

    '''
    return rst + template


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
    path = None
    for p in spec.get("paths").keys():
        path = p

    if path == None:
        print("-"*40)
        print(f"Ignoring trn {trn}, has bad spec")
        print(spec)
        return

    # Replace model path with a generic path
    spec["paths"]["/model_specific_path"] = spec["paths"].pop(path)
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


TIMESERIES_V1_KLASSES = [
    "timeseries-exo",
    "prophet-multi-ts",
    "autosarimax-multi-ts",
    "sarimax-multi-ts",
    "sarimax-uni-ts",
    "autoarima-uni-ts",
    "autosarimax-uni-ts",
    "prophet-uni-ts",
    "fbprophet-uni-ts",
    "ops-test"
]


def getAllSpecs():
    # Get all the supported model types i.e. klasses
    klasses = DBHelper.getAllModelClasses()

    # Get the swagger 2.0 spec for each class
    for klass in klasses:
        # skip V1 timeseries classes, they will be handled below
        if klass in TIMESERIES_V1_KLASSES:
            continue
        trn = DBHelper.getAModelForClass(klass)
        if trn is not None:
            getSwaggerSpec(klass, trn)

    # Get all the supported timesereis subclasses
    tsSubKlasses = DBHelper.getTimeseriesV2Subclasses()
    for subKlass in tsSubKlasses:
        trn = DBHelper.getAModelForSubClass(subKlass)
        getSwaggerSpec(subKlass, trn)

    # Generate apiref.rst
    rst = baseAPIRefRST()
    for klass in klasses:
        rst = addApiRefRST(rst, klass)

    apiRST = "./source/apiref.rst"
    with open(apiRST, "w") as f:
        f.write(rst)


if __name__ == "__main__":
    #trn = "AI4Afrika-health-chatbot"
    #getSwaggerSpec("translation", trn)
    getAllSpecs()
