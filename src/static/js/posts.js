(function() {
  $('.posts .panel-body').on('shown.bs.collapse', onPostOpen);
  $('.posts .panel-body').on('hide.bs.collapse', onPostClose);
  $('.posts .comment-submit').on('click', onPostComment);
  $(document).keydown(function(event) {
    console.log(event.keyCode);
    if (event.keyCode == 74) {
      // Scroll down
      if ($('.selected-post').length > 0) {
        var next = $('.selected-post').next();
        $('.selected-post').find('.post-panel').collapse('toggle');
        next.find('.post-panel').collapse('toggle');
      } else {
        $('.post-panel').first().collapse('toggle');
      }
    } else if (event.keyCode == 75) {
      if ($('.selected-post').length > 0) {
        var previous = $('.selected-post').prev();
        $('.selected-post').find('.post-panel').collapse('toggle');
        previous.find('.post-panel').collapse('toggle');
      }
    } else if (event.keyCode == 79) {
      if ($('.selected-post').length > 0) {
        window.open($('.selected-post').find('.post-link').attr('href'));
      }
    }
  });

  function onPostOpen(event) {
    console.log(event.target);
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
    $('html,body').animate({
      scrollTop: $(event.target).parent().offset().top - 10
    });
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
