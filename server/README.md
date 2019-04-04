#### Generate flask server python code:
```
wget http://central.maven.org/maven2/org/openapitools/openapi-generator-cli/3.3.4/openapi-generator-cli-3.3.4.jar -O openapi-generator-cli.jar
java -jar openapi-generator-cli.jar generate -i TranslatorReasonersAPI.yaml -g python-flask -o python-flask-server
```
