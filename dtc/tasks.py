# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from dtc.models import SuggestionForReview
from dtc.models import StartSearch
from django.db.models import Q
import pdb

@shared_task
def process_suggestions():
	suggestions = SuggestionForReview.objects.filter(Q(status='NEW') & (Q(dtc_molregno__isnull=True) | Q(dtc_doc_id__isnull=True) | Q(dtc_tid__isnull=True)))
	print(suggestions.count())
	for idx, suggestion in enumerate(suggestions):
		if not suggestion.dtc_molregno:
			if suggestion.compound_name:
				instance = StartSearch.objects.filter(term_name=suggestion.compound_name,term_type='COMPOUND')
				if len(instance) == 1:
					suggestion.dtc_molregno = instance.first().term_id
				else:
					print(suggestion.compound_name," doesn't exist")	
		if not suggestion.dtc_doc_id:		
			if suggestion.pubmed_id:
				instance = StartSearch.objects.filter(term_name=suggestion.pubmed_id,term_type='PUBLICATION')
				if len(instance) == 1:
					suggestion.dtc_doc_id = instance.first().term_id
				else:
					print(suggestion.pubmed_id," doesn't exist")	
		if not suggestion.dtc_tid:
			if suggestion.target_pref_name:
				instance = StartSearch.objects.filter(term_name=suggestion.target_pref_name,term_type='TARGET')
				if len(instance) == 1:
					suggestion.dtc_tid = instance.first().term_id
				else:
					print(suggestion.target_pref_name," doesn't exist")
		if suggestion.has_changed():
			suggestion.save()			
		
		print (idx)
			
		

  