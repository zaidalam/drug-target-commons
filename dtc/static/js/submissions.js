   var editedCells = new Array();
        var editable = false;
        $(document).ready(function () {
            //Getting the source data with ajax GET request                   
            //SearchText();
            //setTextBoxColor();
            //$('#txtSearchClient').val(get('value'));


            selection = 'none'
        
          

           
            var source =
            {
                async: false,
                url: '/GUI/BrowseSuggestion.aspx/load_submissions',
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
                             data: "{'inchikey':'key'}",
                             dataType: "json",
                             success: function (data) {
                                 var json = jQuery.parseJSON(data.d);
                                 
                                 callback({ records: json });
                             }
                         });
                     }

                 }
             );

              
           
            var cellclass = function (row, datafield, value) {


                if (datafield == 'status_id') {
                    if (value == 'NEW') {
                        return 'alert-success';
                    }
                    else if (value == 'DECLINED') {
                        return 'alert-danger';
                    }
                    else return 'alert-info';
                }

                for (var i = 0; i < editedCells.length; i++) {
                    if (editedCells[i].row == row && editedCells[i].column == datafield) {
                        return "editedCell";
                    }
                }


            }
            var cellvaluechanging = function (row, datafield, columntype, oldvalue, newvalue) {
                if (oldvalue != newvalue) {
                    editedCells.push({ row: row, column: datafield });

                }
            };

            // $("#jqxgrid").jqxGrid(
            // {
            //     width: '100%',
            //     height: '600px',
            //     source: dataAdapter,
            //     filterable: true,
            //     columnsresize: true,
            //     autoshowfiltericon: false,
            //     sortable: true,
            //     altrows: true,
            //     theme: 'bootstrap',
            //     editable: editable,
            //     pageable: true,
            //     selectionmode: selection,
            //     pagesizeoptions: ['25', '50', '100'],
            //     ready: function () {
            //         $("#jqxgrid").jqxGrid({ pagesize: 25 });

            //     },

            //     columns: [

                   
            //           { text: 'Status', datafield: 'status_id', width: 80, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Curator's email", pinned: true, datafield: 'curator_email', width: 200 },
            //           { text: 'Compound ID', datafield: 'compound_id', width: 200, cellsrenderer: linkrenderer, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: 'Standard Inchikey', datafield: 'standard_inchi_key', width: 250, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: 'Compound Name', datafield: 'compound_name', width: 200 },
            //           { text: 'Target ID', datafield: 'target_id', width: 200, cellsrenderer: linkrenderer, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: 'Target Name', datafield: 'target_pref_name', width: 200 },
            //             {
            //                 text: "Wild type or mutated", datafield: 'wildtype_or_mutant', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
            //                 initeditor: function (row, cellvalue, editor) {
            //                     editor.jqxDropDownList({ source: wildType });
            //                 }
            //             },
                   
            //           { text: "Mutation information", datafield: "mut_info", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: 'PubMed ID', datafield: 'pubmed_id', width: 200, cellsrenderer: linkrenderer, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: 'End Point Standard Type', datafield: 'ep_standard_type', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: 'End Point Standard Relation', datafield: 'ep_standard_relation', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: 'End Point Standard Value', datafield: 'ep_standard_value', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: 'End Point Standard Units', datafield: 'ep_standard_units', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           {
            //               text: "Endpoint Mode of Action", datafield: 'endpoint_actionmode_id', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
            //               initeditor: function (row, cellvalue, editor) {
            //                   editor.jqxDropDownList({ source: EMA });
            //               }
            //           },
            //           {
            //               text: "Assay Format", datafield: 'assay_format_id', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
            //               initeditor: function (row, cellvalue, editor) {
            //                   editor.jqxDropDownList({ source: assayFormat });
            //               }
            //           },
            //           {
            //               text: "Assay Type", datafield: 'assay_type_id', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
            //               initeditor: function (row, cellvalue, editor) {
            //                   editor.jqxDropDownList({ source: assayType});
            //               }
            //           },
            //           {
            //               text: "Assay Sub Type", datafield: 'assay_sub_type_id', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
            //               initeditor: function (row, cellvalue, editor) {
            //                   editor.jqxDropDownList({ source: assaySubtype });
            //               }
            //           },
            //           {
            //               text: "Inhibitor Type", datafield: 'inhibitor_type_id', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
            //               initeditor: function (row, cellvalue, editor) {
            //                   editor.jqxDropDownList({ source: inhibitorType });
            //               }
            //           },
            //           {
            //               text: "Detection Technology", datafield: 'detection_technology_id', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
            //               initeditor: function (row, cellvalue, editor) {
            //                   editor.jqxDropDownList({ source: detectionTech });
            //               }
            //           },
                    
            //           { text: 'Compound concentration value', datafield: 'compound_single_conc_value', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: 'Compound concentration value units', datafield: 'cscv_stand_unit', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Substrate's type", datafield: "substrate_type", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Substrate Type's Standard Relation", datafield: "subs_standard_relation", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Substrate Type's Standard Value", datafield: "subs_standard_value", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Substrate Type's Standard Units", datafield: "subs_stand_units", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Assay cell line", datafield: 'assay_cell_Line', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Assay Description", datafield: 'assay_description', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Activity Comments", datafield: 'activity_comment', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Title", datafield: "title", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Journal", datafield: "journal", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Year", datafield: '_year', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Volume", datafield: 'volume', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Issue", datafield: 'issue', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Authors", datafield: 'authors', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Annotation comments", datafield: 'annotation_comments', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "User", datafield: 'user_stamp', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Time", datafield: 'time_stamp', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Assay ID", datafield: 'assay_id', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Local Target ID", datafield: 'tid', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Activity ID", datafield: 'activity_id', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Molregno", datafield: 'molregno', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Record ID", datafield: 'record_id', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
            //           { text: "Document ID", datafield: 'doc_id', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging }

            //         ]

            });
            // select or unselect rows when the checkbox is clicked.


            //$("#jqxcheckbox").on('change', function (event) {
            //    alert('asdsad')
            //    if ($("#jqxgrid").jqxGrid('selectedrowindexes').length > 0) {
            //        $('.action').removeClass('disabled'); // Disables visually
            //        $('.action').prop('disabled', false); // Disables visually + functionally
            //    } else {
            //        $('.action').addClass('disabled'); // Disables visually
            //        $('.action').prop('disabled', true); // Disables visually + functionally
            //    }
            //});

            $("#btnDecline").click(function () {
                data = getSelection();
                if (data.length > 0) {
                    alertify.confirm(data.length + " Entries are selected,Are you sure?",
                        function (e) {
                            if (e) {
                                confirm_review(data, 'declined')

                            }
                        });
                } else {
                    alertify.alert('Select entries by checking the checkbox');

                }




            });
            $("#btnAccept").click(function () {
                data = getSelection();
                if (data.length > 0) {
                    alertify.confirm(data.length + " Entries are selected,Are you sure?",
                        function (e) {
                            if (e) {
                                confirm_review(data, 'accepted')


                            }
                        });

                } else {
                    alertify.alert('Select entries by checking the checkbox');
                }


            });
            $("#btnSuspend").click(function () {
                data = getSelection();
                if (data.length > 0) {
                    alertify.confirm(data.length + " Entries are selected,Are you sure?",
                      function (e) {
                          if (e) {
                              confirm_review(data, 'pending')
                          }
                      });
                } else {
                    alertify.alert('Select entries by checking the checkbox');
                }

            });

        });

        function confirm_review(data,status) {


            $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                url: '/GUI/BrowseSuggestion.aspx/process_submissions',
                data: "{'status':'" + status + "','json_table':" + JSON.stringify(data) + "}",
                dataType: "json",
                success: function (data) {
                    results = data.d.split(';')

                    alertify.success(results[1] + ' entries ' + results[0]);
                    $('#jqxgrid').jqxGrid('updatebounddata');
                }
            });


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

        // get all selected records.
        function getSelection() {

            var rows = $("#jqxgrid").jqxGrid('selectedrowindexes');
            var selectedRecords = new Array();
            for (var m = 0; m < rows.length; m++) {
                var row = $("#jqxgrid").jqxGrid('getrowdata', rows[m]);
                selectedRecords[selectedRecords.length] = row;
            }
            return selectedRecords

        }
