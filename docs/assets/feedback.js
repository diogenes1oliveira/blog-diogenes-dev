/**
 * Post feedback widget — handles the 😊 / 😕 button clicks.
 *
 * Uses MkDocs Material's `document$` observable so that the handler
 * re-attaches correctly after soft navigations (instant loading).
 */

function postFeedback(btn, reaction) {
  var widget = btn.closest('.post-feedback');
  if (!widget) return;

  // Save to localStorage
  var slugAttr = widget.getAttribute('data-slug') || window.location.pathname;
  var slug = slugAttr.split('/').filter(Boolean).pop().replace('.md', '');
  var key = '/posts/slug=' + slug + '/feedbacks/binary';
  localStorage.setItem(key, reaction);

  // Toggle visual selection
  var buttons = widget.querySelectorAll('.post-feedback__btn');
  buttons.forEach(function (b) {
    b.classList.remove('selected');
  });
  btn.classList.add('selected');

  var msg = reaction === 'like'
    ? 'Thanks! I\'m glad you enjoyed it!'
    : "Thanks for the feedback, I'll use it to improve!";

  var toast = document.createElement('div');
  toast.className = 'custom-toast';
  toast.textContent = msg;
  toast.setAttribute('role', 'alert');
  widget.appendChild(toast);

  // Trigger reflow to start transition
  toast.offsetHeight;
  toast.classList.add('show');

  // Remove after 1.5 seconds
  setTimeout(function() {
    toast.classList.remove('show');
    setTimeout(function() {
      toast.remove();
    }, 300);
  }, 1500);
}
