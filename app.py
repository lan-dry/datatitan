from flask import Flask, render_template
from easybase import get, post, update, delete
from bokeh.models import ColumnDataSource, Select, Slider
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.callbacks import CustomJS

app = Flask(__name__)

offset = None
limit = 50000
""""--------------------"""
labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

transactions = get("pKlngQAWSGXeC43W", offset, limit)
marital = get("diQ0ryFirYwMT8zz", offset, 5000)
incomerange = get("TzcadwKl75tjUUtm", offset, 5000)
print(incomerange)

num = list([d['hshdnum'] for d in transactions])
amount = list([d['transactionamount'] for d in transactions])

num1 = list([d['hshdnum'] for d in marital])
status = list([d['maritalstatus'] for d in marital])

num2 = list([d['hshdnum'] for d in incomerange])
income = list([d['incomerange'] for d in incomerange])
# print(bar)


@app.route('/bar')
def bar():
    bar_labels=num
    bar_values=amount
    return render_template('bar_chart.html', title=' Data in bars ', max=17000, labels=bar_labels, values=bar_values)

@app.route('/line')
def line():
    line_labels=num
    line_values=amount
    return render_template('line_chart.html', title='Data in line', max=17000, labels=line_labels, values=line_values)

@app.route('/pie')
def pie():
    pie_labels = num1
    pie_values = status
    return render_template('pie_chart.html', title='data in pie', max=17000, set=zip(values, labels, colors))

@app.route('/income')
def income():
    line_labels = num2
    line_values = income
    return render_template('income_chart.html', title='Data in line', max=17000, labels=line_labels, values=line_values)

"""----------------------"""
@app.route('/')

def index():
    
    transactioncity_list = ['All', 'CINCINNATI', 'CLEARWATER', 'WAXHAW', 'SIDNEY', 'Richmond', 'PARKERSBURG', 'ELGIN', 'ROUND LAKE', 'EAST PEORIA', 'BARTONVILLE', 'MOORESVILLE', 'TROUTMAN', 'ERLANGER', 'LOUISVILLE', 'ELKHART', 'MERRILLVILLE', 'EVANSVILLE', 'MOORESVILLE', 'ROCKY RIVER', 'WAPAKONETA', 'Columbus', 'LEXINGTON']

    controls = {
        "transactionamount": Slider(title="Min # transaction amount", value=10, start=10, end=200000, step=10),
        "min_year": Slider(title="Start Year", start=1970, end=2021, value=1970, step=1),
        "max_year": Slider(title="End Year", start=1970, end=2021, value=2021, step=1),
        "transactioncity": Select(title="transaction city", value="All", options=transactioncity_list)
    }

    controls_array = controls.values()

    def selectedData():
        res = get("pKlngQAWSGXeC43W", offset, limit)
        return res

    source = ColumnDataSource()

    callback = CustomJS(args=dict(source=source, controls=controls), code="""
        if (!window.full_data_save) {
            window.full_data_save = JSON.parse(JSON.stringify(source.data));
        }
        var full_data = window.full_data_save;
        var full_data_length = full_data.x.length;
        var new_data = { x: [], y: [], color: [], title: [], released: [], imdbvotes: [] }
        for (var i = 1; i < full_data_length; i++) {
            if (full_data.imdbvotes[i] === null || full_data.released[i] === null || full_data.transactioncity[i] === null)
                continue;
            if (
                full_data.imdbvotes[i] > controls.transactionamount.value &&
                Number(full_data.released[i].slice(-4)) >= controls.min_year.value &&
                Number(full_data.released[i].slice(-4)) <= controls.max_year.value &&
                (controls.transactioncity.value === 'All' || full_data.transactioncity[i].split(",").some(ele => ele.trim() === controls.transactioncity.value))
            ) {
                Object.keys(new_data).forEach(key => new_data[key].push(full_data[key][i]));
            }
        }
        
        source.data = new_data;
        source.change.emit();
    """)

    fig = figure(plot_height=600, plot_width=720, tooltips=[("transaction date", "@transactiondate"), ("transaction type", "@transactiontype"), ("merchant city", "@merchantcity")])
    fig.circle(x="x", y="y", source=source, size=5, color="color", line_color=None)
    fig.xaxis.axis_label = "User Identifiers"
    fig.yaxis.axis_label = "User transaction amounts"

    transactions = selectedData()
    # print(transactions)

    source.data = dict(
        x = [d['hshdnum'] for d in transactions],
        y = [d['transactionamount'] for d in transactions],
        color = ["#FF9900" for d in transactions],
        date = [d['transactiondate'] for d in transactions],
        type = [d['transactiontype'] for d in transactions],
        # imdbvotes = [d['imdbvotes'] for d in transactions],
        transactioncity = [d['merchantcity'] for d in transactions]
    )

    for single_control in controls_array:
        single_control.js_on_change('value', callback)

    inputs_column = column(*controls_array, width=320, height=1000)
    layout_row = row([ inputs_column, fig ])

    script, div = components(layout_row)
    return render_template(
        'index.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    )

if __name__ == "__main__":
    app.run(debug=True)