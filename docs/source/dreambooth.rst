DreamBooth Training API
=========================

.. _dreambooth:

Tiyaro supports training a diffusion model using DreamBooth. If you want to do the training using the UI 
in the Tiyaro console you can refer to this `step-by-step blog <https://www.tiyaro.ai/blog/dreambooth-retraining/>`_. This document
will guide you through the API way to start the training.

All the training methods described below are implemented as GraphQL API. You can access them from the following graphql endpoint.

https://control.tiyaro.ai/graphql



Here is a working sample program that shows how you can call the Tiyaro GraphQL API from python. This sample is for illustration
only. Its main purpose is to show the Headers that are needed to make the GraphQL call. Most languages have some high level library
that makes it much easier to call GraphQL API, 'gql' is one such library for Python.

:: 

  import requests
  import os
  import sys
  
  url = "https://control.tiyaro.ai/graphql"
  
  apiKey = os.getenv("TIYARO_API_KEY")
  if apiKey is None:
      print("Set your TIYARO_API_KEY env variable")
      sys.exit(1)
  
  #
  # NOTE: Replace the following with a valid jobID
  #
  jobID = "replace_with_your_job_id"
  if jobID == "replace_with_your_job_id":
      print("Please set jobID to a valid job id that you got back from the 'newJobID' method")
      sys.exit(1)
  
  
  query = f'query {{getJobStatus(jobID: "{jobID}") {{statusEnum errMsg created finished}}}}'
  payload = {"variables": {}, "query": query}
  
  headers = {
      "content-type": "application/json",
      "authorization": f"{apiKey}"
  }
  
  response = requests.request("POST", url, json=payload, headers=headers)
  print(response.text)


.. note:: As shown above you have to provide your Tiyaro API key in the authorization header to your request. You can
  generate your API key from the `API Keys <https://console.tiyaro.ai/apikeys>`_ page on Tiyaro.

High Level Workflow for training via GraphQL API
  #. :ref:`createNewRetrain`
  #. :ref:`getPresgined`
  #. :ref:`uploadZip`
  #. :ref:`startRetrain`
  #. :ref:`checkStatus`
  #. :ref:`getRetrainModels`

.. _createNewRetrain:

Create a new training job
---------------------------
``newJobID(jobType: JobType): String``
  First thing you do to start your training is to create a new job using ``newJobID``. This call returns you a 'jobID' that you will use in the rest of the methods. 

Input
+++++

jobType : JobType
  value is 'dreambooth'

Output
++++++

jobID: String
  this is the 'jobID'

.. _getPresgined:

Get presigned S3 url to upload your images in a zip file
--------------------------------------------------------
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
if you are training multiple instances of the same class, you may provide the same set of class images for 
each taining that will speed up your training. Again, this is optional.

In the zip file you provide, the instance images should be added to the root of the package. The class images should
be added to a subdirectory called dataset_class. See example below::

  zip -sf dog_toy_example.zip 
  Archive contains:
    alvan-nee-9M0tSjb-cpA-unsplash.jpeg
    alvan-nee-bQaAJCbNq3g-unsplash.jpeg
    alvan-nee-brFsZ7qszSY-unsplash.jpeg
    alvan-nee-eoqnr8ikwFE-unsplash.jpeg
    alvan-nee-Id1DBHv4fbg-unsplash.jpeg
    dataset_class/
    dataset_class/dog5.jpeg
    dataset_class/dog4.jpeg
    dataset_class/dog3.jpeg
    dataset_class/dog1.jpeg
    dataset_class/dog2.jpeg

In the above example 'alvan-nee-9M0tSjb-cpA-unsplash.jpeg', 'alvan-nee-bQaAJCbNq3g-unsplash.jpeg' etc are instance images that are directly at the root
of the package. Whereas 'dog5.jpeg', 'dog4.jpeg' etc are class images that are added to a subdirectly 'dataset_class'. You can
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

Start training job
--------------------
``startTrainingJob(jobID: String, input: JobInput): String``
  This method is used to start the training job. The return value of this method can be ignored as it is the
  same jobID as was passed in the input. You can check the status of this job by using the ``getJobStatus`` method.

Input
+++++

