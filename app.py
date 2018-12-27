import dash
import dash_core_components as dcc
import dash_html_components as html

import eda 

df = eda.read_data()

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H4(children='Rentfaster Data'),
    generate_table(df)
])

if __name__ == '__main__':
    # Basic start with dash. This may be a challenge...
    app.run_server(debug=True)