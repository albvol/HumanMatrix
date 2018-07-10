# HumanMatrix
Supporting the Project Manager in the realisation of the Responsibility Assignment Matrix (RAM).

GitHub integration: based on the tasks of the RAM the PM can choose the best team components.

For more informations check the following links:

https://www.slideshare.net/albertovolpe9/feasibility-study-human-matrix-it-project-management 
https://www.slideshare.net/albertovolpe9/business-case-human-matrix-it-project-management 
https://www.slideshare.net/albertovolpe9/project-charter-human-matrix-it-project-management 
https://www.slideshare.net/albertovolpe9/intermediate-human-matrix-it-project-management 
https://www.slideshare.net/albertovolpe9/it-project-management-human-matrix

# Installation and Configuration

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
Import the dbms by using the .sql files in the resource folder

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


# Other Info

Template based on bootstrap: https://wrappixel.com/demos/admin-templates/admin-pro/main/index2.html (https://wrappixel.com)
