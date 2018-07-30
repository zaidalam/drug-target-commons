import json,pdb,re,decimal,io
from xlsxwriter.workbook import Workbook
from itertools import *
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render,get_object_or_404
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
#from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.db import connection
import urllib.parse as urlparse
from dtc.tasks import process_suggestions
from .models import SuggestionForReview
from allauth.account.forms import LoginForm
def decimal_default(obj):
	if isinstance(obj, decimal.Decimal):
		return float(obj)
	#raise TypeError


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

@never_cache
def home(request):
	# user = authenticate(username='zalam', password='')
	form = LoginForm()
	return render(request, "dtc/home.html", {'form': form,'nbar': 'home'})

def bulk_import(request):
	form = LoginForm()
	return render(request, "dtc/bulk_import.html", {'form': form,'nbar': 'bulk'})

@login_required()
def submissions(request):
	form = LoginForm()
	return render(request, "dtc/submissions.html", {'form': form,'nbar': 'submissions'})

def userguide(request):
	form = LoginForm()
	return render(request, "dtc/userguide.html", {'form': form,'nbar': 'userguide'})

def reference(request):
	form = LoginForm()
	return render(request, "dtc/reference.html", {'form': form,'nbar': 'reference'})	

def glossary(request):
	form = LoginForm()
	return render(request, "dtc/glossary.html", {'form': form,'nbar': 'glossary'})

def annotation_guidlines(request):
	form = LoginForm()
	return render(request, "dtc/annotation_guidlines.html", {'form': form,'nbar': 'annotation_guidlines'})


@csrf_exempt
def autosuggest(request):
	body = json.loads(request.body.decode('utf-8')) # decode POST parameters and convert into json object
	suggestion = ''.join([body['suggestedtext'].upper(),'%']) # join '%' with the parameter for the like sql statement
	#between = ''.join(['%',body['suggestedtext'].upper(),'%']) # join '%' before and after  the parameter for the like sql statement
	cursor = connection.cursor()
	sql = "SELECT distinct term_name as autosuggest_result from drugtargetcommons.start_search  where term_name like '%(my_like)s' LIMIT 40" % {'my_like': suggestion}

	cursor.execute(sql)
	row = cursor.fetchall()
	result = ','.join(chain(*row)).split(',')

	return HttpResponse(json.dumps(result),content_type="application/json")

def search(request):
	form = LoginForm()
	request.session['search'] = request.GET['txtSearchClient']
	request.session['ref_url'] = request.get_full_path()
	context = {
		"txtSearchClient": request.GET['txtSearchClient'],
		'form': form
	}
	return render(request, "dtc/search.html", context)
@csrf_exempt
def initial_search(request):
	
	body = json.loads(request.body.decode('utf-8')) # decode POST parameters and convert into json object
	searchText = body['searchText']
	end_with = ''.join([str(searchText).upper(),'%']) # join '%' with the parameter for the like sql statement
	start_with = ''.join(['%',str(searchText).upper()])

	cursor = connection.cursor()
	if searchText.isdigit():
		sql = "SELECT distinct '' as dtc_molregno, CAST(d.pubmed_id AS TEXT) as Name,'' as dtc_tid, '' as mutation_info, 'Publication'  as Category from drugtargetcommons.docs d  where CAST(d.pubmed_id AS TEXT)='%(equal)s' union SELECT distinct cim.dtc_molregno, cpn.pref_name as Name, '' as dtc_tid, '' as mutation_info, 'Compound' as Category from  drugtargetcommons.compound_id_mapping cim left join drugtargetcommons.compound_pref_names cpn  on cim.dtc_molregno=cpn.dtc_molregno where cim.dtc_molregno in (select distinct dtc_molregno from drugtargetcommons.compound_id_mapping where compound_id='%(equal)s' and  src_id in (4,7,10,20,21,31))    union select distinct '' as dtc_molregno, td.pref_name as Name,  dtc_tid, '' as mutation_info, 'Target' as Category from drugtargetcommons.target_dictionary td where td.dtc_tid in (select distinct td.dtc_tid from  drugtargetcommons.target_components tc,drugtargetcommons.component_sequences cs, drugtargetcommons.target_id_mapping tim where  tim.id_value='%(equal)s' and ID_type not in ('PDB','OrthoDB','MINT','KO', 'KEGG', 'HPA', 'HOVERGEN','GeneWiki', 'GeneTree','GeneCards','neXtProt', 'eggNOG','UniRef90','UniRef50','UniRef100', 'UniProtKB-ID','UniParc','UniGene', 'TreeFam', 'Reactome' ,'STRING','PharmGKB', 'EMBL-CDS', 'EMBL', 'DrugBank', 'DIP', 'ChEMBL','BioMuta'  ) and  tim.uniprotkbac=cs.accession and cs.component_id = tc.component_id and tc.dtc_tid = td.dtc_tid) " % {'equal': searchText,'end_with':end_with,"chembl":'CHEMBL%'}

	elif len(searchText) == 27 and re.match( r'^[-A-Z|]+$', searchText) and searchText[14] == '-' and searchText[25] == '-':
		searchText = str(searchText).upper()
		sql = "SELECT distinct c_s.dtc_molregno, cpn.pref_name as Name, '' as dtc_tid, '' as mutation_info, 'Compound' as Category  from  drugtargetcommons.compound_structures c_s left join drugtargetcommons.compound_pref_names cpn on c_s.dtc_molregno=cpn.dtc_molregno where standard_inchi_key = '%(equal)s'" % {'equal': searchText}
	else:
		searchText = str(searchText).upper()
		contain_space_before = ''.join(['% ',searchText,'%'])
		contain_space_after = ''.join(['%',searchText,'% '])
		between = ''.join(['%',searchText,'%'])
		contain_dash = ''.join(['%-',searchText,'%'])
		contain_slash = ''.join(['%/',searchText,'%'])

		sql = "SELECT distinct ss.term_id as dtc_molregno , ss.term_name as Name, '' as tid, '' as mutation_info,'Compound'  as Category from drugtargetcommons.start_search ss where term_name like '%(end_with)s' and term_type= 'COMPOUND' union  SELECT distinct '' as dtc_molregno , ss.term_name as Name,  ss.term_id as dtc_tid, '' as mutation_info,'Target'  as Category from drugtargetcommons.start_search ss where (term_name like '%(end_with)s' or term_name like '%(contain_space_before)s') and term_type= 'TARGET' union SELECT distinct '' as dtc_molregno , '' as Name,  '' as dtc_tid, ss.term_name mutation_info,'Mutation'  as Category from drugtargetcommons.start_search ss where term_name like '%(end_with)s' and term_type= 'MUTATION' union SELECT distinct cim.dtc_molregno, cpn.pref_name as Name, '' as dtc_tid, '' as mutation_info, 'Compound' as Category from  drugtargetcommons.compound_id_mapping cim left join drugtargetcommons.compound_pref_names cpn  on cim.dtc_molregno=cpn.dtc_molregno where cim.dtc_molregno in (select distinct dtc_molregno from drugtargetcommons.compound_id_mapping where compound_id='%(equal)s' and  src_id not in (4,7,10,20,21,31))    union select distinct '' as dtc_molregno, td.pref_name as Name,  dtc_tid, '' as mutation_info, 'Target' as Category from drugtargetcommons.target_dictionary td where td.dtc_tid in (select distinct td.dtc_tid from  drugtargetcommons.target_components tc,drugtargetcommons.component_sequences cs, drugtargetcommons.target_id_mapping tim where  tim.id_value='%(end_with)s' and ID_type in ('PDB','OrthoDB','MINT','KO', 'KEGG', 'HPA', 'HOVERGEN','GeneWiki', 'GeneTree','GeneCards','neXtProt', 'eggNOG','UniRef90','UniRef50','UniRef100', 'UniProtKB-ID','UniParc','UniGene', 'TreeFam', 'Reactome' ,'STRING','PharmGKB', 'EMBL-CDS', 'EMBL', 'DrugBank', 'DIP', 'ChEMBL','BioMuta'  ) and  tim.uniprotkbac=cs.accession and cs.component_id = tc.component_id and tc.dtc_tid = td.dtc_tid)" % {"start_with":start_with,"end_with":end_with,"contain_space_after":contain_space_after,"contain_space_before":contain_space_before,"contain_dash":contain_dash,"contain_slash":contain_slash,"equal":searchText,"chembl":'CHEMBL%',"between":between}

	cursor.execute(sql)
	result = dictfetchall(cursor)	
	return HttpResponse(json.dumps(result),content_type="application/json")	

def bioactivities(request):
	
	form = LoginForm()
	if request.session.get('ref_url'):
		context = {
			"category": request.GET['category'],
			"id": request.GET['id'],
			"form":form,
			"url":request.session['ref_url'],
			"search":request.session['search'],
			"name":request.GET.get('name') if request.GET.get('name')  else request.GET.get('id') if request.GET.get('category') == 'Mutation' else request.GET.get('category')
		}
		
	else:
		context = {
			"category": request.GET['category'],
			"id": request.GET['id'],
			"form":form,
			"name":request.GET.get('name') if request.GET.get('name')  else request.GET.get('id') if request.GET.get('category') == 'Mutation' else request.GET.get('category')
		}
	return render(request, "dtc/bioactivities.html", context)

