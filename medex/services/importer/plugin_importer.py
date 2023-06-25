import importlib
import importlib.util
import os
import pathlib
from datetime import datetime

import pandas as pd
from sqlalchemy import and_, func
from sqlalchemy.orm import Query, aliased

from interfaces.plugin_interface import PluginInterface
from medex.database_schema import TableCategorical, TableNumerical, NameType
from medex.dto.entity import EntityType


class PluginImporter:
    def __init__(self, plugin_folder):
        self.plugin_folder = plugin_folder
        self.plugin_modules = []
        # list[calc_plugin] = []

    @staticmethod
    def _get_module_name(file):
        module_name = os.path.splitext(file)[0]
        return module_name

    # Hier werden nach Ausführung alle vorhandene Plugins geladen.
    def load_plugins(self):
        print("start load_plugins")
        plugin_files = self._get_plugin_files()

        for file in plugin_files:
            print("file in plugin_files")
            module_name = PluginImporter._get_module_name(file)
            plugin_module = self._import_module(module_name, file)
            print(plugin_module)
            if plugin_module is not None:
                print("adding Plugin to plugin_modules")
                self.plugin_modules.append(plugin_module)

    def _get_plugin_files(self):
        if not os.path.exists(self.plugin_folder):
            return []

        folders = pathlib.Path(self.plugin_folder).glob('*/')
        plugin_files: list[str] = [str(plugin) for folder in folders for plugin in folder.glob('*.py')]
        return plugin_files

    # Hier wird die Liste mit den bereits geladenen Plugins benutzt und diese werden automatisch ausgeführt.
    def on_db_ready(self, db_session):
        print('Start on_db_ready')

        for plugin_module in self.plugin_modules:
            print('current Plugin: ' + plugin_module.get_name())
            table = TableNumerical if plugin_module.get_entity_type() == EntityType.NUMERICAL else TableCategorical
            query = self.build_query(db_session, plugin_module, table)
            entity_key = f'calculated_{plugin_module.get_name()}'

            resultList = query.all()
            print(resultList)
            df = pd.DataFrame(query.all())

            if df.empty:
                print('No suitable database entries found')
                return
            print('current Plugin: ' + plugin_module.get_name())

            calc_result = plugin_module.calculate(self, df)
            db_session.merge(
                NameType(key=entity_key, synonym=entity_key, description='', unit='', show='', type="String")
            )

            today = datetime.now()

            date = today.strftime("%d/%m/%Y")
            time = today.strftime("%H:%M:%S")

            for index, row in calc_result.iterrows():
                calc_row = table(
                    name_id=row["name_id"],
                    key=entity_key,
                    value=row["value"],
                    case_id=row["name_id"],
                    measurement="",
                    date=date,
                    time=time
                )
                db_session.add(calc_row)

            db_session.commit()
            print(f'{plugin_module.get_name}: Added entries f {len(calc_result)} patients')

    @staticmethod
    def _import_module(module_name, file):
        try:
            spec = importlib.util.spec_from_file_location(module_name, file)
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)

            get_class_function_name = 'get_plugin_class'

            if not hasattr(plugin_module, get_class_function_name):
                return None

            get_plugin_class = getattr(plugin_module, get_class_function_name)
            PluginClass = get_plugin_class()

            plugin = PluginClass()

            if issubclass(PluginClass, PluginInterface):
                return plugin
            else:
                print(f"Error importing module '{module_name}': Does not implement PluginInterface")
                return None

        except Exception as e:
            print(f"Error importing module '{module_name}': {e}")

        return None

    # Bildet die base query und ruft danach join() auf.
    def build_query(
            self,
            database_session,
            plugin,
            table
    ) -> Query:
        cat_keys, num_keys = plugin.get_param_name()

        query = database_session.query(table.name_id) \
            .group_by(table.name_id)

        query = self.join(query, table, TableCategorical, cat_keys)
        query = self.join(query, table, TableNumerical, num_keys)

        print(query)
        return query

    # Hier werden die joins zur query hinzugefügt.
    @classmethod
    def join(cls, query: Query, base_table, current_table, keys: list[str]) -> Query:
        for key in keys:
            alias = aliased(current_table, name='table_' + key)
            query = query.join(
                alias,
                and_(
                    base_table.name_id == alias.name_id,
                    alias.key == key
                )
            ).add_columns(
                func.max(alias.value).label(key)
            )

        return query
