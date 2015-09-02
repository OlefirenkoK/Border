; hideNavigatorDownInput() ;

var city , wireless , wired, 
	sleepTime = 1200 ,
	timer = null ;

function getName(obj) {
	
	var str = $(obj).val() ; 
	
	if (str.lastIndexOf('\\')){
        var strLast = str.lastIndexOf('\\')+1;
    }
    else{
        var strLast = str.lastIndexOf('/')+1;
    }
	
	var filename = str.slice(strLast);
	
	var lable = $(obj).parent().find('.fileformlabel') ;
	lable.text(filename) ;
	
	return null ;
	
}

function verificateUploadFiles(crt, key, backup) {
	
	var result = {} ;  
	
	( crt.slice(-4) === '.crt' || crt === '') ? result['crt'] = true : result['crt'] = false ; 
	( key.slice(-4) === '.key' || key === '') ? result['key'] = true : result['key'] = false ; 
	( backup.slice(-7) === '.backup' || backup === '') ? result['backup'] = true : result['backup'] = false ;
	
	return result ; 
}

function clickInput(inputField , arrayStatic, datalist) {
	if ($(inputField).val() === '') {
		$(datalist).empty() ;
		for (var i = 0 ; i < arrayStatic.length ; i++) {
			$('<option></option>').appendTo(datalist).attr({'value' : arrayStatic[i],	'id' : 'option' + i }) ;
		}
	}
}

function getJson(arg) {
	
	if (typeof(arg) === 'string') {		
		var post = {'item' : arg } ;

		$.ajax({
			url : '/list/get_item/' ,
			data : post, 
			type: 'POST',
			success : function(data) {
				var responce = JSON.parse(data) ;
				if (!responce.error) {
					window[arg] = responce ;
				} else {
					console.log(responce.error) ;
				}
			}
		})
	}
}

