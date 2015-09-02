// ajax request for any browsers 
function CreateRequest(){

	var Request = false;
	if (window.XMLHttpRequest){
		//Gecko-совместимые браузеры, Safari
		Request = new XMLHttpRequest();
	}
	else if (window.ActiveXObject) {
		//Internet explorer
		try {
			Request = new ActiveXObject("Microsoft.XMLHTTP");
		}
		catch (CatchException){
			Request = new ActiveXObject("Msxml2.XMLHTTP");
		}
	}
	if (!Request){
	console.log("XMLHttpRequest hasn't created")
	}

	return Request;
} ;


//get cookie 
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// get csrf cookie
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    var host = document.location.host; 
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;

    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||

        !(/^(\/\/|http:|https:).*/.test(url));
}

// setup ajax (csrf cookie)
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function(){
	console.log('work work')
	$('#button_ajax').click(function(){
		var per1 = $('#test_ajax').val() ;
		
		$.post("/list/get_ajax/" , 
			   {per : per1} , 
			   function(data){
					$('#p_ajax').html(data) ;
				})
	})
})

// disappear navigator down
function hideNavigatorDown() {
	$(document).ready(function(){
		$('#navigator-down').hide() ; 
		$('#navigator').css('height', '50px') ;
		$('#illusion').css('height', '50px') ;
	})
}

// disappear input and button in navigator-down
function hideNavigatorDownInput() {
	$(document).ready(function() {
		$('#ndi-change').hide(1200) ;
		$('#ndb-change').hide(1200) ;
		//$('#ni-first').hide(1000) ;
})
}

//document ready 
$(document).ready(function(){
	
	$.post('/list/getICWW/' ,
	    {} ,
		function(data){ 
			json = JSON.parse(data) ;
		}
	)
	
	$('#ndb-info').click(function(){
		var tt = parseInt($('#ndi-info').val()) ;
		if ($('#' + tt.length)) {
			location.href = '/list/tt_info/' + tt + '/' ;    
		} else { 
			console.log('some alert') 
		} ; 
	})
})
