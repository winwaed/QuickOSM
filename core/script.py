import datetime

file = '/home/etienne/tmp/houses.osm'
layers = ['points', 'lines', 'multilinestrings', 'multipolygons']
match = {
    'points': 'node',
    'lines': 'way',
    'multilinestrings': 'relation',
}

print(datetime.datetime.now())
for layer in layers:
    source = '{}|layername={}'.format(file, layer)

    if layer != 'multipolygons':
        expression = '\'{}\''.format(match[layer])
    else:
        expression = 'if("osm_way_id",\'way\', \'relation\')'

    params = {
        'INPUT': source,
        'FIELD_NAME': 'osm_type',
        'FIELD_TYPE': 2,
        'FIELD_LENGTH': 15,
        'FIELD_PRECISION': 3,
        'NEW_FIELD': True,
        'FORMULA': expression,
        'OUTPUT': 'memory:'
    }
    result = processing.run("qgis:fieldcalculator", params)

    # Refactoring fields
    params = {
        'INPUT': result['OUTPUT'],
        'FIELDS_MAPPING': [
            {
                'expression': ' left( "osm_type", 1) ||  coalesce( "osm_way_id", "osm_id")',
                'length': 255,
                'name': 'full_id',
                'precision': 0,
                'type': 10
            }, {
                'expression': 'coalesce( "osm_way_id", "osm_id")',
                'length': 255,
                'name': 'osm_id',
                'precision': 0,
                'type': 10
            }, {
                'expression': '"osm_type"',
                'length': 255,
                'name': 'osm_type',
                'precision': 0,
                'type': 10
            }, {
                'expression': '"other_tags"',
                'length': 255,
                'name': 'other_tags',
                'precision': 3,
                'type': 10
            }
        ],
        'OUTPUT': 'memory:'
    }

    result = processing.run("qgis:refactorfields", params)

    params = {
       'INPUT': result['OUTPUT'],
       'FIELD': 'other_tags',
       'OUTPUT': 'memory:'
    }
    result = processing.run("native:explodehstorefield", params)

    params = {
        'INPUT': result['OUTPUT'],
        'COLUMN': ['other_tags'],
        'OUTPUT': 'memory:'}

    processing.runAndLoadResults("qgis:deletecolumn", params)

    print(result)

print(datetime.datetime.now())
