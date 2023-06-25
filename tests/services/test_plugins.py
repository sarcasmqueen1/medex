import pandas as pd

from interfaces.plugin_interface import PluginInterface
from medex.database_schema import TableCategorical, TableNumerical, Header
from medex.dto.entity import EntityType
from medex.services.importer import PluginImporter


def test_one_numerical_plugin(db_session):
    plugin_folder = '/path/to/plugin/folder'

    db_session.add_all([
        TableNumerical(
            name_id='p1', case_id='c1', measurement='0', date='2021-05-15', key='HNR05', value=32.5
        ),
        TableNumerical(
            name_id='p1', case_id='c1', measurement='0', date='2021-05-15', key='HNR05', value=36.5
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='0', date='2021-05-15', key='HNR05', value=38.5
        ),
        TableNumerical(
            name_id='p3', case_id='c3', measurement='0', date='2021-05-15', key='HNR05', value=39.5
        ),
    ])

    importer = PluginImporter(plugin_folder)

    # Anstatt das plugin_module aus dem Plugin Ordner zu holen und so das tatsächliche Plugin zu laden,
    # wird das Tesplugin in der Klasse genutzt, um verschiedene Testfälle testen zu können
    importer.plugin_modules = [TestPluginOneNumericalValue.get_plugin_class()]

    # 'Mock' für die DB mit der fixtures db
    importer.on_db_ready(db_session)

    # Holt alle Einträge aus table numerical nach Plugin Ausführung
    all_numerical_entries = db_session.query(TableNumerical).order_by(TableNumerical.id).all()

    # Holt die letzten drei Einträge aus num. entries. Werden durch das Plugin geaddet
    added_rows = all_numerical_entries[-3:]

    # Sortiert die Liste nach dem Objektattribut "name_id" aufsteigend
    added_rows.sort(key=lambda x: x.name_id)

    assert len(all_numerical_entries) == 7
    assert len(added_rows) == 3
    assert added_rows[0].name_id == 'p1'
    assert float(added_rows[0].value) == 36.5 + 1
    assert added_rows[1].name_id == 'p2'
    assert float(added_rows[1].value) == 38.5 + 1
    assert added_rows[2].name_id == 'p3'
    assert float(added_rows[2].value) == 39.5 + 1


def test_one_categorical_plugin(db_session):
    plugin_folder = '/path/to/plugin/folder'

    db_session.add_all([
        TableCategorical(
            name_id='p1', case_id='c1', measurement='0', date='2021-05-15', key='Gender', value='male'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='0', date='2021-05-15', key='Gender', value='male'
        ),
        TableCategorical(
            name_id='p3', case_id='c3', measurement='0', date='2022-05-15', key='Gender', value='female'
        )
    ])

    importer = PluginImporter(plugin_folder)
    # Anstatt das plugin_module aus dem Plugin Ordner zu holen und so das tatsächliche Plugin zu laden,
    # wird das Tesplugin in der Klasse genutzt, um verschiedene Testfälle testen zu können

    importer.plugin_modules = [TestPluginOneCategoricalValue.get_plugin_class()]

    # 'Mock' für die DB mit der fixtures db
    importer.on_db_ready(db_session)

    # Holt alle Einträge aus table categorical nach Plugin Ausführung
    all_categorical_entries = db_session.query(TableCategorical).order_by(TableCategorical.id).all()

    # Holt die letzten drei Einträge aus num. entries. Werden durch das Plugin geaddet
    added_rows = all_categorical_entries[-3:]

    # Sortiert die Liste nach dem Objektattribut "name_id" aufsteigend
    added_rows.sort(key=lambda x: x.name_id)

    assert len(all_categorical_entries) == 6
    assert len(added_rows) == 3
    assert added_rows[0].name_id == 'p1'
    assert added_rows[0].value == 'female'
    assert added_rows[1].name_id == 'p2'
    assert added_rows[1].value == 'female'
    assert added_rows[2].name_id == 'p3'
    assert added_rows[2].value == 'male'


