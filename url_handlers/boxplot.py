from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
import url_handlers.filtering as filtering
from webserver import rdb, all_numeric_entities_sc, all_categorical_entities_sc, all_measurement,\
    all_subcategory_entities, measurement_name,Name_ID, block, data

boxplot_page = Blueprint('boxplot', __name__,
                         template_folder='templates')


@boxplot_page.route('/boxplot', methods=['GET'])
def get_boxplots():
    categorical_filter, categorical_names = filtering.check_for_filter_get(data)
    return render_template('boxplot.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           all_categorical_entities=all_categorical_entities_sc,
                           all_numeric_entities=all_numeric_entities_sc,
                           all_subcategory_entities=all_subcategory_entities,
                           all_measurement=all_measurement,
                           filter=categorical_filter,
                           )


@boxplot_page.route('/boxplot', methods=['POST'])
def post_boxplots():

    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')

    numeric_entities = request.form.get('numeric_entities')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')

    id_filter = data.id_filter
    categorical_filter, categorical_names, categorical_filter_zip = filtering.check_for_filter_post(data)

    # handling errors and load data from database
    error = None
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif numeric_entities == "Search entity" or categorical_entities == "Search entity":
        error = "Please select entity"
    elif not subcategory_entities:
        error = "Please select subcategory"
    if not error:
        df, error = ps.get_num_cat_values(numeric_entities, categorical_entities, subcategory_entities, measurement,
                                          categorical_filter, categorical_names, id_filter, rdb)
        df = filtering.checking_for_block(block, df, Name_ID, measurement_name)
        numeric_entities_unit, error = ps.get_unit(numeric_entities, rdb)
        if numeric_entities_unit:
            numeric_entities_unit = numeric_entities + ' (' + numeric_entities_unit + ')'
            df.columns = [Name_ID, numeric_entities_unit,categorical_entities]
        else:
            numeric_entities_unit = numeric_entities
        if not error:
            df = df.dropna()
            if len(df.index) == 0:
                error = "This two entities don't have common values"

    if error:
        return render_template('boxplot.html',
                               name='{}'.format(measurement_name),
                               block=block,
                               error=error,
                               all_categorical_entities=all_categorical_entities_sc,
                               all_numeric_entities=all_numeric_entities_sc,
                               all_subcategory_entities=all_subcategory_entities,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               measurement1=measurement,
                               all_measurement=all_measurement,
                               filter=categorical_filter_zip,
                               how_to_plot=how_to_plot
                               )

    # Plot figure and convert to an HTML string representation
    if block == 'none':
        if how_to_plot == 'linear':
            fig = px.box(df, x=categorical_entities, y=numeric_entities_unit, color=categorical_entities, template="plotly_white")
        else:
            fig = px.box(df, x=categorical_entities, y=numeric_entities_unit, color=categorical_entities, template="plotly_white", log_y=True)
    else:
        if how_to_plot == 'linear':
            fig = px.box(df, x=measurement_name, y=numeric_entities_unit, color=categorical_entities, template="plotly_white")
        else:
            fig = px.box(df, x=measurement_name, y=numeric_entities_unit, color=categorical_entities, template="plotly_white", log_y=True)
    fig.update_layout(font=dict(size=16))
    fig = fig.to_html()

    return render_template('boxplot.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           all_categorical_entities=all_categorical_entities_sc,
                           all_numeric_entities=all_numeric_entities_sc,
                           all_subcategory_entities=all_subcategory_entities,
                           all_measurement=all_measurement,
                           numeric_entities=numeric_entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           measurement1=measurement,
                           filter=categorical_filter_zip,
                           how_to_plot=how_to_plot,
                           plot=fig)
