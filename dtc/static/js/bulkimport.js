     var X = XLSX;
    var i;
    editedCells = new Array();
    //incorrectCells = new Array();
    function fixdata(data) {
      
        var o = "", l = 0, w = 10240;
        for (; l < data.byteLength / w; ++l) o += String.fromCharCode.apply(null, new Uint8Array(data.slice(l * w, l * w + w)));
        o += String.fromCharCode.apply(null, new Uint8Array(data.slice(l * w)));
        return o;
    }

   
    function to_json(workbook) {
        var result = {};
        var roa = X.utils.sheet_to_row_object_array(workbook.Sheets[workbook.SheetNames[0]]);

        if (roa.length > 0) {
            result = roa;
        }     
        return keysToLowerCase(result);
    }

    // global filter search for jqx grid
    function setGlobalFilter(filtervalue) {
        var columns = $("#jqxgrid").jqxGrid('columns');
        var filtergroup, filter;
        // clear filters and exit if filter expression is empty
        $("#jqxgrid").jqxGrid('clearfilters');
        if (filtervalue == null || filtervalue == '') {
            return;
        }
        // the filtervalue must be aplied to all columns individually,
        // the column filters are combined using "OR" operator
        for (var i = 0; i < columns.records.length; i++) {
            if (!columns.records[i].hidden && columns.records[i].filterable) {
                filtergroup = new $.jqx.filter();
                filtergroup.operator = 'or';
                filter = filtergroup.createfilter('stringfilter', filtervalue, 'contains');
                filtergroup.addfilter(1, filter);
                $("#jqxgrid").jqxGrid('addfilter', columns.records[i].datafield, filtergroup);
            }
        }
        $("#jqxgrid").jqxGrid('applyfilters');
    }

    function keysToLowerCase(obj) {

        Object.keys(obj).forEach(function (key) {
            
           
            var lowerObj = _.transform(obj[key], function (result, val, key) {
                result[key.toLowerCase()] = val;
               
            })
            obj[key] = lowerObj;
        });
 
        return (obj);
    }
    var cellclass = function (row, datafield, value) {

      if (datafield == 'wild type or mutant' && $.inArray(value, wildType) == -1) {

        
          return "wrongCellvalue";

      }
      if (datafield == 'endpoint mode of action' && $.inArray(value, EMA) == -1) {

          //incorrectCells.push({ row: row, column: datafield, value: value })
          return "wrongCellvalue";

      }
      if (datafield == 'assay type' && $.inArray(value, assayType) == -1) {

          
          return "wrongCellvalue";

      }
      if (datafield == 'assay format' && $.inArray(value, assayFormat) == -1) {

         
          return "wrongCellvalue";

      }
      if (datafield == 'assay sub type' && $.inArray(value, assaySubtype) == -1) {

         
          return "wrongCellvalue";

      }
      if (datafield == 'inhibitor type' && $.inArray(value, inhibitorType) == -1) {

         
          return "wrongCellvalue";

      }
      if (datafield == 'detection technology' && $.inArray(value, detectionTech) == -1) {

         
          return "wrongCellvalue";

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
            // function to render links for certain columns
var linkrenderer = function (row, column, value) {
    var href = '';

    if (column == 'Compound ID') {
        href = "https://www.ebi.ac.uk/chembl/compound/inspect/" + value;
    } else if (column == 'Uniprot ID') {
        if (value.indexOf(',') != -1) {
            href = 'http://www.uniprot.org/uniprot/?query=accession:" + value';
        } else {
            var values = value.split(',');
            for (var i = 0; i < values.length; i++) {
                values[i] = "accession:" + values[i];
            }
            value = values.join(" OR ");
            href = "http://www.uniprot.org/uniprot/?query=" + value;
        }

    } else {
        href = "http://www.ncbi.nlm.nih.gov/pubmed/?term=" + value;
    }
    return '<div style="margin: 5px;"><a target= "_blank" href="' + href + '">' + value + '</a></div>';
}    
    // main function which initialized the jqx grid
    function process_wb(wb) {
        
        data = to_json(wb);
        
     



        var source =
    {

        localdata: data,
        datatype: "array",
        datafields: [
                           { name: 'compound id', type: 'string' },
                           { name: 'standard inchi key', type: 'string' },
                           { name: 'compound name', type: 'string' },
                           { name: 'uniprot id', type: 'string' },
                           { name: 'target pref name', type: 'string' },
                           { name: 'wild type or mutant', type: 'string' },
                           { name: 'mutation information', type: 'string' },
                           { name: 'pubmed id', type: 'int' },
                           { name: 'end point standard type', type: 'string' },
                           { name: 'end point standard relation', type: 'string' },
                           { name: 'end point standard value', type: 'float' },
                           { name: 'end point standard units', type: 'string' },
                           { name: 'endpoint mode of action', type: 'string' },
                           { name: 'assay format', type: 'string' },
                           { name: 'assay type', type: 'string' },
                           { name: 'assay sub type', type: 'string' },
                           { name: 'inhibitor type', type: 'string' },
                           { name: 'detection technology', type: 'string' },
                           { name: 'assay cell line', type: 'string' },
                           { name: 'compound concentration value', type: 'string' },
                           { name: 'compound concentration value units', type: 'string' },
                           { name: 'substrate type', type: 'string' },
                           { name: 'substrate type standard relation', type: 'string' },
                           { name: 'substrate type standard value', type: 'string' },
                           { name: 'substrate type standard units', type: 'string' },
                           { name: 'activity comments', type: 'string' },
                           { name: 'title', type: 'string' },
                           { name: 'year', type: 'int' },
                           { name: 'volume', type: 'string' },
                           { name: 'issue', type: 'string' },
                           { name: 'authors', type: 'string' },
                           { name: 'weblink', type: 'string' },
                           { name: 'dtc_assay_id', type: 'int' },
                           { name: 'assay description', type: 'string' },
                           { name: 'curator email', type: 'string' },
                           { name: 'user', type: 'string' },
                           //{ name: 'time', type: 'string' },
                           { name: 'annotation comments', type: 'string' },
                           { name: 'dtc_tid', type: 'int' },
                           { name: 'dtc_activity_id', type: 'int' },
                           { name: 'dtc_molregno', type: 'int' },
                           { name: 'journal', type: 'string' },
                           { name: 'dtc_record_id', type: 'int' },
                           { name: 'dtc_doc_id', type: 'int' }
        ],
    };

        var adapter = new $.jqx.dataAdapter(source);

        $('#clearfilteringbutton').click(function () { $("#jqxgrid").jqxGrid('clearfilters'); });
       
        //initialize jqx grid
        $("#jqxgrid").jqxGrid(
        {
          width: '100%',
          height: '600px',
          source: adapter,
          filterable: true,
          sortable: true,
          editable: true,
          selectionmode: 'multiplecellsadvanced',
          pageable: true,
          columnsresize: true,
          enabletooltips: true,
          theme: 'bootstrap',
          altrows: true,
          autoshowfiltericon: false,
          ready: function()
          {
              $("#jqxgrid").jqxGrid({ pagesize: 20 });
              $('#inputsearch').show();
              $('#grid-buttons').show();
          },
          pagesizeoptions: ['20', '50', '100'],
          columns: [

                    { text: 'Compound ID', datafield: 'compound id', pinned: true, width: 200, cellsrenderer: linkrenderer, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: 'Standard inchi key', datafield: 'standard inchi key', width: 250, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: 'Compound name', datafield: 'compound name', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: 'Uniprot ID', datafield: 'uniprot id', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging, cellsrenderer: linkrenderer },

                      { text: 'Target Pref. Name', datafield: 'target pref name', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      {
                        text: "Wild type or mutant", datafield: 'wild type or mutant', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
                        initeditor: function (row, cellvalue, editor) {
                            editor.jqxDropDownList({ source: wildType });
                        }
                      },
                      { text: "Mutation information", datafield: "mutation information", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: 'PubMed ID', datafield: 'pubmed id', width: 200, cellsrenderer: linkrenderer, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      //{ text: 'Reference ', datafield: 'Reference ', width: 200, cellsrenderer: linkrenderer, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: 'End Point Standard Type', datafield: 'end point standard type', cellclassname: cellclass, width: 200, cellvaluechanging: cellvaluechanging },
                      { text: 'End Point Standard Relation', datafield: 'end point standard relation', columntype: 'textbox', cellclassname: cellclass, width: 200, cellvaluechanging: cellvaluechanging },
                      { text: 'End Point Standard Value', datafield: 'end point standard value', width: 200, columntype: 'textbox', cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: 'End Point Standard Units', datafield: 'end point standard units', width: 200, columntype: 'textbox', cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      {
                          text: "Endpoint Mode of Action", datafield: 'endpoint mode of action', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
                          initeditor: function (row, cellvalue, editor) {
                              editor.jqxDropDownList({ source: EMA });
                          }
                      },
                      {
                          text: "Assay Format", datafield: 'assay format', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
                          initeditor: function (row, cellvalue, editor) {
                              editor.jqxDropDownList({ source: assayFormat });
                          }
                      },
                      {
                          text: "Assay Type", datafield: 'assay type', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
                          initeditor: function (row, cellvalue, editor) {
                              editor.jqxDropDownList({ source: assayType });
                          }
                      },
                      {
                          text: "Assay Sub Type", datafield: 'assay sub type', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
                          initeditor: function (row, cellvalue, editor) {
                              editor.jqxDropDownList({ source: assaySubtype });
                          }
                      },
                      {
                          text: "Inhibitor Type", datafield: 'inhibitor type', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
                          initeditor: function (row, cellvalue, editor) {
                              editor.jqxDropDownList({ source: inhibitorType });
                          }
                      },
                      {
                          text: "Detection Technology", datafield: 'detection technology', width: 200, columntype: 'dropdownlist', cellclassname: cellclass, cellvaluechanging: cellvaluechanging,
                          initeditor: function (row, cellvalue, editor) {
                              editor.jqxDropDownList({ source: detectionTech });
                          }
                      },
                      { text: "Assay cell line", datafield: 'assay cell line', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },

                      { text: 'Compound concentration value', datafield: 'compound concentration value', width: 200, columntype: 'textbox', cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: 'Compound concentration value units', datafield: 'compound concentration value units', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Substrate type", datafield: "substrate type", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Substrate Type Standard Relation", datafield: "substrate type standard relation", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Substrate Type Standard Value", datafield: "substrate type standard value", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Substrate Type Standard Units", datafield: "substrate type standard units", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Activity Comments", datafield: 'activity comments', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },

                      { text: "Title", datafield: "title", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Journal", datafield: "journal", width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Year", datafield: 'year', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Volume", datafield: 'volume', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Issue", datafield: 'issue', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Authors", datafield: 'authors', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Weblink", datafield: 'weblink', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Assay ID", datafield: 'dtc_assay_id', width: 200, cellclassname: cellclass, editable: false, cellvaluechanging: cellvaluechanging },
                      { text: "Assay Description", datafield: 'assay description', width: 200, columntype: 'textbox', cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: 'Curator Email', datafield: 'curator email', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: 'User', datafield: 'user', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      //{ text: 'Time', datafield: 'time', width: 200, cellclassname: cellclass, cellvaluechanging: cellvaluechanging },
                      { text: "Annotation Comments", datafield: 'annotation comments', width: 200, columntype: 'textbox', cellclassname: cellclass, cellvaluechanging: cellvaluechanging },

                      { text: 'Local Target ID', datafield: 'dtc_tid', width: 200, cellclassname: cellclass, editable: false, cellvaluechanging: cellvaluechanging },
                      { text: 'Activity ID', datafield: 'dtc_activity_id', width: 200, cellclassname: cellclass, editable: false, cellvaluechanging: cellvaluechanging },
                      { text: 'Molregno', datafield: 'dtc_molregno', width: 200, cellclassname: cellclass, editable: false, cellvaluechanging: cellvaluechanging },
                      { text: 'Record ID', datafield: 'dtc_record_id', width: 200, cellclassname: cellclass, editable: false, cellvaluechanging: cellvaluechanging },
                      { text: 'Document ID', datafield: 'dtc_doc_id', width: 200, cellclassname: cellclass, editable: false, cellvaluechanging: cellvaluechanging },
          


              ]


      });
    }

    if (user == '' && email == ''){

        $("#send_review").click(function (e) {

            e.preventDefault();
            $('#userinfomodel').modal('show');
        });

        $('#userinfo_form').validator().on('submit', function (e) {

           
            if (!e.isDefaultPrevented()) {
                e.preventDefault();
                rows = $('#jqxgrid').jqxGrid('getrows');
                $('#send_review').toggleClass('active');
                $('#userinfomodel').modal('hide');
                user = $('#curator_name').val();
                email = $('#curator_email').val();
                sendData(user, email, rows);
            }


        });

        

      }else{
        $("#send_review").click(function (e) {
            
            e.preventDefault();
            $(this).toggleClass('active');
            rows = $('#jqxgrid').jqxGrid('getrows');
            sendData(user,email,rows)
        });

      }

    function sendData(user, email, data) {

            
            $.ajax({
                type: "POST",
                url: "/upload_annotations/",
                data: JSON.stringify({'json_table':data ,'_user':user ,'_email':email }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                error: function (xhr, ajaxOptions, thrownError) {
                    //alert(xhr.status);
                    //alert(xhr.responseText);
                    //alert(thrownError);
                },
                success: function (msg) {

                    var count = $("#jqxgrid").jqxGrid('getdatainformation').rowscount;
                   
                    $('#userinfomodel').modal('hide');
                    $("#send_review").toggleClass('active');
                    alertify.success(count + ' bioactivities sent Successfully');
               
                }
            });
    }

    $('#inputsearch').keyup(function (e) {
        var searchText = $('#inputsearch').val();
        setGlobalFilter(searchText);
    });
    var drop = document.getElementById('drop');
    function handleDrop(e) {
        
        e.stopPropagation();
        e.preventDefault();
        var files = e.dataTransfer.files;
        var f = files[0];
       
       
        {
            var reader = new FileReader();
            var name = f.name;
            reader.onload = function (e) {
                function doit() {
                   
                    try {
                        
                        var data = e.target.result;
                        var wb;
                        var arr = fixdata(data);
                        wb = X.read(btoa(arr), { type: 'base64' });
                        result = process_wb(wb);
                       

                    } catch (e) { console.log(e); }
                }

                // if (e.target.result.byteLength > 3000000) alertify.alert("This file is " + e.target.result.byteLength + " bytes and is too large to process , currently files with less then 15000 rows can be processed ", function () { });
                // else { doit(); }
                doit()
            };
           
            reader.readAsArrayBuffer(f);
        }
        $('#drop').hide();


    }

    function handleDragover(e) {
        e.stopPropagation();
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';

    }

    

    if(drop.addEventListener) {
      drop.addEventListener('dragenter', handleDragover, false);
      drop.addEventListener('dragover', handleDragover, false);
      drop.addEventListener('drop', function(e){
          e.preventDefault();
          var ext = e.dataTransfer.files[0].name.split('.').pop().toLowerCase();
        if(user){  
          if ($.inArray(ext, ['xls', 'xlsx']) == -1) {
              alertify.alert("Opps!,Wrong file format, please select(xls or xlsx) again, ", function () { });
          } else {
              handleDrop(e);
          }
        }else{
           alertify.confirm("Login Required!", function () {location.href = "/accounts/login/" + request_path });
        }  
      }
      , false);
    }

    var xlf = document.getElementById('xlf');
    function handleFile(e) {
       
        
        var files = e.target.files;
        var f = files[0];
      
        var reader = new FileReader();
        var name = f.name;
        reader.onload = function (e) {
            
            function doit() {
               
                try {
                   
                    var data = e.target.result;
                    var wb;
                    var arr = fixdata(data);
                    wb = X.read(btoa(arr), { type: 'base64' });
                   
                    result = process_wb(wb);
                   

                } catch (e) { console.log(e); }
            }

            // if (e.target.result.byteLength > 3000000) alertify.alert("This file is " + e.target.result.byteLength + " bytes and is too large to process , currently files with less then 15000 rows can be processed ", function () { });
            // else { doit(); $('#drop').hide();}
            doit()
            $('#drop').hide()
        };

        reader.readAsArrayBuffer(f);
       
    }

    if(xlf.addEventListener) xlf.addEventListener('change', function(e){
      var ext = $(this).val().split('.').pop().toLowerCase();
      if(user){
        if ($.inArray(ext, ['xls', 'xlsx']) == -1) {
            alertify.alert("Opps!,Wrong file format, please select(xls or xlsx) again, ", function () { });
        } else {
            handleFile(e);
        }
      }else{
        alertify.confirm("Login Required!", function () {location.href = "/accounts/login/" + request_path });
      }  
    }, false);

    