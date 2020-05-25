import psycopg2.extras
import os
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
host = os.environ['POSTGRES_HOST']
database = os.environ['POSTGRES_DB']
port = os.environ['POSTGRES_PORT']
DATABASE_URL=f'postgresql://{user}:{password}@{host}:{port}/{database}'

r = psycopg2.connect(DATABASE_URL)

def create_table(header):
    """create table in the PostgreSQL database"""
    sql1 = "DROP TABLE IF EXISTS name_type,examination,examination_categorical,examination_numerical"

    statment_entities = """CREATE TABLE name_type ("Key" text Primary key, "type" text)"""
    with open(header, 'r') as in_file:
        statment_examination = "CREATE TABLE examination ("
        for line in in_file:
            statment_examination = statment_examination + '{}'.format(line)
        statment_examination = statment_examination + ")"
    in_file.close()
    print('start')
    cur = r.cursor()
    cur.execute(sql1)
    r.commit()
    cur.execute(statment_entities)
    r.commit()
    cur.execute(statment_examination)
    r.commit()


def load_data(entities,dataset,header):
    cur = r.cursor()
    with open(entities, 'r') as in_file:
        print('open')
        for row in in_file:
            row = row.replace("\n", "").split(",")
            cur.execute("INSERT INTO name_type VALUES (%s, %s) ON CONFLICT DO NOTHING",row)
    r.commit()
    in_file.close()
    print('stop')
    a=[]
    with open(header) as in_file:
        row_count = sum(1 for row in in_file)
    in_file.close()
    for i in range(row_count):
        a.append('%s')
    col = ','.join(a)
    with open(dataset, 'r') as in_file:
        print('start2')
        for row in in_file:
            row = row.replace("\n", "").split(",")
            cur.execute("INSERT INTO examination VALUES ("+col+")", row)
    r.commit()
    in_file.close()
    print('stop')


def alter_table():
    cur = r.cursor()
    sql1 = """CREATE TABLE examination_categorical AS SELECT e.* from examination as e join name_type as n
            on e."Key" = n."Key" where n."type" = 'String'"""
    sql2 = """CREATE TABLE examination_numerical AS SELECT e.* from examination as e join name_type as n
                on e."Key" = n."Key" where not n."type" = 'String'"""
    sql3 = """ALTER TABLE examination_numerical ALTER COLUMN "Value" Type double precision Using ("Value"::double precision)"""
    sql4 = """CREATE INDEX "Key_index" ON examination_numerical("Key")"""
    sql5 = """CREATE EXTENSION IF NOT  EXISTS tablefunc"""
    sql6 = """DROP TABLE examination"""
    cur.execute(sql1)
    r.commit()
    cur.execute(sql2)
    r.commit()
    cur.execute(sql3)
    r.commit()
    cur.execute(sql4)
    r.commit()
    cur.execute(sql5)
    r.commit()





















