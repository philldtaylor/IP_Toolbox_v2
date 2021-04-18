from operator import methodcaller
from website.models import Resultfile
from flask import Blueprint, render_template, request, flash, jsonify
from flask.json import jsonify
from flask_login import login_required, current_user
from . import db # we also need to import the db if we are adding to it
import json
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

# define that this file is a blueprint

views = Blueprint('views', __name__)

@views.route('/', methods=['GET','POST'])
@login_required # this decorator makes it so that this is only available to logged in users
def home():
    return render_template('home.html', user=current_user)

@views.route('/enricher_front', methods=['GET','POST'])
@login_required # this decorator makes it so that this is only available to logged in users
def enricher_front():
    return render_template('enricher_front.html', user=current_user)

@views.route('/resultfiles')
@login_required
def result_files():
    return render_template('result_files.html', user=current_user)

@views.route('/enricher_results',methods=['GET','POST'])
def enricher_results():
    #return render_template('enricher_results.html')
    requests_dict = {}
    f = request.files['file'] # get whatever the user put into the form as an input file
    f_path = 'user_files\\' + secure_filename(f.filename)
    f.save(f_path) # save in a local dir
    outfilename = request.form['outputfile'] # get whatever the user put into the form as an output file
    return_dict = {}
    return_dict['file'] = f_path
    return_dict['outfilename'] = outfilename
    result_file = Resultfile(data=outfilename,user_id=current_user.id) # add outfilename to database as the name of a result file
    db.session.add(result_file)
    db.session.commit()
    requests_dict[secure_filename(f.filename)] = {'outputname':outfilename}

    inputfile = f_path
    outputfile = 'website\\output_files\\' + outfilename

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

    return render_template('enricher_results.html', filename=outfilename,fullpath=outputfile, user=current_user)

@views.route('/output_files/<string:outfilename>')
def download(outfilename):
    outfilename = session.get('outfilename',None)
    outfilefullpath = session.get('outputfile',None)
    outfilefullpath = '..//' + str(outfilefullpath) # we need this as the output files is within website, without this we call website twice

    
    return send_file(outfilefullpath,as_attachment=True,attachment_filename='',mimetype='text/csv') #to switch to excel make mimetype='application/vnd.ms-exel', for csv mimetype='text/csv'