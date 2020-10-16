
###########################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################
import os
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import plotly.offline as py
import plotly.graph_objs as go
from plotly import tools
import pickle
###########################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################

## Mod 4 Question 1
offset = 1000
max_row = 2000

'''
Retrieve data set of NYC trees through API call using Socrata query.
'''
#------------ Data Part 1 
soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,boroname,health,steward,count(tree_id)' +\
        '&$group=spc_common,boroname,health,steward').replace(' ', '%20')

pg1 = pd.read_json(soql_url)
pg2 = pd.read_json(soql_url + '&$offset=1000')
pg3 = pd.read_json(soql_url + '&$offset=2000')
pg4 = pd.read_json(soql_url + '&$offset=3000')
pg5 = pd.read_json(soql_url + '&$offset=4000')

trees = pd.concat([pg1,pg2,pg3,pg4,pg5])
# Moving the above code as part pickle code logic to speed up logic
# with open("count.pickle","wb") as f:
#         pickle.dump(df, f)
datainput1 = open('count.pickle', 'rb')
trees= pickle.load( datainput1)
datainput1.close()

url = 'https://data.cityofnewyork.us/resource/nwxe-4ae8.json'
trees = pd.read_json(url)

#------------ Data Part 1 
# for x in range(0, max_row, offset):
#     #print('x is ' + str(x))
#     soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$limit=1000&$offset=' + str(x) +\
#         '&$select=borocode,spc_common,health,steward,count(tree_id)' +\
#         '&$group=borocode,spc_common,health,steward').replace(' ', '%20')
#     soql_trees = pd.read_json(soql_url)
#     if(x==0):
#         df = pd.DataFrame(columns=list(soql_trees.columns.values))
#     df = df.append(soql_trees)
#     #print(df)
# Moving above code to pickle
# with open("df.pickle","wb") as f:
#         pickle.dump(df, f)
datainput2 = open('df.pickle', 'rb')
df= pickle.load( datainput2)
datainput2.close()

df = df.reset_index(drop=True)
#Data for Q1:
df_totals = df.groupby(['borocode', 'spc_common'])['count_tree_id'].sum()
df_total_by_borocode_specie_health = df.groupby(['borocode', 'spc_common', 'health'])['count_tree_id'].sum()
df_totals = df_totals.reset_index(drop=False)
df_total_by_borocode_specie_health = df_total_by_borocode_specie_health.reset_index(drop=False)
df_totals.columns = ['borocode', 'spc_common', 'total_for_specie_in_borough']
df_total_by_borocode_specie_health.columns = ['borocode', 'spc_common', 'health', 'total']
tree_proportions = pd.merge(df_total_by_borocode_specie_health, df_totals, on=['borocode', 'spc_common'])
tree_proportions['ratio'] = tree_proportions['total']/ tree_proportions['total_for_specie_in_borough']
tree_proportions.head(10)
#For species dropdown:
species = np.sort(tree_proportions.spc_common.unique())

# Data for Q2
#Reshape data for question 2:
df_total_by_steward = df.groupby(['borocode', 'spc_common', 'steward'])['count_tree_id'].sum()
df_total_by_steward = df_total_by_steward.reset_index(drop=False)
df_total_by_steward.columns = ['borocode', 'spc_common', 'steward', 'steward_total']
df['borocode'] = pd.to_numeric(df['borocode'])
df_steward = pd.merge(df, df_total_by_steward, on=['borocode', 'spc_common', 'steward'])
di = {'Poor':1, 'Fair':2, 'Good':3}
df_steward['health_level'] = df_steward['health'].map(di)
df_steward['health_index'] = (df_steward['count_tree_id']/df_steward['steward_total']) * df_steward['health_level']
df_overall_health_index = df_steward.groupby(['borocode', 'spc_common', 'steward'])['health_index'].sum()
df_overall_health_index = df_overall_health_index.reset_index(drop=False)
df_overall_health_index.columns = ['borocode', 'spc_common', 'steward', 'overall_health_index']
di2 = {'3or4':3, '4orMore':4, 'None':1, '1or2':2}
df_overall_health_index['steward_level'] = df_overall_health_index['steward'].map(di2)
di3 = { 1:'Manhattan', 2:'Bronx', 3:'Brooklyn', 4:'Queens', 5:'Staten Island'}
df_overall_health_index['borough'] = df_overall_health_index['borocode'].map(di3)
df_overall_health_index['spc_common'] = df_overall_health_index['spc_common'].apply(lambda x: x.title())
#For species dropdown:
species = np.sort(tree_proportions.spc_common.unique())
# ------------
#gather data for question 1 
trees_q1 = trees[['spc_common','health','boroname']]
#convert nans to 'Uknown'
trees_q1['spc_common'].fillna('Unknown',inplace = True)
#drop remaining nans
trees_q1.dropna(inplace = True)

