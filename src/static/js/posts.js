(function() {
  $('.posts .panel-body').on('show.bs.collapse', onPostOpen);
  $('.posts .panel-body').on('hide.bs.collapse', onPostClose);
  $('.posts .comment-submit').on('click', onPostComment);

  function onPostOpen(event) {
    $.post('/posts/' + event.target.id + '/read');
    $(event.target).parent().removeClass('unread');
    $(event.target).parent().addClass('selected-post');
    
    var commentStatus =  $(event.target).parent().find('.comment-count');
    if (commentStatus.hasClass('unread-comments')) {
      commentStatus.removeClass('unread-comments');
      commentStatus.addClass('read-comments');
    }

    $.get('/posts/' + event.target.id + '/comments',
        _.partial(onPostsRecieved, event.target.id));
  }

  function onPostClose(event) {
    $(event.target).parent().removeClass('selected-post');
  }

  function onPostComment(event) {
    var postBody = $(event.target).parents('.panel-body');
    var id = postBody.attr('id');
    var textarea = postBody.find('.comment-content');
    textarea.attr('disabled', true);
    $.post('/posts/' + id + '/comments', {
      content: textarea.val()
    }, function(posts) {
      textarea.val('');
      textarea.attr('disabled', false);
      onPostsRecieved(id, posts);
    });
  }

  function onPostsRecieved(id, posts) {
    $('#' + id).find('.post-comments').html(posts);
  }
})();