def annotations(request):
	form = LoginForm()
	context = {
		'form': form
	}
	return render(request, "dtc/annotations.html", context)

@csrf_exempt
def export_to_excell(request):

	body = json.loads(request.body.decode('utf-8')) # decode POST parameters and convert into json object
	hidden_columns = body['hidden_columns']
	# # Save the file
	output = io.BytesIO()
	workbook = Workbook(output, {'in_memory': True})
	worksheet = workbook.add_worksheet("Bioactivities")
	bold = workbook.add_format({'bold': True})

	columns = ["Compound ID", "Uniprot ID","Compound Name", "Standard inchi key","Max Phase","Target Pref Name", "Gene Names", "Target Class","Wild type or mutant", "Mutation information", "PubMed ID", "End Point Standard Type", "End Point Standard Relation", "End Point Standard Value", "End Point Standard Units", "Endpoint Mode of Action", "Assay Format", "Assay Type", "Assay Sub Type", "Inhibitor Type", "Detection Technology", "Compound concentration value", "Compound concentration value units", "Substrate type", "Substrate Type Standard Relation", "Substrate Type Standard Value", "Substrate Type Standard Units", "Assay cell line", "Assay Description", "Activity Comments", "Title", "Journal", "Year", "Volume", "Issue", "Authors", "Annotation Comments", "Assay ID", "DTC Tid", "DTC Activity ID", "DTC Molregno", "Record ID", "DTC Document ID" ]
	row = 0
	col = 0
	for i,elem in enumerate(columns):
		worksheet.write(row, i, elem, bold)


	for index, b in enumerate(body['json_table']):
		data = [b['compound_id'],b['target_id'],b['compound_name'],b['standard_inchi_key'],b['max_phase'],b['target_pref_name'],b['gene_names'],b['target_class'],b['wildtype_or_mutant'],b['mutation_info'],b['pubmed_id'],b['ep_standardtype'],b['ep_standardrelation'],b['ep_standardvalue'],b['ep_standardunits'],b['ep_action_mode'],b['assay_format'],b['assaytype'],b['assay_subtype'],b['inhibitor_type'],b['detection_tech'],b['compound_concentration_value'],b['compound_concentration_value_unit'],b['substrate_type'],b['substrate_relation'],b['substrate_value'],b['substrate_units'],b['assay_cell_line'],b['assay_description'],b['activity_comment'],b['title'],b['journal'],b['year'],b['volume'],b['issue'],b['authors'],b['annotation_comments'],b['assay_id'],b['dtc_tid'],b['dtc_activity_id'],b['dtc_molregno'],b['dtc_record_id'],b['dtc_doc_id']]
		worksheet.write_row(index+1,0,tuple(data))


	worksheet.data_validation('I1:I1048576', {'validate': 'list','source': ['wild_type', 'mutated'],'ignore_blank':True})

	worksheet.data_validation('P1:P1048576', {'validate': 'list','source': ['activation','cytotoxocity','inhibition','growth_inhibition','inverse_agonist'],'ignore_blank':True})

	worksheet.data_validation('Q1:Q1048576', {'validate': 'list','source': ['biochemical','cell_based','cell_free','physiochemical','tissue','organism_based'],'ignore_blank':True})

	worksheet.data_validation('R1:R1048576', {'validate': 'list','source': ['functional','binding','phenotypic'],'ignore_blank':True})

	worksheet.data_validation('S1:S1048576', {'validate': 'list','source': ['binding_reversible','binding_irreversible','binding_saturation','enzyme_activity','process','reporter_gene','signalling','uptake','viability'],'ignore_blank':True})

	worksheet.data_validation('T1:T1048576', {'validate': 'list','source': ['competitive_inhibitor','non_competitive_inhibitor','allosteric_inhibitor'],'ignore_blank':True})

	worksheet.data_validation('U1:U1048576', {'validate': 'list','source': ['fluoresecence','luminescence','spectrophotometry','radiometry','microscopy','label_free_technology','fluorescence_polarization','TRF','TR_FRET','AlphaScreen','qPCR','termal_shift' ],'ignore_blank':True})

	worksheet.set_column('AN:AQ', None, None, {'hidden': True})
	workbook.close()
	output.seek(0) 
	response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
	return response
@csrf_exempt
def getbioactivities(request):

	body = json.loads(request.body.decode('utf-8')) # decode POST parameters and convert into json object
	searchitem = body['searchText']
	category = body['category']
	cursor = connection.cursor()
	if category == "Compound":
		Condition_searchtype = " md.dtc_molregno = '%s'" % searchitem
	elif category == "Target":
		Condition_searchtype = " td.dtc_tid = '%s'"  % searchitem
	elif category == "Mutation":
		Condition_searchtype = " dal.mutation_info = '%s'" % searchitem	
	else:
		Condition_searchtype = "  d.pubmed_id = %s" % searchitem

	_sql = "SELECT distinct md.chembl_id as compound_id,  md.pref_name as compound_name,  (select distinct standard_inchi_key from drugtargetcommons.compound_structures c_s where c_s.dtc_molregno=md.dtc_molregno ) as standard_inchi_key, md.max_phase,  array_to_string(array(select cs.accession from drugtargetcommons.target_components tc,drugtargetcommons.component_sequences cs where cs.component_id = tc.component_id and td.tid = tc.tid), ', ') as Target_ID, td.pref_name as Target_Pref_Name, array_to_string(array(select distinct tim.id_value from drugtargetcommons.target_id_mapping tim, drugtargetcommons.component_sequences cs,drugtargetcommons.target_components tc   where cs.accession = tim.uniprotkbac and  tim.id_type= 'GeneCards' and cs.component_id = tc.component_id and   td.tid = tc.tid), ', ') as gene_names, td.target_type,  array_to_string(array(select distinct  pc.protein_class_DTC from drugtargetcommons.target_components tc, drugtargetcommons.component_sequences cs , drugtargetcommons.protein_family_classification pc, drugtargetcommons.component_class cc where cs.component_id = tc.component_id and td.tid = tc.tid and cc.component_id=cs.component_id and cc.protein_class_id = pc.protein_class_id  ), ', ') as target_class, dal.WildType_or_Mutant, dal.Mutation_Info , d.Pubmed_ID, act.standard_type as EP_StandardType,act.standard_relation as EP_StandardRelation, act.standard_value as EP_StandardValue, act.standard_units as EP_StandardUnits, (select AM.term from drugtargetcommons.assay_action_mode AM where dal.endpoint_actionmode_id = AM.pk_id) as EP_Action_Mode, (select AF.term from drugtargetcommons.assay_format AF where dal.assay_format_id = AF.pk_id )   as  Assay_Format, (select AT.term from drugtargetcommons.assay_type AT  where dal.assay_type_id = AT.pk_id ) as AssayType, (select  AST.term from  drugtargetcommons.assay_sub_type ast  where dal.assay_sub_type_id = AST.pk_id ) as Assay_SubType, (select IT.term from drugtargetcommons.assay_inhibitor_type IT  where dal.inhibitor_type_id = IT.pk_id )as Inhibitor_Type, ( select DT.term from drugtargetcommons.assay_detection_technology DT where dal.detection_technology_id = DT.pk_id ) as  Detection_tech, a.Assay_Cell_type as Assay_Cell_Line, dal.compound_concentration_value, dal.compound_concentration_value_unit, dal.Substrate_Type, dal.Substrate_relation, dal.Substrate_value, dal.Substrate_units,  d.Title, d.Journal, d.Year, d.Volume, d.Issue, d.Authors, a.Assay_ID, a.DESCRIPTION AS Assay_Description, act.Activity_Comment, td.dtc_TID, act.dtc_Activity_ID, md.dtc_Molregno, act.dtc_Record_ID, d.dtc_Doc_ID, dal.Annotation_comments, dal.curator_email, dal.annotations_flag from drugtargetcommons.compound_records cr, drugtargetcommons.DOCS D, drugtargetcommons.ASSAYS A, drugtargetcommons.molecule_dictionary md,  drugtargetcommons.activities act, drugtargetcommons.target_dictionary td, drugtargetcommons.dtc_annotation_layer dal WHERE   %(Condition_searchtype)s and md.dtc_molregno = act.dtc_molregno AND act.dtc_record_id=cr.dtc_record_id and  act.dtc_DOC_ID = D.dtc_DOC_ID and act.dtc_assay_id = a.dtc_assay_id  AND  D.dtc_DOC_ID = A.dtc_DOC_ID  and d.dtc_doc_id = cr.dtc_doc_id AND a.dtc_tid = td.dtc_tid  and  dal.dtc_tid=td.dtc_tid and dal.dtc_doc_id=d.dtc_doc_id and  dal.dtc_molregno=md.dtc_molregno and dal.dtc_record_id=act.dtc_record_id and dal.dtc_activity_id=act.dtc_activity_id    and dal.dtc_assay_id=a.dtc_assay_id and  (td.Target_type = 'PROTEIN COMPLEX' or td.Target_type = 'PROTEIN' or td.Target_type = 'SINGLE PROTEIN' or   td.Target_type = 'PROTEIN-PROTEIN INTERACTION' or td.Target_type is null or td.Target_type = 'PROTEIN COMPLEX GROUP' or td.Target_type = 'PROTEIN FAMILY' or   td.Target_type = 'CHIMERIC PROTEIN') order by  compound_id, Target_ID desc" % {'Condition_searchtype':Condition_searchtype}
	cursor.execute(_sql)
	result = dictfetchall(cursor)
	return HttpResponse(json.dumps(result,default=decimal_default),content_type="application/json")
