# import the Flask class from the flask module
from flask import Flask, redirect, session, send_file
import os
import io
from modules.import_scheduler import Scheduler
import modules.load_data_postgre as ps
from db import connect_db


# create the application object
app = Flask(__name__)
SESSION_TYPE = 'redis'
app.secret_key = os.urandom(24)
with app.app_context():
    rdb = connect_db()


def check_for_env(key: str, default=None, cast=None):
    if key in os.environ:
        if cast:
            return cast(os.environ.get(key))
        return os.environ.get(key)
    return default

# date and hours to import data
day_of_week = check_for_env('IMPORT_DAY_OF_WEEK', default='mon-sun')
hour = check_for_env('IMPORT_HOUR', default=5)
minute = check_for_env('IMPORT_MINUTE', default=5)


# Import data using function scheduler from package modules
if os.environ.get('IMPORT_DISABLED') is None:
    scheduler = Scheduler(rdb,day_of_week=day_of_week, hour=hour, minute=minute)
    scheduler.start()
    scheduler.stop()

# get all numeric and categorical entities from database
all_numeric_entities = ps.get_numeric_entities(rdb)
all_categorical_entities, all_subcategory_entities = ps.get_categorical_entities(rdb)
all_entities = all_numeric_entities .append(all_categorical_entities, ignore_index=True, sort=False)
all_entities = all_entities.to_dict('index')
all_numeric_entities = all_numeric_entities.to_dict('index')
all_categorical_entities = all_categorical_entities.to_dict('index')
all_visit = ps.get_visit(rdb)

# Urls in the 'url_handlers' directory (one file for each new url)
# import a Blueprint

from url_handlers.data import data_page
from url_handlers.basic_stats import basic_stats_page
from url_handlers.histogram import histogram_page
from url_handlers.boxplot import boxplot_page
from url_handlers.scatter_plot import scatter_plot_page
from url_handlers.barchart import barchart_page
from url_handlers.heatmap import heatmap_plot_page
from url_handlers.clustering_pl import clustering_plot_page
from url_handlers.coplots_pl import coplots_plot_page
from url_handlers.logout import logout_page

# register blueprints here:
app.register_blueprint(data_page)
app.register_blueprint(logout_page)
app.register_blueprint(basic_stats_page)
app.register_blueprint(histogram_page)
app.register_blueprint(boxplot_page)
app.register_blueprint(scatter_plot_page)
app.register_blueprint(barchart_page)
app.register_blueprint(heatmap_plot_page)
app.register_blueprint(clustering_plot_page)
app.register_blueprint(coplots_plot_page)


""" Direct to Basic Stats website during opening the program."""
@app.route('/', methods=['GET'])
def login():
    return redirect('/basic_stats')

@app.route("/download", methods=['GET', 'POST'])
def download():

    csv = session["df"] if "df" in session else ""
    # Create a string buffer
    buf_str = io.StringIO(csv)

    # Create a bytes buffer from the string buffer
    #buf_byt = io.BytesIO(buf_str.read().encode("utf-8"))
    return send_file(buf_str,
                    mimetype='"text/csv"',
                    as_attachment=True,
                    attachment_filename="data.csv"
                    )

def main():
    return app
