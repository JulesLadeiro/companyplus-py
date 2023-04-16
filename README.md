# Company +

🙌 Python FastAPI Company+ API 🙌

## Setup

### Installation

Install python 3.11.2 (or higher), or install docker.

### Install dependencies (python installation only)

```bash
pip install -r requirements.txt
```

### Run

### Run with Docker

```bash
docker-compose up --build
```

### Run with uvicorn

```bash
uvicorn main:app --reload
```

## Swagger Documentation

<http://localhost:8080/docs>  (docker installation)

<http://localhost:8000/doc> (python installation)

## Database information

### By default

The database is located in the `app/db` folder, and the default name is `companyplus.db`.

Know that the database is sqlite. It's recommended to use the default database with testable datas, but you can use another database or delete the default one if you want.

### Tables

Here are the tables of the database:

- Users
- Companies
- Plannings
- Events

Below sections are the tables with their columns and some example content.

Know that fields with a ? at the end are optional. And fields with a ! at the end are auto-generated.

### Users table

| id! | email | password | role |
| --- | --- | --- | --- |
| 1 | jules@jules.ju | azerty | maintainer |

### Companies table

| id! | name | email | website? |
| --- | --- | --- | --- |

### Plannings table

TBD

### Events table

TBD
