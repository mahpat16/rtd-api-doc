Developer Guide
===============

.. _servicetier:

Service Tier
------------

The following service tiers are supported for each API. Service tiers define the backend that will service your API call and the infrastructure used to run your model inference.

cpuflex
   This service tier means that your API inference will run on cpu instance. It is the **default** service tier for each API.

gpuflex
   This service tier means that your API inference will run on gpu instance. You have to add the query parameter **"serviceTier=gpuflex"** to an API endpoint to use gpu instance (see below). 

.. csv-table:: 
   :header: "API endpoint", "Service Tier"

   "https://api.tiyaro.ai/v1/ent/huggingface/1/facebook/bart-large-cnn", cpuflex
   "https://api.tiyaro.ai/v1/ent/huggingface/1/facebook/bart-large-cnn?serviceTier=gpuflex", gpuflex


.. hint:: On the model card if you click the "FlexGPU" button the API URL is updated to show the gpuflex url


.. _apitoken:

API Key
---------
You need an API Key to invoke a model API. You can generate an API key for your account from the `API Keys page <https://console.tiyaro.ai/apikeys>`_. You pass in this API key as a **Bearer** token with the Authorization HTTP header in your http request. 

The following example shows how you can pass in the API key in `cURL <https://curl.se/>`_  (replace 'YOUR_API_KEY' with your key). `Code samples repo <https://github.com/tiyaro/code-samples>`_ has examples for other programming languages for your reference.

.. code-block:: console

   curl --request POST \
  --url https://api.tiyaro.ai/v1/ent/huggingface/1/facebook/bart-large-cnn \
  --header 'accept: */*' \
  --header 'authorization: Bearer YOUR_API_KEY' \
  --header 'content-type: application/json' \
  --data '{"input": "I feel the need - the need for speed!"}'


.. _modeltype:

Model Type
----------
There are literally thousands of models available on Tiyaro. Models built using Tensorflow, PyTorch, 
Transformers just to name a few frameworks. Models from various github repos. We even have models from various SaaS providers. At Tiyaro 
we have cataloged and normalized all these various models into specific **Model Types**. Each model type has 
a specific input and output signature. What this means is that as a developer you only have to know the 'Type' of a 
model to understand how you can invoke that model (input signature) and what response you can expect from it (output signature).

Model types not only provide a uniform way to invoke models of the same type. But it also allows you to 
compare and run experiments on different models of the same type. Thus allowing you to quickly narrow down the 
model that works best for your use case and for your data. All with the assurance that if there is a newer model 
of the same type that comes along tomorrow, you wont have to change the API inputs or process its outputs differently. 
All you need to do is use the API URL of the new model.

You can find out the Model Type for a model from its :ref:`Model card <modeltypeoncard>`. 

Some of the Model Types are
   * summarization
   * fill-mask 
   * image-object-detection
   * image-classification
   * translation
   * text-classification
   * question-answering
   * audio-classification
   * automatic-speech-recognition

.. important:: The API reference is organized by Model Types. If you are looking for the API reference for a specific model, find out its model type and then use the API reference.

.. _openapispec:

Open API Specification
----------------------
Open api specs


.. _codesamples:

Code Samples
------------
Code samples