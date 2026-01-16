// static/js/posts.js

document.addEventListener('DOMContentLoaded', function() {
    // Like functionality
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', async function() {
            const postId = this.closest('.post-card').dataset.postId;
            try {
                const response = await fetch(`/accounts/post/${postId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                });
                const data = await response.json();
                
                const likesCount = this.querySelector('.likes-count');
                likesCount.textContent = data.likes_count;
                
                if (data.liked) {
                    this.classList.add('liked');
                    this.querySelector('i').classList.replace('bi-heart', 'bi-heart-fill');
                } else {
                    this.classList.remove('liked');
                    this.querySelector('i').classList.replace('bi-heart-fill', 'bi-heart');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });

    // Comment functionality
    document.querySelectorAll('.comment-button').forEach(button => {
        button.addEventListener('click', function() {
            const commentsSection = this.closest('.post-card').querySelector('.comments-section');
            commentsSection.style.display = commentsSection.style.display === 'none' ? 'block' : 'none';
        });
    });

    document.querySelectorAll('.comment-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const postId = this.closest('.post-card').dataset.postId;
            const input = this.querySelector('input');
            const content = input.value.trim();
            
            if (!content) return;
            
            try {
                const response = await fetch(`/accounts/post/${postId}/comment/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ content }),
                });
                
                const data = await response.json();
                if (data.success) {
                    const commentsList = this.closest('.comments-section').querySelector('.comments-list');
                    commentsList.insertAdjacentHTML('beforeend', data.comment_html);
                    input.value = '';
                    
                    // Update comment count
                    const commentCount = this.closest('.post-card').querySelector('.comments-count');
                    commentCount.textContent = parseInt(commentCount.textContent) + 1;
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });

    // Poll functionality
    document.querySelectorAll('.poll-options').forEach(pollDiv => {
        const endsAt = new Date(pollDiv.dataset.endsAt);
        
        function updateTimer() {
            const now = new Date();
            const timeLeft = endsAt - now;
            
            if (timeLeft <= 0) {
                pollDiv.querySelector('.poll-timer').textContent = 'Poll ended';
                return;
            }
            
            const hours = Math.floor(timeLeft / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            pollDiv.querySelector('.poll-timer').textContent = `${hours}h ${minutes}m`;
        }
        
        updateTimer();
        setInterval(updateTimer, 60000);
        
        pollDiv.querySelectorAll('.poll-option button').forEach(button => {
            button.addEventListener('click', async function() {
                const optionId = this.closest('.poll-option').dataset.optionId;
                
                try {
                    const response = await fetch(`/accounts/poll/vote/${optionId}/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        },
                    });
                    
                    const data = await response.json();
                    if (data.results) {
                        Object.entries(data.results).forEach(([optionId, result]) => {
                            const option = pollDiv.querySelector(`[data-option-id="${optionId}"]`);
                            option.querySelector('.progress-bar').style.width = `${result.percentage}%`;
                            option.querySelector('.vote-count').textContent = `(${result.votes})`;
                        });
                        
                        // Disable all buttons after voting
                        pollDiv.querySelectorAll('button').forEach(btn => btn.disabled = true);
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            });
        });
    });
});