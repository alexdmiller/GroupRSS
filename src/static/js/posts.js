(function() {
  $('.posts .panel-body').on('show.bs.collapse', onPostOpen);

  function onPostOpen(event) {
    $.post('/posts/' + event.target.id + '/read');
    $(event.target).parent().removeClass('unread');
  }  
})();
