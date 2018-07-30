$(document).ready(function () {
            //Getting the source data with ajax GET request

            $('#title').html('DTC annotated data for Standard Inchikey:<strong>' + get('key')+'</strong>');
            var source =
            {
                async: false,
                url: 'get_annotations',
                datatype: "json"
            };

            var dataAdapter = new $.jqx.dataAdapter(source,
                {

                    contentType: 'application/json; charset=utf-8',
                    loadServerData: function (serverdata, source, callback) {
                        $.ajax({
                            type: "POST",
                            contentType: "application/json; charset=utf-8",
                            url: source.url,
                            data:JSON.stringify({'inchikey': get('key') }),
                            dataType: "json",
                            success: function (data) {                              
                                callback({ records: data });
                            }

                        });
                    }
                }
            );
            $("#jqxgrid").jqxGrid(
                                  {
                                      width: '100%',
                                      height:'600px',
                                      source: dataAdapter,
                                      filterable: true,
                                      columnsresize: true,
                                      autoshowfiltericon: false,
                                      sortable: true,
                                      pageable: true,
                                      enablebrowserselection:true,
                                      theme: 'bootstrap',
                                      altrows: true,
                                      pagesizeoptions: ['25', '50', '100'],
                                      ready: function () {
                                          $("#jqxgrid").jqxGrid({ pagesize: 25 });
                                      },

                                      columns: [
                         

                                  { text: 'Compound ID', datafield: 'compound_id', width: 200, cellsrenderer: linkrenderer },
					                        { text: 'Standard Inchikey', datafield: 'standard_inchi_key', width: 250 },
					                        { text: 'Compound Name', datafield: 'compound_name', width: 200 },
                                  { text: 'Target ID', datafield: 'target_id', width: 200, cellsrenderer: linkrenderer },
                                  { text: 'Target Name', datafield: 'target_pref_name', width: 200 },
                                  { text: "Gene Name", datafield: "gene_names", width: 200 },                                         
                                  { text: "Wild type or mutant", datafield: "wildtype_or_mutant", width: 200 },
					                        { text: "Mutation information", datafield: "mut_info", width: 200 },
					                        { text: 'PubMed ID', datafield: 'pubmed_id', width: 200, cellsrenderer: linkrenderer },
                                           // { text: 'PubMed ID', datafield: 'pubmed_id', width: 200 },
					                        { text: 'End Point Standard Type', datafield: 'ep_standardtype', width: 200 },
					                        { text: 'End Point Standard Relation', datafield: 'ep_standardrelation', width: 200 },
					                        { text: 'End Point Standard Value', datafield: 'ep_standardvalue', width: 200 },
					                        { text: 'End Point Standard Units', datafield: 'ep_standardunits', width: 200 },
					                        { text: 'Endpoint Mode of Action', datafield: 'ep_action_mode', width: 200 },
                                  { text: 'Assay Format', datafield: 'assay_format', width: 200 },
                                  { text: 'Assay Type', datafield: 'assaytype', width: 200 },
                                  { text: 'Assay Sub Type', datafield: 'assay_subtype', width: 200 },
					                        { text: 'Inhibitor Type', datafield: 'inhibitor_type', width: 200 },
					                        { text: 'Detection Technology', datafield: 'detection_tech', width: 200 },
                                            { text: 'Compound concentration value', datafield: 'concentration_val', width: 200 },
					                        { text: 'Compound concentration value units', datafield: 'concentration_value_units', width: 200 },
                                             { text: "Substrate's type", datafield: "substrate_type", width: 200 },
					                        { text: "Substrate Type's Standard Relation", datafield: "substrate_relation", width: 200 },
					                        { text: "Substrate Type's Standard Value", datafield: "substrate_value", width: 200 },
					                        { text: "Substrate Type's Standard Units", datafield: "substrate_units", width: 200 },
                                  { text: "Assay cell line", datafield: 'assay_cell_Line', width: 200 },
                                  { text: "Assay Description", datafield: 'assay_description', width: 200 },
                                  { text: "Activity Comments", datafield: 'activity_comments', width: 200 },
					                        { text: "Title", datafield: "title", width: 200 },
					                        { text: "Journal", datafield: "journal", width: 200 },
					                        { text: "Year", datafield: 'year', width: 200 },
					                        { text: "Volume", datafield: 'volume', width: 200 },
					                        { text: "Issue", datafield: 'issue', width: 200 },
					                        { text: "Authors", datafield: 'authors', width: 200 },
                                  { text: "Annotation comments", datafield: 'ann_comments', width: 200 },
                                  { text: "Curator's email", datafield: 'email', width: 200 },
                                  { text: "User", datafield: 'user', width: 200 },
                                  { text: "Time", datafield: 'time', width: 200 }
                                ]
                                  });

           
          // $("#excelExport").click(function () {

          //     var count = $("#jqxgrid").jqxGrid('getdatainformation').rowscount;
          //     if (count > 15000) {

          //         alertify.error('Too many records,apply filtering to reduce records');

          //     } else {

          //         export_data();
          //     }

          // });

        });
      // function export_data() {


      //     xhttp = new XMLHttpRequest();
      //     xhttp.onreadystatechange = function() {
      //         var a, today;
      //         if (xhttp.readyState === 4 && xhttp.status === 200) {
      //             a = document.createElement('a');
      //             a.href = window.URL.createObjectURL(xhttp.response);
      //             today = new Date();
      //             a.download = "bioactivities_" + today.toDateString().split(" ").join("_") + ".xlsx";
      //             a.style.display = 'none';
      //             document.body.appendChild(a);
      //             return a.click();
      //         }
      //     };
      //     xhttp.open("POST", "/export_to_excell/", true);
      //     xhttp.setRequestHeader("Content-Type", "application/json");
      //     xhttp.responseType = 'blob';
      //     xhttp.send(JSON.stringify({'json_table':$('#jqxgrid').jqxGrid('getrows')}));

      // }
        function get(name) {
            if (name = (new RegExp('[?&]' + encodeURIComponent(name) + '=([^&]*)')).exec(location.search))
                return decodeURIComponent(name[1]);
        }
     
        var columnrenderer = function (value) {
            return '<div style="text-align: center; margin-top: 5px;">' + value + '</div>';
        }
        var linkrenderer = function (row, column, value) {
            var href = '';
            if (column == 'compound_id') {
                href = "https://www.ebi.ac.uk/chembl/compound/inspect/" + value;
            } else if (column == 'target_id') {
                href = "http://www.uniprot.org/uniprot/?query=accession:" + value.replace(',', 'or accession:');

            } else {
                href = "http://www.ncbi.nlm.nih.gov/pubmed/?term=" + value;
            }

            return '<div style="margin: 5px;"><a target= "_blank" href="' + href + '">' + value + '</a></div>';
        }