def test_two_categorical_plugin(db_session):
    plugin_folder = '/path/to/plugin/folder'

    db_session.add_all([
        TableCategorical(
            name_id='p1', case_id='c1', measurement='0', date='2022-05-15', key='Diabetes', value='no'
        ),
        TableCategorical(
            name_id='p1', case_id='c1', measurement='0', date='2021-05-15', key='Gender', value='male'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='0', date='2022-05-15', key='Diabetes', value='yes'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='0', date='2021-05-15', key='Gender', value='female'
        ),
        TableCategorical(
            name_id='p3', case_id='c3', measurement='0', date='2021-05-15', key='Diabetes', value='yes'
        ),
        TableCategorical(
            name_id='p3', case_id='c3', measurement='0', date='2022-05-15', key='Gender', value='male'
        ),
        TableNumerical(
            name_id='p3', case_id='c3', measurement='0', date='2022-05-15', key='blood pressure', value=135
        )
    ])

    importer = PluginImporter(plugin_folder)
    # Anstatt das plugin_module aus dem Plugin Ordner zu holen und so das tatsächliche Plugin zu laden,
    # wird das Tesplugin in der Klasse genutzt, um verschiedene Testfälle testen zu können
    importer.plugin_modules = [TestPluginTwoCategoricalValues.get_plugin_class()]

    # 'Mock' für die DB mit der fixtures db
    importer.on_db_ready(db_session)

    # Holt alle Einträge aus table categorical nach Plugin Ausführung
    all_categorical_entries = db_session.query(TableCategorical).order_by(TableCategorical.id).all()

    # Holt die letzten drei Einträge aus num. entries. Werden durch das Plugin geaddet
    added_rows = all_categorical_entries[-3:]

    # Sortiert die Liste nach dem Objektattribut "name_id" aufsteigend
    added_rows.sort(key=lambda x: x.name_id)

    assert len(all_categorical_entries) == 9
    assert len(added_rows) == 3
    assert added_rows[0].name_id == 'p1'
    assert added_rows[0].value == 'male_no'
    assert added_rows[1].name_id == 'p2'
    assert added_rows[1].value == 'female_yes'
    assert added_rows[2].name_id == 'p3'
    assert added_rows[2].value == 'male_yes'


def test_categorical_numerical_plugin(db_session):
    plugin_folder = '/path/to/plugin/folder'

    db_session.add_all([
        TableCategorical(
            name_id='p1', case_id='c1', measurement='0', date='2022-05-15', key='Gender', value='male'
        ),
        TableNumerical(
            name_id='p1', case_id='c1', measurement='0', date='2021-05-15', key='Delta9', value=36.5
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='0', date='2022-05-15', key='Gender', value='female'
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='0', date='2021-05-15', key='Delta9', value=129
        ),
        TableCategorical(
            name_id='p3', case_id='c3', measurement='0', date='2021-05-15', key='Gender', value='female'
        ),
        TableNumerical(
            name_id='p3', case_id='c3', measurement='0', date='2022-05-15', key='Delta9', value=135
        )
    ])

    importer = PluginImporter(plugin_folder)
    # set the plugin_modules to the inner class Plugin we want to test
    # anstatt das plugin module aus dem pluin ordner
    # zu holen und es so real zu laden, wird das tesplugin in der klasse genutzt, um konstellationen zu testen
    importer.plugin_modules = [TestPluginCategoricalNumericalValues.get_plugin_class()]

    # 'Mock' für die DB mit der fixtures db
    importer.on_db_ready(db_session)

    # Holt alle Einträge aus table categorical nach Plugin Ausführung
    all_categorical_entries = db_session.query(TableCategorical).order_by(TableCategorical.id).all()

    # Holt die letzten drei Einträge aus num. entries. Werden durch das Plugin geaddet
    added_rows = all_categorical_entries[-3:]

    # Sortiert die Liste nach dem Objektattribut "name_id" aufsteigend
    added_rows.sort(key=lambda x: x.name_id)

    assert len(all_categorical_entries) == 6
    assert len(added_rows) == 3
    assert added_rows[0].name_id == 'p1'
    assert added_rows[0].value == 'male' + '36.5'
    assert added_rows[1].name_id == 'p2'
    assert added_rows[1].value == 'female' + '129.0'
    assert added_rows[2].name_id == 'p3'
    assert added_rows[2].value == 'female' + '135.0'


