# Gym Management System

## Webpage routings:
### User routes:
/  
/register  
/login  
/dashboard  
/logout  
### Trainer routes:
/trainer/login
/trainer/dashboard
/trainer/logout
### Admin routes:
/temp  
/admin/create_tables  
/admin/create_admin  
/admin/login  
/admin/hire_trainer  
/admin/logout

## Classes:
### Members:
**Data:** id, name, phone_number, email, memeber_since, password  
**Functions:**   
1. __init__(self, name, phone_number, email, password, member_since)  

### Trainers:
**Data:** id, name, phone_number, email, experience, trainer_since, password  
**Functions:**  
1. __init__(self, name, phone_number, email, password, experience, trainer_since)  

### Admin:
**Data:** id, name, phone_number, email, password  
**Functions:**  
1. __init__(self, name, phone_number, email, password)  
