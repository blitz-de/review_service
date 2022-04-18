# Inside the Review-Service

## Makefile

There is a file called makefile, inside of it are various commands to run different containers within the service, for example:

### To run the service
`make run review-service`

### To create a superuser inside the User-Management-Service Database
`make superuser`

*** The Admin Panel for this service is
`http:localhost:8080/admin/`

### To run the makemigration command inside the container
`make makemigration`

### To run the migrate command inside the container
`make migrate`

### To run the test coverage
`make test`

# The available Endpoints using swagger UI
`http:localhost:8080/reviews/api/swagger/`


# Link to the User-Management-Service Travis-CI Dashboard
`https://app.travis-ci.com/github/blitz-de/review_service`