#identify different health conditions
statuses = list(set(trees_q1['health']))
#create colors for different health conditions
colors = ['rgb(49,130,189)','rgb(204,204,204)','rgba(222,45,38,0.8)']

#create columns that specify tree health conditions
for status in set(trees_q1['health']):
    trees_q1[status] = np.where(trees_q1['health']==status,1,0)
    
trees_q1 = pd.DataFrame(trees_q1.groupby(['boroname','spc_common']).sum())

#find out boroughs
boroughs = list(set(trees['boroname']))

#calculate proportion of trees in different conditions
trees_q1['total'] = trees_q1.sum(axis=1)
for column in list(trees_q1.columns):
    trees_q1[column] = (trees_q1[column]/trees_q1['total'])*100
trees_q1.head()

#create list to store data for each borough
trace_list = []

#create plot titles
borough_list = list(map(lambda x: str(x), boroughs))
row = 1
col = len(boroughs)

fig_q1 = tools.make_subplots(rows=row, cols=col, subplot_titles=tuple(borough_list))

#iterate through boroughs
for borough in boroughs:
        for i in range(0,len(statuses)):
            trace = go.Bar(
            x = list(trees_q1.loc[borough].index),
            y = list(trees_q1.loc[borough][statuses[i]]),
            name = statuses[i],
            marker=dict(color=colors[i])
            )
            trace_list += [trace]

row_i = []
col_j = []
for i in range(1,row+1):
    for j in range (1,col+1):
        for n in range (1,4):
            row_i.append(i)
            col_j.append(j)

for i in range(0,len(trace_list)):        
     fig_q1.append_trace(trace_list[i], row_i[i],col_j[i]) 
 
        
fig_q1['layout'].update(showlegend=False,height=400, width=1400, title='Proportion of Trees in Good, Fair and Poor Conditions', barmode='stack')

#---------------
## Mod 4 Question 2
## Are stewards (steward activity measured by the ‘steward’ variable) having an impact on the health of trees?

#Are stewards (steward activity measured by the 'steward' variable) having an impact on the health of trees? In order to answer this question correlation between 'stewards' amnd 'health' should be correlated.

trees_q1 = trees[['spc_common','status','boroname']]
trees_q1['spc_common'].fillna('Unknown',inplace = True)

#create columns that specify tree status
for status in set(trees_q1['status']):
    trees_q1[status] = np.where(trees_q1['status']==status,1,0)
    
trees_q1 = pd.DataFrame(trees_q1.groupby(['boroname','spc_common']).sum())
trees_q1.head()

#find out boroughs
boroughs = list(set(trees['boroname']))

trace_list_q2 =[]

#create plot titles
borough_list = list(map(lambda x: str(x), boroughs))

trees_q2 = trees[['spc_common','health','boroname','steward']]

trees_q2['spc_common'].fillna('Unknown',inplace = True)
trees_q2.dropna(inplace = True)
trees_q2[['steward','health']] = trees_q2[['steward','health']].apply(lambda x : pd.factorize(x)[0])
trees_q2_cor = pd.DataFrame(trees_q2.groupby(['boroname','spc_common']).corr())
fig_q2 = tools.make_subplots(rows=1, cols=len(boroughs), subplot_titles=tuple(borough_list))

boroughs = list(set(trees_q2['boroname']))
plants = list(set(trees_q2['spc_common']))

for borough in boroughs:
    trace = go.Bar(
            x = list(trees_q1.loc[borough].index),
            y = list(trees_q2_cor.loc[borough]['steward'][::2])
            )
    trace_list_q2 += [trace]

for i in range(len(boroughs)):
    fig_q2.append_trace(trace_list_q2[i], 1, i+1) 
        
fig_q2['layout'].update(showlegend=False,height=500, width=1400, title='Proportion of Trees in Good, Fair and Poor Conditions')



## App code
colors = {
    'background': '#ffffff',
    'text': '#111111'
}

'''
Code below if for DASH application
'''
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

## BOOTSTRAP
 
cresult1 = html.Div(
    [
        dbc.Card(
            dbc.CardBody("This is some text within a card body"),
            className="mb-3",
        ),
        dbc.Card("This is also within a body", body=True),
    ]
)

