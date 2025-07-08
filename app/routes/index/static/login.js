(function () {
	'use strict'

	window.addEventListener('focus', function(event) {
		// Fetch all the item we want to apply custom behaviour
		var items = document.querySelectorAll('input[autofocus]')

		for (const [index, item] of items.entries()) {
			if(!item.value){
				document.getElementById(item.id).focus();
				document.getElementById(item.id).select();
				break;
			}
		}
	});
	
})()