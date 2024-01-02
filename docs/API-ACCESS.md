# Give api access

In order to give API access to a user, follow these steps:

## Create a user

1. Connect to superset container in Nomad.
2. Run flask create-user '<username>_api@zerofox.com' '<the-password>' '<firstname>' '<lastname>'
   1. **Important**: The username must end with `_api@zerofox.com` in order to be able to access the API.
   2. Use a strong password.
3. Send the user the password.

## Accessing the API
1. User need to connect to the VPN.
2. They will have to request an access token using username and password from "Create a user" step:
    ```sh
    curl -X 'POST' \
      'https://superset-prod.zerofox.com/api/v1/security/login' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "password": "<the-password>",
      "provider": "db",
      "refresh": true,
      "username": "<the-username>"
    }'
    ```
3. Call any endpoint of desired API using the token from the previous step:
    ```sh
    curl --request GET \
      --url https://superset-prod.zerofox.com/api/v1/advanced_data_type/types \
      --header 'Authorization: Bearer <token>'
    ```