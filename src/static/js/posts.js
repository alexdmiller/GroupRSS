(function() {
  $(document).ready(function() {
    $(document).keydown(onKeyDown);
    $(window).scroll(_.throttle(retrievePostsIfScrolledToBottom, 1000));
    // Populate with first posts.
    retrievePostsIfScrolledToBottom();
  });


  // Indicates whether an AJAX call is being made.
  var currentlyRetrievingPosts = false;

  // Set to true when the server returns an empty page of posts.
  var noMorePages = false;

  // The index of the most recently retrieved page.
  var latestPageRetrieved = 0;

  function retrievePostsIfScrolledToBottom() {
    var windowScroll = $(window).scrollTop();
    var windowHeight = $(window).height();
    var bottomElementPosition = $('.post-loading-indicator').offset().top;
    if (bottomElementPosition >= windowScroll &&
        bottomElementPosition <= windowScroll + windowHeight) {
      getPosts(latestPageRetrieved + 1);
    }
  }

  function getPosts(page) {
    if (!currentlyRetrievingPosts && !noMorePages) {
      $('.post-loading-indicator .loader-icon').show();
      currentlyRetrievingPosts = true;
      $.get('/groups/' + GROUP_KEY_NAME + '/posts/' + page, onPostsReceived);      
    }
  }

  function onPostsReceived(event) {
    currentlyRetrievingPosts = false;
    latestPageRetrieved++;
    if (event == '') {
      noMorePages = true;
      $('.post-loading-indicator').html("That's all!");
    } else {
      $('.posts').append(event);
      $('.post-loading-indicator .loader-icon').hide();

      // Add event listeners to newly appended post elements.
      $('.posts .panel-body').off('show.bs.collapse');
      $('.posts .panel-body').off('shown.bs.collapse');
      $('.posts .panel-body').off('hide.bs.collapse');
      $('.posts .comment-submit').off('click');
      $('.posts .panel-body').on('show.bs.collapse', prePostOpen);
      $('.posts .panel-body').on('shown.bs.collapse', onPostOpen);
      $('.posts .panel-body').on('hide.bs.collapse', onPostClose);
      $('.posts .comment-submit').on('click', onPostComment);

      // If we still haven't filled up the screen, get more posts.
      retrievePostsIfScrolledToBottom();
    }
  }

  function prePostOpen(event) {
    $.post('/posts/' + event.target.id + '/read');
    $(event.target).parent().removeClass('unread');
    $(event.target).parent().addClass('selected-post');
  }

  function onPostOpen(event) {
    var commentStatus =  $(event.target).parent().find('.comment-count');
    if (commentStatus.hasClass('unread-comments')) {
      commentStatus.removeClass('unread-comments');
      commentStatus.addClass('read-comments');
    }

    $.get('/posts/' + event.target.id + '/comments',
        _.partial(onCommentsRecieved, event.target.id));
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
    console.log(id);
    $.post('/posts/' + id + '/comments', {
      content: textarea.val()
    }, function(posts) {
      textarea.val('');
      textarea.attr('disabled', false);
      onCommentsRecieved(id, posts);
    });
  }

  function onCommentsRecieved(id, posts) {
    $('#' + id).find('.post-comments').html(posts);
  }

  function onKeyDown(event) {
    if (!$('input,textarea').is(':focus')) {
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
        // Scroll up
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
    }
  }
})();
