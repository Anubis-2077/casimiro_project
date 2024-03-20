$(document).ready(function() {
    // Abrir el aside
    $("#openAsideBtn").click(function() {
        $("#myAside").show().css('transform', 'translateX(0)'); // Muestra y mueve el aside
        $("#backdrop").show(); // Muestra el backdrop
    });

    // Cerrar el aside con el botón de cierre
    $("#closeAsideBtn").click(function() {
        $("#myAside").css('transform', 'translateX(-100%)'); // Oculta el aside
        $("#backdrop").hide(); // Oculta el backdrop
    });

    // Opcional: cerrar el aside haciendo clic en el backdrop
    $("#backdrop").click(function() {
        $("#myAside").css('transform', 'translateX(-100%)');
        $(this).hide();
    });
});


$(document).ready(function() {
    $('.btn-incremento').click(function() {
        // Encuentra el input de cantidad relacionado y aumenta su valor
        var cantidadInput = $(this).siblings('.cantidad-input');
        var valorActual = parseInt(cantidadInput.val());
        cantidadInput.val(valorActual + 1);
    });

    $('.btn-decremento').click(function() {
        // Encuentra el input de cantidad relacionado y disminuye su valor, pero no menos de 1
        var cantidadInput = $(this).siblings('.cantidad-input');
        var valorActual = parseInt(cantidadInput.val());
        if (valorActual > 1) {
            cantidadInput.val(valorActual - 1);
        }
    });
});