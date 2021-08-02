from re import template
from flask import Flask, render_template, send_file
from flask_cors import CORS
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

URL_TO_READ = "https://www.fundsexplorer.com.br/ranking"
cors = CORS(app, resource={r"/*":{"origins": "*"}})

def scrapyContent():
    res = requests.get(URL_TO_READ)
    soup = BeautifulSoup(res.content,'lxml')
    table = soup.find_all('table')[0] 
    df = pd.read_html(str(table))
    df[0] = df[0][['Códigodo fundo', 'DividendYield']]
    df[0].dropna(inplace=True)
    df[0]['DividendYield'] = df[0]['DividendYield'].str.replace('%','')    
    df[0].columns = df[0].columns.str.replace('Códigodo fundo','Cod FII')
    df[0].columns = df[0].columns.str.replace('DividendYield','Dividend Yield')
    df[0]['Dividend Yield'] = df[0]['Dividend Yield'].replace(',','.', regex=True).astype(float)
    df[0] = df[0][(df[0]['Dividend Yield'] > 1) & (df[0]['Dividend Yield'] < 8)]
    return(df[0])
    #print( tabulate(df[0], headers='keys', tablefmt='psql') )

@app.route("/")
def index():    
    return render_template('index.html')

@app.route("/grafico", methods=["GET"])
def enviaGrafico():
    df = scrapyContent()
    print(df)
    fig,ax = plt.subplots(figsize=(15, 6))    
    ax = sns.set_style(style="darkgrid")
    sns.barplot(x='Cod FII', y='Dividend Yield (%)', palette=['r','b'], data=df.reset_index())
    plt.rcParams["savefig.directory"] = './templates/'
    canvas=FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='img/png')

def main():
     port = int(os.environ.get("PORT", 5000))
     app.run(host = "0.0.0.0", port = port)

if __name__ == "__main__":
    main()