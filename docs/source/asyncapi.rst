Async API
=========

.. _asyncapi:

Asynchronous APIs (Async API for short) are supported for long running methods. Take audio transcrption is an example, if you wanted 
to transcribe an hour long audio file then doing a synchronous API call is not viable. You could break the
audio file into smaller chunks, say 1 min chunk and then use the synchronous API. On the other hand this is a 
perfect use case to simply use the Async API. Async API gives you a way to submit a request and then
poll for the request to finish.

There are 4 steps in an Async API
  #. :ref:`getPayloadPresignedURL`
  #. :ref:`uploadPayload`
  #. :ref:`submitAsyncRequest`
  #. :ref:`checkAsyncStatus`


.. _getPayloadPresignedURL:

Get Payload Presigned URL
-------------------------

API endpoint: https://api.tiyaro.ai/v1/input/upload-url'

(See following sample code and API documentation for more details on the input params and output.)

This is the first step of sending an Async API request. Use this method to get a presigned URL that
you can use to upload your payload. e.g. your audio file.

.. _uploadPayload:

Upload Payload
--------------
In this step you upload your payload to the url that you get from the above call. Since this is a presgined URL
you can use any utility to upload your payload file to this presigned URL. See the sample code below to see how 
you can upload a file in Python


.. _submitAsyncRequest:

Submit Async request
--------------------
After you have uploaded your payload. You invoke the Async API for the model that you want to call inference on.
The async API endpoint for a model is available on its model card on the tiyaro console. Currently, the whisper AI
models are the only ones supporting the Async API. For convenience we are listing those async API end points here

https://api.tiyaro.ai/v1/async/ent/tiyarofs/1/openai/whisper-large?serviceTier=gpuflex'
https://api.tiyaro.ai/v1/async/ent/tiyarofs/1/openai/whisper-medium?serviceTier=gpuflex'
https://api.tiyaro.ai/v1/async/ent/tiyarofs/1/openai/whisper-small?serviceTier=gpuflex'
https://api.tiyaro.ai/v1/async/ent/tiyarofs/1/openai/whisper-tiny?serviceTier=gpuflex'


See the sample code below and the API documentation below for details on the input parameters and output from this request.
This particular method returns a 'GET' url for you to poll for the results of this operation.


.. _checkAsyncStatus:

Check Async request
-------------------
You can then poll on the 'GET' url returned from the above async request to check if the request is completed. The 'status' fields
in the response can have one of the following states.

* accepted - The request has been accepted in the system
* pending - The request is queued for execution
* processing - The request is being processed
* success - The request finished successfully
* failed - The request failed
* cancelled - The request was cancelled.

Note: When the status is 'success', ths same method also returns the 'results' of your request. Again, check the following
sample code and API spec for details of the fields.

.. note:: The following sample code is also available in our `sample code repo <https://github.com/tiyaro/code-samples/tree/main/python/async-api>`_. You can simply clone that repo and
  run the fully working sample code.

Sample Python code calling Async API
------------------------------------

:: 

  import requests
  import json
  import os
  import sys
  import time
  
  PROD_BASE = 'https://api.tiyaro.ai'
  WHISPER_LARGE_ASYNC_PATH = f'{PROD_BASE}/v1/async/ent/tiyarofs/1/openai/whisper-large?serviceTier=gpuflex'
  MP3_UPLOAD_URL = f'{PROD_BASE}/v1/input/upload-url?extension=mp3'
  
  
  def getHeaders():
      api_key = os.environ.get('TIYARO_API_KEY')
      return {
          'Content-Type': 'application/json',
          'Authorization': f'Bearer {api_key}'
      }
  
  
  def whisper_input():
      return {
          "no_speech_threshold": 0.6,
          "patience": 1,
          "suppress_tokens": "-1",
          "compression_ratio_threshold": 2.4,
          #
          # NOTE Remove 'language' parame if you want native language
          #
          "language": "en",
          "temperature_increment_on_fallback": 0.2,
          "length_penalty": None,
          "logprob_threshold": -1,
          "condition_on_previous_text": True,
          "initial_prompt": None,
          "task": "transcribe",
          "temperature": 0,
          "beam_size": 5,
          "best_of": 5
      }
  
  
  def get_upload_url(extension='mp3'):
      resp = requests.request("POST", MP3_UPLOAD_URL,
                              json={}, headers=getHeaders())
      assert resp.status_code == 201
      result = json.loads(resp.text)
      uploadURL = result['uploadUrl']['PUT']
      print('-- Input payload_url --', uploadURL)
      return uploadURL
  
  
  def upload_mp3_to_url(mp3File, upload_url):
      resp = requests.request("PUT", upload_url, data=open(mp3File, 'rb'))
      assert resp.status_code == 200
      print(f'-- {mp3File} uploaded --')
  
  
  def send_async_infer_request(upload_url):
      modelURL = WHISPER_LARGE_ASYNC_PATH
  
      payload = {
          "input": whisper_input(),
          "URL": upload_url
      }
  
      resp = requests.post(modelURL, headers=getHeaders(), json=payload)
      assert resp.status_code == 202
      print('-- async request submitted --')
      result = json.loads(resp.text)
      request_id = result['response']['id']
      print(f'requestId: {request_id}')
      return result['response']['urls']['GET']
  
  
  def check_status_and_result(inference_result_url):
      status = "NA"
      result = None
      while True:
          resp = requests.request(
              "GET", inference_result_url, headers=getHeaders())
          assert resp.status_code == 200
          result = json.loads(resp.text)
          status = result["status"]
          if status == 'success':
              print("status: ", status)
              break
          print("status: ", status)
          time.sleep(15)
      print(json.dumps(result, indent=2))
      text = result["result"]["text"]
      print("-- Transcribed Text --\n", text)
      print("-- Done -- \n")
  
  
  def async_infer(input_mp3):
      # Step 1 - Get a presigned url to upload your audio file
      upload_url = get_upload_url()
  
      # Step 2 - Upload your mp3 file to the presinged url
      upload_mp3_to_url(input_mp3, upload_url)
  
      # Step 3 - Submit an Async request. You get a inference_result_url that you can poll on.
      inference_result_url = send_async_infer_request(upload_url)
  
      # Step 4 - Poll/Wait for request to finish
      check_status_and_result(inference_result_url)
  
  
  def main():
      api_key = os.environ.get('TIYARO_API_KEY')
      if not api_key:
          raise ValueError("TIYARO_API_KEY not set")
  
      if len(sys.argv) != 2:
          print("Usage: asyncWhisper.py <mp3_file>")
          sys.exit(1)
  
      input_mp3 = sys.argv[1]
      print("-- processing input file --", input_mp3)
  
      start = time.time()
      async_infer(input_mp3)
  
      print("\n--- Inference time:", round(time.time() - start, 2), "secs ---")
  
  
  if __name__ == "__main__":
      main()


Async API
---------

.. _async-api:

.. openapi:: ./apiref/async-api.yaml