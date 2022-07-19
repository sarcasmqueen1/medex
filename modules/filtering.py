def clean_filter(r):
    sql = "DROP TABLE IF EXISTS temp_table_ids"
    sql_drop = "DROP TABLE IF EXISTS temp_table_name_ids"

    r.execute(sql)
    r.execute(sql_drop)


def first_filter(query, query2, r):
    create_table = """ CREATE TEMP TABLE IF NOT EXISTS temp_table_name_ids as ({}) """.format(query)
    create_table_2 = """ CREATE TEMP TABLE IF NOT EXISTS temp_table_ids as ({}) """.format(query2)

    r.execute(create_table)
    r.execute(create_table_2)


def next_filter(query, query2, r):
    create_table = """ DELETE FROM temp_table_name_ids WHERE name_id NOT IN ({})""".format(query)
    create_table_2 = """ INSERT INTO temp_table_ids ({}) """.format(query2)

    r.execute(create_table)
    r.execute(create_table_2)


def add_categorical_filter(filters, n, r):
    subcategory = "$$" + "$$,$$".join(filters[1].get('sub')) + '$$'

    query = """SELECT DISTINCT ec.name_id FROM examination_categorical ec 
                WHERE ec.key = '{0}' AND ec.value IN ({1}) 
    """.format(filters[0].get('cat'), subcategory)
    query2 = """SELECT DISTINCT ec.name_id,ec.key FROM examination_categorical ec 
    WHERE ec.key = '{0}' AND ec.value IN ({1}) """.format(filters[0].get('cat'), subcategory,)

    if n == 1:
        first_filter(query, query2, r)
    else:
        next_filter(query, query2, r)


def add_numerical_filter(filters, n, r):
    from_to = filters[1].get('from_to').split(";")
    query = """ SELECT DISTINCT en.name_id FROM examination_numerical en 
    WHERE en.key = '{0}'  AND en.value BETWEEN {1} AND {2}""".format(filters[0].get('num'), from_to[0], from_to[1])
    query2 = """ SELECT DISTINCT en.name_id,en.key FROM examination_numerical en 
    WHERE key = '{0}' AND en.value BETWEEN {1} AND {2} """.format(filters[0].get('num'), from_to[0], from_to[1])

    if n == 1:
        first_filter(query, query2, r)
    else:
        next_filter(query, query2, r)


def create_temp_table_case_id(case_id, n, check_case_id, r):
    case_id_all = "$$" + "$$,$$".join(case_id) + "$$"

    query = """ SELECT DISTINCT name_id FROM patient WHERE case_id in ({0}) """.format(case_id_all)

    query2 = """ SELECT name_id,(CASE WHEN case_id !='' THEN 'case_id' END) as key 
    from patient where case_id in ({0}) """.format(case_id_all)
    if check_case_id == 'Yes' and n == 1:
        clean_filter(r)
    elif check_case_id == 'Yes' and n != 1:
        remove_one_filter('case_id', n, r)

    if n == 1:
        first_filter(query, query2, r)
    else:
        next_filter(query, query2, r)


def remove_one_filter(filters, filter_update, r):
    update_table = """ DELETE FROM temp_table_ids WHERE key = '{}' """.format(filters)
    sql_drop = "DROP TABLE IF EXISTS temp_table_name_ids"

    query = """ SELECT name_id FROM temp_table_ids 
                    GROUP BY name_id 
                    HAVING count(name_id) = {} """.format(filter_update)
    create_table = """ CREATE TEMP TABLE temp_table_name_ids as ({}) """.format(query)

    r.execute(update_table)
    r.execute(sql_drop)
    r.execute(create_table)