card_content2 = [
    dbc.CardHeader("Question 2 :Are stewards (steward activity measured by the 'steward' variable) having an impact on the health of trees? In order to answer this question correlation between 'stewards' amnd 'health' should be correlated."),
    dbc.CardBody(
        [
            html.H5("Solution", className="card-title"),
            html.P("An overall health index is determined by assigning a numeric value to each health level (Poor=1, Fair=2, Good=3) and then calculating a weighted average for the selected specie for each borough. The overall health index score has a minimum score of 1 and a maximum score of 3.",
                 className="card-text",
            ),
            dbc.Col(dcc.Graph(id="graph-health")),           
        ]
    ),
]


card_content1 = [
    dbc.CardHeader("Question 1: What proportion of trees are in good, fair, or poor health according to the 'health' variable?"),
    dbc.CardBody(
        [
            html.H5("Solution", className="card-title"),
            html.P(
                "The application will allow arborist to select one specie, and the application will display proportion of trees that are in good, fair, or poor health across all boroughs.",
                className="card-text",
            ),
            html.Div(dcc.Graph(id="graph-ratio")),
            
        ]
    ),
]
cards =  dbc.Row([dbc.Col(card_content1, width=12), dbc.Col(card_content2, width=12)])
# cards = html.Div(
#      dbc.Row(
#          dbc.Col(dbc.Card(card_content1, color="light"))
#      ),
#      dbc.Row(
#         dbc.Col(dbc.Card(card_content2, color="light"))
#      )
# )
    
controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Choose Specie"),
                dcc.Dropdown(
                    id="specie-variable",
                    options=[{'label': i, 'value': i} for i in species],
                    value="'Schubert' Chokecherry",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Choose Borough"),
                dcc.Dropdown(
                    id="borough-variable",
                     options=[
                        {"label": i, "value": i}
                        for i in [
                            "Bronx",
                            "Brooklyn",
                            "Manhattan",
                            "Queens",
                            "Staten Island",
                        ]
                    ],
                    value="Bronx",
                    searchable=True,
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Cluster count"),
                html.Span(id="example-output", style={"vertical-align": "middle"}),
                dbc.Button("Exist", id="example-button", className="mr-2")
            ]
        ),
        dbc.FormGroup(
            [
                  
                   dbc.Spinner(html.Div(id="loading-output")),
            ]
        )
        
    ],
    body=True,
)



app.layout = dbc.Container(
    [
        html.H1("Selection"),
        html.Hr(),
        # dbc.Row(progress),
        dbc.Row([
            dbc.Col(controls,md=4),
            dbc.Col(cards)]
            ),
        dbc.Row(
            [   #dbc.Spinner(html.Div(id="loading-output")),     
                # dbc.Col(dcc.Graph(id="graph-ratio"),md=6,xs=12, lg=6),
                # dbc.Col(dcc.Graph(id="graph-health"),md=6,xs=12, lg=6)
            ],
            align="center",
        ),
    ],
    fluid=True,
)

# @app.callback(
#     [Output("progress", "value"), Output("progress", "children")],
#     [Input("progress-interval", "n_intervals")],
# )
# def update_progress(n):
#     # check progress of some background process, in this example we'll just
#     # use n_intervals constrained to be in 0-100
#     progress = min(n % 110, 100)
#     # only add text after 5% progress to ensure text isn't squashed too much
#     return progress, f"{progress} %" if progress >= 5 else ""




@app.callback(
    Output("example-output", "children"), 
    [Input("example-button", "n_clicks")]
)
def on_button_click(n):
    if n is None:
        return "Not clicked."
    else:
       return app.stop()
    
    
    
## BOOTSTRAP

