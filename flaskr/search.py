from flask import (
    Blueprint, flash, g, redirect, render_template, request, current_app, url_for, session
)
from werkzeug.exceptions import abort
from SolrClient import SolrClient
from solrq import Q
import math
import re

bp = Blueprint('search', __name__)

def set_key(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = value
    else:
        value += dictionary[key]
        dictionary[key] = value

def collect(fac):
    """
    faculteiten kunnen op de volgende manieren voorkomen:
    ["FNWI"]
    ["FNWI / Instituut voor Theoretische Fysica"]
    ["FNWI / Instituut voor Theoretische Fysica", "FNWI"]
    ["FNWI / Instituut voor Theoretische Fysica", "FNWI / Instituut voor Theoretische Fysica""]
    NB de tweede (of derde...) kan hetzelfde zijn maar kan ook 'n andere faculteit zijn
    
    """
    items = dict()
    for key, value in fac.items():
        # faculteiten met evt. met 'n komma in de naam; die moet er uit voor de facet-list
        key = re.sub(',', '', key)
        key += ','
        # first, split on comma
        faculties = key.split(',')
        # loop over results
        for faculty in faculties:
            if (faculty == ''):
                continue
            faculty += '/'
            faculty, dummy = faculty.split('/', 1)
            faculty = faculty.strip()
            set_key(items, faculty, value)
    return items

def buildQuery():
    """
    faculteit kan meerdere keren voorkomen
    vandaar de dict.getlist
    zie: https://werkzeug.palletsprojects.com/en/1.0.x/datastructures/#werkzeug.datastructures.MultiDict
    NB nu ff niet geimplementeerd
    dit werkt niet: return Q(text="amsterdam", type="master", faculteit="FEB", faculteit="FMG")
    dit werkt wel:  return Q(text="amsterdam", type="master", faculteit="FEB") & Q(faculteit="FMG")
    """
    dict = request.args
    dict.getlist('faculteit')
    return Q(**dict)

def simple_query(page):
    d = dict()
    query = buildQuery()
    print(query)
    solr = SolrClient(current_app.config['SOLR'])
    res = solr.query('scripties',{
            'q':query,
            'rows':'0',
    })
    count = res.get_num_found()
    pages = math.ceil(count/10)
    start = (page-1)*10
    res = solr.query('scripties',{
            'q':query,
            'rows':'10',
            'start':start,
            'fl':'id,titel,auteur,jaar',
            'facet':True,
            'facet.field':['jaar','type', 'faculteit'],
    })
    facets = res.get_facets()
    d['result'] = res
    d['pages']  = pages
    d['page']   = page
    d['f_jaar'] = facets['jaar']
    d['f_type'] = facets['type']
    d['f_faculteit'] = collect(facets['faculteit'])
    d['f'] = request.args.get('faculteit')
    d['j'] = request.args.get('jaar')
    d['t'] = request.args.get('type')
    return d

def detail_query(key):
    solr = SolrClient(current_app.config['SOLR'])
    q = 'id:{}'.format(key)
    res = solr.query('scripties',{
            'q':q,
            'fl':'titel,auteur,jaar,supervisor,type,faculteit,opleiding,taal',
    })
    return res

@bp.route('/result/')
@bp.route('/result/<int:page>/')
def result(page=1):
    result = simple_query(page)
    if page > result['pages']:
        abort(404)
    return render_template('results.html', result=result, section="results")

@bp.route('/detail/<key>')
def detail(key):
    result = detail_query(key)
    return render_template('detail.html', result=result)
