Welcome to readme.md of my final internship project in Capgemini Engineering. 
I have develop a API app in FastAPI with all super cool features (part of them is described below and more details about app and it funcionality will be added pretty soon!

# Task 1
Added three local hooks (pre-commit, pre-commit-msg and commit-msg) and one server side hook (pre-reveive hook). 

# Task 2 
Added a new file (in .yaml format) that contains an API documentations about User Service.

# Task 2.1
Fixed API documentation according to feedback.

# Task 3
Added User Service application (based on documentation from Swagger) created by using FastApi framework. 

# Task 3.1
Fixed User Service application according to feedback:
- Changed list to dictionary.
- Implement (probably) more simply logic for search and filter function (mutual exclusivity).

# Task 3.2
Another fixes for User Service application: 
- Global "id" variable changed with yield generator for creating new ids for users.
- Dictionary that contains users is now updated with dict.update(). (PUT method)  
- Relative imports have been replaced 

# Task 4
Added file that contain tests for User Service Application. Tests achieve 97% of test coverage (based on main app).
Also, main.py file was modified (by adding a random user to dictionary) to have an ability to run tests.

# Task 4.1
Fixed test file for User Service application according to feedback:
- Some function names has been changed. 
- Implement more simply logic for functions that return response (json responses).  

# Task 5 
Users Service wrapped into virtual environment using Poetry. Added poetry.lock and pyproject.toml files to project.
To run tests after this (commit) you must run it as module using command "python -m pytest".

# Task 6 
Dockerized Users Service application.
Added two files: 
- Dockerfile 
- docker-compose.yaml
Docker-compose file contain one service - Users.
 
