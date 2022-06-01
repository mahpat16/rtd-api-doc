import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import boto3
import os

DB_COLL_MLMODELS = "mlmodels"
DB_COLL_CODE_SNIPPETS = "model_code_snippets"
DB_COLL_SWAGGER_SPEC = "model_swagger"
DB_COLL_RESPONSES = "model_sample_responses"
DB_COLL_JOBS = "batchJobs"


class DBHelper:
    db = None
    ssm = boto3.client('ssm')

    @classmethod
    def getServiceAccountKey(cls):
        serviceAccount = os.getenv(
            "FIRESTORE_ACCOUNT", "/jukebox/firestore-account")
        if serviceAccount is None:
            print("Set env variable FIRESTORE_ACCOUNT to SSM path of your json")
            raise Exception(
                "Internal error. Connection to records missing")

        response = cls.ssm.get_parameters(
            Names=[serviceAccount], WithDecryption=True
        )
        for parameter in response['Parameters']:
            return parameter['Value']

    @classmethod
    def _connectToFirestore(cls):
        serviceAccount = json.loads(cls.getServiceAccountKey())
        # Use a service account
        cred = credentials.Certificate(serviceAccount)
        firebase_admin.initialize_app(cred)
        cls.db = firestore.client()
        return cls.db

    @classmethod
    def handle(cls):
        if cls.db is not None:
            return cls.db
        return cls._connectToFirestore()

    # @classmethod
    # def docHandlerFirebase(cls, i):
    #     db = cls.handle()
    #     return db.collection(u'modelMetaDataSearch').where(u'indexVal', u'==', i).stream()

    @classmethod
    def getModelInfo(cls, vendor, name, version):
        db = cls.handle()
        docs = db.collection(DB_COLL_MLMODELS).where('vendor', '==', vendor).where(
            'name', '==', name).where('version', '==', version).get()
        if len(docs) != 1:
            raise Exception(
                f"Bad trn({vendor}, {name}, {version}) in request. Num recs found {len(docs)}")
        return docs[0].to_dict()

    @classmethod
    def getModelCodeSnippets(cls, klass):
        db = cls.handle()
        doc = db.collection(DB_COLL_CODE_SNIPPETS).document(klass).get()
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"class {klass} does not have any snippets")
            raise Exception(f"No snippets found for {klass}")

    @classmethod
    def getSampleResponse(cls, klass):
        db = cls.handle()
        doc = db.collection(DB_COLL_RESPONSES).document(klass).get()
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"class {klass} does not have any sample responses")
            raise Exception(f"No responses found for {klass}")

    @classmethod
    def getAllModelClasses(cls):
        db = cls.handle()
        docs = db.collection(DB_COLL_RESPONSES).get()
        klasses = set()
        for d in docs:
            doc = d.to_dict()
            klasses.add(doc.get("class"))
        return klasses

    @classmethod
    def getAModelForClass(cls, klass):
        db = cls.handle()
        docs = db.collection(DB_COLL_MLMODELS).where(
            'class', '==', klass).limit(1).get()
        if len(docs) != 1:
            raise Exception(
                f"Bad klass({klass}) in request. Num recs found {len(docs)}")
        doc = docs[0].to_dict()
        return doc.get('trn')

    @classmethod
    def getModelInfoFromTRN(cls, trn):
        db = cls.handle()
        docs = db.collection(DB_COLL_MLMODELS).where('trn', '==', trn).get()
        if len(docs) != 1:
            raise Exception(
                f"Bad trn({trn}) in request. Num recs found {len(docs)}")
        return docs[0].to_dict()

    @classmethod
    def getAllSwaggerSpec(cls):
        db = cls.handle()
        docs = db.collection(DB_COLL_SWAGGER_SPEC).get()
        rtn = {}
        for d in docs:
            doc = d.to_dict()

        return docs[0].to_dict()

    @classmethod
    def createMLModel(cls, id, payload):
        db = cls.handle()
        doc = db.collection(DB_COLL_MLMODELS).document(id)
        doc.set(payload)

    @classmethod
    def createJob(cls, jobid, payload):
        db = cls.handle()
        doc = db.collection(DB_COLL_JOBS).document(jobid)
        doc.set(payload)

    @classmethod
    def updateJob(cls, jobid, payload):
        db = cls.handle()
        doc = db.collection(DB_COLL_JOBS).document(jobid)
        doc.update(payload)

    @classmethod
    def _testGetModelFromClass(cls, klass):
        db = cls.handle()
        docs = db.collection(DB_COLL_MLMODELS).where(
            'class', '==', klass).get()
        i = 0
        for d in docs:
            doc = d.to_dict()
            print(doc)
            i += 1
            if i > 25:
                return
