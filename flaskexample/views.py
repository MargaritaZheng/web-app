import os

from flask import request, render_template, redirect, url_for
from flaskexample import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from werkzeug.utils import secure_filename
from subprocess import call

user = 'uaaejtj1b7rkqe'
host = 'localhost'
dbname = 'dbbkm9u60mbres'
pswd = 'pe4q7e9c1ejfah9nnj0vipbtsjb'
db = create_engine('postgres://%s@%s/%s'%(user, host, dbname))
con = psycopg2.connect(
        database=dbname,
        user=user,
        host='ec2-52-5-130-157.compute-1.amazonaws.com',
        password=pswd
    )

UPLOAD_FOLDER = '/home/daisyz/tf_files/upload_pic'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
        title = 'Home', user = {'nickname': 'Daisy'}
        )

@app.route('/upload-target', methods=['POST'])
def handle_upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        f = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            file_upload_path = os.path.join(
                app.config['UPLOAD_FOLDER'], filename
            )
            f.save(file_upload_path)

#--------------DAISY EDITS--------------------------------------------
    # Delete 'out.txt' file from upload_pic
    try:
        os.remove('/home/daisyz/tf_files/upload_pic/out.txt')
    except:
        print('out.txt does not exist yet')
    # TensorFlow stuff here run in command line
    os.system('docker run -v /home/daisyz/tf_files/upload_pic:/pic daisy/goat /bin/bash script.sh')
    # Read 'out.txt' for shoe and percentage % accuracy
    with open('/home/daisyz/tf_files/upload_pic/out.txt', 'r') as f:
        first_line=f.readline()
    print('first line', first_line)
    # Separate product ID from percentage and show separately
    pulled_id=first_line[:6]
    print('id', pulled_id)
    pulled_perc=first_line[15:-2]
    print('perc', pulled_perc)
    pulled_perc=int(float(pulled_perc))*100
    # Use id number to find shoe name in SQL
    pulled_id=int(float(pulled_id))
    sql_query = """
    SELECT name, sku, product_templates.id, count(product_templates.id), array_agg(pictures.id) as PictureID
    FROM products
        JOIN pictures
        ON products.outer_picture_id=pictures.id
        JOIN product_templates
        ON products.product_template_id=product_templates.id
    WHERE products.sale_status IN ('active') and product_templates.id={}
    GROUP BY name, sku, product_templates.id
        """.format(pulled_id)

    query_results = pd.read_sql_query(sql_query, con)
    shoename=query_results['name'].iloc[0]
    shoesku=query_results['sku'].iloc[0]
    numcursold=query_results['id'].iloc[0]
    print(shoename)
    # return redirect(url_for('handle_upload', filename=filename, query_results=query_results))
    #-------------DAISY EDITS----------------------------------------
    # delete all previously uploaded jpegs
    # filelist = [ f for f in os.listdir("/home/daisyz/tf_files/upload_pic/") if f.endswith(".jpeg") ]
    # print('filelist=', filelist)
    # for f in filelist:
    #     os.remove(f)
    #-------------DAISY EDITS----------------------------------------
    return render_template('index.html',
        title = 'Home',
        user = {'nickname': 'Daisy'},
        shoename=shoename,
        shoesku=shoesku,
        numcursold=numcursold
        )

#---------------DAISY EDITS-----------------------------------------------
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
   ?'''
