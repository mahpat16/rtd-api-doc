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
Model Types


.. _openapispec:

Open API Specification
----------------------
Open api specs


.. _codesamples:

Code Samples
------------
Code samples