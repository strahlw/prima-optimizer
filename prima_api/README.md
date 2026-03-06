# PRIMO - API

This project accompanies the [PRIMO - The P&A Project Optimizer Toolkit](https://github.com/NEMRI-org/primo-optimizer). [PRIMO](https://primo.readthedocs.io/en/latest/) aims to provide multi-scale, simulation-based, open source computational tools and models to support the Methane Emissions Reduction Program (MERP) and the National Emissions Reduction Initiative (NEMRI).

This project wraps up PRIMO in an API layer built using [FastAPI](https://fastapi.tiangolo.com/), [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html), and [Docker](https://www.docker.com/). This makes it possible to use PRIMO as an API service in your application of choice.

## Running the API service

The Docker containers can be spun up using:

```sh
$ docker-compose up -d --build
```

### Mac Users:
```sh
$ docker-compose -f docker-compose.mac.yml up -d --build
```

Open your browser to http://localhost:9090/docs to view the API documentation on querying the service and
http://localhost:5555 to view the Flower dashboard. 

For more details, please see the [Docker Compose recipe](docker-compose.yml)

## Funding acknowledgements

This work was conducted as part of the [National Emissions Reduction Initiative](https://edx.netl.doe.gov/nemri/)
with support through the [Environmental Protection Agency - Methane Emissions Reduction Program](https://www.epa.gov/inflation-reduction-act/methane-emissions-reduction-program)
within the U.S. Department of Energy’s [Office of Fossil Energy and Carbon Management (FECM)](https://www.energy.gov/fecm/office-fossil-energy-and-carbon-management).
As of 2023, additional support was provided by FECM’s [Solid Oxide Fuel Cell Program](https://www.energy.gov/fecm/science-innovation/clean-coal-research/solid-oxide-fuel-cells),
and [Transformative Power Generation Program](https://www.energy.gov/fecm/science-innovation/office-clean-coal-and-carbon-management/advanced-energy-systems/transformative).

## Contributing

**By contributing to this repository, you are agreeing to all the terms set out in the LICENSE.md and COPYRIGHT.md files in this directory.**