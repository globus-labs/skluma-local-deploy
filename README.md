# skluma-local-deploy
A file-level metadata extraction service that interfaces with zero cloud service. Skluma processes a number
of well-defined file types such as the following: 

* __Tabular__: classic row-column files organized with a consistent delimiter (e.g., CSV, TSV)
* __Structured__: common file formats not necessarily in a tabular format (e.g., JSON, XML)
* __Unstructured__: free text documents that do not adhere to a schema (e.g., TXT, PDF) 
* __Images__: any image represented by the common formats (e.g., TIF, PNG, JPG, BMP, etc.) 

## Get Started

There are only three dependencies to run skluma-local-deploy: 
* docker
* python3
* pip3

Before running, you will first need to create a configuration file in the following JSON format
(let's name the file skluma-config.json): 

```
{ 
    "username" : "<email-address>", 
    "add-container" : "None",
    "intercept-types" : "None", 
    "add-db" : "None", 
    "extraction-path" : "<absolute-path-to-file>"
}
```

Once skluma-local-deploy is cloned to your local system, you may run it via the following: 
```
cd skluma-local-deploy
pip3 install requirements
python3 skluma.py <absolute path to skluma-config.json>
```

## Feedback
We welcome any thoughts or feature-adds you would like to see with skluma-local-deploy. Please use this 
repository's issue tracker (https://github.com/globus-labs/skluma-local-deploy/issues) and we will respond promptly. 
