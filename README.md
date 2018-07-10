# HumanMatrix
Supporting the Project Manager in the realisation of the Responsibility Assignment Matrix

For more informations check this links:
https://www.slideshare.net/albertovolpe9/feasibility-study-human-matrix-it-project-management 
https://www.slideshare.net/albertovolpe9/business-case-human-matrix-it-project-management 
https://www.slideshare.net/albertovolpe9/project-charter-human-matrix-it-project-management 
https://www.slideshare.net/albertovolpe9/intermediate-human-matrix-it-project-management 
https://www.slideshare.net/albertovolpe9/it-project-management-human-matrix

# Fruition of the Story 

## Dependecies
Flask microframework http://flask.pocoo.org
PyGithub https://github.com/PyGithub/PyGithub
Python 3
MySQL db

pandas
``` 
    pip install pandas
``` 

matplotlib
``` 
    pip install matplotlib
``` 

## Step1
Import the dbms

## Step2
Set the following vars:
``` 
    app.config['MYSQL_DATABASE_USER'] = 'user'
    app.config['MYSQL_DATABASE_PASSWORD'] = '***********'
    app.config['MYSQL_DATABASE_DB'] = 'HumanMatrix'
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
``` 

## Run
From the main folder, open the terminal and run the following command:
``` 
    FLASK_APP=app.py flask run
    
``` 
