from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_measurement,all_entities,len_numeric,size_categorical,size_numeric,len_categorical,all_subcategory_entities,database,name,name2,block

boxplot_page = Blueprint('boxplot', __name__,
                         template_folder='templates')


@boxplot_page.route('/boxplot', methods=['GET'])
def get_boxplots():

    return render_template('boxplot.html',
                           name='{} number'.format(name),
                           block=block,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_measurement=all_measurement,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical
                           )


@boxplot_page.route('/boxplot', methods=['POST'])
def post_boxplots():
    # get selected entities
    numeric_entities = request.form.get('numeric_entities')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')
    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')

    # handling errors and load data from database
    error = None
    if not measurement:
        error = "Please select number of {}".format(name)
    elif numeric_entities == "Search entity" or categorical_entities == "Search entity":
        error = "Please select entity"
    elif not subcategory_entities:
        error = "Please select subcategory"
    if not error:
        numeric_df,error = ps.get_num_cat_values(numeric_entities, categorical_entities, subcategory_entities,measurement, rdb)
        numeric_df = numeric_df.rename(columns={"Name_ID": "{}".format(name2), "measurement": "{}".format(name)})
        if not error:
            numeric_df = numeric_df.dropna()
            if len(numeric_df.index) == 0:
                error = "This two entities don't have common values"
        else: (None, error)

    if error:
        return render_template('boxplot.html',
                               name='{} number'.format(name),
                               block=block,
                               error=error,
                               all_categorical_entities=all_categorical_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               measurement1=measurement,
                               all_measurement=all_measurement)


    # Plot figure and convert to an HTML string representation
    if block == 'none':
        if how_to_plot == 'linear':
            fig = px.box(numeric_df, x=categorical_entities, y=numeric_entities, color=categorical_entities, template="plotly_white")
        else:
            fig = px.box(numeric_df, x=categorical_entities, y=numeric_entities, color=categorical_entities, template="plotly_white", log_y=True)
    else:
        if how_to_plot == 'linear':
            fig = px.box(numeric_df, x=name, y=numeric_entities, color=categorical_entities, template="plotly_white")
        else:
            fig = px.box(numeric_df, x=name, y=numeric_entities, color=categorical_entities, template="plotly_white", log_y=True)
    fig.update_layout(font=dict(size=16))
    fig = fig.to_html()


    return render_template('boxplot.html',
                           name='{} number'.format(name),
                           block=block,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_measurement=all_measurement,
                           numeric_entities=numeric_entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           measurement1=measurement,
                           plot=fig)