# Ab hier beginnen die inner class Testplugins für jeden individuellen Testfall
class TestPluginOneNumericalValue(PluginInterface):

    @staticmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        print(df)
        hnr05_numbers = df['HNR05'].tolist()
        name_ids = df['name_id'].tolist()

        result_list = []

        for i in range(len(hnr05_numbers)):
            result_list.append(hnr05_numbers[i] + 1)

        data = {
            "name_id": name_ids,
            "value": result_list
        }
        result_df = pd.DataFrame(data)
        print(result_df)

        return result_df

    @classmethod
    def get_name(cls) -> str:
        return "hnr05_plus_one"

    @classmethod
    def get_param_name(cls) -> tuple[list[str], list[str]]:
        cat_keys = []
        num_keys = ['HNR05']
        return cat_keys, num_keys

    @classmethod
    def get_entity_type(cls) -> EntityType:
        return EntityType.NUMERICAL

    @staticmethod
    def get_plugin_class():
        return TestPluginOneNumericalValue


class TestPluginOneCategoricalValue(PluginInterface):

    @staticmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        print(df)
        gender_list = df['Gender'].tolist()
        name_ids = df['name_id'].tolist()

        result_list = []

        for i in range(len(gender_list)):
            if gender_list[i] == "male":
                result_list.append("female")
            else:
                result_list.append("male")

        data = {
            "name_id": name_ids,
            "value": result_list
        }
        result_df = pd.DataFrame(data)
        print(result_df)

        return result_df

    @classmethod
    def get_name(cls) -> str:
        return "opposite_gender"

    @classmethod
    def get_param_name(cls) -> tuple[list[str], list[str]]:
        cat_keys = ['Gender']
        num_keys = []
        return cat_keys, num_keys

    @classmethod
    def get_entity_type(cls) -> EntityType:
        return EntityType.CATEGORICAL

    @staticmethod
    def get_plugin_class():
        return TestPluginOneCategoricalValue


class TestPluginTwoCategoricalValues(PluginInterface):

    @staticmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        print(df)
        gender_list = df['Gender'].tolist()
        diabetes_list = df['Diabetes'].tolist()
        name_ids = df['name_id'].tolist()

        result_list = []

        for i in range(len(gender_list)):
            result_list.append(gender_list[i] + "_" + diabetes_list[i])

        data = {
            "name_id": name_ids,
            "value": result_list
        }
        result_df = pd.DataFrame(data)
        print(result_df)

        return result_df

    @classmethod
    def get_name(cls) -> str:
        return "gender_diabetes_concat"

    @classmethod
    def get_param_name(cls) -> tuple[list[str], list[str]]:
        cat_keys = ['Gender', 'Diabetes']
        num_keys = []
        return cat_keys, num_keys

    @classmethod
    def get_entity_type(cls) -> EntityType:
        return EntityType.CATEGORICAL

    @staticmethod
    def get_plugin_class():
        return TestPluginTwoCategoricalValues


class TestPluginCategoricalNumericalValues(PluginInterface):

    @staticmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        print(df)
        gender_list = df['Gender'].tolist()
        delta9_numbers = df['Delta9'].tolist()
        name_ids = df['name_id'].tolist()

        result_list = []

        for i in range(len(delta9_numbers)):
            result_list.append(gender_list[i] + str(round(delta9_numbers[i], 1)))

        data = {
            "name_id": name_ids,
            "value": result_list
        }
        result_df = pd.DataFrame(data)
        print(result_df)

        return result_df

    @classmethod
    def get_name(cls) -> str:
        return "gender_plus_number"

    @classmethod
    def get_param_name(cls) -> tuple[list[str], list[str]]:
        cat_keys = ['Gender']
        num_keys = ['Delta9']
        return cat_keys, num_keys

    @classmethod
    def get_entity_type(cls) -> EntityType:
        return EntityType.CATEGORICAL

    @staticmethod
    def get_plugin_class():
        return TestPluginCategoricalNumericalValues
