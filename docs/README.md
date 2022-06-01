Run generateApiRef.py to upate apiref to reflect all the supported model classes/types.

The above needs the following to be pip installed
- firebase_admin
- boto3

It also needs the following utility to convert OpenApiSpec3.0 to SwaggerSpec2.0 because the sphinx openapi plugin only supports SwaggerSpec2.0.

api-spec-converter
https://www.npmjs.com/package/api-spec-converter
