# Company +

🙌 __Python FastAPI Company+ API__ 🙌

Made by Jules Ladeiro for school project in Python with FastAPI!

## Setup

Install python <= 3.11.2, or install docker.

If you choose to install python, don't forget to install the requirements.

```bash
pip install -r requirements.txt
```

### Run with Docker

```bash
docker-compose up --build
```

### Run with Uvicorn (python)

```bash
uvicorn main:app --reload
```

## Swagger Documentation

<http://localhost:8080/docs>  (docker installation default port)

<http://localhost:8000/doc> (python installation default port)

## Authentication

Don't forget to authenticate yourself to use the API, only the /login route is public.

Please note that when you will authenticate yourself, you will have to enter your email in the `username` field and your password in the `password` field.

Know that your password is encrypted AND after that, hashed! __Si t'as le hash, t'as pas le mot de passe!__

## Database information

### By default

The database is sqlite. It's recommended to use the default database with testable datas, but you can use another database or delete the default one if you want.

It is located in the `app/db` folder, and its default name is `companyplus.db`.

### Tables

Here are the tables of the database:

- Users
- Companies
- Plannings
- Events

Below sections are the tables with their columns and some example content that are in the default database (companyplus.db).

Know that fields with a ? at the end are optional. And fields with a ! at the end are auto-generated.

| character | meaning                     |
| --------- | --------------------------- |
| ?         | optional                    |
| *         | auto-generated              |
| !         | any value / encrypted field |
| #         | hashed field                |

### Users table

| id* | first_name! | last_name! | email!         | password!# | role       |
| --- | ----------- | ---------- | -------------- | ---------- | ---------- |
| 3   | !           | !          | admin@cp.cp    | admin      | MAINTAINER |
| 1   | !           | !          | jules@jules.ju | azerty     | ADMIN      |
| 2   | !           | !          | yan@yan.yan    | azertyuiop | USER       |

### Companies table

| id* | name! | email! | website? | city! | country! | member_ids |
| --- | ----- | ------ | -------- | ----- | -------- | ---------- |

### Plannings table

| id* | name! | company_id! |
| --- | ----- | ----------- |

### Events table

| id* | name! | start_date! | end_date! | planning_id! | member_ids |
| --- | ----- | ----------- | --------- | ------------ | ---------- |
