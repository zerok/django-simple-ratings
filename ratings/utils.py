from math import sqrt

from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import connection

def get_content_object_field(rating_model):
    opts = rating_model._meta
    for virtual_field in opts.virtual_fields:
        if virtual_field.name == 'content_object':
            return virtual_field # break out early
    return opts.get_field('content_object')

def is_gfk(content_field):
    return isinstance(content_field, GenericForeignKey)

def sim_euclidean_distance(ratings_queryset, user_a, user_b):
    rating_model = ratings_queryset.model
    content_field = get_content_object_field(rating_model)
    
    if is_gfk(content_field):
        lookups = ['%s_id' % content_field.ct_field, content_field.fk_field]
    else:
        lookups = ['%s_id' % content_field.name]
    
    lookup_query = ' AND '.join(['r1.%(f)s = r2.%(f)s' % {'f': f} for f in lookups])

    sql = """
    SELECT r1.score - r2.score AS diff
    FROM
        %(ratings_table)s AS r1,
        %(ratings_table)s AS r2
    WHERE
        r1.user_id = %(user_a)s AND
        r2.user_id = %(user_b)s AND
        %(lookup_query)s
        %(queryset_filter)s
    """
    
    rating_query = ratings_queryset.values_list('pk').query
    if rating_query.where.as_sql()[0] is None:
        queryset_filter = ''
    else:
        rating_qs_sql = rating_query.as_sql()[0] % rating_query.as_sql()[1]
        queryset_filter = ' AND r1.id IN (%s)' % rating_qs_sql
    
    params = {
        'ratings_table': rating_model._meta.db_table,
        'user_a': user_a.pk,
        'user_b': user_b.pk,
        'lookup_query': lookup_query,
        'queryset_filter': queryset_filter
    }

    cursor = connection.cursor()
    cursor.execute(sql % params)
    
    sum_of_squares = 0
    while True:
        result = cursor.fetchone()
        if result is None:
            break
        sum_of_squares += result[0] ** 2
    
    return 1 / (1 + sum_of_squares)