from os import unlink
from os.path import dirname, join, exists
from unittest.mock import MagicMock

from pytest import fixture
from sqlalchemy import select, func
from integration_tests.fixtures.db_session import db_session  # noqa

from medex.database_schema import TableNumerical, TableCategorical
from medex.services.config import Config, set_config
from medex.services.importer import get_importer, PluginImporter


@fixture
def config():
    my_config = Config(import_directory=join(dirname(__file__), 'data/plugin_importer'))
    set_config(my_config)
    yield my_config


@fixture()
def marker(config):
    yield
    if exists(config.import_marker_path):
        unlink(config.import_marker_path)


def test_plugin_importer(db_session, config, marker):
    importer = get_importer()
    importer.setup_database()

    rs_num = db_session.execute(select(func.count(TableNumerical.id).label('count'))).first()
    numerical_values = rs_num.count
    rs_cat = db_session.execute(select(func.count(TableCategorical.id).label('count'))).first()
    categorical_values = rs_cat.count

    # Holt alle Einträge aus table numerical nach Plugin Ausführung
    all_numerical_entries = db_session.query(TableNumerical).order_by(TableNumerical.id).all()

    # Holt die letzten drei Einträge aus num. entries. Werden durch das Plugin geaddet
    added_rows = all_numerical_entries[-3:]

    # Sortiert die Liste nach dem Objektattribut "name_id" aufsteigend
    added_rows.sort(key=lambda x: x.name_id)

    assert numerical_values + categorical_values == 12
    assert len(added_rows) == 3
    assert added_rows[0].name_id == 'p000024'
    assert float(added_rows[0].value) == 1.7 + 37.5
    assert added_rows[1].name_id == 'p000042'
    assert float(added_rows[1].value) == 0.9 + 56.7
    assert added_rows[2].name_id == 'p000098'
    assert float(added_rows[2].value) == 91.8 + 0.8


def test_load_plugins():
    plugin_folder = 'plugins/calculation_plugin/calc_plugin'
    importer = PluginImporter(plugin_folder)

    importer._import_module = MagicMock(return_value=None)

    importer.load_plugins()
    assert importer._import_module.call_count == len(importer._get_plugin_files())