jobID - Type String
  job id of the job created by ``newJobID``

input -  Type JobInput
  input parameters for training. See details below.

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
| **model** -	The base stable diffusion model to fine tune using dreambooth.
| **vae** -	The VAE required to run dreambooth training.
| **seed** -	A seed for reproducible training.
| **prior_loss_weight** -	The weight of prior preservation loss.
| **instance_prompt** -	The prompt with identifier specifying the instance concept you want your base stable diffusion model to train on.
| **class_prompt** -	The prompt to specify images in the same class (concept) as provided instance images.
| **resolution** -	The resolution for input images, all the images in the train/validation dataset will be resized to this resolution.
| **train_batch_size** -	Batch size (per device) for the training dataloader.
| **lr_warmup_steps** -	Number of steps for the warmup in the lr scheduler.
| **lr_scheduler** -	The scheduler type to use. Choose between ["linear", "cosine", "cosine_with_restarts", "polynomial", "constant", "constant_with_warmup"]
| **num_class_images** -	Minimal class images for prior preservation loss. If not have enough images, additional images will be sampled with class_prompt.
| **learning_rate	Initial** - learning rate (after the potential warmup period) to use.
| **gradient_accumulation_steps** -	Number of updates steps to accumulate before performing a backward/update pass.
| **max_train_steps** -	Total number of training steps to perform.  If provided, overrides num_train_epochs.
| **train_text_encoder** -	Whether to train the text encoder.
| **use_8bit_adam** -	Whether or not to use 8-bit Adam from bitsandbytes.
| **mixed_precision** -	Whether to use mixed precision. Choose between fp16 and bf16 (bfloat16). Bf16 requires PyTorch >= 1.10 and an Nvidia Ampere GPU.
| **with_prior_preservation** -	IF this is true then the class images are actually required, which are by default taken care of by the program, if you have yours the class images can used thereby reducing the time required to train dreambooth
| **adam_beta1** -	The beta1 parameter for the Adam optimizer.
| **adam_beta2** -	The beta2 parameter for the Adam optimizer.
| **adam_weight_decay** -	Weight decay to use.
| **adam_epsilon** -	Epsilon value for the Adam optimizer.
| **max_grad_norm** -	Max gradient norm.

Output
++++++
* String - Returns the jobID (this is the same jobID as subimtted). Can be ignored.

.. note:: Your zip file name is referred in 2 methods. The name of the fields is slightly different. 
          
          e.g. If your zip file is called **milkyway.zip**

          * In getJobInputURL the **objName** should be milkyway.zip
          * In startTrainingJob the **datasetS3ObjName** should be milkyway.zip


.. _checkStatus:
 
Check status of job
-------------------
``getJobStatus(jobID: String): JobStatus``
  The ``getJobStatus`` method returns the status of a training job. statusEnum == ``done`` denotes a job that 
  has successfully finished. If the statusEnum == ``failed`` you can check the error for the failure in ``errMsg``. Note that
  the getJobStatus call `only` makes sense for a job that has been started with the ``startTrainingJob`` method. If you simply
  create a newJobID and call job status on that newly created job you wont get any status back as the job hasnt even been submitted/started yet.


Input
+++++

jobID: Type String
  job id of the job created by ``newJobID``

Output
++++++

JobStatus: Type JobStatus
  status of the job submitted using ``startTrainingJob``

::

  type JobStatus {
    errMsg: String
    created: String
    finished: String
    statusEnum: JobStatusEnum
    jobInput: String
  }

  enum JobStatusEnum {
    running
    done
    failed
    notfound
  }

Note: **jobInput** is the json string representing the input parameters that were sent to this job. We return this
input back so you can find out the params used to train this job. This is more of a convenience in case you
dont want to store that meta data yourself. 

.. _getRetrainModels:

Get the API and ModelCard URL after successful training
---------------------------------------------------------
``getTrainedModels(jobID: String): [TrainedModels]``

The ``getTrainedModels`` method returns the information of the models that are created after a 
successful training

Input
+++++

jobID: Type String
  job id of the job created by ``newJobID``

Output
++++++

TrainedModels: Type TrainedModels
  Information about the trained models

::

  type TrainedModels {
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

