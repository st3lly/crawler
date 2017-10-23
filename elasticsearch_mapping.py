from elasticsearch_dsl import Mapping
from elasticsearch_dsl.connections import connection

connections.create_connection(hosts = ['localhost'])

def createMapping():
    m = Mapping('car')

    m.field('title', 'text')
    m.field('price', 'integer')
    m.field('date_of_production', 'text')
    m.field('mileage', 'integer')
    m.field('fuel', 'text')
    m.field('cubic_capacity', 'text')
    m.field('power', 'text')
    m.field('gearbox', 'text')
    m.field('body', 'text')
    m.field('drive', 'text')
    m.field('color', 'text')
    m.field('safety', 'text')
    m.field('comfort', 'text')
    m.field('other_equipment', 'text')
    m.field('more_details', 'text')
    m.field('notes', 'text')

    m.save('autobazar')

if __name__ == '__main__':
    createMapping()