# app.layout = html.Div(children=[
#      ######################################################################################################################################################################
#     html.H2('Select Tree Specie'),
#     dcc.Dropdown(
#         id='specie-variable', 
#         options=[{'label': i, 'value': i} for i in species],
#         value="'Schubert' Chokecherry",
#         style={'height': 'auto', 'width': '300px'}
#     ),
#     dcc.Dropdown(
#                     id="borough-variable",
#                     options=[
#                         {"label": i, "value": i}
#                         for i in [
#                             "Bronx",
#                             "Brooklyn",
#                             "Manhattan",
#                             "Queens",
#                             "Staten Island",
#                         ]
#                     ],
#                     value="Bronx",
#                     searchable=True,
#                 ),
#     html.H3(
#         children='Question #1',
#         style={
#             'textAlign': 'center',
#             'color': colors['text']
#         }
#     ),
#      html.Div(children='Proportion of trees in Good, Fair and Poor conditions', style={
#         'textAlign': 'center',
#         'color': colors['text']
#     }),
#      html.Div([
#         dcc.Graph(figure=fig_q1, id='my-figure-q1')
#     ]),
#     html.H1(children='NYC Street Tree Health'),
#     html.P('These graphics display the overall health of trees along city streets in NYC'),
#     html.P('First select a Borough: '),
#     dcc.RadioItems(
#         id='dropdown-a',
#         options=[{'label': i, 'value': i} for i in ['Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island']],
#         value='Queens'
#     ),
#     html.Div(id='output-a'),
#     html.P("0 = Poor Health; 1 = Fair Health, 2 = Good Health"),
#     dcc.RadioItems(
#         id='dropdown-b',
#         options=[{'label': i, 'value': i} for i in df['spc_common'].unique()],
#         value='None'
#     ),
#     html.Div(id='output-b'),
#     html.P("0 = Poor Health; 1 = Fair Health, 2 = Good Health"),
#     ######################################################################################################################################################################
#     html.H1(
#         children='Question #2',
#         style={
#             'textAlign': 'center',
#             'color': colors['text']
#         }
#     ),
#      html.Div(children='Correlation between stewards and health of trees', style={
#         'textAlign': 'center',
#         'color': colors['text']
#     }),
#     html.Div([
#         dcc.Graph(figure=fig_q2, id='my-figure-q2'),
#           dcc.Graph(id='graph-ratio')
# 	])
# ])

# -- CALL BACK FOR SPIN
@app.callback(
    Output("loading-output", "children"), [
        Input("specie-variable", "value"),
        Input("borough-variable", "value")
    ],
)
def load_output(s,b):
    if b:
        time.sleep(10)
    else :
        time.sleep(5)

# -- CALL BACK FOR SPIN


@app.callback(
    Output("graph-ratio", "figure"),
    [
        Input("specie-variable", "value"),
        Input("borough-variable", "value")
    ],
)
def make_graph(selected_specie, selected_borough):
    print("CALLING FM.........................")
    filtered_df = tree_proportions[tree_proportions.spc_common == selected_specie]
    #borocode: 1 (Manhattan), 2 (Bronx), 3 (Brooklyn), 4 (Queens), 5 (Staten Island)
    manhattan = filtered_df[filtered_df.borocode == 1]
    bronx = filtered_df[filtered_df.borocode == 2]
    brooklyn = filtered_df[filtered_df.borocode == 3]
    queens = filtered_df[filtered_df.borocode == 4]
    staten_island = filtered_df[filtered_df.borocode == 5]
    
    traces = []

    traces.append(go.Bar(
    x=queens['health'],
    y=queens['ratio'],
    name='Queens',
    opacity=0.9
    ))

    traces.append(go.Bar(
    x=manhattan['health'],
    y=manhattan['ratio'],
    name='Manhattan',
    opacity=0.9
    ))

    traces.append(go.Bar(
    x=bronx['health'],
    y=bronx['ratio'],
    name='Bronx',
    opacity=0.9
    ))

    traces.append(go.Bar(
    x=brooklyn['health'],
    y=brooklyn['ratio'],
    name='Brooklyn',
    opacity=0.9
    ))

    traces.append(go.Bar(
    x=staten_island['health'],
    y=staten_island['ratio'],
    name='Staten Island',
    opacity=0.9
    ))
    
    return go.Figure(
        data= traces,
        layout= go.Layout(
            xaxis={'title': 'Health of Trees'},
            yaxis={'title': 'Proportion of Trees in Borough'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend=dict(x=-.1, y=1.2)
        )
    )
    
@app.callback(
    Output('graph-health', 'figure'),
    [Input("specie-variable", "value"),
     Input("borough-variable", "value")]
)

def update_figure2(selected_specie,selected_borough):
    print('here: ' + selected_specie + ' Loc: ' + selected_borough)
    filtered_df =  df_overall_health_index[df_overall_health_index.spc_common.str.upper() == str.upper(selected_specie)]
    traces2 = []
        
    for i in filtered_df.borough.unique():
        df_by_borough = filtered_df[filtered_df['borough'] == i]
        traces2.append(go.Scatter(
            x=df_by_borough['steward_level'],
            y=df_by_borough['overall_health_index'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))
    print(traces2)
    return go.Figure(
        data= traces2,
        layout= go.Layout(
            yaxis={'title': 'Overall Health Index'},
            xaxis=dict(tickvals = [1,2,3,4], ticktext = ['None', '1or2', '3or4', '4orMore'], title='Steward'),
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},legend=dict(x=-.1, y=1.2)))


if __name__ == '__main__':
    app.run_server(debug=True)