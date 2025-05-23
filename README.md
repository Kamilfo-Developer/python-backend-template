# python-backend-template

## This is a multifunctional Python backend template
It provides:
- Dependency injection through [dishka](https://github.com/reagento/dishka)
- [Specification pattern](https://en.wikipedia.org/wiki/Specification_pattern)
- A convinient way to manage exception using global framework handler
- Clickhouse integration including an easy way to manage migrations

The template is based on Uncle Bob's [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) approach.

## Installation guide
- Install [UV](https://docs.astral.sh/uv/)
- `uv venv`
- Activate venv
- Run `uv sync`
- To run the application in dev mode:
  - Use `make dev-compose`
  - Use `uv run -m app dev`
  - To get rid of undesired containers, use `make dev-destroy` when needed
- To run the application in production mode, use Docker

## Testing
If you use the original Clean Architecture approach, the application should be really easy to test.
- For testing the application, use `make test`
- If you want to see the test coverage, use `make testcvg`
