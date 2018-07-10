URL = 'http://127.0.0.1:5000/'

function post(section, data, callback, callbackError){

	$.ajax({
		  type: 'POST',
		  url: URL + section,
          data: data,
          dataType: 'json',
		  success:function(response){
              console.log(response);
		  	if(response.status == 'error-alert'){
				error(response.message);
				callbackError(response.data);
			}else if(response.status == 'success-alert')
			   {
					success(response.message);
					callback(response.data);
			   }else if(callback != null) callback(response.data);
		  }
	});
}

function get(section, data, callback, callbackError){

	$.ajax({
		  type: 'GET',
		  url: URL + section,
          data: data,
          dataType: 'json',
		  success:function(response){
			  
		  	if(response.status == 'error-alert'){
				  error(response.message);
				  callbackError(response.data);
			  }else if(response.status == 'success-alert')
			   {
					success(response.message);
					callback(response.data);
			   }else if(callback != null) callback(response.data);
		  }
	});
}


idxErrorAlert = -1;
function error(message){
    idxErrorAlert = idxErrorAlert+1;
    $('#message-layer').append('<div class="error-alert" id="error-alert-'+idxErrorAlert+'">'+message+'</div>');
    $('#error-alert-'+idxErrorAlert).fadeIn(3000).fadeOut(3000);
}

idxSuccessAlert = -1;
function success(message){
    idxSuccessAlert = idxSuccessAlert+1;
	$('#message-layer').append('<div class="success-alert" id="success-alert-'+idxSuccessAlert+'">'+message+'</div>');	
    $('#success-alert-'+idxSuccessAlert).fadeIn(3000).fadeOut(3000);
}