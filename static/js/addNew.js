; hideNavigatorDownInput() ;

function Change(obj) {
	var el = document.getElementById(obj.id);
	var text = el.innerHTML ;
	document.getElementById('change').value = text ; 
	console.log(text) ; 
} ; 

function getChar(event) {
	if (event.which == null) { // IE
		if (event.keyCode < 32) return null; // спец. символ
		return String.fromCharCode(event.keyCode)
	}

	if (event.which != 0 && event.charCode != 0) { // все кроме IE
		if (event.which < 32) return null; // спец. символ
		return String.fromCharCode(event.which); // остальные
	}

	return null; // спец. символ
	}

function getPostData() {
	var post = {} ,
		inp = $('#form-info-left p input') ,
		sel = $('#form-info-left p select option'), 
		inpAd = $('#form-info-right p input') ,
		selAd = $('#form-info-right p select option') ,
		textareaRight = $('#form-info-right p textarea') ;
	for (var i = 0 ; i < sel.length ; i++) {
		if ($(sel[i]).is(':checked')) {
			post[$(sel[i]).parent().attr('name')] = $(sel[i]).val() ;
			break ;
		}
	}
	for (var i = 0; i < inp.length; i++) {
		post[$(inp[i]).attr('name')] = $(inp[i]).val() ;
	}
	for (var i = 0 ; i < inpAd.length ; i++) {
		post[$(inpAd[i]).attr('name')] = $(inpAd[i]).val() ; 
	}
	for (var i = 0 ; i < selAd.length ; i++) {
		if ($(selAd[i]).is(':checked')) {
			post[$(selAd[i]).parent().attr('name')] = $(selAd[i]).val() ;
			break ;
		}
	}
	post[$('#form-info-right p textarea').attr('name')] = $('#form-info-right p textarea').val()
	
	return post ;
}

function clickInput(inputField , arrayStatic, datalist) {
	if ($(inputField).val() === '') {
		$(datalist).empty() ;
		for (var i = 0 ; i < arrayStatic.length ; i++) {
			$('<option></option>').appendTo(datalist).attr({'value' : arrayStatic[i],	'id' : 'option' + i }) ;
		}
	}
}

function choosePress(inputField, datalist, arrayDynamic, letter) {
	$(datalist).empty() ;
	console.log(inputField) ;
	var kastiyl = false ;
	if ($(inputField).val() === ''){
		var c = String.fromCharCode(letter.which).toUpperCase() ;
		$(inputField).val(c) ;
		kastiyl = true ; 
		letter.preventDefault() ;
	} else {
		var c = String.fromCharCode(letter.which) ;
	}
	if (kastiyl) {
		var text = $(inputField).val() ; 
	} else {
		var text = $(inputField).val() + c;
	}
	var flag = 0 ; 
	for (var i = 0; i < arrayDynamic.length; i++) {
		if (arrayDynamic[i].indexOf(text) !== -1) {
			$('<option></option>').appendTo(datalist).attr({'value' : arrayDynamic[i]}) ;
			++flag ;
			if (flag >= 5) { break ; }
		}
	}
}

function macFieldVerificate(field, letter) {
	
	var text = $(field).val().toUpperCase() ,
	    c = String.fromCharCode(letter.which) ;
	
	if ( $(field).val().length < 17 ) {
		if ($(field).val().length in {2 : 2, 5 : 5, 8 : 8, 11 : 11, 14 : 14}) {
			if (letter.which !== 58) {
				$(field).val(text + ':' + c.toLocaleUpperCase()) ;
				letter.preventDefault() ;
			} 
		} else if (letter.which === 58){
			letter.preventDefault() ;
		} else {
			$(field).val(text + c.toUpperCase()) ;
			letter.preventDefault() ;
		}
	} else {
		letter.preventDefault() ;
	}
}



$(document).ready(function(){
	
	$('body').css({ 'background-color' : '#7c7c7c' })
	
	$('#navigator-add-new a').css( { "background" : "rgb(10, 10, 10)" , "color" : "green" } ) ; 
	
	$('#submit').click(function(){
		
		var post = getPostData() ; 
		
		$.post('/list/addNew/' ,
		    post ,
			function(data){ 
				$('li.success-addNew').hide(0) ;
				$('li.errors-addNew').hide(0) ;
				if (data === 'success') {
					//$('.success-addNew p.answer-addNew').text('TT' + post['idTT'] + ' was added successfully!!!') ; 
					//$('li.success-addNew').fadeToggle(1200) ;
					location.href = '/list/' ; 
				} else {
					$('.errors-addNew p.answer-addNew').text(data) ;
					$('li.errors-addNew').fadeToggle(1200) ;
				}
			}
		)

	})
	
	$('#submit-and-add').click(function(){
		var post = getPostData() ; 
		
		$.post('/list/addNew/' ,
		    post ,
			function(data){ 
				$('li.success-addNew').hide(0) ;
				$('li.errors-addNew').hide(0) ;
				if (data === 'success') {
					$('.success-addNew p.answer-addNew').text('TT' + post['idTT'] + ' was added successfully!!!') ; 
					$('li.success-addNew').fadeToggle(1200) ;
					$('#form-info').children().find('input , textarea').val('') ;
					var sel = $('#form-info').children().find('select option') ;
					for (var i = 0 ; i < sel.length ; i++) {
						if ($(sel[i]).val() === '1') {
							$(sel[i]).prop('selected', true) ; 
						}
					}
				} else {
					$('.errors-addNew p.answer-addNew').text(data) ;
					$('li.errors-addNew').fadeToggle(1200) ;
				}
			}
		)
	})
	
	$('#form-info-left [name = city]').click(function(){
		
		var cities = ["Киев", "Львов", "Харьков", "Днепропетровск", "Одесса"] ,
			list = '#city_list' ;
		
		clickInput(this , cities, list) ;
	})
	
	$('#form-info-left [name = city]').keypress(function(e){
		
		var list = '#city_list' ;
		
		choosePress(this, list, json.city, e) ; 
	})
	
	$('#form-info-left [name = wireless]').click(function(){
		
		var wireless = ["Ultra", "Navigator", "BuisnessL", "Intertelecomm", "MTS"] ,
			list = '#wireless_list' ;
		
		clickInput(this , wireless, list) ;
	})
	
	$('#form-info-left [name = wireless]').keypress(function(e){
		
		var list = '#wireless_list' ;
		
		choosePress(this, list, json.wireless, e) ; 
	})
	
	$('#form-info-left [name = wiredProvider]').click(function(){
		
		var wired = ["Lanet", "Триолан", "Мегалинк", "Wnet", "Datagroup"] ,
			list = '#wiredProvider_list' ;
		
		clickInput(this , wired, list) ;
	})
	
	$('#form-info-left [name = wiredProvider]').keypress(function(e){
		
		var list = '#wiredProvider_list' ;
		
		choosePress(this, list, json.wired, e) ; 
	})
	
	$('#form-info-right [name = ovpnMac]').keypress(function(e){
		
		macFieldVerificate(this, e) ;
	})
	
})