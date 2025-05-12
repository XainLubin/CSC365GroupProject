dump_sql:
   export PGPASSWORD="spencerperley11"
   pg_dump -h aws-0-us-east-2.pooler.supabase.com -U postgres.rzrrlmaylovxlbljigxd -d postgres -p 5432 -Fc --no-owner --no-comments -n public -f backup.sql

copy_to_docker:
   docker cp backup.sql mypostgres:/backup.sql

run:
   find /home/spenc/calPoly/class/db/potions/src/api/ -type f | entr -r uv run main.py

freeze_packages:
   uv pip compile pyproject.toml -o requirements.txt

