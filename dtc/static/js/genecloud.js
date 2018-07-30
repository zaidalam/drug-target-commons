var draw = function(words, divId, w, h, tip, url_query) {
    var fill = d3.scale.category20();
    $( divId ).empty();
    var svg = d3.select(divId).append("svg")
        .attr("style", "font-family: Arial;")
        .attr("width", w)
        .attr("height", h);

    svg.call(tip);

    svg.append("g")
        .attr("transform", "translate("+w/2+","+h/2+")")
      .selectAll("text")
        .data(words)
      .enter().append("text")
        .style("font-size", function (d) {
           
            return d.size + "px";
        })
        .style("font-weight", "bold")
	    .style("cursor" ,"pointer")
        .style("fill", function(d, i) { return fill(i); })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { return d.text; })
        .on("click", function(d) {
			window.open(url_query.replace("KEY", d.id),'_blank');
		  })
        .on("mouseover", function(d){ tip.show(d.value) })
        .on("mouseout", function(d) { tip.hide() });
  }

var preparecloud = function(genes, text_field, size_field,id) {
        var domain = [];
        for (g in genes) {
            domain.push(genes[g][size_field])
        }
    //var scale = d3.scale.log().domain(d3.extent(domain)).range([15, 50]);
        var max = Math.max.apply(null, Object.keys(genes).map(function (e) { return genes[e]['bioactivities']; }));
        var min = Math.min.apply(null, Object.keys(genes).map(function (e) { return genes[e]['bioactivities']; }));
  

        var scale = d3.scale.linear().domain([min,max]).range([15,60]);
        var gene_list = [];
        for (g in genes) {
                var muts = genes[g][size_field]
                gene_list.push({
                 text: genes[g][text_field],
                 size: scale(genes[g][size_field]),
                 value: genes[g][size_field],
				 id: genes[g][id]
                });
        }
        return gene_list;
}

var drivercloud = function(divId, gene_list, tipMessageFunc, url_query){

    if ($('#fullscreen-dropback.fullreport').length > 0 && $('.fulltarget #drivers').length == 0 ) {
        return;
    }

    var fontSize = d3.scale.log().range([10, 100]);
   
    var w = $(divId).parent().width();
    var h = 400;

    // tip instance
    tip = d3.tip()
      .attr('class', 'd3-tip')
      .offset([-10, 0])
      .html(function(d) {
        return tipMessageFunc(d);
      });

    // draw function wrapper
    var mydraw = function(words) { return draw(words, divId, w, h, tip, url_query); };

    d3.layout.cloud()
        .size([w, h])
        .words(gene_list)
        .padding(2)
        .rotate(function() { return ~~(0) * 90; })
        .font("Arial")
        .fontSize(function (d) {return d.size;})
        .on("end", mydraw)
        .start();

	responsiveSVGs[divId] = {func: drivercloud, args: [divId, gene_list, tipMessageFunc, url_query]}
}
