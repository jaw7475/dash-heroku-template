import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://raw.githubusercontent.com/jaw7475/dash-heroku-template/master/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

context = """
According to the American Association of University Women, still in 2022, women working full time only make 83 cents 
on the male dollar. At the current rate of equity improvement, women would not achieve pay equity until 2111. This 
persistent pay gap exists across all races in the United States, but is wider for women of color. The gap exists at all 
levels of work, in almost every industry, and in every U.S. state.

According to the GSS Website the General Social Survey (GSS Website Homepage) has studied the growing complexity of 
American society. It is the only full-probability, personal-interview survey designed to monitor changes in both social 
characteristics and attitudes currently being conducted in the United States.(GSS Website). According to GSS codebook 
the GSS collects data on contemporary American society to monitor and explain trends in opinions, attitudes, and 
behaviors. The GSS has adapted questions from earlier surveys, thereby allowing researchers to conduct comparisons for 
up to 80 years. The codebook also states the data contains a standard core of demographic, behavioral, and attitudinal 
questions, plus topics of special interest. Among the topics covered are civil liberties, crime and violence, intergroup
tolerance, morality, national spending priorities, psychological well-being, social mobility, and stress and traumatic
events. (GSS Codebook Page 11) The data is collected through mail and online surveys, with great care taken to ensure 
questions are asked in similar ways to keep the data as accurate as possible.'

Source: https://www.aauw.org/issues/equity/pay-gap/
"""

genders = gss_clean.groupby('sex').agg({'income':'mean', 'job_prestige':'mean', 'socioeconomic_index':'mean',
                                        'education':'mean'}).round(2).reset_index()
genders = genders.rename({'income':'Income', 'job_prestige': 'Occupational Prestige', 'socioeconomic_index': 
                          'Socioeconomic Status', 'education':'Years of Education', 'sex':'Sex'}, axis=1)
genders_table = ff.create_table(genders)

gss_clean['male_breadwinner'] = gss_clean['male_breadwinner'].astype('category').cat\
.reorder_categories(['strongly agree','agree','disagree','strongly disagree'])
bread = gss_clean.groupby(['sex', 'male_breadwinner']).size().reset_index()
bread = bread.rename({'sex':'Sex', 'male_breadwinner': 'Breadwinner Response', 0:'Count'}, axis = 1)

bread_bar = px.bar(bread, x='Breadwinner Response', y='Count', color='Sex', 
                   barmode = 'group', width=800, height=600)

fig = px.scatter(gss_clean, x='job_prestige', y='income', color='sex',
                 height=600, width=600,
                 trendline='ols',
                 labels={'job_prestige':'Occupational Prestige', 
                        'income':'Income'},
                 hover_data=['education', 'socioeconomic_index'])
fig.update(layout=dict(title=dict(x=0.5)))

income_box = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
                   labels={'sex':'', 'income':'Income'})
income_box.update(layout=dict(title=dict(x=0.5)))
income_box.update_layout(showlegend = False)

prestige_box = px.box(gss_clean, x='job_prestige', y = 'sex', color = 'sex',
                   labels={'sex':'', 'job_prestige':'Occupational Prestige'})
prestige_box.update(layout=dict(title=dict(x=0.5)))
prestige_box.update_layout(showlegend = False)

smalldf = gss_clean[['income', 'sex', 'job_prestige']].dropna()
smalldf['prestige_cats'] = pd.cut(smalldf.job_prestige, 6)
facet_box = px.box(smalldf, x='income', y = 'sex', color = 'sex',
                   facet_col='prestige_cats', facet_col_wrap=2,
                   labels={'sex':'', 'income':'Income'},
                   color_discrete_map = {'male':'blue', 'female':'red'})
facet_box.update_layout(showlegend = False)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

myfigs = [genders_table, bread_bar, fig, income_box, prestige_box, facet_box]

for x in myfigs:
    x.update_layout(
        plot_bgcolor = '#FAEBD7',
        paper_bgcolor = '#FAEBD7', 
        font_color = '#2F4F4F'
    )

app.layout = html.Div(
    [
        dcc.Tabs([
            dcc.Tab(label='Overview', children=[

                html.H1("Exploring the General Social Survey"),    
                dcc.Markdown(children = context),
        
                html.H2("Income and Occupational Statistics by Gender"),
                dcc.Graph(figure=genders_table)
                
            ]),
            
            dcc.Tab(label='Survey Responses', children=[
                
                html.Div([
                    
                    html.H2("Responses to the Breadwinner Survey Question by Gender"),
                    dcc.Graph(figure=bread_bar)
                    
                ], style = {'width':'48%', 'float':'left'}),
                
                html.Div([

                    html.H2("Occupational Prestige and Income by Gender"),
                    dcc.Graph(figure=fig)
                    
                ], style = {'width':'48%', 'float':'right'}),
                
            ]),
            
            dcc.Tab(label='Income and Prestige Stats', children=[
        
                html.H2("Income by Gender Grouped by Prestige"),
                dcc.Graph(figure=facet_box),
                
                html.Div([

                    html.H2("Income by Gender"), 
                    dcc.Graph(figure=income_box)

                ], style = {'width':'48%', 'float':'left'}),

                html.Div([

                    html.H2("Occupational Presige by Gender"),
                    dcc.Graph(figure=prestige_box)

                ], style = {'width':'48%', 'float':'right'}),
            
            ])
        
        ])
        
    ], style = {'backgroundColor': '#FAEBD7', 'color': '#2F4F4F', 'padding': 10, 'flex': 1}
)

if __name__ == '__main__':
    app.run_server(debug=True)
