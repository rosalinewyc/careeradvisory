$(".option").click(function(){
	$( this ).find( 'span' ).toggleClass( 'inactive' );
	$( this ).toggleClass('active');
	
});

$( "#btn-modal" ).click(function(){
	$( "#summary-list" ).empty();
	
	$( ".option" ).each(function() {
	  if( ! $( this ).children().hasClass( 'inactive' ))
	  	$( "#summary-list" ).append( "<li>" + $( this ).text() + "</li>" );

	});
	
	if( $( "#summary-list" ).children().length == 0 )
		$( "#summary-list" ).append( "<li>No options selected</li>" );
	
});

$( "#btn-reset" ).click( function(){
	$( ".option" ).each( function(){
		$( this ).children().addClass( 'inactive' );
		$( this ).removeClass( 'active' );

	});
});