@csrf_exempt
def getsubmissions(request):
	_sql = "SELECT SFR.status, SFR.ID, SFR.Compound_ID, SFR.standard_inchi_key, SFR.Compound_Name, SFR.Target_ID, SFR.Target_Pref_Name, SFR.gene_names, SFR.PUBMED_ID, SFR.dtc_assay_id , SFR.TITLE, SFR.JOURNAL, SFR.YEAR, SFR.VOLUME, SFR.ISSUE, SFR.AUTHORS,  SFR.assay_description, AF.term as assay_format_id, AT.term as assay_type_id, AST.term as assay_sub_type_id,IT.term as inhibitor_type_id, DT.term as detection_technology_id, AM.term as  endpoint_actionmode_id,  SFR.ep_standard_type, SFR.ep_standard_relation, SFR.ep_standard_value,SFR.ep_standard_units, SFR.activity_comment, SFR.Assay_cell_type, SFR.WildType_or_Mutant, SFR.Mutation_Info, SFR.compound_concentration_value, SFR.compound_concentration_value_unit,SFR.substrate_Type, SFR.substrate_relation, SFR.substrate_value, SFR.substrate_units, SFR.curator_email, SFR.curator_name, SFR.Time_Stamp, SFR.annotation_comments, SFR.dtc_tid,SFR.dtc_Activity_ID , SFR.dtc_Molregno, SFR.dtc_Record_ID, SFR.dtc_Doc_ID as DTC_Doc_ID, SFR.annotations_flag from drugtargetcommons.suggestion_for_review SFR,drugtargetcommons.assay_action_mode AM,drugtargetcommons.assay_detection_technology DT, drugtargetcommons.assay_format AF, drugtargetcommons.assay_type AT, drugtargetcommons.assay_sub_type AST, drugtargetcommons.assay_inhibitor_type IT where  user_id = %(user_id)s AND SFR.assay_format_id = AF.pk_id  AND SFR.assay_type_id = AT.pk_id AND SFR.assay_sub_type_id = AST.pk_id  AND  SFR.inhibitor_type_id = IT.pk_id   AND SFR.endpoint_actionmode_id = AM.pk_id  AND SFR.detection_technology_id = DT.pk_id order by Time_Stamp desc, curator_email, user" % {'user_id':request.user.id}


	cursor = connection.cursor()
	cursor.execute(_sql)
	result = dictfetchall(cursor)
	return HttpResponse(json.dumps(result,default=decimal_default),content_type="application/json")
#change query in some point in the furture
@csrf_exempt
def getallsubmissions(request):
    _sql = "SELECT SFR.status, SFR.ID, SFR.Compound_ID, SFR.standard_inchi_key, SFR.Compound_Name, SFR.Target_ID, SFR.Target_Pref_Name, SFR.gene_names, SFR.PUBMED_ID, SFR.dtc_assay_id , SFR.TITLE, SFR.JOURNAL, SFR.YEAR, SFR.VOLUME, SFR.ISSUE, SFR.AUTHORS,  SFR.assay_description, AF.term as assay_format_id, AT.term as assay_type_id, AST.term as assay_sub_type_id,IT.term as inhibitor_type_id, DT.term as detection_technology_id, AM.term as  endpoint_actionmode_id,  SFR.ep_standard_type, SFR.ep_standard_relation, SFR.ep_standard_value,SFR.ep_standard_units, SFR.activity_comment, SFR.Assay_cell_type, SFR.WildType_or_Mutant, SFR.Mutation_Info, SFR.compound_concentration_value, SFR.compound_concentration_value_unit,SFR.substrate_Type, SFR.substrate_relation, SFR.substrate_value, SFR.substrate_units, SFR.curator_email, SFR.curator_name, SFR.Time_Stamp, SFR.annotation_comments, SFR.dtc_tid,SFR.dtc_Activity_ID , SFR.dtc_Molregno, SFR.dtc_Record_ID, SFR.dtc_Doc_ID as DTC_Doc_ID, SFR.annotations_flag from drugtargetcommons.suggestion_for_review SFR,drugtargetcommons.assay_action_mode AM,drugtargetcommons.assay_detection_technology DT, drugtargetcommons.assay_format AF, drugtargetcommons.assay_type AT, drugtargetcommons.assay_sub_type AST, drugtargetcommons.assay_inhibitor_type IT where  SFR.assay_format_id = AF.pk_id  AND SFR.assay_type_id = AT.pk_id AND SFR.assay_sub_type_id = AST.pk_id  AND  SFR.inhibitor_type_id = IT.pk_id   AND SFR.endpoint_actionmode_id = AM.pk_id  AND SFR.detection_technology_id = DT.pk_id order by Time_Stamp desc, curator_email, user"

    cursor = connection.cursor()
    cursor.execute(_sql)
    result = dictfetchall(cursor)
    return HttpResponse(json.dumps(result,default=decimal_default),content_type="application/json")
@csrf_exempt
def get_annotations(request):

	body = json.loads(request.body.decode('utf-8')) # decode POST parameters and convert into json object
	cursor = connection.cursor()

	sql = "SELECT md.chembl_id as compound_id, c_s.standard_inchi_key, md.pref_name as compound_name, array_to_string(array(select cs.accession from drugtargetcommons.target_components tc, drugtargetcommons.component_sequences cs where cs.component_id = tc.component_id and td.tid = tc.tid), ', ') as Target_ID, td.pref_name as Target_Pref_Name,   array_to_string(array(select distinct tim.id_value from drugtargetcommons.target_id_mapping tim, drugtargetcommons.component_sequences cs, drugtargetcommons.target_components tc   where cs.accession = tim.uniprotkbac and  tim.id_type= 'GeneCards' and cs.component_id = tc.component_id and   td.tid = tc.tid), ', ') as gene_names,  dal.WildType_or_Mutant as wildtype_or_mutant, dal.Mutation_Info  as mut_info, d.Pubmed_ID, act.standard_type as  ep_standard_type, act.standard_relation as ep_standard_relation, act.standard_value as ep_standard_value, act.standard_units as ep_standard_units,  AM.term as endpoint_actionmode_id, AF.term as assay_format_id, AT.term as assay_type_id, AST.term as assay_sub_type_id, IT.term as inhibitor_type_id, DT.term as detection_technology_id,dal.compound_concentration_value as compound_single_conc_value,dal.compound_concentration_value_unit as cscv_stand_unit,  dal.Substrate_Type as substrate_type ,  dal.Substrate_relation as subs_standard_relation, dal.Substrate_value as subs_standard_value, dal.Substrate_units as subs_stand_units,   a.Assay_Cell_type as Assay_Cell_Line,  a.DESCRIPTION as Assay_Description, act.Activity_Comment as activity_comment, D.TITLE as TITLE, D.JOURNAL as JOURNAL,D.YEAR as _YEAR, D.VOLUME as VOLUME, D.ISSUE as ISSUE, D.AUTHORS as AUTHORS , dal.Annotation_comments as annotation_comments,  dal.curator_email as Email  from drugtargetcommons.DOCS D, drugtargetcommons.ASSAYS A, drugtargetcommons.compound_structures c_s, drugtargetcommons.molecule_dictionary md,  drugtargetcommons.activities act, drugtargetcommons.target_dictionary td, drugtargetcommons.compound_records cr, drugtargetcommons.dtc_annotation_layer dal, drugtargetcommons.assay_action_mode AM, drugtargetcommons.assay_detection_technology DT, drugtargetcommons.assay_format AF, drugtargetcommons.assay_type AT,  drugtargetcommons.assay_sub_type ast,  drugtargetcommons.assay_inhibitor_type IT WHERE  md.dtc_molregno=  '%(dtc_molregno)s' and dal.assay_format_id = AF.pk_id  AND dal.assay_type_id = AT.pk_id AND dal.assay_sub_type_id = AST.pk_id AND  dal.inhibitor_type_id = IT.pk_id AND dal.endpoint_actionmode_id = AM.pk_id  AND dal.detection_technology_id = DT.pk_id and md.dtc_molregno = act.dtc_molregno AND  act.dtc_DOC_ID = D.dtc_DOC_ID  and act.dtc_record_id = cr.dtc_record_id and c_s.dtc_molregno=  md.dtc_molregno AND act.dtc_assay_id = a.dtc_assay_id AND D.dtc_DOC_ID = A.dtc_DOC_ID  and cr.dtc_doc_id = d.dtc_doc_id AND a.dtc_tid = td.dtc_tid  and md.dtc_molregno=cr.dtc_molregno  and dal.dtc_assay_id=a.dtc_assay_id and dal.dtc_tid=td.dtc_tid and dal.dtc_doc_id=d.dtc_doc_id and  dal.dtc_molregno=md.dtc_molregno and dal.dtc_record_id=cr.dtc_record_id and dal.dtc_activity_id=act.dtc_activity_id  and act.standard_value is not null  and (td.Target_type='PROTEIN COMPLEX' or td.Target_type = 'PROTEIN' or td.Target_type = 'PROTEIN NUCLEIC-ACID COMPLEX' or td.Target_type = 'SINGLE PROTEIN' or   td.Target_type = 'PROTEIN-PROTEIN INTERACTION' or td.Target_type = 'PROTEIN COMPLEX GROUP' or td.Target_type = 'PROTEIN FAMILY' or  td.Target_type = 'CHIMERIC PROTEIN') and dal.annotations_flag='yes' order by  compound_id, Target_ID desc" % {"dtc_molregno":body['id']}
	cursor.execute(sql)
	result = dictfetchall(cursor)
	return HttpResponse(json.dumps(result,default=decimal_default),content_type="application/json")

