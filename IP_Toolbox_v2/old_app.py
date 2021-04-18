from flask import Flask, render_template, url_for, request, redirect, send_file,session
import json
import os.path
from werkzeug.utils import secure_filename
import requests
import json
import os
import configparser
from pprint import pprint
import pandas as pd
import openpyxl
import sys
import configparser
import argparse
import os
import datetime
import hmac
import hashlib
import netaddr
import re
from ipwhois import IPWhois

app = Flask(__name__)
app.secret_key = 'iuhiuhiuhihuihuiuh'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/enricher_front', methods=['GET','POST'])
def enricher_front():
    return render_template('enricher_front.html')

@app.route('/enricher_results',methods=['GET','POST'])
def enricher_results():
    #return render_template('enricher_results.html')
    requests_dict = {}
    f = request.files['file'] # store the file in f
    f_path = 'user_files\\' + secure_filename(f.filename) 
    f.save(f_path) # save in a local dir
    outfilename = request.form['outputfile']
    return_dict = {}
    return_dict['file'] = f_path
    return_dict['outfilename'] = outfilename
    requests_dict[secure_filename(f.filename)] = {'outputname':outfilename}

    inputfile = f_path
    outputfile = 'output_files\\' + outfilename

    date = datetime.datetime.now()
    date = date.strftime('%d-%m-%Y')


    def ipwho(inputfile):
        df1 = pd.read_csv(inputfile)
        ipaddrlist = list(df1.loc[:,'IP'])
        asnlist = []
        asn_desclist = []
        namelist = []
        entitieslist = []
        reglist = []
        descriptionlist = []
        cidrlist = []

        for ipaddr in ipaddrlist:
            inreglist = []
            indescriptionlist = []

            try:
                obj = IPWhois(str(ipaddr).strip('\n'))
                results = obj.lookup_rdap(asn_methods=['whois'])
            except Exception as e:
                print(e)
            orgs = results['objects']

            try:
                cidr = results['network']['cidr']
                cidrlist.append(cidr)
            except Exception as e:
                cidrlist.append('n/a')
            
            for org in orgs:
                try:
                    if orgs[org]['roles'][0] == 'registrant':
                        inreglist.append(orgs[org]['contact']['name'])
                except Exception as e:
                    inreglist.append('n/a')
            try:
                description = results['network']['remarks'][0]['description']
                indescriptionlist.append(description)
            except Exception as e:
                indescriptionlist.append('n/a')

            try:
                asnlist.append(results['asn'])
                asn_desclist.append(results['asn_description'])
                namelist.append(results['network']['name'])
            except Exception as e:
                print(e)

            reglist.append(inreglist)
            descriptionlist.append(indescriptionlist)

        d = {'ASN':asnlist,'ASN Description':asn_desclist,'Network Name':namelist,'Registrant':reglist, 'Network Description':descriptionlist, 'Whois CIDR':cidrlist}
        df = pd.DataFrame(data=d)

            ###################################################################
            # df 1 is the original df, df is the new df, df2 is the combined df
            ###################################################################

        frames = [df1,df]
        df2 = pd.concat(frames, axis=1)

        df2.to_csv(outputfile,index=False)
    
    def top_level():
        ipwho(inputfile)
        
    top_level()

    #outfilename is just the filename
    #outputfile is the name plus the folder where we are storing it

    session['outfilename'] = outfilename
    session['outputfile'] = outputfile

    return render_template('enricher_results.html', filename=outfilename,fullpath=outputfile)


@app.route('/output_files/<string:outfilename>')
def download(outfilename):
    outfilename = session.get('outfilename',None)
    outfilefullpath = session.get('outputfile',None)
    
    return send_file(outfilefullpath,as_attachment=True,attachment_filename='',mimetype='text/csv') #to switch to excel make mimetype='application/vnd.ms-exel', for csv mimetype='text/csv'

