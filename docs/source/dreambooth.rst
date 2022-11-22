DreamBooth Retraining API
=========================

.. _dreambooth:

Tiyaro supports retraining a diffusion model using DreamBooth. If you want to try using the retraining
from the Tiyaro console you can refer to this `step-by-step blog <https://www.tiyaro.ai/blog/dreambooth-retraining/>`_. This document
will guide you through the API way to trigger the retraining.

All the APIs described below are implemented using GraphQL. You can access them from the following graphql endpoint.

https://tbi56pnorvhbzbalsqal2is7dy.appsync-api.us-west-2.amazonaws.com/graphql

.. note:: You have to provide authorization header to your request to access the endpoint. The header is
  ``Authorization: <YOUR_TIYARO_API_KEY>``


High Level Workflow for retraining via API
  #. :ref:`createNewRetrain`
  #. :ref:`getPresgined`
  #. :ref:`uploadZip`
  #. :ref:`startRetrain`
  #. :ref:`checkStatus`
  #. :ref:`getRetrainModels`

.. _createNewRetrain:

Create a new retraining job
---------------------------
``newJobID(jobType: JobType): String``
  First thing you do to start your retraining is to create a new job using ``newJobID``. This call returns you a 'jobID' that you will use in the rest of the methods.

Input
+++++

jobType : JobType
  value is 'dreambooth'

Output
++++++

jobID: String
  this is the 'jobID'

.. _getPresgined:

Get presigned S3 url to upload your zipped images
-------------------------------------------------
``getJobInputURL(jobID: String, objName: String): String``
  The images that you want to upload must all be packaged into a zip file. Use this method to get a presigned S3
  url where you can upload that zip file. The format of the zip file is explained below.

Input
+++++

jobID - Type String
  job id of the job created by ``newJobID``

objName  - Type String
  name of your zip file

Output
++++++

presignedURL: String
  the presignedURL to which you can upload your zip file

ZIP file format
+++++++++++++++
There are 2 types of images that you can upload. 

1. The images which add a new concept to the diffusion models. Lets call this **instance** images. This type of images are **required**.
2. The images which are required by dreambooth training for an existing concept. Lets call this **class images**. This type of images are **optional**.

Providing class images will help you to cut down training cost both in terms of time and credits. Especially 
if you are retraining multiple instances of the same class, you may provide the same set of class images for 
each taining that will speed up your retraining. Again, this is optional.

In the zip file you provide the instance images should be added to the root of the package. The class images should
be added to a subdirectory called dataset_class. See example below::

  └── milkyway.zip/
      ├── instance-image1.jpeg
      ├── instance-image2.jpeg
      ├── .
      ├── .
      └── dataset_class/
          ├── class-image1.jpeg
          └── class-image2.jpeg
  
In the above example 'instance-image1.jpeg' and 'instance-image2.jpeg' are instance images that are directly at the root
of the package. Whereas 'class-image1.jpeg' and 'class-image2.jpeg' are added to a subdirectly 'dataset_class'. You can
also examine this `sample zip file <https://public-model-demo.s3.us-west-2.amazonaws.com/dog_toy_example.zip>`_ to see how it is packaged.


.. _uploadZip:

Upload your zip file to the presigned S3 URL
--------------------------------------------
You can use any library or command line tool to upload your zip file to the presigned S3 URL that you get from the ``getJobInputURL`` method above.
You have to however make sure to pass the same headers as shown in the python example below.

As an example here is a sample python program that uploads a (zip) file to the presigned S3 URL recevied from the ``getJobInputURL`` method::

  import requests

  # Replace with presigned url that you get from getJobInputURL method
  presignedURL = "replace_with_presigned_url"

  # Replace with your zip file
  fname = "/home/user/data/milkyway.zip"
  
  def upload_file_to_presigned_url(url, fname):
      headers = { 'Content-Type': 'application/octet-stream'}
      print(f'Uploading {fname} to {url}')
      response = requests.request("PUT", url, data=open(fname, 'rb'), headers=headers)
      print(response.status_code)
  
  if __name__ == "__main__":
    upload_file_to_presigned_url(presignedURL, fname)


.. _startRetrain:

Start retraining job
--------------------
``startRetrainingJob(jobID: String, input: JobInput): String``
  This method is used to start the retraining job. The return value of this method can be ignored as it is the
  same jobID as was passed in the input. You can check the status of this job by using the ``getJobStatus`` method.

Input
+++++

jobID - Type String
  job id of the job created by ``newJobID``

input -  Type JobInput
  input parameters for retraining. See details below.

::

  input JobInput {
    jobType: JobType
    dreamboothInput: DreamBoothInput
  }
  input DreamBoothInput {
    name: String!
    version: String!
    desc: String
    datasetS3ObjName: String!
  
    #  Parameters to the training job - required
    class_prompt: String!
    instance_prompt: String!
  
    #  Parameters to the training job all optional
    model: String
    vae: String
    seed: Int
    prior_loss_weight: Float
    resolution: Int
    train_batch_size: Int
    lr_warmup_steps: Int
    lr_scheduler: String
    num_class_images: Int
    learning_rate: Float
    gradient_accumulation_steps: Int
    max_train_steps: Int
    train_text_encoder: Boolean
    use_8bit_adam: Boolean
    mixed_precision: String
    with_prior_preservation: Boolean
    adam_beta1: Float
    adam_beta2: Float
    adam_weight_decay: Float
    adam_epsilon: Float
    max_grad_norm: Float
  }

Here is what the above parameters mean

| **name** - The name of your model. NOTE: Use a unique name for each of your model
| **version** - The version of the model
| **desc** - A description for this model
| **datasetS3ObjName**: This is the name of your zip file. **This is the same name you used in the getJobInputURL for objName**
| The other parameters are documented <here>

Output
++++++
* String - Returns the jobID (this is the same jobID as subimtted). Can be ignored.

.. note:: Your zip file name is referred in 2 methods. The name of the fields is slightly different. 
          
          e.g. If your zip file is called **milkyway.zip**

          * In getJobInputURL the **objName** should be milkyway.zip
          * In startRetrainingJob the **datasetS3ObjName** should be milkyway.zip


.. _checkStatus:
 
Check status of job
-------------------
``getJobStatus(jobID: String): JobStatus``
  The ``getJobStatus`` method returns the status of a retraining job. statusEnum == ``done`` denotes a job that 
  has successfully finished. If the statusEnum == ``failed`` you can check the error for the failure in ``errMsg``

Input
+++++

jobID: Type String
  job id of the job created by ``newJobID``

Output
++++++

JobStatus: Type JobStatus
  status of the job submitted using ``startRetrainingJob``

::

  type JobStatus {
    errMsg: String
    created: String
    finished: String
    statusEnum: JobStatusEnum
  }

  enum JobStatusEnum {
    running
    done
    failed
    notfound
  }


.. _getRetrainModels:

Get the API and ModelCard URL after successful retraining
---------------------------------------------------------
``getRetrainedModels(jobID: String): [RetrainedModels]``

The ``getRetrainedModels`` method returns the information of the models that are created after a 
successful retraining

Input
+++++

jobID: Type String
  job id of the job created by ``newJobID``

Output
++++++

RetrainedModels: Type RetrainedModels
  Information about the retrained models

::

  type RetrainedModels {
    vendor: String!
    version: String!
    name: String!
    url: String!
    modelCard: String!
  }

| **vendor** - The vendor of the model
| **version** - The version of the model
| **name** - The name of the model
| **url** - The API endpoint of the model
| **modelCard** - The API for the model card of the model