@csrf_exempt
def upload_annotations(request):

	body = json.loads(request.body.decode('utf-8')) # decode POST parameters and convert into json object
	id_mapping = { "BIOCHEMICAL":0, "CELL_BASED":1, "CELL_FREE":2, "PHYSIOCHEMICAL":4,"TISSUE":5, "ORGANISM_BASED":3, 
	"FUNCTIONAL":6,"BINDING":13,"PHENOTYPIC":0,"BINDING_REVERSIBLE":0,"BINDING_IRREVERSIBLE":1,"BINDING_SATURATION":2,"ENZYME_ACTIVITY":3,"PROCESS":4,"REPORTER_GENE":5,"SIGNALLING":6,"UPTAKE":7,"VIABILITY":8,"COMPETITIVE_INHIBITOR":0,"NON_COMPETITIVE_INHIBITOR":1,"ALLOSTERIC_INHIBITOR":2,"ACTIVATION":0,"CYTOTOXOCITY":1,"GROWTH_INHIBITION":2,"INHIBITION":3,"INVERSE_AGONIST":4,"FLUORESECENCE":0,"LUMINESCENCE":1,"SPECTROPHOTOMETRY":2,"RADIOMETRY":3,"MICROSCOPY":4,"LABEL_FREE_TECHNOLOGY":5,"FLUORESCENCE_POLARIZATION":6,"TRF":7,"TR_FRET":8,"ALPHASCREEN":9,"QPCR":10,"TERMAL_SHIFT":11,"":100 }
	
	objs = [
		SuggestionForReview(
			compound_id= None if 'compound id'  not in a else (str(a['compound id']).upper() if a['compound id'] else None),
			standard_inchi_key= None if 'standard inchi key'  not in a else (str(a['standard inchi key']).upper() if a['standard inchi key'] else None),
			compound_name= None if 'compound name'  not in a else (str(a['compound name']).upper() if a['compound name'] else None),
			target_id= None if 'uniprot id'  not in a else (str(a['uniprot id']).upper() if a['uniprot id'] else None),
			target_pref_name= None if 'target pref name'  not in a else (str(a['target pref name']).upper() if a['target pref name'] else None),
			gene_names= None if 'gene names'  not in a else (str(a['gene names']).upper() if a['gene names'] else None),
			wildtype_or_mutant=None if 'wild type or mutant'  not in a else (str(a['wild type or mutant']).lower() if a['wild type or mutant'] else None ),
			mutation_info= None if 'mutation information'  not in a else (str(a['mutation information']).upper() if a['mutation information'] else None),
			pubmed_id= None if 'pubmed id'  not in a else (int(a['pubmed id']) if a['pubmed id'] else None),
			weblink = None if 'weblink'  not in a else (str(a['weblink']).upper() if a['weblink'] else None),
			ep_standard_type= None if 'end point standard type'  not in a else (str(a['end point standard type']).upper() if a['end point standard type'] else None),
			ep_standard_relation= None if 'end point standard relation'  not in a else (str(a['end point standard relation']).upper() if a['end point standard relation'] else None),
			ep_standard_value=None if 'end point standard value'  not in a else (float(a['end point standard value']) if a['end point standard value'] else None),
			ep_standard_units= None if 'end point standard units'  not in a else (str(a['end point standard units']).upper() if a['end point standard units'] else None),
			endpoint_actionmode_id=100 if 'endpoint mode of action'  not in a else (id_mapping[str(a['endpoint mode of action']).upper()] if a['endpoint mode of action'] else 100),
			assay_format_id= 100 if 'assay format'  not in a else (id_mapping[str(a['assay format']).upper()] if a['assay format'] else 100),
			assay_type_id=100 if 'assay type'  not in a else (id_mapping[str(a['assay type']).upper()] if a['assay type'] else 100),
			assay_sub_type_id= 100 if 'assay sub type'  not in a else (id_mapping[str(a['assay sub type']).upper()] if a['assay sub type'] else 100),
			inhibitor_type_id= 100 if 'inhibitor type'  not in a else (id_mapping[str(a['inhibitor type']).upper()] if a['inhibitor type'] else 100),
			detection_technology_id=100 if 'detection technology'  not in a else (id_mapping[str(a['detection technology']).upper()] if a['detection technology'] else 100),
			assay_cell_type= None if 'assay cell line'  not in a else (str(a['assay cell line']) if a['assay cell line'] else None),
			compound_concentration_value=None if 'compound concentration value'  not in a else (str(a['compound concentration value']) if a['compound concentration value'] else None),
			compound_concentration_value_unit= None if 'compound concentration value units'  not in a else (str(a['compound concentration value units']).upper() if a['compound concentration value units'] else None),
			substrate_type= None if 'substrate type'  not in a else (str(a['substrate type']).upper() if a['substrate type'] else None),
			substrate_relation= None if 'substrate type standard relation'  not in a else (str(a['substrate type standard relation']).upper() if a['substrate type standard relation'] else None ),
			substrate_value= None if 'substrate type standard value'  not in a else (str(a['substrate type standard value']) if a['substrate type standard value'] else None),
			substrate_units= None if 'substrate type standard units'  not in a else (str(a['substrate type standard units']).upper() if a['substrate type standard units'] else None),
			title= None if 'title'  not in a else (str(a['title']).upper() if a['title'] else None),
			journal= None if 'journal'  not in a else (str(a['journal']).upper() if a['journal'] else None),
			year=None if 'year'  not in a else (str(a['year']) if a['year'] else None),
			volume= None if 'volume'  not in a else (str(a['volume']) if a['volume'] else None),
			issue= None if 'issue'  not in a else (str(a['issue']) if a['issue'] else None),
			authors= None if 'authors'  not in a else (str(a['authors']).upper() if a['authors'] else None),
			dtc_assay_id=None if 'dtc_assay_id'  not in a else (int(a['dtc_assay_id']) if a['dtc_assay_id'] else None),
			assay_description= None if 'assay description'  not in a else (str(a['assay description']).upper() if a['assay description'] else None),
			activity_comment= None if 'activity comments'  not in a else (str(a['activity comments']).upper() if a['activity comments'] else None),
			curator_email= None if '_email'  not in body else (str(body['_email']) if body['_email'] else None),
			curator_name=None if '_user'  not in body else str(body['_user']),
			time_stamp=datetime.now(),
			annotation_comments=None if 'annotation comments'  not in a else (str(a['annotation comments']).upper() if a['annotation comments'] else None),
			dtc_tid=None if 'dtc_tid'  not in a else str(a['dtc_tid']),
			dtc_activity_id=None if 'dtc_activity_id'  not in a else (int(a['dtc_activity_id']) if a['dtc_activity_id'] else None),
			dtc_molregno = None if 'dtc_molregno'  not in a else (str(a['dtc_molregno']) if a['dtc_molregno'] else None),
			dtc_record_id=None if 'dtc_record_id'  not in a else (int(a['dtc_record_id']) if a['dtc_record_id'] else None),
			dtc_doc_id=None if 'dtc_doc_id'  not in a else (int(a['dtc_doc_id']) if a['dtc_doc_id'] else None),
			annotations_flag='no' if 'annotations flag'  not in a else (bool(a['annotations flag']) if a['annotations flag'] else 'no'),
			user_id=request.user.id,		
			status='NEW'
	    )
    	for a in body['json_table']
	]
	
	SuggestionForReview.objects.bulk_create(objs)
	return HttpResponse(json.dumps({'success':1}),content_type="application/json")
