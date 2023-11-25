# Ark Summer 2024 Software Engineering Internship Take Home Project

## Introduction

At Ark Biotech, we're building bioreactors purpose-built for cultivated meat, with a mission to 100x the industry’s capacity by 2035. The Data Systems team is responsible for everything from production, model-based control software to web-based data monitoring applications.

In this take home project, you'll get the chance to demonstrate your proficiency in Python, building a simple web-based dashboard to visualize real-time process data originating from one of our bioreactors.

## Technical Details

In this directory, you'll find
- a `src` directory with a simple `ark_app` package in it, providing the scaffolding and an entrypoint function for you to write your application.
- a `Dockerfile` that defines the image your code will be copied into and installed in.
- a `compose.yaml` that defines the container that'll be used to run your code.
- a `local.env` with example environment variables to provide database credentials.
- a `pyproject.toml` configuring the `ark_app` package, including the entrypoint for your application and its dependencies.
- this `README.md`

To serve your web-based dashboard in a local browser at http://localhost:8000/, Docker is configured to start the container by executing `run_ark_app`, the entrypoint configured for your application that executes the `main` function in the `ark_app` package. In that function, you'll want to start a web server configured to run at port `8000` and host `0.0.0.0`.

### The database

The data you'll be visualizing will be in a Postgres database, also configured in `compose.yaml`. Credentials to access this database will be provided in the following environment variables:
- `POSTGRES_HOST` provides the host
- `POSTGRES_PORT` provides the port
- `POSTGRES_USER` provides the user
- `POSTGRES_PASSWORD` provides the password
- `POSTGRES_DB` provides the database

An example can be found in `local.env`. Note that these will be subject to change, so make sure not to hard code these.

### The data

The tables in the database:
```
                      List of relations
 Schema |           Name           | Type  |      Owner       
--------+--------------------------+-------+------------------
 public | CM_HAM_DO_AI1/Temp_value | table | process_trending
 public | CM_HAM_PH_AI1/pH_value   | table | process_trending
 public | CM_PID_DO/Process_DO     | table | process_trending
 public | CM_PRESSURE/Output       | table | process_trending
```

Each table has the same schema, like so:
```
public."CM_HAM_DO_AI1/Temp_value"
                Table "public.CM_HAM_DO_AI1/Temp_value"
 Column |            Type             | Collation | Nullable | Default 
--------+-----------------------------+-----------+----------+---------
 time   | timestamp without time zone |           |          | 
 value  | double precision            |           |          | 
```

Each table contains the following data:
| Table                    | Name             | Units   |
|--------------------------|------------------|---------|
| CM_HAM_DO_AI1/Temp_value | Temperature      | Celsius |
| CM_HAM_PH_AI1/pH_value   | pH               | n/a     |
| CM_PID_DO/Process_DO     | Dissolved Oxygen | %       |
| CM_PRESSURE/Output       | Pressure         | psi     |

### How to test your code

Run `docker compose up` and navigate your browser to http://localhost:8000/. That's it!

## Minimum Viable (Take Home) Project

The dashboard should serve an interactive plot each of these four series (Temperature, pH, Distilled Oxygen, and Pressure) over time.

### How you'll be evaluated

1) Does your package install successfully?
2) Can your dashboard be viewed at http://localhost:8000/, does it fulfill the MVP specification, and does it look good?
3) Is your code high quality, e.g. does it follow PEP8, is it fully type annotated, how does it handle configuration, does it have useful logging, docstrings, and/or comments, and so on.

## Submission Instructions

To package up your code into a Python wheel, run `docker compose run app python -m build`. This will build a Python wheel and source distribution in a new `dist` directory. Please submit your `.whl` file at this [Google Form](https://forms.gle/cbRsUXBGDiXTAUc88) by Sunday, November 26th, 2023.

## Proprietary & Confidential

Please note that this project and the accompanying dataset is proprietary and confidential to Ark Biotech Inc. We ask that you keep these project materials private. For example, please do not post this information or your solution to publicly available websites like GitHub or Google Drive.
