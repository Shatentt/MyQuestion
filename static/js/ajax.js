function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function() {
    $('.js-vote').click(function() {
        const $btn = $(this);
        const questionId = $btn.data('id');
        const voteType = $btn.data('type');
        const objType = $btn.data('obj');
        
        const $container = $btn.closest('.rate');
        const $btnLike = $container.find('[data-type="like"]');
        const $btnDislike = $container.find('[data-type="dislike"]');

        $.ajax({
            url: '/vote/',
            type: 'POST',
            data: {
                'data_id': questionId,
                'vote_type': voteType,
                'obj_type': objType,
            },
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            
            success: function(response) {
                console.log("Success:", response);

                if (response.new_rating !== undefined) {
                    $btn.closest('.question-answer__likes').find('.like_count').text(response.new_rating);

                    const userVote = response.user_vote;
                    
                    if (userVote === 1) {
                        $btnLike.prop('disabled', true);
                        $btnDislike.prop('disabled', false);
                    } else if (userVote === -1) {
                        $btnLike.prop('disabled', false);
                        $btnDislike.prop('disabled', true);
                    }
                }
            },
            error: function(xhr, status, error) {
                if (xhr.status === 403 || xhr.status === 401) {
                    window.location.href = '/login/?next=' + window.location.pathname;
                } else {
                    console.log('Error: ' + error);
                }
            }
        });
    });
    $('.js-correct').change(function() {
        const $checkbox = $(this);
        const answerId = $checkbox.data('aid');
        
        $.ajax({
            url: '/correct/',
            type: 'POST',
            data: {
                'answer_id': answerId,
            },
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            
            success: function(response) {
                if (response.status === 'ok') {
                    if (response.is_correct) {
                        $('.js-correct').not($checkbox).prop('checked', false);
                    }
                } else {
                    console.log("Error logic:", response);
                }
            },
            error: function(xhr, status, error) {
                console.log("AJAX Error:", error);
                $checkbox.prop('checked', !$checkbox.prop('checked'));
                alert("Something went wrong or you don't have permission.");
            }
        });
    });
});