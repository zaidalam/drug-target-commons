
        $(document).ready(function () {

            toastr.info('To Add/Update Bioacitvities,Please log in', 'Update Bioactivities', {timeOut: 5000,closeButton: true,positionClass:'toast-top-right'})
            //Getting the source data with ajax GET request
            SearchText();
            editable = true;
            var hidden_columns = [];
            var editedRows = new Array();
            $('#send').addClass('disabled'); // Disables visually
            $('#send').prop('disabled', true); // Disables visually + functionally

            if (user == '' && email == ''){
              editable = false;
              // $("#send").click(function (e) {
              //     e.preventDefault();
              //     $('#userinfomodel').modal('show');
              // });

              // $('#userinfo_form').validator().on('submit', function (e) {

              //   if (!e.isDefaultPrevented()) {
              //       e.preventDefault();
              //       $('#send').toggleClass('active');
              //       $('#userinfomodel').modal('hide');
              //       // var user = $('#curator_name').val();
              //       // var email = $('#curator_email').val();
              //       send_review(user, email);
              //   }  
              // });

            }else{
              $('#send').click(function (e) {
                  e.preventDefault();
                  $('#send').toggleClass('active');
                  send_review(user, email)
                  return false;
              })


            }


           
     
  
          function send_review(user, email) {

              var result = new Array();
              $.each(editedRows, function (index, val) {
                  result.push(val.data);
              });


              $.ajax({
                  type: "POST",
                  url: "/send_review/",
                  data: JSON.stringify({'json_table':result ,'_user':user ,'_email':email }),
                  contentType: "application/json; charset=utf-8",
                  dataType: "json",
                  error: function (xhr, ajaxOptions, thrownError) {

                      console.log(xhr.responseText);

                  },
                  success: function (msg) {
                      var count = result.length;
                      $("#send").toggleClass('active');
                      alertify.success(count + 'bioactivities sent Successfully');
                  }
              });


          }

          $('#txtSearchClient').val(get('value'));
          // validate function
          var validateFunc = function (datafield, value) {
              switch (datafield) {
                  case "End Point Standard Value":
                      if (value.length > 6) {
                          return { message: "Entered value should be more than 6 ", result: false };
                      }
                      return true;

              }
              return true;
          }

          var cellclass = function (row, datafield, value) {



              for (var i = 0; i < editedCells.length; i++) {
                  if (editedCells[i].row == row && editedCells[i].column == datafield) {
                      return "editedCell";
                  }
              }


          }
          var cellsrenderer = function (row, column, value, defaultHtml){

                var annotation = $("#jqxgrid").jqxGrid("getcellvalue", row, "annotations_flag");
                var element = $(defaultHtml);
                if (annotation == 'yes'){
                  // $("#jqxgrid").jqxGrid('setcellvalue',row,'annotations_flag','Yes');
                   var element = $(defaultHtml);
                    element.css({ 'background-color': '#deeff5', 'color':'#000','width': '100%', 'height': '100%', 'margin': '0px','padding':'5px' });
                    if (column == 'annotations_flag'){
                      element[0].innerHTML = '<div class="text-center"><span class="glyphicon glyphicon-ok"></span></div>'
                    }

                    return element[0].outerHTML;
                }else{
                  if (column == 'annotations_flag'){
                      element[0].innerHTML = '<div class="text-center"><span class="glyphicon glyphicon-remove"></span></div>'
                      return element[0].outerHTML;
                    }

                }
                return defaultHtml;
            }
          var cellvaluechanging = function (row, datafield, columntype, oldvalue, newvalue) {
              if (oldvalue != newvalue) {
                  editedCells.push({ row: row, column: datafield });
              }
          };
          var beginedit = function (row, datafield, columntype,oldvalue) {
                
                var value = $("#jqxgrid").jqxGrid("getcellvalue", row, "annotations_flag");
                if (value == true){
                  return false;
                }
          };
          editedCells = new Array();
          var source =
          {
              updaterow: function (rowid, rowdata, commit) {
                  // that function is called after each edit.

                  var html = '';
                  var rowindex = $("#jqxgrid").jqxGrid('getrowboundindexbyid', rowid);
                  index = editedRows.map(function (e) { return e.index; }).indexOf(rowid)
                  if (index != -1) {
                      editedRows[index] = { index: rowindex, data: rowdata }
                  } else {
                      editedRows.push({ index: rowindex, data: rowdata });
                  }
                  if (editedRows.length > 0) {
                      $('#send').removeClass('disabled'); // Disables visually
                      $('#send').prop('disabled', false); // Disables visually + functionally
                  }
                  commit(true);
              },
              async: false,
              url: '/getbioactivities/',
              //url: '/GUI/BrowseSuggestion.aspx/load_submissions',
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
                          data: JSON.stringify({'searchText': get('id'),'category': get('category')}),
                          dataType: "json",
                          success: function (data) {
                              
                            
                              callback({ records: data });
                          }

                      });
                  },

              }
          );
          $("#jqxgrid").jqxGrid(
                                {
                                    width: '100%',
                                    height: '600px',
                                    source: dataAdapter,
                                    filterable: true,
                                    sortable: true,
                                    editable: editable,
                                    theme: 'bootstrap',
                                    selectionmode: 'multiplecellsadvanced',
                                    pageable: true,
                                    columnsresize: true,
                                    enabletooltips: true,
                                    altrows: true,
                                    autoshowfiltericon: false,
                                    ready: function () {
                                        $("#jqxgrid").jqxGrid({ pagesize: 25 });
                                    },

                                    pagesizeoptions: ['25', '50', '100'],


                                    columns: [
                                       { text: "Annotated", datafield: 'annotations_flag',pinned:true,width: 80,filtertype: 'list', filteritems: ['yes', 'no'], editable: false,cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer,
                                          rendered: function (element) {
                                              $(element).jqxTooltip({ position: 'mouse', content: "Annotated Bioactivities" });
                                          }

                                        },
 
                                       { text: 'Compound ID', datafield: 'compound_id',pinned:true, width: 120, editable: false,cellsrenderer: linkrenderer, cellclassname: cellclass, cellvaluechanging: cellvaluechanging, cellbeginedit: beginedit,
                                       rendered: function (element) {
                                              $(element).jqxTooltip({ position: 'mouse', content: "Link to Chembl source" });
                                          }

                                        },
                                       { text: 'Standard inchi key', datafield: 'standard_inchi_key', editable: false,width: 250, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer,
                                        rendered: function (element) {
                                              $(element).jqxTooltip({ position: 'mouse', content: "Standard Inchi Key" });
                                          }
                                        },

                                       { text: 'Compound name', datafield: 'compound_name', width: 200, editable: false,cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: 'Max phase', datafield: 'max_phase', width: 90, editable: false,cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: 'Uniprot ID', datafield: 'target_id', pinned:true,width: 200, editable: false,cellsrenderer: linkrenderer, cellclassname: cellclass, cellvaluechanging: cellvaluechanging,cellbeginedit: beginedit },
                                       { text: 'Target Pref Name', datafield: 'target_pref_name', width: 200, editable: false,cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: 'Gene Name', datafield: 'gene_names', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: 'Target class', datafield: 'target_class', width: 150, editable: false,cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                        {
                                            text: "Wild type or mutant", datafield: 'wildtype_or_mutant', width: 150, columntype: 'dropdownlist', cellclassname: cellclass,cellbeginedit: beginedit ,cellsrenderer:cellsrenderer,cellvaluechanging: cellvaluechanging,
                                            initeditor: function (row, cellvalue, editor) {
                                                editor.jqxDropDownList({ source: wildType });
                                            }
                                        },
                                  
                                        { text: "Mutation information", datafield: "mutation_info", width: 150, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},

                                       { text: 'PubMed ID', datafield: 'pubmed_id', width: 100, cellsrenderer: linkrenderer, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit},
                                      // { text: 'PubMed ID', datafield: 'pubmed_id', width: 200 },
                                       { text: 'End Point Standard Type', datafield: 'ep_standardtype', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: 'End Point Standard Relation', datafield: 'ep_standardrelation', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: 'End Point Standard Value', datafield: 'ep_standardvalue', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: 'End Point Standard Units', datafield: 'ep_standardunits', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       {
                                           text: "Endpoint Mode of Action", datafield: 'ep_action_mode', width: 200, columntype: 'dropdownlist', cellclassname: cellclass,cellbeginedit: beginedit,cellsrenderer:cellsrenderer, cellvaluechanging: cellvaluechanging,
                                           initeditor: function (row, cellvalue, editor) {
                                               editor.jqxDropDownList({ source: EMA });
                                           }
                                       },

                                       {
                                           text: "Assay Format", datafield: 'assay_format', width: 100, columntype: 'dropdownlist', cellclassname: cellclass,cellbeginedit: beginedit,cellsrenderer:cellsrenderer, cellvaluechanging: cellvaluechanging,
                                           initeditor: function (row, cellvalue, editor) {
                                               editor.jqxDropDownList({ source: assayFormat });
                                           }
                                       },
                                       {
                                           text: "Assay Type", datafield: 'assaytype', width: 100, columntype: 'dropdownlist', cellclassname: cellclass,cellbeginedit: beginedit,cellsrenderer:cellsrenderer, cellvaluechanging: cellvaluechanging,
                                           initeditor: function (row, cellvalue, editor) {
                                               editor.jqxDropDownList({ source: assayType });
                                           }
                                       },
                                       {
                                           text: "Assay Sub Type", datafield: 'assay_subtype', width: 150, columntype: 'dropdownlist', cellclassname: cellclass,cellbeginedit: beginedit,cellsrenderer:cellsrenderer, cellvaluechanging: cellvaluechanging,
                                           initeditor: function (row, cellvalue, editor) {
                                               editor.jqxDropDownList({ source: assaySubtype });
                                           }
                                       },
                                       {
                                           text: "Inhibitor Type", datafield: 'inhibitor_type', width: 120, columntype: 'dropdownlist', cellclassname: cellclass,cellbeginedit: beginedit,cellsrenderer:cellsrenderer,cellvaluechanging: cellvaluechanging,
                                           initeditor: function (row, cellvalue, editor) {
                                               editor.jqxDropDownList({ source: inhibitorType });
                                           }
                                       },
                                       {
                                           text: "Detection Technology", datafield: 'detection_tech', width: 160, columntype: 'dropdownlist', cellclassname: cellclass,cellbeginedit: beginedit,cellsrenderer:cellsrenderer,cellvaluechanging: cellvaluechanging,
                                           initeditor: function (row, cellvalue, editor) {
                                               editor.jqxDropDownList({ source: detectionTech });
                                           }
                                       },
                                       { text: 'Compound concentration value', datafield: 'compound_concentration_value', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: 'Compound concentration value units', datafield: 'compound_concentration_value_unit', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Substrate type", datafield: "substrate_type", width: 150, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Substrate Type Standard Relation", datafield: "substrate_relation", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Substrate Type Standard Value", datafield: "substrate_value", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Substrate Type Standard Units", datafield: "substrate_units", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Assay cell Type", datafield: 'assay_cell_line', width: 150, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Assay Description", datafield: 'assay_description', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging,cellbeginedit: beginedit ,cellsrenderer:cellsrenderer},
                                       { text: "Activity Comments", datafield: 'activity_comment', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Title", datafield: "title", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Journal", datafield: "journal", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Year", datafield: 'year', width: 100, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Volume", datafield: 'volume', width: 100, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Issue", datafield: 'issue', width: 100 ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Authors", datafield: 'authors', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Annotation Comments", datafield: 'annotation_comments', width: 300 ,cellbeginedit: beginedit,cellsrenderer:cellsrenderer},
                                       { text: "Assay ID", datafield: 'assay_id', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,hidden: true,cellsrenderer:cellsrenderer},
                                       { text: "Local Target ID", datafield: 'tid', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,hidden: true,cellsrenderer:cellsrenderer},
                                       { text: "Activity ID", datafield: 'activity_id', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,hidden: true,cellsrenderer:cellsrenderer},
                                       { text: "Molregno", datafield: 'molregno', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,hidden: true,cellsrenderer:cellsrenderer},
                                       { text: "Record ID", datafield: 'record_id', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,hidden: true,cellsrenderer:cellsrenderer},
                                       { text: "Document ID", datafield: 'doc_id', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging ,cellbeginedit: beginedit,hidden: true,cellsrenderer:cellsrenderer}
                                       
                                    ]
                                });


          
          var cols = $("#jqxgrid").jqxGrid("columns");
          
          removed_columns = ['assay_id','tid','activity_id','molregno','record_id','doc_id','annotations_flag']
  
          var listColhtml = ''
          for (var i = 0; i < cols.length; i++) {
              if($.inArray(cols[i].datafield, removed_columns) === -1){
                listColhtml = listColhtml + '<li><a href="#" class="small" data-value="'+cols[i].datafield+'" tabIndex="-1"><input checked="checked" type="checkbox"/>&nbsp;'+cols[i].text+'</a></li>'
              }
          }
          $('#hideShow').append(listColhtml);

          $( '#hideShow a' ).on( 'click', function( event ) {

             var $target = $( event.currentTarget ),
                 val = $target.attr( 'data-value' ),
                 $inp = $target.find( 'input' ),
                 idx;

             if ( $inp.is( ":checked" )) {
                hidden_columns.push( val );
                $("#jqxgrid").jqxGrid('hidecolumn', val);
                setTimeout( function() { $inp.prop( 'checked', false ) }, 0);
             } else {
                hidden_columns.splice( idx, 1 );
                $("#jqxgrid").jqxGrid('showcolumn', val);
                setTimeout( function() { $inp.prop( 'checked', true ) }, 0);
             }

             $( event.target ).blur();
                
          
             return false;
          });

          var click = new Date();
          var lastClick = new Date();
          var lastRow = -1;
          $("#jqxgrid").bind('rowclick', function (event) {
            click = new Date();
            if (click - lastClick < 300) {
              if (event.args.row.bounddata.annotations_flag == 'yes') {
                alertify.error('Cannot edit annotated data');
              }
            }
            lastClick = new Date();
          });  
          $('#clearfilteringbutton').click(function () { $("#jqxgrid").jqxGrid('clearfilters'); });

          $("#excelExport").click(function () {
              
              var count = $("#jqxgrid").jqxGrid('getdatainformation').rowscount;
              if (count > 50000) {

                  alertify.error('Too many records,apply filtering to reduce records');

              } else {
                
                  export_data(hidden_columns);
              }

          });




      });

      function export_data(hidden_columns) {
                 
          xhttp = new XMLHttpRequest();
          xhttp.onreadystatechange = function() {
              var a, today;
              if (xhttp.readyState === 4 && xhttp.status === 200) {
                  a = document.createElement('a');
                  a.href = window.URL.createObjectURL(xhttp.response);
                  today = new Date();
                  a.download = "bioactivities_" + today.toDateString().split(" ").join("_") + ".xlsx";
                  a.style.display = 'none';
                  document.body.appendChild(a);
                  return a.click();
              }
          };
          xhttp.open("POST", "/export_to_excell/", true);
          xhttp.setRequestHeader("Content-Type", "application/json");
          xhttp.responseType = 'blob';
          xhttp.send(JSON.stringify({'json_table':$('#jqxgrid').jqxGrid('getrows'),'hidden_columns':hidden_columns}));

      }

      function get(name) {
          if (name = (new RegExp('[?&]' + encodeURIComponent(name) + '=([^&]*)')).exec(location.search))
              return decodeURIComponent(name[1]);
      }

      //alert(get('value'))
      function txtSearchClient_onclick() {

      }
    $("#jqxgrid").on('cellselect',function (event) 
    {
      // event arguments.
      var args = event.args;
      // get the column's text.
      var column = $("#jqxgrid").jqxGrid('getcolumn', event.args.datafield).text;
      // column data field.
      var dataField = event.args.datafield;
      // row's bound index.
      var rowBoundIndex = event.args.rowindex;
      // cell value
      var value = args.value;
    });
      // function to render links for certain columns
    var linkrenderer = function (row, column, value){
          var href = '';
          var annotated = $("#jqxgrid").jqxGrid("getcellvalue", row, "annotations_flag");
          if (column == 'compound_id') {
              href = "https://www.ebi.ac.uk/chembl/compound/inspect/" + value;
          } else if (column == 'target_id') {
              href = "http://www.uniprot.org/uniprot/?query=accession:" + value.replace(',', ' or accession:');

          } else {
              href = "http://www.ncbi.nlm.nih.gov/pubmed/?term=" + value;
          }
          if (annotated == 'yes'){
            return '<div style="padding: 5px;background-color: #deeff5; color:#000;height:100%"><a target= "_blank" href="' + href + '">' + value + '</a></div>';
          }else{
            return '<div style="padding: 5px;"><a target= "_blank" href="' + href + '">' + value + '</a></div>';
          }
          
      }