@csrf_exempt
def send_review(request):
	body = json.loads(request.body.decode('utf-8')) # decode POST parameters and convert into json object
	id_mapping = { "BIOCHEMICAL":0, "CELL_BASED":1, "CELL_FREE":2, "PHYSIOCHEMICAL":4,"TISSUE":5, "ORGANISM_BASED":3, 
	"FUNCTIONAL":6,"BINDING":13,"PHENOTYPIC":0,
	"BINDING_REVERSIBLE":0,"BINDING_IRREVERSIBLE":1,"BINDING_SATURATION":2,"ENZYME_ACTIVITY":3,"PROCESS":4,"REPORTER_GENE":5,"SIGNALLING":6,"UPTAKE":7,"VIABILITY":8,
	"COMPETITIVE_INHIBITOR":0,"NON_COMPETITIVE_INHIBITOR":1,"ALLOSTERIC_INHIBITOR":2,
	"ACTIVATION":0,"CYTOTOXOCITY":1,"GROWTH_INHIBITION":2,"INHIBITION":3,"INVERSE_AGONIST":4,
	"FLUORESECENCE":0,"LUMINESCENCE":1,"SPECTROPHOTOMETRY":2,"RADIOMETRY":3,"MICROSCOPY":4,"LABEL_FREE_TECHNOLOGY":5,"FLUORESCENCE_POLARIZATION":6,"TRF":7,"TR_FRET":8,"ALPHASCREEN":9,"QPCR":10,"TERMAL_SHIFT":11,
	"":100,"NONE":100 }
	
	objs = [
		SuggestionForReview(
			compound_id= None if 'compound_id'  not in a else (str(a['compound_id']).upper() if a['compound_id'] else None),
			standard_inchi_key= None if 'standard_inchi_key'  not in a else (str(a['standard_inchi_key']).upper() if a['standard_inchi_key'] else None),
			compound_name= None if 'compound_name'  not in a else (str(a['compound_name']).upper() if a['compound_name'] else None),
			target_id= None if 'target_id'  not in a else (str(a['target_id']).upper() if a['target_id'] else None),
			target_pref_name= None if 'target_pref_name'  not in a else (str(a['target_pref_name']).upper() if a['target_pref_name'] else None),
			gene_names= None if 'gene_names'  not in a else (str(a['gene_names']).upper() if a['gene_names'] else None),
			wildtype_or_mutant=None if 'wildtype_or_mutant'  not in a else (str(a['wildtype_or_mutant']).lower() if a['wildtype_or_mutant'] else None ),
			mutation_info= None if 'mutation_info'  not in a else (str(a['mutation_info']).upper() if a['mutation_info'] else None),
			pubmed_id= None if 'pubmed_id'  not in a else (int(a['pubmed_id']) if a['pubmed_id'] else None),
			weblink = None if 'weblink'  not in a else (str(a['weblink']).upper() if a['weblink'] else None),
			ep_standard_type= None if 'ep_standardtype'  not in a else (str(a['ep_standardtype']).upper() if a['ep_standardtype'] else None),
			ep_standard_relation= None if 'ep_standardrelation'  not in a else (str(a['ep_standardrelation']).upper() if a['ep_standardrelation'] else None),
			ep_standard_value=None if 'ep_standardvalue'  not in a else (float(a['ep_standardvalue']) if a['ep_standardvalue'] else None),
			ep_standard_units= None if 'ep_standardunits'  not in a else (str(a['ep_standardunits']).upper() if a['ep_standardunits'] else None),
			endpoint_actionmode_id=100 if 'ep_action_mode'  not in a else (id_mapping[str(a['ep_action_mode']).upper()] if a['ep_action_mode'] else 100),
			assay_format_id= 100 if 'assay_format'  not in a else (id_mapping[str(a['assay_format']).upper()] if a['assay_format'] else 100),
			assay_type_id=100 if 'assaytype'  not in a else (id_mapping[str(a['assaytype']).upper()] if a['assaytype'] else 100),
			assay_sub_type_id= 100 if 'assay_subtype'  not in a else (id_mapping[str(a['assay_subtype']).upper()] if a['assay_subtype'] else 100),
			inhibitor_type_id= 100 if 'inhibitor_type'  not in a else (id_mapping[str(a['inhibitor_type']).upper()] if a['inhibitor_type'] else 100),
			detection_technology_id=100 if 'detection_tech'  not in a else (id_mapping[str(a['detection_tech']).upper()] if a['detection_tech'] else 100),
			assay_cell_type= None if 'assay_cell_line'  not in a else (str(a['assay_cell_line']) if a['assay_cell_line'] else None),
			compound_concentration_value=None if 'compound_concentration_value'  not in a else (str(a['compound_concentration_value']) if a['compound_concentration_value'] else None),
			compound_concentration_value_unit= None if 'compound_concentration_value_unit'  not in a else (str(a['compound_concentration_value_unit']).upper() if a['compound_concentration_value_unit'] else None),
			substrate_type= None if 'substrate_type'  not in a else (str(a['substrate_type']).upper() if a['substrate_type'] else None),
			substrate_relation= None if 'substrate_relation'  not in a else (str(a['substrate_relation']).upper() if a['substrate_relation'] else None ),
			substrate_value= None if 'substrate_value'  not in a else (str(a['substrate_value']) if a['substrate_value'] else None),
			substrate_units= None if 'substrate_units'  not in a else (str(a['substrate_units']).upper() if a['substrate_units'] else None),
			title= None if 'title'  not in a else (str(a['title']).upper() if a['title'] else None),
			journal= None if 'journal'  not in a else (str(a['journal']).upper() if a['journal'] else None),
			year=None if 'year'  not in a else (str(a['year']) if a['year'] else None),
			volume= None if 'volume'  not in a else (str(a['volume']) if a['volume'] else None),
			issue= None if 'issue'  not in a else (str(a['issue']) if a['issue'] else None),
			authors= None if 'authors'  not in a else (str(a['authors']).upper() if a['authors'] else None),
			dtc_assay_id=None if 'assay_id'  not in a else (int(a['assay_id']) if a['assay_id'] else None),
			assay_description= None if 'assay_description'  not in a else (str(a['assay_description']).upper() if a['assay_description'] else None),
			activity_comment= None if 'activity_comment'  not in a else (str(a['activity_comment']).upper() if a['activity_comment'] else None),
			curator_email= None if '_email'  not in body else (str(body['_email']) if body['_email'] else None),
			curator_name=None if '_user'  not in body else str(body['_user']),
			time_stamp= datetime.now(),
			annotation_comments=None if 'annotation_comments'  not in a else (str(a['annotation_comments']).upper() if a['annotation_comments'] else None),
			dtc_tid=None if 'dtc_tid'  not in a else str(a['dtc_tid']),
			dtc_activity_id=None if 'dtc_activity_id'  not in a else (int(a['dtc_activity_id']) if a['dtc_activity_id'] else None),
			dtc_molregno = None if 'dtc_molregno'  not in a else (str(a['dtc_molregno']) if a['dtc_molregno'] else None),
			dtc_record_id=None if 'dtc_record_id'  not in a else (int(a['dtc_record_id']) if a['dtc_record_id'] else None),
			dtc_doc_id=None if 'dtc_doc_id'  not in a else (int(a['dtc_doc_id']) if a['dtc_doc_id'] else None),
			annotations_flag='no' if 'annotations_flag'  not in a else (bool(a['annotations_flag']) if a['annotations_flag'] else 'no'),
			user_id=request.user.id,	
			status='NEW'
	    )
    	for a in body['json_table']
	]

	SuggestionForReview.objects.bulk_create(objs)
	return HttpResponse(json.dumps({'success':1}),content_type="application/json")

