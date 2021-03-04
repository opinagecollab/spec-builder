# Spec Builder
This builder reads product and category information from the Warehouse DB, analyzes it, and uses it to identify the 
specs that are more relevant for each category. In order to do so, the builder needs to have a set of specs and 
questions that are relevant to the domain at hand. Currently, it only has fashion related specs (please check the 
`/assets/` folder), but new files can easily be added to support other domains. 

Note that the specs analysis is done on each product and the results are then aggregated into the parent categories. 

Notes: 
- Currently, the builder runs only once. 
- If there's a job ongoing, it will resume it. 
(It assumes there's only one job running at at time)
- The works is done in batches.  
- We need to determine if it's possible to parallelize jobs or not. 

## Prerequisites
The following sections describe the requirements that are necessary to run this builder. 

### Warehouse
The Warehouse DB must be up and running. Also, it must be populated via the Meltano and Singer taps 
(`tap-sap-commerce-cloud` and `tap-sap-upscale`). 

### Parameters 
Before the builder can be executed, it is necessary to provide the following parameters: 
- DATABASE_HOST: The URL of the host currently running the Warehouse DB. 
- DATABASE_USERNAME: The name of the user that can be used to access the Warehouse DB. 
- DATABASE_PASSWORD: The password of the user that can be used to access the Warehouse DB. 
- DATABASE_PORT: The port used to connect to the Warehouse DB. 
- DATABASE_NAME: The name of the Warehouse DB. 

Note: This information can be provided via an `.env` file or as environment variables. Please check the `config.py` file 
for more information. 

## Running Builder
This skill is built and runs as a Docker container. 
To build this skill run the following command:
- ```docker build -t spec-builder:latest .```

To execute this builder, execute the following command:
- ```docker run -d -t spec-builder:latest``` 

Please note that this builder will not run if the Warehouse DB is not running.  