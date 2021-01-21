# IMPORTAMOS LAS LIBRERIAS NECESARIAS
from matplotlib import cm, colors
from flask import Flask, render_template, request
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
from matplotlib.figure import Figure
import os
import base64
import io
import pandas as pd
import matplotlib
matplotlib.use('Agg')

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = Flask(__name__)
app.config.from_mapping(config)
PORT=5000
DEBUG=False
UPLOAD_FOLDER = 'archivos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def formulario():

    return render_template("formulario.html")
 # METODO QUE RECIBE UN FORMULARIO (DOCUMENTO,SEPARADOR)


@app.route('/upload', methods=['POST'])
def uploader():
    if request.method == 'POST':
        # RECIBE DATOS Y GUARDA EL ARCHIVO
        f = request.files['filename']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        separador = request.form['separador']
        fil = 'archivos/'+f.filename
    # ABRE EL ARCHIVO
        df = pd.read_csv('archivos/'+f.filename, sep=separador)
        df2 = df.head(10)
        col = []
        col2 = []
    # CICLO PARA SEPARAR LAS COLUMNAS NUMERICAS Y LAS TIPO OBJETO
        for c in df.columns:
            t = str(df[c].dtype)
            if "int" in t or "float" in t:
                col.append(c)
            else:
                col2.append(c)
    # RETORNA TITULOS,FILAS Y VARIABLES QUE NECESITAREMOS DESPUES AL MISMO TIEMPO QUE ABRE EL ARCHIVO FORMULARIO2.HTML
        return render_template('formulario2.html',  row_data=list(df2.values.tolist()), title=df.columns.values, titles=col, titles2=col2, file=fil, sep=separador)

# METODO QUE RECIBE UN FORMULARIO PARA GRAFICAR


fig = Figure()

fig, axes = plt.subplots(nrows=1, ncols=1)


@app.route('/graficar', methods=['GET', 'POST'])
def graficar():
    if request.method == 'POST':
        # RECIBE EL TIPO DE RAFICA,EJES PARA GRAFICAR Y LA DIRECCION DEL ARCHIVO CON SU SEPARADOR
        tipo = request.form['tipo']
        nombre = request.form['nombre']
        sep = request.form['sep']
        columnaX = request.form['columnaX']
        columnaY = request.form['columnaY']
        ruta = request.form['fil']
        print('Tipo: '+tipo)
        print('Nombre: '+nombre)
        print('Separador: '+sep)
        print('ColumnaX: '+columnaX)
        print('ColumnaY: '+columnaY)
        print('Ruta: '+ruta)
        # ABRE EL ARCHIVO
        df = pd.read_csv(ruta, sep=sep)
        df = df.head(10)
        # INGRESA AL IF CON EL TIPO DE GRAFICA SELECCIONADA
        if tipo == '1':
            img = None
            img = io.BytesIO()
            print('Lineal')

            # UTILIZA LOS DATOS DADOS PARA REALIZAR LA GRAFICA
            plt.plot(df[columnaX], df[columnaY])
            plt.xticks(df[columnaX], rotation=75)
            plt.xlabel(columnaX)
            plt.ylabel(columnaY)
            plt.title(nombre)
            # GRAFICA Y GUARDA EL ARCHIVO
            plt.tight_layout()
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
            # ABRE EL ARCHIVO GRAFICA.HTML DONDE SE MUESTRA LA GRAFICA REALIZADA
            return render_template("Grafica.html", imagen={'imagen': plot_url}, file=ruta, sep=sep,)

        if tipo == '2':
            print('Barras')
            img2 = None
            img2 = io.BytesIO()
            plt.bar(df[columnaX], df[columnaY], edgecolor='black')
            plt.xticks(df[columnaX], rotation=75)
            plt.xlabel(columnaX)
            plt.ylabel(columnaY)
            plt.title(nombre)
            plt.tight_layout()
            plt.savefig(img2, format='png')
            img2.seek(0)
            plot_url2 = base64.b64encode(img2.getvalue()).decode()
            plt.close()
            return render_template("Grafica.html", imagen={'imagen': plot_url2}, file=ruta, sep=sep)
        if tipo == '3':
            print('Pastel')
            img3 = None
            img3 = io.BytesIO()
            normdata = colors.Normalize(min(df[columnaY]), max(df[columnaY]))
            colormap = cm.get_cmap("Blues")
            colores = colormap(normdata(df[columnaY]))
            plt.pie(df[columnaY], labels=df[columnaX], autopct='%1.1f%%',
                    startangle=90, colors=colores, counterclock=False, labeldistance=1.2)
            plt.title(nombre)
            plt.tight_layout()
            plt.savefig(img3, format='png')
            img3.seek(0)
            plot_url3 = base64.b64encode(img3.getvalue()).decode()
            plt.close()
            return render_template("Grafica.html", imagen={'imagen': plot_url3}, file=ruta, sep=sep)


@app.route('/upload2', methods=['POST'])
def uploader2():

    if request.method == 'POST':
        # RECIBE DATOS Y GUARDA EL ARCHIVO
        filename = request.form['filename']
        separador = request.form['sep']
    # ABRE EL ARCHIVO
        df = pd.read_csv(filename, sep=separador)
        df2 = df.head(10)
        col = []
        col2 = []
    # CICLO PARA SEPARAR LAS COLUMNAS NUMERICAS Y LAS TIPO OBJETO
        for c in df.columns:
            t = str(df[c].dtype)
            if "int" in t or "float" in t:
                col.append(c)
            else:
                col2.append(c)
    # RETORNA TITULOS,FILAS Y VARIABLES QUE NECESITAREMOS DESPUES AL MISMO TIEMPO QUE ABRE EL ARCHIVO FORMULARIO2.HTML
        return render_template('formulario2.html',  row_data=list(df2.values.tolist()), title=df.columns.values, titles=col, titles2=col2, file=filename, sep=separador)


if __name__ == "__main__":
    app.run(debug=DEBUG,port=PORT)