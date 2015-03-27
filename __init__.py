import logging

from sqlalchemy.orm.properties import RelationshipProperty as RelationshipField

from zope.dottedname.resolve import resolve

from .documents import (
    BaseDocument, ESBaseDocument, BaseMixin,
    get_document_cls)
from .serializers import JSONEncoder, ESJSONSerializer
from .signals import ESMetaclass
from .utils import (
    relationship_fields, is_relationship_field,
    relationship_cls)
from .fields import (
    BigIntegerField,
    BooleanField,
    DateField,
    DateTimeField,
    ChoiceField,
    FloatField,
    IntegerField,
    IntervalField,
    BinaryField,
    DecimalField,
    PickleField,
    SmallIntegerField,
    StringField,
    TextField,
    TimeField,
    UnicodeField,
    UnicodeTextField,
    Relationship,
    PrimaryKeyField,
    ForeignKeyField,
)

log = logging.getLogger(__name__)


def includeme(config):
    """ Include required packages. """
    config.include('pyramid_tm')
    config.include('pyramid_sqlalchemy')

    def _valid_global(g):
        ignored = ('log', 'includeme')
        return (not g.startswith('__') and g not in ignored)

    engine_path = config.registry.settings['db_engine']
    config.include(engine_path)
    engine_module = resolve(engine_path)
    engine_globals = {k: v for k, v in engine_module.__dict__.iteritems()
                      if _valid_global(k)}
    globals().update(engine_globals)


def setup_database(config):
    """ Setup db engine, db itself. Create db if not exists. """
    from sqlalchemy import engine_from_config
    from sqlalchemy_utils import database_exists, create_database
    from pyramid_sqlalchemy import BaseObject
    engine = engine_from_config(config.registry.settings, 'sqlalchemy.')
    BaseObject.metadata.bind = engine
    if not database_exists(engine.url):
        log.info(
            'Database does not exit. Creating database at %s' % engine.url)
        create_database(engine.url)
    BaseObject.metadata.create_all(engine)