function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  
  const csrftoken = getCookie('csrftoken');
  
  // Agrega el token CSRF a la configuración de AJAX
  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });
  
  $(document).ready(function() {
    var contador = 0;

    $('#agregar_producto').click(function() {
      // Obtener el token CSRF
      var csrfToken = $('#csrf_token').val();
      var depositoId = $('#depositoId').val();
      if(contador < 9) {
        var nuevoFormulario = `
          <tr>
            <td><strong class="campo_lote"></strong></td>
            <form action="" method="post">
              {% csrf_token %}
              
              <td>
                <select class="custom-select select_producto">
                  <option selected value="">Seleccione un producto</option>
                  {% for producto in stock_etiquetado %}
                      <option value="{{ producto.id }}" data-model="etiquetado">{{ producto.varietal }}</option>
                  {% endfor %}
                  {% for producto in stock_empaquetado %}
                      <option value="{{ producto.id }}" data-model="empaquetado">{{ producto.varietal }}</option>
                  {% endfor %}
              </select>
              </td>
              <td><strong class="tipo"></strong></td>
              <td><strong class="fecha_envasado"></strong></td>
              <td><input type="number" class="form-control" name=""></td>
              <td><button type="button" class="btn btn-block btn-outline-danger btn-sm eliminar_producto">Eliminar</button></td>
              <input type="hidden" name="deposito" value="${depositoId}">
              
            </form>
          </tr>`;
        $('table > tbody').append(nuevoFormulario);
        contador++;
      }
    });

    // Eliminar producto
    $('table').on('click', '.eliminar_producto', function() {
      $(this).closest('tr').remove();
      contador--;
    });

    $('table').on('change', '.select_producto', function() {
      var productoId = $(this).val();
      var tr = $(this).closest('tr');

      if(productoId === "seleccione_un_producto") {
        tr.find('.campo_lote').text('');  
        tr.find('.fecha_envasado').text(''); 
        tr.find('.tipo').text(''); 
      } else {
        $.ajax({
          url: '/get_producto_info/' + productoId + '/',
          dataType: 'json',
          success: function(data) {
            tr.find('.campo_lote').text(data.lote);  
            tr.find('.fecha_envasado').text(data.fecha_envasado); 
            tr.find('.tipo').text(data.tipo); 
          },
          error: function(xhr, status, error) {
            console.error("Error en AJAX: ", status, error);
          }
        });
      }
    });

    $('table').on('change', '.select_producto', function() {
      cambiarNombreCampoCantidad(this);
    });

    function cambiarNombreCampoCantidad(selectElement) {
      var modeloSeleccionado = selectElement.options[selectElement.selectedIndex].getAttribute('data-model');
      var campoCantidad = selectElement.closest('tr').querySelector('input[type=number]');
      
      if (modeloSeleccionado === 'etiquetado') {
          campoCantidad.name = 'cantidad_botellas';
      } else if (modeloSeleccionado === 'empaquetado') {
          campoCantidad.name = 'cantidad_cajas';
      } else {
          campoCantidad.name = ''; // Un valor por defecto, si es necesario
      }
    }

    $(document).on('click', '#boton_envio_general', function() {
      console.log("Botón cliqueado");
      var depositoId = $('#depositoId').val();
      var data = {};
  
      $('form').each(function(index) {
          $(this).serializeArray().forEach(function(field) {
              data[field.name + '_' + index] = field.value;
          });
      });
  
      console.log("URL: ", '/deposito/mover_stock/'+ depositoId + '/');
      console.log("Datos a enviar: ", data);
  
      $.ajax({
          type: 'POST',
          url: '/deposito/mover_stock/'+ depositoId + '/',
          data: data,
          success: function(response) {
              console.log("Respuesta exitosa: ");
          },
          error: function(xhr, status, error) {
              console.error("Error en AJAX: ", status, error);
          }
      });
  });
    
  });

