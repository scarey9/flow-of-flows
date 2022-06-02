brew install postgresql
docker run -d --name demo_postgres -v dbdata:/var/lib/postgresql/data -p 5432:5432 -e POSTGRES_PASSWORD=your_password_1234 postgres:11
prefect create project jaffle_shop
prefect register --project jaffle_shop -p flows/
# adjust the path to where you cloned the repository e.g. -p ~/repos/flow-of-flows/
prefect agent local start --label dev --no-hostname-label -p ~/projects/flow-of-flows/
prefect run --id 1725e2ce-bc19-4a96-bd87-9a6c7c021d11 --watch
