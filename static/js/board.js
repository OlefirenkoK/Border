var bodyClass = '.bord-city-body, .bord-addr-body, .bord-phone-body, .bord-wireless-body, .bord-wired-body, .bord-contract-body, .bord-support-body' ;

var SelectedElement = function() {
	this.idElement = null ; 
	this.idTT = null ;
}

var inObj = function(value , obj) {
	for (key in obj) {
		if (value === key) { //obj[key]
			return true ; 
		}  
	}
	return false ;
} ; 

var inArray = function(array , filterName) {
	for (var i = 0; i < array.length; i++) {
		if (array[i] === filterName) {
			return true ;
		}
	}
	
	return false ;
} ;

var filter = {
	'arrayHide' : {} ,
	
	'addElement' : function(elID, filterName) { 
		
		if ( !inObj(elID, this.arrayHide) ) {
			this.arrayHide[elID] = new Array(filterName) ; //this.arrayHide[elID].push(filterName) ;
			this.hideElements.push(elID) ; 
		} else if ( !inArray(this.arrayHide[elID], filterName) ) {
			this.arrayHide[elID].push(filterName) ; 
		}
	} , 
		
	'removeFilter' : function(filterName) {
		var removeEl = [] ;
		
		for (key in this.arrayHide) {
			
			for (var i = 0 ; i < this.arrayHide[key].length ; i++) {
				if (this.arrayHide[key][i] === filterName) {
					if (this.arrayHide[key].length === 1) {
						this.opentElements.push(key) ;
						delete this.arrayHide[key] ;
						break ; 	
					} else {
						this.arrayHide[key].splice(i, 1) ; //? addE
					}
				}
			}
		}
	} ,	
	
	'opentElements' : [] ,
	
	'hideElements' : [] ,
	
	'setArrToDef' : function() {
		this.hideElements = [] ; 
		this.opentElements = [] ;
	} ,
	
	'executeArray' : function() {
		console.log(this.arrayHide) ;
		var speedOpen, speedHide ; 
		if ( this.hideElements.length > this.opentElements.length ) {
			speedHide = 1200 ; 
			speedOpen = 200 ; 
		} else {
			speedOpen = 1200 ; 
			speedHide = 200 ; 
		}
		
		//console.log(this.opentElements) ;
		//console.log(this.hideElements) ;
		
		for (var i = 0 ; i < this.hideElements.length; i++) {
			$('.' + this.hideElements[i]).fadeToggle(speedHide) ;
		}
		
		for (var i = 0 ; i < this.opentElements.length; i++) {
			$('.' + this.opentElements[i]).fadeToggle(speedOpen) ;
		}
		
	} ,
	
} ; 

SelectedElement.prototype.setElement = function(el) {
	if (typeof(el) === typeof(String())) {
		this.idElement = el ;
		var id = (this.idElement.match(/\d+/g)) ;
		if ((id !== 0) && (id.length === 1)) {
			this.idTT = id[0]; 
		} else {
			this.idTT = null ;
		}
		$(this.idElement).addClass('body-tt-click') ;
	} else {
		console.log('board.js selectedElement.setElement error: id isnt string')
	}
}

SelectedElement.prototype.removeElement = function(){
	if (this.idElement) { 
		$(this.idElement).removeClass('body-tt-click') ;
		this.idElement = null; 
		this.idTT = null ; 
	} else { 
		console.log('Element has already Null') ;
	}
}

SelectedElement.prototype.getColumn = function() { //косяк костыль велосипед 
	
	column  = ['city', 'addr', 'phone', 'wireless', 'wired', 'contract', 'support']
	var pattern, elClass ;
	
	if (this.idElement !== null) {
		var elClass = $(this.idElement).attr('class') ; 
		pattern = /bord\-(city|addr|phone|wireless|wired|contract|support)\-body/i  ;
		col = pattern.exec(elClass) ; 
		for (var i = 0 ; i < column.length ; i++) { 
			if (col[1] === column[i]) {
				return col[1]
			}
		}
	}
}