function choosePress(inputField, datalist, arrayDynamic, letter) {
	
	$(datalist).empty() ;
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

function makeForm(array) {
	
	var dic = new Object() ;
	
	for (var i = 0 ; i < array.length ; i++) {
		if ($(array[i]).is(':visible')) {
			if (array[i].tagName === 'INPUT' || 'TEXTAREA') {
				dic[$(array[i]).attr('name')] = $(array[i]).val() ;
			} else if (array[i].tagName === 'SELECT') {
				dic[$(array[i]).attr('name')] = $(array[i]).parent().find('option:selected').val() ;
			}
		}
	}
	
	return dic ;
}

function hideForm(obj, el) {
	
	var element ;
	
	if ( typeof(obj) === 'object' ) {
		
		for (var key in obj) {
			
			element = $(el).find('[name = ' + key + ']') ;
			element.hide() ;
			p = element.parent().find('p') ;
			if ( element[0].tagName === 'SELECT' ) {
				p.text(element.find('option:selected').text()) ;
			} else {
				p.text(obj[key]) ;
			}
			p.fadeToggle(1200) ;
			button1 = element.parent().next().find('.change-cancel') ;
			button1.text('Change') ; 
			button2 = button1.next() ;
			button2.hide() ;
			
		}
		
		return true ;
		
	} else {
		return false ;
	}
} 
	
$(document).ready(function(){
	
	$('body').css({ 'background-color' : '#7c7c7c' }) ;
	
	//; displayError() ;
	
	$('#city-tt .text-tt input').click(function(){
		
		if (!city) {
			console.log('test') ;
			getJson('city') ; 
		}
		
		if ($(this).val() === '') {
			var cities = ["Киев", "Львов", "Харьков", "Днепропетровск", "Одесса"] ,
			list = '#city_list' ;
		
			clickInput(this , cities, list) ;
		}
	})
	
	$('#city-tt .text-tt input').keypress(function(e){
		
		var list = '#city_list' ;
		
		choosePress(this, list, city, e) ; 
	})
	
	
	$('#wiredProvider-tt .text-tt input').click(function(){
		
		if (!wired) {
			getJson('wired') ;
		}
		
		if ($(this).val() === '') {
			var wired = ["Lanet", "Триолан", "Мегалинк", "Wnet", "Datagroup"] ,
				list = '#wiredProvider_list' ;
		
			clickInput(this , wired, list) ;
		}
	})
	
	$('#wiredProvider-tt .text-tt input').keypress(function(e){
		
		var list = '#wiredProvider_list' ;
		
		choosePress(this, list, wired, e) ; 
	})
	
	$('#wireless-tt .text-tt input').click(function(){
		
		if (!wireless) {
			getJson('wireless') ;
		}
		
		if ($(this).val() === '') {
			var wireless = ["Ultra", "Navigator", "BuisnessL", "Intertelecomm", "MTS"] ,
				list = '#wireless_list' ;
		
			clickInput(this , wireless, list) ;
		}
	})
	
	$('#wireless-tt .text-tt input').keypress(function(e){
		
		var list = '#wireless_list' ;
		
		choosePress(this, list, wireless, e) ; 
	})
	
	$('#change-and-state').click(function(){
		
		$('#response-info-field').hide(0) ;
		
		var post = new FormData ,
			crt = $('#upload-crt') ,
			key = $('#upload-key') ,
			backup = $('#upload-backup') ,
			result = verificateUploadFiles(crt.val(), key.val(), backup.val()) , 
			left = $('#table-info-left .text-tt ').find('input,select,textarea') ,
			right = $('#table-info-right .text-tt ').find('input,select,textarea') ,
			main = makeForm(left) ,
			addition = makeForm(right) ,
			error ;
		
		for (var val in result) {
			if ( result[val] !== true ) {
				(error) ? error += 'Name ' + val + ' is not valid ! ' : error = 'Name ' + val + ' is not valid' ; 
			}
		}
		
		post.append('main' , JSON.stringify(main)) ; 
		post.append('addition' , JSON.stringify(addition)) ;
		console.log(main) ;
		console.log(addition) ;
		console.log(post) ;
		
		if (!error) {
			crt.val() ? post.append(crt.attr('name') , crt[0].files[0]) : post ;  
			key.val() ? post.append(key.attr('name') , key[0].files[0]) : post ;  
			backup.val() ? post.append(backup.attr('name') , backup[0].files[0]) : post ;  
			$.ajax({
				url : '/list/tt_info/' + TTID + '/' ,
				data : post , 
				processData: false,
				contentType: false,
				type: 'POST',
				success : function(data) {
					if (data === 'success') {
						crt.replaceWith(crt.clone()) ;
						key.replaceWith(key.clone()) ;
						backup.replaceWith(backup.clone()) ;
						$('.fileformlabel').text('') ;
						post = {} ;
						$('#response-header').text('Success!!!') ;
						$('#response-header').attr({'class' : 'success-ttInfo'}) ;
						$('#response-body').text('The data was applied successfully!') ;
						$('#response-body').attr({'class' : 'success-ttInfo'}) ;
						$('#response-info-field').fadeToggle(1200) ;
						hideForm(main, '.text-tt, select,input,textarea') ;
						hideForm(addition, '.text-tt, select,input,textarea') ;
					}
				}
			})
		} else {
			console.log('exeption') ;
			$('#response-header').text('Error!!!') ;
			$('#response-header').attr({'class' : 'error-ttInfo'}) ;
			$('#response-body').text(error) ;
			$('#response-body').attr({'class' : 'error-ttInfo'}) ;
			$('#response-info-field').fadeToggle(1200) ;
		}
	})
	
	$('.change-cancel').click(function(){
		
		var tr = $(this).parent().parent() ,
			infoItem = $(tr).find('.text-tt p').text() ;
		
		if ($(tr).find('.text-tt select')) {
			var selectVal = $(tr).find('.text-tt select').val() ;
		}
		
		if ($(this).text() === 'Change') {
			$(this).text('Cancel') ;
			$(this).parent().find('.apply-tt-info').fadeToggle(1200) ;
			$(tr).find('.text-tt p').hide() ;
			$(tr).find('.text-tt input,select,textarea').fadeToggle(1200) && $(tr).find('.text-tt input,textarea').val(infoItem) ;
		} else {
			$(tr).find('.text-tt input,textarea').val('') ;
			$(this).parent().find('.apply-tt-info').hide() ;
			$(tr).find('.text-tt input,textarea,select').hide() && $(tr).find('.text-tt p').fadeToggle(1200) ;
			if ( $(tr).find('.text-tt datalist').attr('id') ) {
				$(tr).find('.text-tt datalist').empty() ;
			}
			$(this).text('Change') ;
		}
	})
	
	$('.apply-tt-info').click(function(){
		
		$('#response-info-field').hide(0) ;
		
		var tr = $(this).parent().parent() ,
			post = {} ;
		
		if ($(tr).find('.text-tt select').attr('name') && $(tr).find('.text-tt select').css('display') !== 'none' || undefined) {
			var select = $(tr).find('.text-tt select option') ;
			console.log('test') ;
			for (var i = 0 ; i < select.length ; i++) {
				if ( $(select[i]).is(':checked') ) {
					post['column'] = $(tr).find('.text-tt select').attr('name') ;
					post['value'] = $(select[i]).val()
					break ;
				}
			}
		} else if ( $(tr).find('.text-tt input,textarea').attr('name') && $(tr).find('.text-tt input,textarea').css('display') !== 'none' || undefined)  {			
			var select = $(tr).find('.text-tt input,textarea') ;
			
			post['column'] = $(select).attr('name') ;
			post['value'] = $(select).val() ;
			console.log(post)
			
		} else {
			post['bug'] = 'some bug' ;
		}
		
		$.ajax({
			url : '/list/update_item/' + TTID + '/' ,
			data : post, 
			type: 'POST',
			success : function(data) {
				console.log(data)
				var responce = JSON.parse(data) ; 
				console.log(responce)
				
				if (responce.success || responce.success === '') {
					
					$(tr).find('.text tt p').text(responce.success) ; 
					$('#response-header').text('Success!!!') ;
					$('#response-header').attr({'class' : 'success-ttInfo'}) ;
					$('#response-body').text('The data was applied successfully!') ;
					$('#response-body').attr({'class' : 'success-ttInfo'}) ;
					$('#response-info-field').fadeToggle(1200) ;
					
					if ($(tr).find('.text-tt select').attr('name')) {
						$(tr).find('.text-tt p').text($(tr).find('.text-tt select option:selected').text()) ;
						$(tr).find('.text-tt p').fadeToggle(1200) ;
					} else {
						$(tr).find('.text-tt p').text(responce.success) && $(tr).find('.text-tt p').fadeToggle(1200);
					}
					$(tr).find('.text-tt input, select, textarea').hide() ;
					$(tr).find('.apply-tt-info').fadeToggle(1200) ;
					$(tr).find('.change-cancel').text('Change') ;
					
				} else if (responce.error) {
					
					errorInfo(responce.error)
					
					$(tr).find('.apply-tt-info').fadeToggle(1200) ;
					$(tr).find('.change-cancel').text('Change') ;
				} 
				else {
					
					errorInfo('error') ;
					
					$(tr).find('.apply-tt-info').fadeToggle(1200) ;
					$(tr).find('.change-cancel').text('Change') ;
				}
			}
		})
	})
	
	$('.download').click(function(){
		
		$('#response-info-field').hide(0) ;
		
		var el_id = $(this).attr('id') ,
			post = {};
		
		post[el_id] = true ; 
		
		$.ajax({
			url : '/list/downloadCKB/' + TTID + '/' ,
			data : post ,
			type: 'POST',
			//contentType : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ,
			success : function(data) {
				
				download(data, makeFileName(TTID, el_id), 'text/plain')		
			} ,
			error : function() {
				
				errorInfo('There is not file in DB!!!')
			}
		})
	})
	
	$('#migrate').click(function(){
		
		if ( timer === null ) {
			
			timer = true ;
			if ( $('#request-body').is(':visible') ) {
				$('#request-body').fadeToggle(sleepTime) ;
				$('#request-field').fadeToggle(sleepTime) ;
			} else {
				$('#request-body').fadeToggle(sleepTime) ;
				$('#request-field').fadeToggle(sleepTime) ;
			} 
			setTimeout(function(){ timer = null }, sleepTime)
		}
	})
	
	
	$('#request-body').click(function(){
		
		if ( timer === null ) {
			
			timer = true ;
			if ( $('#request-body').is(':visible') ) {
				$('#request-body').fadeToggle(sleepTime) ;
				$('#request-field').fadeToggle(sleepTime) ;
			}
			setTimeout(function(){ timer = null } , sleepTime)
		}
	})
	
	$('#first-apply').click(function(){
		if ( $(this).parent().is(':visible') ) {
			if ( $('#id_mikrotik').is(':checked') ) {
				$('#migrate-choose').show() ;
			} else {
				$('#apply-form').click() ;
			}
		}
	})
	
	$('#migrate-yes').click(function(){
		if ( $(this).parent().is(':visible') ) {
			console.log('test') ;
			$('#apply-form').click() ;
		} 
	})
	
	$('#migrate-no').click(function(){
		if ( $(this).parent().is(':visible') ) {
			$(this).parent().hide() ;
			$('#id_mikrotik').prop('checked' , false) ;
		}
	})
	
	$('#verification').click(function(){
		
		var post = {'tt_id' : TTID}
		
		$.ajax({
			url : '/list/verificate_tt/' ,
			data : post, 
			type: 'POST',
			success : function(data) {
				var responce = JSON.parse(data) ;
				if ( responce.success ) {
					for (var key in responce.success) {
						$('[name=' + key + ']').parent().find('p').text(responce.success[key]) ;
					}
				}
				else {
					console.log(data) ;
				}
			},
		})
	})
	
})

function displayError() {
	if ( ERROR_ANSWER ) {
		$('#response-info-field').css('display' , 'block') ;
	}
}

function makeFileName(tt, type) {
	
	if ( typeof(tt) === 'number' && typeof(type) === 'string' ) {
		if ( tt < 10.001 && tt > 0) {
			return '00' + tt + '.' + type ;
		} else if ( tt >= 10 && tt < 100 ) {
			return '0' + tt + '.' + type ;
		} else if ( tt >= 100 ) {
			return tt + '.' + type ;
		} else {
			return false ;
		}
	} else {
		return false ;
	}
}

function errorInfo(text) {
	
	$('#response-header').text('Error!!!') ;
	$('#response-header').attr({'class' : 'error-ttInfo'}) ;
	$('#response-body').text(text) ;
	$('#response-body').attr({'class' : 'error-ttInfo'}) ;
	$('#response-info-field').fadeToggle(1200) ;
}

function download(content, filename, contentType) {
	
    if (!contentType) {
		contentType = 'application/octet-stream'; 
	}
	var a = document.createElement('a');
	var blob = new Blob([content], {'type':contentType});
	a.href = window.URL.createObjectURL(blob);
	a.download = filename;
	a.click();
}