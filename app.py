from re import template
from flask import Flask, render_template
from flask_cors import CORS
from flask_material import Material
import pandas as pd
import os, io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import seaborn as sns
import matplotlib.pyplot as plt

app = Flask(__name__)
Material(app)

URL_TO_READ = "https://www.fundsexplorer.com.br/ranking"
cors = CORS(app, resource={r"/*":{"origins": "*"}})

def scrapyContent():
    res = requests.get(URL_TO_READ)
    soup = BeautifulSoup(res.content,'lxml')
    table = soup.find_all('table')[0] 
    df = pd.read_html(str(table))
    #print(df[0].columns)
    df[0] = df[0][['Códigodo fundo', 'DividendYield', 'Preço Atual']]
    df[0].dropna(inplace=True)
    #Tratamento do atributo Código do Fundo
    df[0].columns = df[0].columns.str.replace('Códigodo fundo','Cod FII')
    #Tratamento do atributo Dividend Yield
    df[0]['DividendYield'] = df[0]['DividendYield'].str.replace('%','')
    df[0].columns = df[0].columns.str.replace('DividendYield','Dividend Yield')
    df[0]['Dividend Yield'] = df[0]['Dividend Yield'].replace(',','.', regex=True).astype(float)     
    #Tratamento do atributo Preço Atual
    df[0]['Preço Atual'] = df[0]['Preço Atual'].str.replace('\$', '').str.replace('R', '')   
    df[0]['Preço Atual'] = df[0]['Preço Atual'].str.replace('.','', regex=True)
    df[0]['Preço Atual'] = df[0]['Preço Atual'].str.replace(',','.', regex=True)
    df[0]['Preço Atual'] = df[0]['Preço Atual'].astype(float)
    #Filtro dos DY 
    df[0] = df[0][(df[0]['Dividend Yield'] > 1) & (df[0]['Dividend Yield'] < 8)]
    print( tabulate(df[0], headers='keys', tablefmt='psql') )
    return(df[0])    

def criaBarplot(df):
    fig,ax = plt.subplots(figsize=(15, 6))    
    ax = sns.set_style(style="darkgrid")
    sns.barplot(x='Cod FII', y='Dividend Yield', palette=['grey'], data=df.reset_index())
    canvas=FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    with open("./static/barplot.png", "wb") as f:
        f.write(img.getbuffer())
    return ("./static/barplot.png")

def criaScatterPlot(df):
    fig,ax = plt.subplots(figsize=(15, 6))    
    ax = sns.set_style(style="darkgrid")
    sns.scatterplot(data=df, x='Cod FII', y='Preço Atual', palette=['blue'])
    canvas=FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    with open("./static/scatterplot.png", "wb") as f:
        f.write(img.getbuffer())
    return ("./static/scatterplot.png")

@app.route("/")
def index():    
    return render_template('index.html')

@app.route("/graficos", methods=["GET"])
def enviaGrafico():
    df = scrapyContent()
    #print(df)    
    barplotPath = criaBarplot(df) #Barplot
    scatterplotPath = criaScatterPlot(df) #Scatterplot
    result = "- Gráfico salvo com sucesso em: " + barplotPath + """<html><br></html>""" \
             "- Gráfico salvo com sucesso em: " + scatterplotPath
    return (result)

def main():
     port = int(os.environ.get("PORT", 5000))
     app.run(host = "0.0.0.0", port = port)

if __name__ == "__main__":
    main()