@csrf_exempt
def process_submissions(request):
	#import User Model 
	from django.contrib.auth.models import User
	#initialize database connection
	cursor = connection.cursor()
	# get/decode data to be inserted/updated
	data = json.loads(request.body.decode('utf-8'))

	

	id_mapping = { "BIOCHEMICAL":0, "CELL_BASED":1, "CELL_FREE":2, "PHYSIOCHEMICAL":4,"TISSUE":5, "ORGANISM_BASED":3, 
	"FUNCTIONAL":6,"BINDING":13,"PHENOTYPIC":0,
	"BINDING_REVERSIBLE":0,"BINDING_IRREVERSIBLE":1,"BINDING_SATURATION":2,"ENZYME_ACTIVITY":3,"PROCESS":4,"REPORTER_GENE":5,"SIGNALLING":6,"UPTAKE":7,"VIABILITY":8,
	"COMPETITIVE_INHIBITOR":0,"NON_COMPETITIVE_INHIBITOR":1,"ALLOSTERIC_INHIBITOR":2,
	"ACTIVATION":0,"CYTOTOXOCITY":1,"GROWTH_INHIBITION":2,"INHIBITION":3,"INVERSE_AGONIST":4,
	"FLUORESECENCE":0,"LUMINESCENCE":1,"SPECTROPHOTOMETRY":2,"RADIOMETRY":3,"MICROSCOPY":4,"LABEL_FREE_TECHNOLOGY":5,"FLUORESCENCE_POLARIZATION":6,"TRF":7,"TR_FRET":8,"ALPHASCREEN":9,"QPCR":10,"TERMAL_SHIFT":11,
	"":100,"NONE":100 }

	#get total rows
	total_rows = len(data['json_table'])
	# data inserted cannot be more then 6001 to make sure then is not much load(this will not be required with a cron job later) 
	if total_rows < 100000000000000000:
		#get user id from session
		uid = request.session['_auth_user_id']
		# get user object using user id to validate User
		user=User.objects.get(id=uid)
		#keeping track of approved ids which will be deleted from suggestion_fro_review table
		approved_ids = []
		#check if user is a superuser
		if user.is_superuser:	
			#check status of operataion to be performed(acdepted,deleted or update)
			if data['status'] == "accepted":
				#inititalize row count
				row_count = 0;
				#intitalize update insert query variable
				update_insert= "";
				#loop through each record
				for row in data['json_table']:
					#c
					print('suggestionForReview#' ,end=',')
					print(row['id'])
					temp_assay_Id=int(row['dtc_assay_id']) if row['dtc_assay_id'] else None
					temp_molregno=str(row['dtc_molregno']) if row['dtc_molregno'] else None
					temp_doc_id=int(row['dtc_doc_id']) if row['dtc_doc_id'] else None
					temp_record_id= int(row['dtc_record_id']) if row['dtc_record_id'] else None
					temp_tid=str(row['dtc_tid']) if row['dtc_tid'] else None
					temp_activity_id=int(row['dtc_activity_id']) if row['dtc_activity_id'] else None

				

					if row['ep_standard_value'] and not row['ep_standard_relation']:
						row['ep_standardrelation'] = '='

					if row['substrate_value'] and not row['substrate_relation']:
						row['substrate_relation'] = '='
					

					if temp_assay_Id  and temp_molregno  and temp_doc_id  and temp_record_id  and temp_tid  and temp_activity_id: # there are no negative IDs in our databases
						print('updated')

						temp_assay_Id=str(temp_assay_Id)
						temp_molregno=str(temp_molregno)
						temp_doc_id=str(temp_doc_id)
						temp_record_id= str(temp_record_id)
						temp_tid=str(temp_tid)
						temp_activity_id=str(temp_activity_id)

	
						for key,value in row.items():
							if value:
								value = str(value)

								if key == "id":
									approved_ids.append(value)
								if key == "compound_name":
									update_insert = update_insert + " update drugtargetcommons.molecule_dictionary set pref_name = '" + value + "' where dtc_molregno = '" + temp_molregno + "'; "
								if key == "target_pref_name":
									update_insert = update_insert + " update drugtargetcommons.target_dictionary set pref_name = '" + value + "' where dtc_tid = '" + temp_tid + "'; "
								if key ==  "wildtype_or_mutant":
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set wildtype_or_mutant = '" + value + "' where dtc_molregno = '" + temp_molregno + "' "  
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
									
								if key ==  "mutation_info":
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set mutation_info = '" + value + "'where dtc_molregno = '" + temp_molregno + "' "
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "pubmed_id":
									update_insert = update_insert + " update drugtargetcommons.docs set pubmed_id = '" + value + "' where dtc_doc_id = '" + temp_doc_id + "'; "
								

								if key ==  "ep_standard_type":
									update_insert = update_insert + " update drugtargetcommons.activities set standard_type  = '" + value + "' where dtc_activity_id = '" + temp_activity_id + "' ; "
								
								if key ==  "ep_standard_relation":
									update_insert = update_insert + " update drugtargetcommons.activities set standard_relation  = '" + value + "' where dtc_activity_id = '" + temp_activity_id + "'; "

								if key ==  "ep_standard_value":
									update_insert = update_insert + " update drugtargetcommons.activities set standard_value  = '" + value + "' where dtc_activity_id = '" + temp_activity_id + "'; "
								
								if key ==  "ep_standard_units":
									update_insert = update_insert + " update drugtargetcommons.activities set standard_units   = '" + value + "' where dtc_activity_id = '" + temp_activity_id + "'; "
								
								if key ==  "endpoint_actionmode_id":
									value = str(id_mapping[str(value).rstrip().upper()])
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set endpoint_actionmode_id = '" + value + "' where dtc_molregno = '" + temp_molregno + "' "
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "assay_format_id":
									value = str(id_mapping[str(value).rstrip().upper()])
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set assay_format_id = '" + value + "' where dtc_molregno = '" + temp_molregno + "' "
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "assay_type_id":
									
									value = str(id_mapping[str(value).rstrip().upper()])
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set assay_type_id = '" + value + "' where dtc_molregno = '" + temp_molregno + "' "
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "assay_sub_type_id":
								
									value = str(id_mapping[str(value).rstrip().upper()])
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set assay_sub_type_id = '" + value + "' where dtc_molregno = '" + temp_molregno + "' "
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "inhibitor_type_id":
									value = str(id_mapping[str(value).rstrip().upper()])
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set inhibitor_type_id = '" + value + "' where dtc_molregno = '" + temp_molregno + "' "
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "detection_technology_id":

									value = str(id_mapping[str(value).rstrip().upper()])

									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set detection_technology_id = '" + value + "' where dtc_molregno = '" + temp_molregno + "' "
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "assay_cell_type":
									update_insert = update_insert + " update drugtargetcommons.assays set assay_cell_type = '" + value + "' where   = '" + temp_assay_Id + "'; "
								
								if key ==  "compound_concentration_value":
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set compound_concentration_value = '" + value + "' where dtc_molregno = '" + temp_molregno + "' "
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "compound_concentration_value_unit":
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set compound_concentration_value_unit = '" + value + "' where dtc_molregno = '" + temp_molregno + "' "
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "substrate_type":
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set substrate_type = '" + value + "' where dtc_molregno = '" + temp_molregno + "' " ; 
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "substrate_relation":
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set substrate_relation = '" + value + "' where dtc_molregno = '" + temp_molregno + "' " ; 
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "substrate_value":
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set substrate_value = '" + value + "' where dtc_molregno = '" + temp_molregno + "' " ; 
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
									
								if key ==  "substrate_units":
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set substrate_units = '" + value + "' where dtc_molregno = '" + temp_molregno + "' " ; 
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
								
								if key ==  "title":
									update_insert = update_insert + " update drugtargetcommons.docs set title = '" + value + "' where dtc_doc_id = '" + temp_doc_id + "'; "
								
								if key ==  "journal":
									update_insert = update_insert + " update drugtargetcommons.docs set journal = '" + value + "' where dtc_doc_id = '" + temp_doc_id + "'; "
								
								if key ==  "year":
									update_insert = update_insert + " update drugtargetcommons.docs set year = '" + value + "' where dtc_doc_id = '" + temp_doc_id + "'; "
								
								if key ==  "volume":
									update_insert = update_insert + " update drugtargetcommons.docs set volume = '" + value + "' where dtc_doc_id = '" + temp_doc_id + "'; "
								
								if key ==  "issue":
									update_insert = update_insert + " update drugtargetcommons.docs set issue = '" + value + "' where dtc_doc_id = '" + temp_doc_id + "'; "
								if key ==  "authors":
									update_insert = update_insert + " update drugtargetcommons.docs set authors = '" + value + "' where dtc_doc_id = '" + temp_doc_id + "'; "
								if key ==  "assay_description":
									update_insert = update_insert + " update drugtargetcommons.assays set description = '" + value + "' where dtc_assay_id = '" + temp_assay_Id + "'; "
								
								if key ==  "activity_comment":
									update_insert = update_insert + " update drugtargetcommons.activities set activity_comment = '" + value + "' where dtc_activity_id = '" + temp_activity_id + "'; "
								
								if key ==  "time_stamp":
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set time_stamp = '" + value + "' where dtc_molregno = '" + temp_molregno + "' "
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "
									
								if key ==  "annotation_comments":
									update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set annotation_comments = '" + value + "' where dtc_molregno = '" + temp_molregno + "' "
									update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
									update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' ;  "

						update_insert = update_insert + " update drugtargetcommons.dtc_annotation_layer set annotations_flag = 'yes' where dtc_molregno = '" + temp_molregno + "' "
						update_insert = update_insert + " and dtc_tid = '" + temp_tid + "' and dtc_assay_id = '" + temp_assay_Id  + "' and dtc_activity_id = '" + temp_activity_id + "' and dtc_doc_id = '"
						update_insert = update_insert +   temp_doc_id + "'  and dtc_record_id = '" + temp_record_id + "' and approved_by='"+request.user.email+"'; "


						cursor.execute(update_insert)
						sql_del = " delete from drugtargetcommons.suggestion_for_review where id = " + str(row['id'])
						print(row['id'],' updated')
								#command to execute insert sql into data
								# cursor.execute(update_insert)
					#else condition to set missing Ids(molregno,doc_id,record_id,tid,assay_Id,activity_id)			
					else:

						#save id which is approved to be deleted from suggestion_from_review_table
						approved_ids.append(row['id'])
						#check for dtc_molregno if not present
						if not temp_molregno:
							#check if dtc_molregno exits
							dtc_molregno_exist_query = "select (select term_id from drugtargetcommons.start_search where term_name='%(pref_name)s' and term_type = 'COMPOUND' Limit 1) AS dtc_molregno" % {'pref_name':row['compound_name']}
							cursor.execute(dtc_molregno_exist_query)
							
							dtc_molregno_exist = cursor.fetchone()[0]
							
							if dtc_molregno_exist:
								temp_molregno = dtc_molregno_exist
							else:
								
								insert = "insert into drugtargetcommons.molecule_dictionary (pref_name) values('%(pref_name)s') returning dtc_molregno" % {'pref_name':row['compound_name']}
								cursor.execute(insert)
								temp_molregno = cursor.fetchone()[0]
								
							#insert standard_inchi key into compounds_structure table
								cursor.execute("insert into drugtargetcommons.compound_structures (standard_inchi_key, dtc_molregno)values (%s, %s)" , (row['standard_inchi_key'],temp_molregno))
								
								#insert into start_search
								cursor.execute("insert into drugtargetcommons.start_search (term_id, term_name, term_type) values (%s, %s,%s)" , (temp_molregno,row['compound_name'],'COMPOUND'))
						
						
						#check for dtc_doc_id if not present
						if not temp_doc_id:

													#check if dtc_molregno exits
							dtc_doc_exist_query = "select (select term_id from drugtargetcommons.start_search where term_name='%(pubmed_id)s' and term_type = 'PUBLICATION') AS dtc_doc_id" % {'pubmed_id':row['pubmed_id']}

							cursor.execute(dtc_doc_exist_query)
							dtc_doc_exist = cursor.fetchone()[0]
	
							if dtc_doc_exist:
								temp_doc_id = int(dtc_doc_exist)
							else:

								cursor.execute("insert into drugtargetcommons.docs (pubmed_id, journal, title, volume, issue, authors, year )values (%s, %s,%s,%s,%s,%s,%s) returning dtc_doc_id" , (row['pubmed_id'],row['journal'],row['title'],row['volume'],row['issue'],row['authors'],row['year']))
								temp_doc_id = cursor.fetchone()[0]
								
								#insert into start_search
								cursor.execute("insert into drugtargetcommons.start_search (term_id, term_name, term_type) values (%s, %s,%s)" , (temp_doc_id,row['pubmed_id'],'PUBLICATION'))
							
						
						#check for dtc_record_id if not present

						if not temp_record_id:
							if temp_molregno and temp_doc_id:
								temp_record_id_exist_query = "select (select dtc_record_id from drugtargetcommons.compound_records where dtc_molregno='%(dtc_molregno)s' and dtc_doc_id = %(dtc_doc_id)s ) AS dtc_record_id" % {'dtc_molregno':temp_molregno,'dtc_doc_id':temp_doc_id}
								cursor.execute(temp_record_id_exist_query)
								temp_record_id_exist = cursor.fetchone()[0]
								if temp_record_id_exist:
									temp_record_id = temp_record_id_exist
								else:
									cursor.execute("insert into drugtargetcommons.compound_records (compound_name, dtc_doc_id, dtc_molregno)values (%s, %s,%s) returning dtc_record_id" , (row['compound_name'],temp_doc_id,temp_molregno))
									#insert into record id table
									temp_record_id = cursor.fetchone()[0]	
							else:
								cursor.execute("insert into drugtargetcommons.compound_records (compound_name, dtc_doc_id, dtc_molregno)values (%s, %s,%s) returning dtc_record_id" , (row['compound_name'],temp_doc_id,temp_molregno))
								#insert into record id table
								temp_record_id = cursor.fetchone()[0]
									
						
						#check for temp_tid if not present		
						if not temp_tid:
																			#check if dtc_tid exits
							dtc_tid_exist_query = "select (select term_id from drugtargetcommons.start_search where term_name='%(pref_name)s' and term_type = 'TARGET' Limit 1) AS dtc_tid" % {'pref_name':row['target_pref_name']}
							cursor.execute(dtc_tid_exist_query)
							
							dtc_tid_exist = cursor.fetchone()[0]
							
							if dtc_tid_exist:
								temp_tid = dtc_tid_exist
							else:
								
								# Insertion of ‘pref_name’ in target_dictionary table (save auto generated dtc_ tid into variable)
								insert = "insert into drugtargetcommons.target_dictionary (pref_name)values('%(pref_name)s') returning dtc_tid" % {'pref_name':row['target_pref_name']}
								cursor.execute(insert)
								temp_tid = cursor.fetchone()[0]
								#insert into start_search
								cursor.execute("insert into drugtargetcommons.start_search (term_id, term_name, term_type) values (%s, %s,%s)" , (temp_tid,row['target_pref_name'],'TARGET'))


							
						#check for temp_assay_Id if not present		
						if not temp_assay_Id:
							if temp_tid:
								# Insertion of ‘pref_name’ in target_dictionary table (save auto generated dtc_ tid into variable)
								cursor.execute("insert into drugtargetcommons.assays (description, dtc_doc_id, dtc_tid,assay_cell_type)values (%s,%s,%s,%s) returning dtc_assay_id" , (row['assay_description'],temp_doc_id,temp_tid,row['assay_cell_type']))
								temp_assay_Id = cursor.fetchone()[0]
										
						#check for temp_activity_id if not present	
						if not temp_activity_id:

							if row['wildtype_or_mutant'] or row['endpoint_actionmode_id'] != 100 or row['assay_format_id'] != 100 or row['assay_type_id'] != 100 or row['assay_sub_type_id'] != 100 or row['inhibitor_type_id'] != 100 or row['detection_technology_id'] != 100:
								row['annotations_flag'] = 'yes'
							else:
								row['annotations_flag'] = 'no'	
							
							#insert in  tables in dtc Activity table

							cursor.execute("insert into drugtargetcommons.activities (standard_type,standard_relation, standard_value, standard_units, dtc_molregno, dtc_record_id, dtc_doc_id, dtc_assay_id) values (%s,%s,%s,%s,%s,%s,%s,%s) returning dtc_activity_id" , (row['ep_standard_type'],row['ep_standard_relation'],row['ep_standard_value'],row['ep_standard_units'],temp_molregno,temp_record_id,temp_doc_id,temp_assay_Id))

							temp_activity_id = cursor.fetchone()[0]
							


							endpoint_action_id = id_mapping[str(row['endpoint_actionmode_id']).rstrip().upper()]
							assay_format_id =id_mapping[str(row['assay_format_id']).rstrip().upper()]
							assay_type_id = id_mapping[str(row['assay_type_id']).rstrip().upper()]
							assay_sub_type_id = id_mapping[str(row['assay_sub_type_id']).rstrip().upper()]
							inhibitor_type_id = id_mapping[str(row['inhibitor_type_id']).rstrip().upper()]
							detection_technology_id = id_mapping[str(row['detection_technology_id']).rstrip().upper()]

							cursor.execute("insert into drugtargetcommons.dtc_annotation_layer (dtc_molregno, dtc_record_id, dtc_doc_id, dtc_activity_id, dtc_assay_id,dtc_tid, wildtype_or_mutant, mutation_info, endpoint_actionmode_id, assay_format_id, assay_type_id, assay_sub_type_id, inhibitor_type_id, detection_technology_id, compound_concentration_value,  compound_concentration_value_unit, substrate_type,substrate_relation, substrate_value, substrate_units,  annotation_comments, time_stamp,annotations_flag, curator_email,approved_by) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning dtc_activity_id" , (temp_molregno,temp_record_id,temp_doc_id,temp_activity_id,temp_assay_Id,temp_tid,row['wildtype_or_mutant'],row['mutation_info'],endpoint_action_id,assay_format_id,assay_type_id,assay_sub_type_id,inhibitor_type_id,detection_technology_id,row['compound_concentration_value'],row['compound_concentration_value_unit'],row['substrate_type'],row['substrate_relation'],row['substrate_value'],row['substrate_units'],row['annotation_comments'],datetime.now(),row['annotations_flag'],row['curator_email'],request.user.email))
							
					
						sql_del = " delete from drugtargetcommons.suggestion_for_review where id = " + str(row['id'])
							
						cursor.execute(sql_del)
						print(row['id'],' new dtc annotation layer record inserted')	
				
				
			elif data['status'] == 'declined':
				sql_del = " delete from drugtargetcommons.suggestion_for_review where id IN "
				ids = []
				for row in data['json_table']:
					ids.append(row['id'])
				sql_del = sql_del + '(' + ','.join(str(i) for i in ids) + ')'

				cursor = connection.cursor()
				cursor.execute(sql_del)

			elif data['status'] == 'pending':
				# id_list = [row['id'] for row in body['json_table']]
				# SuggestionForReview.objects.filter(id__in=id_list).update(myattribute=True)
				update_insert = ""
				sql = " update drugtargetcommons.suggestion_for_review set status_id='pending' where id = '"
				id_mapping = { "BIOCHEMICAL":0, "CELL_BASED":1, "CELL_FREE":2, "PHYSIOCHEMICAL":4,"TISSUE":5, "ORGANISM_BASED":3, 
				"FUNCTIONAL":6,"BINDING":13,"PHENOTYPIC":0,
				"BINDING_REVERSIBLE":0,"BINDING_IRREVERSIBLE":1,"BINDING_SATURATION":2,"ENZYME_ACTIVITY":3,"PROCESS":4,"REPORTER_GENE":5,"SIGNALLING":6,"UPTAKE":7,"VIABILITY":8,
				"COMPETITIVE_INHIBITOR":0,"NON_COMPETITIVE_INHIBITOR":1,"ALLOSTERIC_INHIBITOR":2,
				"ACTIVATION":0,"CYTOTOXOCITY":1,"GROWTH_INHIBITION":2,"INHIBITION":3,"INVERSE_AGONIST":4,
				"FLUORESECENCE":0,"LUMINESCENCE":1,"SPECTROPHOTOMETRY":2,"RADIOMETRY":3,"MICROSCOPY":4,"LABEL_FREE_TECHNOLOGY":5,"FLUORESCENCE_POLARIZATION":6,"TRF":7,"TR_FRET":8,"ALPHASCREEN":9,"QPCR":10,"TERMAL_SHIFT":11,
				"":100,"NONE":100 }
				field_names = SuggestionForReview._meta.get_all_field_names()
				for row in data['json_table']:
					row['endpoint_actionmode_id']=str(id_mapping[str(row['endpoint_actionmode_id']).upper()])
					row['assay_format_id']=str(id_mapping[str(row['assay_format_id']).upper()])
					row['assay_type_id']=str(id_mapping[str(row['assay_type_id']).upper()])
					row['assay_sub_type_id']=str(id_mapping[str(row['assay_sub_type_id']).upper()])
					row['inhibitor_type_id']=str(id_mapping[str(row['inhibitor_type_id']).upper()])
					row['detection_technology_id']=str(id_mapping[str(row['detection_technology_id']).upper()])
					update_insert = update_insert + " update drugtargetcommons.suggestion_for_review set "
					for key,value in row.items():
						if key in field_names:
							if value and key != 'status' and key != 'time_stamp':
								update_insert = update_insert  + str(key) + "= '" + str(value) + "', "	
					update_insert = update_insert  + " status='pending' where id = '" + str(row['id']) + "';"	
				cursor = connection.cursor()
				cursor.execute(update_insert)
	return HttpResponse(json.dumps({'success':1}),content_type="application/json")

