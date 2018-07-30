from tastypie import fields
from tastypie.serializers import Serializer
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from django.contrib.auth.models import User
from dtc.models import *
import logging

NUMBER_FILTERS = ['exact', 'range', 'gt', 'gte', 'lt', 'lte', 'in', 'isnull']
FLAG_FILTERS = ['exact', 'isnull']
CHAR_FILTERS = ['exact', 'iexact', 'contains', 'icontains', 'istartswith', 'startswith', 'endswith', 'iendswith', 'search', 'regex', 'iregex', 'isnull', 'in']
DATE_FILTERS = ['exact', 'year', 'month', 'day', 'week_day', 'isnull']

# class DTCApiSerializer(Serializer):

#     formats = ['xml', 'json', 'jsonp', 'yaml']

#     content_types = {
#         'json': 'application/json',
#         'jsonp': 'text/javascript',
#         'xml': 'application/xml',
#         'yaml': 'text/yaml',
#         'urlencode': 'application/x-www-form-urlencoded',
#     }

#     def __init__(self, name=None, names=None):
#         self.objName = name
#         self.objNames = names
#         self.log = logging.getLogger(__name__)
#         super(DTCApiSerializer, self).__init__()

class ActivityResource(ModelResource):

	chembl_id = fields.CharField('dtc_molregno__chembl_id', null=True, blank=True)

	pubmed_id = fields.CharField('dtc_doc__pubmed_id', null=True, blank=True)
	compound_name = fields.CharField('dtc_molregno__pref_name', null=True, blank=True)
	dtc_molregno = fields.CharField('dtc_molregno__dtc_molregno', null=True, blank=True)
	dtc_doc_id = fields.CharField('dtc_doc__dtc_doc_id', null=True, blank=True)
	uniprot_id = fields.CharField('target__uniprot_id', null=True, blank=True)
	target_pref_name = fields.CharField('dtc_tid.pref_name', null=True, blank=True)
	gene_name = fields.CharField('target__gene_name', null=True, blank=True)
	
	endpoint_standard_type = fields.CharField('dtc_activity__standard_type', null=True, blank=True)
	endpoint_standard_relation = fields.CharField('dtc_activity__standard_relation', null=True, blank=True)
	endpoint_standard_value = fields.CharField('dtc_activity__standard_value', null=True, blank=True)
	endpoint_standard_units = fields.CharField('dtc_activity__standard_units', null=True, blank=True)
	annotated = fields.CharField('annotations_flag', null=True, blank=True)
	assay_cell_type = fields.CharField('assay__assay_cell_type', null=True, blank=True)
	# assay_description = fields.CharField('assay__description', null=True, blank=True)
	assay_format = fields.CharField('assay_format__term', null=True, blank=True)
	assay_type = fields.CharField('assay_type__term', null=True, blank=True)
	assay_sub_type = fields.CharField('assay_sub_type__term', null=True, blank=True)
	endpoint_actionmode = fields.CharField('endpoint_actionmode__term', null=True, blank=True)
	inhibitor_type = fields.CharField('inhibitor_type__term', null=True, blank=True)
	detection_technology = fields.CharField('detection_technology__term', null=True, blank=True)
	# activity_id = fields.CharField('activity__activity_id', null=True, blank=True)
	# target_chembl_id = fields.CharField('dtc_activity__assay__tid__chembl__chembl_id', null=True, blank=True)
	
	target_organism = fields.CharField('dtc_tid__organism', null=True, blank=True)
	# assay_chembl_id = fields.CharField('activity__assay__chembl__chembl_id', null=True, blank=True)
	assay_type = fields.CharField('assay_type__term', null=True, blank=True)
	# assay_description = fields.CharField('activity__assay__description', null=True, blank=True)
	year = fields.IntegerField('dtc_doc__year', null=True, blank=True)
	journal = fields.CharField('dtc_doc__journal', null=True, blank=True)
	volume = fields.CharField('dtc_doc__volume', null=True, blank=True)
	issue = fields.CharField('dtc_doc__issue', null=True, blank=True)
	authors = fields.CharField('dtc_doc__authors', null=True, blank=True)
	
	
    
	class Meta:
		queryset = DtcAnnotationLayer.objects.all()
		resource_name = 'bioactivity'
		collection_name = 'bioactivities'
		# serializer = DTCApiSerializer(resource_name, {collection_name : resource_name})
		# prefetch_related = ['dtc_molregno'
		#  				# 	 'endpoint_actionmode',
		# 					# 'inhibitor_type',
		#  				# 	'wildtype_or_mutant',
		#  				# 	'detection_technology',
		#  				# 	'targetcomponents_set',
		#  				# 	'dtc_doc',
		# 					]
		fields = (
			'chembl_id',
            'compound_name',
            'gene_name',
            'pubmed_id',
            'assay_cell_type',
			'wildtype_or_mutant',
            'assay_format',
            'assay_type',
            'assay_sub_type',
            'endpoint_actionmode',
            'inhibitor_type',
            'detection_technology',
            'wildtype_or_mutant',
            'mutation_info',
            'compound_concentration_value',
            'compound_concentration_value_unit',
            'substrate_type',
            'substrate_relation',
            'substrate_value',
            'substrate_units',
            'endpoint_standard_type',
            'endpoint_standard_relation',
            'endpoint_standard_value',
            'endpoint_standard_units',
            'assay_cell_type',
            # 'assay_description',
            'curator_email',
            'time_stamp',
            'annotation_comments',
            'target_pref_name',
            'target_organism',
            'dtc_molregno',
            'dtc_doc_id',
            # 'dtc_assay',
            'dtc_record_id',
            # 'dtc_tid',
            'annotated',
			'year',
			'journal',
			'volume',
			'issue',
			'authors'

		)
		filtering = {
			'dtc_molregno' : CHAR_FILTERS,
			'dtc_doc_id' : NUMBER_FILTERS,
			'compound_name': CHAR_FILTERS,
			'pubmed_id':ALL,
			'assay_cell_type':ALL,
			# 'standard_inchi_key':ALL,
			'assay_format' :ALL,
			'assay_type':ALL,
			'assay_sub_type':ALL,
			'endpoint_actionmode':ALL,
			'endpoint_standard_type':ALL,
			'endpoint_standard_value':ALL,
			'endpoint_standard_relation':ALL,
			'endpoint_standard_units':ALL,
			'inhibitor_type':ALL,
			'wildtype_or_mutant':ALL,
			'detection_technology':ALL,
			'mutation_info':ALL,
			# 'assay_description' : ALL,
			'uniprot_id':ALL,
			'journal': ALL,
			'authors': ALL,
			'year' : NUMBER_FILTERS,
			'issue' : ALL,
			# 'molecule_chembl_id' : ALL,
			# 'compound_name':ALL,
			# 'pchembl_value': NUMBER_FILTERS,
			# 'potential_duplicate' : FLAG_FILTERS,
			'curator_email' : CHAR_FILTERS,
			# 'published_type': CHAR_FILTERS,
			# 'published_units' : CHAR_FILTERS,
			# 'published_value' : NUMBER_FILTERS,
			# 'qudt_units' : CHAR_FILTERS,
			# 'record_id' : NUMBER_FILTERS,
			'standard_flag': FLAG_FILTERS,
			'standard_relation' : CHAR_FILTERS,
			'standard_type' : CHAR_FILTERS,
			'standard_units' : CHAR_FILTERS,
			'standard_value' : NUMBER_FILTERS,
			'target_pref_name' : CHAR_FILTERS,
			'gene_name':CHAR_FILTERS,
			'target_organism' : CHAR_FILTERS,
			# 'uo_units' : CHAR_FILTERS,
		}
		ordering = [field for field in filtering.keys()] 