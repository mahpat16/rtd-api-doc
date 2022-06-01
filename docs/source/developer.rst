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

   "https://api.tiyaro.ai/v1/ent/huggingface/1/facebook/bart-large-cnn", cpu-flex
   "https://api.tiyaro.ai/v1/ent/huggingface/1/facebook/bart-large-cnn?serviceTier=gpuflex", gpu-flex


.. hint:: On the model card if you click the "FlexGPU" button the API URL is updated to show the gpuflex url


.. _apitoken:

API Token
---------
This is an api token


.. _modeltype:

Model Type
----------
Model Types


.. _openapispec:

Open API Specification
----------------------
Open api specs


.. _codesamples:

Code Samples
------------
Code samples