#target inditation information
@csrf_exempt
def targetdiseaseinfo(request):
	tid = request.GET['tid']
	
	sql = "select distinct dtc_tid, gene_name, disease_id, disease_name, score, no_of_snps, description, source,  pubmed_id from drugtargetcommons.gene_disease_association where dtc_tid='%(dtc_tid)s'" % {'dtc_tid':tid}
	cursor = connection.cursor()
	cursor.execute(sql)
	result = dictfetchall(cursor)
	return HttpResponse(json.dumps(result,default=decimal_default),content_type="application/json")
#for target cross ref
@csrf_exempt
def gettargetcrfinfo(request):
	tid = request.GET['tid']
	sql = "SELECT uniprotkbac as uniprot_id, id_type as database_name, id_value, link as url from drugtargetcommons.target_id_mapping tim where tim.id_type in ('PharmGKB','Orphanet','GeneTree','KO','DIP','GeneCards','UniRef90','CCDS','MIM','RefSeq','GenomeRNAi','PDB','KEGG','UniRef100','OrthoDB','GuidetoPHARMACOLOGY','HGNC','UniGene','DMDM','Reactome','TreeFam','BioMuta','Ensembl','Ensembl_TRS','UniRef50','MINT','neXtProt','ChEMBL','EMBL','GeneID','DrugBank') and tim.uniprotkbac in(select distinct accession from drugtargetcommons.component_sequences cs, drugtargetcommons.target_components tc where tc.dtc_tid='%(tid)s' and tc.component_id=cs.component_id)" % {'tid':tid}
	cursor = connection.cursor()
	cursor.execute(sql)
	result = dictfetchall(cursor)
	return HttpResponse(json.dumps(result,default=decimal_default),content_type="application/json")