var selectEl = new SelectedElement() ;

$(document).ready(function(){
	$('#navigator-boarder a').css( { "background" : "rgb(10, 10, 10)" , "color" : "green" } ) ;
	$('#navigator-down ul li').hide(0) ;    //css('visibility' , 'hidden') ;
	$('#navigator-down ul li').show(1200) ;   //fadeToggle(3000) ;
	
	$(bodyClass).click(function(){
		var idElement = '#' + this.id ;
		selectEl.removeElement() ;
		selectEl.setElement(idElement) ;
		console.log(selectEl.idTT) ; 
		var textElement = $(idElement).text() ;
		$('#ndi-change').val(textElement) ; 
		console.log(selectEl.getColumn()) ;
	})
	
	$('#ndb-change').click(function() {
		
		var col = selectEl.getColumn() ;
		var value = $('#ndi-change').val() ;
		
		if ( (selectEl.idTT) && (col) ) {
		
			$.post('/list/update_tt/' ,
			   {'idTT' : selectEl.idTT ,
				'column' : col ,
				'value' :  value,
				} ,
				function(data){ 
					if (data === 'success') {
						$(selectEl.idElement).html(value) ;
					}
				}
			)
		}
		})
	
	
	$('#ndb-goto').click(function(){
		var elID = parseInt($('#ndi-goto').val()) + 'tt';
		var scroll = $('#' + elID).offset().top ;
		scroll ? $(document).scrollTop(scroll - 95) : console.log('bug') ;
	})
	
	
	$('.bord-id-filter').on('click', 'input[type = checkbox]', function(e){
		var open = $('input[name = open]'), 
			close = $('input[name = close]'),
			inProgress = $('input[name = inProgress]'), 
			all = $('input[name = all]') ;

		if ($(this).attr('name') === 'all') {
			inProgress.prop('checked' , false) ;
			close.prop('checked' , false) ;
			open.prop('checked' , false) ;
			all.prop('checked' , true) ;
		} else if ( ($(this).attr('name') === 'open' || 'close' || 'inProgress') ) {
			all.prop('checked' , false) ;
			if ((close.is(':checked')) && (open.is(':checked')) && (inProgress.is(':checked'))){
				close.prop('checked' , false) ;
				open.prop('checked' , false) ;
				inProgress.prop('checked' , false) ;
				all.prop('checked' , true) ;
			}
		}
		if ( (!all.is(':checked') && !open.is(':checked') && !close.is(':checked') && !inProgress.is(':checked'))) {
			all.prop('checked' , true) ;	
		}
	})

	$('.bord-city-filter input').click(function(){
		
		if ($('.bord-city-filter input').val() === '') {
			var array = ["Киев", "Львов", "Харьков", "Днепропетровск", "Одесса"] ;
			$('#data_list_city').empty() ;
			for (var i = 0 ; i < array.length ; i++) {
				//$('#data_list_city').createElement('option').attr({'value' : array[i],	'id' : 'option' + i }) ;
				$('<option></option>').appendTo('#data_list_city').attr({'value' : array[i],	'id' : 'option' + i }) ;
			}
		}
	})
	
	$('.bord-city-filter input').keypress(function(e){
		$('#data_list_city').empty() ;
		var kastiyl = false ;
		if ($('.bord-city-filter input').val() === ''){
			var c = String.fromCharCode(e.which).toUpperCase() ;
			$('.bord-city-filter input').val(c) ;
			kastiyl = true ; 
			e.preventDefault() ;
		} else {
			var c = String.fromCharCode(e.which) ;
		}
		if (kastiyl) {
			var text = $('.bord-city-filter input').val() ; 
		} else {
			var text = $('.bord-city-filter input').val() + c;
		}
		var flag = 0 ; 
		for (var i = 0; i < json.city.length; i++) {
			if (json.city[i].indexOf(text) !== -1) {
				$('<option></option>').appendTo('#data_list_city').attr({'value' : json.city[i]}) ;
				++flag ;
				if (flag >= 5) { break ; }
				
			}
		}
	})
	
	$('.bord-city-filter button').click(function(){
		var text = $('.bord-city-filter input').val(),
			arrayHTMLp = $('.bord-city-body') ;
		filter.setArrToDef() ; 
		filter.removeFilter('filter-city') ;
		if ( text !== '' ) {
			for (var i = 0; i < arrayHTMLp.length; i++) {
				if ( $(arrayHTMLp[i]).children().text() !== text ) {
					filter.addElement($(arrayHTMLp[i]).parent().prev().attr('id'), 'filter-city') ; 
				}
			}	
		}
		
		filter.executeArray() ; 
	})
	
	$('.bord-id-filter button').click(function(){
		var open = 	$('input[name = open]').is(':checked') , 
			close = $('input[name = close]').is(':checked') ,
			inProgress = $('input[name = inProgress]').is(':checked') ,
			all = $('input[name = all]').is(':checked') ,
			objStatus = { 'status_1' : open,
						  'status_2' : close, 
						  'status_3' : inProgress } ;
			
		filter.setArrToDef() ; 
		
		if ( all ) {
			filter.removeFilter('filter-status') ;
			filter.executeArray() ;
		} else {
			filter.removeFilter('filter-status') ;
			for ( key in objStatus ) {
				if ( !objStatus[key] ) {
					console.log(key) ;
					var arrayHTMLli = $('.bord-id-body.' + key) ; 
					
					for (var i = 0 ; i < arrayHTMLli.length ; i++) {
						filter.addElement( $(arrayHTMLli[i]).attr('id') , 'filter-status') ;
					}
				}
			}
		filter.executeArray() ;
		}
		
	})
	
	$('.bord-wired-filter input').click(function(){
		
		if ($('.bord-wired-filter input').val() === '') {
			var array = ["Lanet", "Триолан", "Мегалинк", "Wnet", "Datagroup"] ;
			$('#data_list_wired').empty() ;
			for (var i = 0 ; i < array.length ; i++) {
				$('<option></option>').appendTo('#data_list_wired').attr({'value' : array[i],	'id' : 'option' + i }) ;
			}
		}
	})
	   
	$('.bord-wired-filter input').keypress(function(e){
		$('#data_list_wired').empty() ;
		var kastiyl = false ;
		if ($('.bord-wired-filter input').val() === ''){
			var c = String.fromCharCode(e.which).toUpperCase() ;
			$('.bord-wired-filter input').val(c) ;
			kastiyl = true ; 
			e.preventDefault() ;
		} else {
			var c = String.fromCharCode(e.which) ;
		}
		if (kastiyl) {
			var text = $('.bord-wired-filter input').val() ; 
		} else {
			var text = $('.bord-wired-filter input').val() + c;
		}
		var flag = 0 ; 
		for (var i = 0; i < json.wired.length; i++) {
			if (json.wired[i].indexOf(text) !== -1) {
				$('<option></option>').appendTo('#data_list_wired').attr({'value' : json.wired[i]}) ;
				++flag ;
				if (flag >= 5) { break ; }
			}
		}
	})
	
	$('.bord-wired-filter button').click(function(){
		var text = $('.bord-wired-filter input').val(),
			arrayHTMLp = $('.bord-wired-body') ;
		filter.setArrToDef() ; 
		filter.removeFilter('filter-wired') ;
		if ( text !== '' ) {
			for (var i = 0; i < arrayHTMLp.length; i++) {
				if ( $(arrayHTMLp[i]).children().text() !== text ) {
					filter.addElement($(arrayHTMLp[i]).parent().prev().attr('id'), 'filter-wired') ; 
				}
			}	
		}
		
		filter.executeArray() ; 
	})
	
	
})