#for Compound
@csrf_exempt
def diseaseinfo(request):
	molregno = request.GET['molregno']
	
	sql = "SELECT distinct study_id, drug, phase, mesh_term, symptoms, study_title, enrollment, study_type, adverse_effects,start_date, status, min_age, max_age, gender, pubmed_ids, dtc_molregno from  drugtargetcommons.clinical_data where dtc_molregno='%(molregno)s'" % {'molregno':molregno}
	cursor = connection.cursor()
	cursor.execute(sql)
	result = dictfetchall(cursor)
	return HttpResponse(json.dumps(result,default=decimal_default),content_type="application/json")
#for compound
@csrf_exempt
def getcrfinfo(request):
	molregno = request.GET['molregno']
	sql = "SELECT distinct cid.src_id, us.name as database_name, cid.compound_id as id, concat(us.base_id_url,cid.compound_id) as url from drugtargetcommons.uc_source us,drugtargetcommons.compound_id_mapping cid where cid.dtc_molregno='%(molregno)s' and us.src_id = cid.src_id and cid.src_id in (1,2,3,4,6,7,9,10,11,12,14,15,17,18, 20 ,22,23,25,26,27,28,29,31)" % {'molregno':molregno}
	cursor = connection.cursor()
	cursor.execute(sql)
	result = dictfetchall(cursor)
	return HttpResponse(json.dumps(result,default=decimal_default),content_type="application/json")


@csrf_exempt
def getmutantinfo(request):

	mutant = ''.join([request.GET['mutant'].split(')')[0],'%'])

	sql = "SELECT mutant as mutated_target, effect as drug_effect, Drug_name as drug_name, evidence_level, gene_name, gdna, tumor_type,reference from drugtargetcommons.mutant_disease_association where mutant like '%(mutant)s'" % {'mutant':mutant}
	cursor = connection.cursor()
	cursor.execute(sql)
	result = dictfetchall(cursor)
	return HttpResponse(json.dumps(result,default=decimal_default),content_type="application/json")

@csrf_exempt
def edit_submissions(request):
	body = json.loads(request.body.decode('utf-8'))
	update_insert = ""
	sql = " update drugtargetcommons.suggestion_for_review set  where id = '"
	id_mapping = { "BIOCHEMICAL":0, "CELL_BASED":1, "CELL_FREE":2, "PHYSIOCHEMICAL":4,"TISSUE":5, "ORGANISM_BASED":3, 
	"FUNCTIONAL":6,"BINDING":13,"PHENOTYPIC":0,
	"BINDING_REVERSIBLE":0,"BINDING_IRREVERSIBLE":1,"BINDING_SATURATION":2,"ENZYME_ACTIVITY":3,"PROCESS":4,"REPORTER_GENE":5,"SIGNALLING":6,"UPTAKE":7,"VIABILITY":8,
	"COMPETITIVE_INHIBITOR":0,"NON_COMPETITIVE_INHIBITOR":1,"ALLOSTERIC_INHIBITOR":2,
	"ACTIVATION":0,"CYTOTOXOCITY":1,"GROWTH_INHIBITION":2,"INHIBITION":3,"INVERSE_AGONIST":4,
	"FLUORESECENCE":0,"LUMINESCENCE":1,"SPECTROPHOTOMETRY":2,"RADIOMETRY":3,"MICROSCOPY":4,"LABEL_FREE_TECHNOLOGY":5,"FLUORESCENCE_POLARIZATION":6,"TRF":7,"TR_FRET":8,"ALPHASCREEN":9,"QPCR":10,"TERMAL_SHIFT":11,
	"":100,"NONE":100 }

	field_names = SuggestionForReview._meta.get_all_field_names()

	for row in body['json_table']:
		row['endpoint_actionmode_id']=str(id_mapping[str(row['endpoint_actionmode_id']).upper()])
		row['assay_format_id']=str(id_mapping[str(row['assay_format_id']).upper()])
		row['assay_type_id']=str(id_mapping[str(row['assay_type_id']).upper()])
		row['assay_sub_type_id']=str(id_mapping[str(row['assay_sub_type_id']).upper()])
		row['inhibitor_type_id']=str(id_mapping[str(row['inhibitor_type_id']).upper()])
		row['detection_technology_id']=str(id_mapping[str(row['detection_technology_id']).upper()])
		update_insert = update_insert + " update drugtargetcommons.suggestion_for_review set "
		for key,value in row.items():
			if key in field_names:
				if value and key != 'status' and key != 'time_stamp':
					update_insert = update_insert  + str(key) + "= '" + str(value) + "', "	
		update_insert = update_insert  + " status='pending' where id = '" + str(row['id']) + "';"
	cursor = connection.cursor()
	cursor.execute(update_insert)
	return HttpResponse(json.dumps({'success':1}),content_type="application/json")